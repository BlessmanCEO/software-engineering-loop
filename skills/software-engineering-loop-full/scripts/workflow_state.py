#!/usr/bin/env python3
"""Durable state, evidence, attempt, and writer-lock checks for the loop."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from workflow_checks import previous_slices_complete, problems, require_no_writer, self_test
from workflow_cli import build_parser
from workflow_evidence import EMPTY_DIFF_HASH, content_hash, evidence_snapshot, git, non_record_dirty, run_with_evidence
from workflow_health import health
from workflow_policy import check_command_policy, verify_policy
from workflow_resume import resume_status
from workflow_store import acquire_finalizer, acquire_writer, read_state, release_writer, write_state

SLICE_STATUSES = {"planned", "in_progress", "complete", "blocked"}
FINAL_GATES = (
    "completion", "codex", "system", "security", "migration", "compatibility",
    "concurrency", "performance", "ux_accessibility", "operations", "premortem", "recovery",
)
REQUIRED_FINAL_GATES = {"completion", "codex", "system"}
MAX_ATTEMPTS = 2
REVIEW_ORDER = FINAL_GATES


def require_choice(value: str, choices: set[str], label: str) -> str:
    if value not in choices:
        raise SystemExit(f"{label} must be one of: {', '.join(sorted(choices))}")
    return value


def command_args(values: list[str]) -> list[str]:
    values = values[1:] if values[:1] == ["--"] else values
    if not values:
        raise SystemExit("command is required after --")
    return values


def require_attempt(attempt: int) -> None:
    if attempt < 1 or attempt > MAX_ATTEMPTS:
        raise SystemExit(f"attempt must be between 1 and {MAX_ATTEMPTS}")


def init(args) -> None:
    args.run_id = args.run_id or datetime.now(UTC).strftime("se-%Y%m%d-%H%M%S-%f")
    args.plan_id = args.plan_id or args.run_id
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.run_id):
        raise SystemExit("run ID may contain only letters, numbers, dot, underscore, and hyphen")
    if args.run_id in {".", ".."}:
        raise SystemExit("run ID cannot be dot or dot-dot")
    repo = Path(args.repo).resolve()
    root = Path(git(repo, "rev-parse", "--show-toplevel").decode().strip())
    if non_record_dirty(root) and not args.allow_dirty:
        raise SystemExit("worktree is dirty; preserve or explicitly scope existing changes first")
    if len(set(args.slices)) != len(args.slices):
        raise SystemExit("slice IDs must be unique")

    raw_base = root / ".codex" / "software-engineering"
    if any(path.is_symlink() for path in (root / ".codex", raw_base)):
        raise SystemExit("workflow record directories cannot be symlinks")
    base_dir = raw_base.resolve()
    if not base_dir.is_relative_to(root):
        raise SystemExit("workflow record directory must remain inside the repository")
    run_dir = (base_dir / args.run_id).resolve()
    if run_dir.parent != base_dir:
        raise SystemExit("run directory must be a direct child of .codex/software-engineering")
    if run_dir.exists() or run_dir.is_symlink():
        raise SystemExit(f"run already exists: {run_dir}")
    state = {
        "runId": args.run_id,
        "repo": str(root),
        "taskClass": args.task_class,
        "status": "planning",
        "planId": args.plan_id,
        "currentSlice": args.slices[0] if args.slices else None,
        "maxAttempts": MAX_ATTEMPTS,
        "writerLock": None,
        "slices": {
            slice_id: {
                "status": "planned",
                "closedSnapshot": None,
            }
            for slice_id in args.slices
        },
        "reviews": {
            name: {
                "status": "pending" if name in REQUIRED_FINAL_GATES else "not_required",
                "required": name in REQUIRED_FINAL_GATES,
                "attempts": 0,
                "evidence": "",
                "reviewedSha": None,
                "diffHash": None,
                "contentHash": None,
                "commandRuns": [],
                "history": [],
            }
            for name in FINAL_GATES
        },
        "checkpointSha": None,
        "finalSha": None,
        "finalValidation": "pending",
        "finalValidationAttempts": 0,
        "finalValidationRuns": [],
        "pushed": False,
    }
    write_state(run_dir, state)
    (run_dir / "slices").mkdir()
    print(run_dir)


def set_slice_status(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    if args.slice not in state["slices"]:
        raise SystemExit(f"unknown slice: {args.slice}")
    status = require_choice(args.status, SLICE_STATUSES, "slice status")
    record = state["slices"][args.slice]
    if record["status"] in {"complete", "blocked"}:
        raise SystemExit(f"terminal slice cannot transition from {record['status']}")
    if not previous_slices_complete(state, args.slice):
        raise SystemExit("previous slice is not complete")
    if status == "planned":
        raise SystemExit("cannot transition a slice back to planned")
    if status == "in_progress":
        raise SystemExit("acquire-writer is the only transition into in_progress")
    if status == "complete":
        require_no_writer(run_dir, state)
        if record["status"] != "in_progress":
            raise SystemExit("slice must be in progress")
        record["closedSnapshot"] = evidence_snapshot(Path(state["repo"]))
    record["status"] = status
    state["currentSlice"] = args.slice
    state["status"] = "blocked" if status == "blocked" else "running"
    write_state(run_dir, state)


def record_final_validation(args) -> None:
    require_attempt(args.attempt)
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    require_no_writer(run_dir, state)
    required_reviews = [
        review for name, review in state["reviews"].items()
        if name not in {"completion", "codex"} and review.get("required", True)
    ]
    if any(review["status"] != "pass" for review in required_reviews):
        raise SystemExit("final validation requires all unified and triggered reviews to pass")
    previous = state.get("finalValidationAttempts", 0)
    prior = [item for item in state.get("finalValidationRuns", []) if item.get("attempt") == previous]
    current_hash = content_hash(Path(state["repo"]))
    changed = bool(prior) and any(item.get("contentHash") != current_hash for item in prior)
    expected = 1 if previous == 0 else previous + 1 if changed else previous
    if args.attempt != expected:
        raise SystemExit(f"final validation attempt must be {expected}")
    command = command_args(args.command)
    check_command_policy(command)
    run = run_with_evidence(Path(state["repo"]), command, args.attempt)
    state.setdefault("finalValidationRuns", []).append(run)
    state["finalValidationAttempts"] = args.attempt
    current = [item for item in state["finalValidationRuns"] if item["attempt"] == args.attempt]
    state["finalValidation"] = "pass" if all(item["exitCode"] == 0 for item in current) else "changes_requested"
    if args.attempt == MAX_ATTEMPTS and state["finalValidation"] != "pass":
        state["finalValidation"] = "blocked"
        state["status"] = "blocked"
    write_state(run_dir, state)
    print(json.dumps(run, indent=2))
    if run["exitCode"]:
        raise SystemExit(run["exitCode"])


def set_review(args) -> None:
    require_attempt(args.attempt)
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    if args.name not in state["reviews"]:
        raise SystemExit(f"unknown review: {args.name}")
    require_no_writer(run_dir, state)
    review = state["reviews"][args.name]
    previous = review.get("attempts", 0)
    command_attempt = max((item.get("attempt", 0) for item in review.get("commandRuns", [])), default=0)
    index = REVIEW_ORDER.index(args.name)
    if any(state["reviews"][name]["status"] not in {"pass", "degraded", "not_required"} for name in REVIEW_ORDER[:index]):
        raise SystemExit("previous final review has not passed")
    if args.name == "codex" and not state.get("checkpointSha"):
        raise SystemExit("Codex review requires a checkpoint commit")
    if args.name == "completion" and any(
        record["status"] != "complete" for record in state["slices"].values()
    ):
        raise SystemExit("completion review requires every slice complete")
    snapshot = evidence_snapshot(Path(state["repo"]))
    if review["status"] in {"pending", "not_required"}:
        expected = max(previous + 1, command_attempt, 1)
    elif review["status"] == "changes_requested":
        expected = previous + 1
    elif review["status"] == "pass" and review.get("contentHash") != snapshot["contentHash"]:
        expected = previous + 1
    else:
        raise SystemExit(f"cannot rerun {args.name} from {review['status']}")
    if args.attempt != expected:
        raise SystemExit(f"review attempt must be {expected}")
    allowed_statuses = {"pass", "changes_requested", "blocked"}
    if args.name == "codex":
        allowed_statuses.add("degraded")
    status = require_choice(args.status, allowed_statuses, "review status")
    if status in {"pass", "degraded"} and not args.evidence:
        raise SystemExit(f"{status} review requires evidence")
    terminal_failure = args.attempt == MAX_ATTEMPTS and status in {"changes_requested", "blocked"}
    review.update(
        status="blocked" if terminal_failure else status,
        required=True,
        attempts=args.attempt,
        evidence=args.evidence,
        reviewedSha=args.sha or snapshot["headSha"],
        diffHash=snapshot["diffHash"],
        contentHash=snapshot["contentHash"],
    )
    review.setdefault("history", []).append(
        {"attempt": args.attempt, "status": status, "evidence": args.evidence, **snapshot}
    )
    if terminal_failure or status == "blocked":
        state["status"] = "blocked"
    write_state(run_dir, state)


def record_review_command(args) -> None:
    require_attempt(args.attempt)
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    if args.name not in state["reviews"]:
        raise SystemExit(f"unknown review: {args.name}")
    require_no_writer(run_dir, state)
    previous = max(
        (item.get("attempt", 0) for item in state["reviews"][args.name].get("commandRuns", [])),
        default=0,
    )
    if args.attempt < previous or args.attempt > previous + 1:
        raise SystemExit(f"review command attempt must be {previous} or {previous + 1}")
    command = command_args(args.command)
    if args.name == "codex":
        expected = ["codex", "review", "--commit", state.get("checkpointSha")]
        if args.sha != state.get("checkpointSha") or command != expected:
            raise SystemExit("Codex review command must exactly review the checkpoint commit")
    check_command_policy(command)
    run = run_with_evidence(Path(state["repo"]), command, args.attempt, args.sha)
    state["reviews"][args.name].setdefault("commandRuns", []).append(run)
    write_state(run_dir, state)
    print(json.dumps(run, indent=2))
    if run["exitCode"]:
        raise SystemExit(run["exitCode"])


def set_commit(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    repo = Path(state["repo"])
    try:
        sha = git(repo, "rev-parse", f"{args.sha}^{{commit}}").decode().strip()
    except subprocess.CalledProcessError:
        raise SystemExit(f"not a commit: {args.sha}") from None
    snapshot = evidence_snapshot(repo)
    if sha != snapshot["headSha"] or snapshot["diffHash"] != EMPTY_DIFF_HASH:
        raise SystemExit("recorded commit must be current HEAD with a clean non-record worktree")
    if args.kind == "checkpoint":
        if any(record["status"] != "complete" for record in state["slices"].values()):
            raise SystemExit("checkpoint requires all slices complete")
        completion = state["reviews"]["completion"]
        if completion["status"] != "pass" or completion.get("contentHash") != snapshot["contentHash"]:
            raise SystemExit("checkpoint content must pass completion review")
    else:
        checkpoint = state.get("checkpointSha")
        if not checkpoint:
            raise SystemExit("final commit requires a checkpoint commit")
        if sha != checkpoint:
            try:
                git(repo, "merge-base", "--is-ancestor", checkpoint, sha)
            except subprocess.CalledProcessError:
                raise SystemExit("final repair commit must descend from the reviewed checkpoint") from None
        system = state["reviews"]["system"]
        if system["status"] != "pass" or system.get("contentHash") != snapshot["contentHash"]:
            raise SystemExit("final content was not passed by system review")
        if any(
            review["status"] != "pass"
            for name, review in state["reviews"].items()
            if name not in {"completion", "codex", "system"} and review.get("required", True)
        ):
            raise SystemExit("a triggered specialist review did not pass")
        runs = [
            item for item in state.get("finalValidationRuns", [])
            if item.get("attempt") == state.get("finalValidationAttempts")
        ]
        if state.get("finalValidation") != "pass" or not runs or any(
            item["exitCode"] != 0 or item.get("contentHash") != snapshot["contentHash"] for item in runs
        ):
            raise SystemExit("final content lacks passing validation evidence")
    key = "checkpointSha" if args.kind == "checkpoint" else "finalSha"
    state[key] = sha
    write_state(run_dir, state)


def check(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    snapshot = evidence_snapshot(Path(state["repo"])) if args.final else None
    issues = problems(state, args.final, run_dir, snapshot)
    if issues:
        print("\n".join(issues))
        raise SystemExit(2)
    if args.final:
        state["status"] = "degraded" if state["reviews"]["codex"]["status"] == "degraded" else "passed"
        write_state(run_dir, state)
    print(state["status"])


if __name__ == "__main__":
    handlers = {
        "init": init, "set-slice-status": set_slice_status,
        "record-final-validation": record_final_validation,
        "set-review": set_review,
        "record-review-command": record_review_command, "acquire-writer": acquire_writer,
        "acquire-finalizer": acquire_finalizer, "release-writer": release_writer,
        "set-commit": set_commit, "check": check, "resume-status": resume_status,
        "health": health, "self-test": self_test,
    }
    arguments = build_parser(handlers, FINAL_GATES).parse_args()
    if not hasattr(arguments, "function"):
        arguments.command_name, arguments.function = "health", health
    if arguments.command_name == "init":
        verify_policy()
    arguments.function(arguments)
