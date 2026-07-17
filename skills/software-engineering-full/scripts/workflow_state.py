#!/usr/bin/env python3
"""Durable state, evidence, attempt, and writer-lock checks for the loop."""

from __future__ import annotations

import json
import hashlib
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from workflow_checks import dependencies_complete, problems, require_no_validation, require_no_writer, self_test
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


def parse_dependencies(raw: str, slices: list[str]) -> dict[str, list[str]]:
    try:
        supplied = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SystemExit(f"dependencies must be a JSON object: {error}") from None
    if not isinstance(supplied, dict):
        raise SystemExit("dependencies must be a JSON object")
    dependencies = {slice_id: supplied.get(slice_id, []) for slice_id in slices}
    if any(not isinstance(items, list) for items in dependencies.values()):
        raise SystemExit("each dependency value must be a JSON list")
    known = set(slices)
    for slice_id, items in dependencies.items():
        if len(items) != len(set(items)) or any(item not in known or item == slice_id for item in items):
            raise SystemExit(f"invalid dependencies for {slice_id}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(slice_id: str) -> None:
        if slice_id in visiting:
            raise SystemExit("slice dependencies contain a cycle")
        if slice_id in visited:
            return
        visiting.add(slice_id)
        for dependency in dependencies[slice_id]:
            visit(dependency)
        visiting.remove(slice_id)
        visited.add(slice_id)

    for slice_id in slices:
        visit(slice_id)
    return dependencies


def plugin_version() -> str:
    manifest = Path(__file__).parents[3] / ".codex-plugin" / "plugin.json"
    return json.loads(manifest.read_text())["version"]


def artifact_hashes(run_dir: Path) -> dict[str, str]:
    files = [run_dir / "plan.md"]
    for directory in ("slices", "evidence", "reviews", "logs"):
        files.extend(path for path in (run_dir / directory).glob("**/*") if path.is_file() and path.name != "manifest.json")
    return {
        str(path.relative_to(run_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(files)
        if path.is_file()
    }


def require_same_repository(repo: Path, worktree: Path) -> None:
    def common_dir(path: Path) -> Path:
        value = git(path, "rev-parse", "--git-common-dir").decode().strip()
        return (path / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()

    if common_dir(repo) != common_dir(worktree):
        raise SystemExit("validation worktree does not belong to the run repository")


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
    dependencies = parse_dependencies(args.dependencies_json, args.slices)
    created_at = datetime.now(UTC).isoformat()

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
        "schemaVersion": 1,
        "pluginVersion": plugin_version(),
        "revision": 0,
        "runId": args.run_id,
        "repo": str(root),
        "taskClass": args.task_class,
        "status": "planning",
        "planId": args.plan_id,
        "currentSlice": args.slices[0] if args.slices else None,
        "maxAttempts": MAX_ATTEMPTS,
        "createdAt": created_at,
        "updatedAt": created_at,
        "activeOperations": [],
        "writerLock": None,
        "writerLease": None,
        "validationLease": None,
        "recovery": {"resumable": True, "lastAction": "initialized"},
        "slices": {
            slice_id: {
                "status": "planned",
                "phase": "planned",
                "dependsOn": dependencies[slice_id],
                "worktree": None,
                "baseSha": None,
                "baseContentHash": None,
                "patchHash": None,
                "validation": "pending",
                "validationAttempts": 0,
                "validationRuns": [],
                "review": {"status": "pending", "attempts": 0, "evidence": "", "history": [], "contentHash": None},
                "proofStatus": "pending",
                "handoff": "",
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
    for directory in ("slices", "evidence", "reviews", "logs"):
        (run_dir / directory).mkdir()
    (run_dir / "plan.md").write_text("# Plan\n\n")
    for slice_id in args.slices:
        (run_dir / "slices" / f"{slice_id}.md").write_text(f"# {slice_id}\n\n")
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
    if not dependencies_complete(state, args.slice):
        raise SystemExit("slice dependencies are not complete")
    if status == "planned":
        raise SystemExit("cannot transition a slice back to planned")
    if status == "in_progress":
        raise SystemExit("acquire-writer is the only transition into in_progress")
    if status == "complete":
        require_no_writer(run_dir, state)
        require_no_validation(state)
        if record["status"] != "in_progress":
            raise SystemExit("slice must be in progress")
        if record.get("validation") != "pass" or record.get("review", {}).get("status") != "pass":
            raise SystemExit("slice requires passing validation and unified review")
        if args.proof_status != "pass" or not args.handoff:
            raise SystemExit("slice closure requires passing proof obligations and handoff notes")
        snapshot = evidence_snapshot(Path(state["repo"]))
        if record["review"].get("contentHash") != snapshot["contentHash"]:
            raise SystemExit("slice content changed after unified review")
        record["proofStatus"] = "pass"
        record["handoff"] = args.handoff
        record["closedSnapshot"] = snapshot
        record["phase"] = "complete"
    record["status"] = status
    state["currentSlice"] = args.slice
    state["status"] = "blocked" if status == "blocked" else "running"
    write_state(run_dir, state)


def record_slice_validation(args) -> None:
    require_attempt(args.attempt)
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    require_no_writer(run_dir, state)
    require_no_validation(state)
    if args.slice not in state["slices"]:
        raise SystemExit(f"unknown slice: {args.slice}")
    record = state["slices"][args.slice]
    if record["status"] not in {"planned", "in_progress"}:
        raise SystemExit("cannot validate a terminal slice")
    previous = record.get("validationAttempts", 0)
    expected = 1 if record["validation"] == "pending" else previous + 1 if record["validation"] == "changes_requested" else previous
    if args.attempt != expected:
        raise SystemExit(f"slice validation attempt must be {expected}")
    worktree = Path(args.worktree).resolve()
    repo = Path(state["repo"])
    require_same_repository(repo, worktree)
    command = command_args(args.command)
    check_command_policy(command)
    lease = {"phase": "slice_validation", "slice": args.slice, "attempt": args.attempt, "worktree": str(worktree)}
    state["validationLease"] = lease
    state["activeOperations"] = [lease]
    write_state(run_dir, state)
    index = len(record.get("validationRuns", [])) + 1
    run = run_with_evidence(worktree, command, args.attempt, log_path=run_dir / "logs" / f"{args.slice}-validation-{args.attempt}-{index}.log")
    record.setdefault("validationRuns", []).append(run)
    record["validationAttempts"] = args.attempt
    current = [item for item in record["validationRuns"] if item["attempt"] == args.attempt]
    record["validation"] = "pass" if all(item["exitCode"] == 0 and not item["mutatedContent"] for item in current) else "changes_requested"
    record.update(
        worktree=str(worktree), baseSha=run["headSha"], baseContentHash=run["preContentHash"],
        patchHash=run["diffHash"], phase="validated" if record["validation"] == "pass" else "validation_failed",
    )
    state["validationLease"] = None
    state["activeOperations"] = []
    if args.attempt == MAX_ATTEMPTS and record["validation"] != "pass":
        record["validation"] = "blocked"
        record["status"] = "blocked"
        state["status"] = "blocked"
    write_state(run_dir, state)
    (run_dir / "evidence" / f"{args.slice}-validation.json").write_text(
        json.dumps(record["validationRuns"], indent=2) + "\n"
    )
    print(json.dumps(run, indent=2))
    if run["exitCode"] or run["mutatedContent"]:
        raise SystemExit(run["exitCode"] or 2)


def set_slice_review(args) -> None:
    require_attempt(args.attempt)
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    require_no_writer(run_dir, state)
    require_no_validation(state)
    if args.slice not in state["slices"]:
        raise SystemExit(f"unknown slice: {args.slice}")
    record = state["slices"][args.slice]
    if record["status"] != "in_progress" or record.get("validation") != "pass":
        raise SystemExit("slice review requires integrated content with passing validation")
    review = record["review"]
    previous = review.get("attempts", 0)
    snapshot = evidence_snapshot(Path(state["repo"]))
    if review["status"] == "pending":
        expected = 1
    elif review["status"] == "changes_requested" or review.get("contentHash") != snapshot["contentHash"]:
        expected = previous + 1
    else:
        raise SystemExit(f"cannot rerun slice review from {review['status']}")
    if args.attempt != expected:
        raise SystemExit(f"slice review attempt must be {expected}")
    status = require_choice(args.status, {"pass", "changes_requested", "blocked"}, "slice review status")
    if status == "pass" and not args.evidence:
        raise SystemExit("passing slice review requires evidence")
    terminal = args.attempt == MAX_ATTEMPTS and status != "pass"
    review.update(status="blocked" if terminal else status, attempts=args.attempt, evidence=args.evidence, contentHash=snapshot["contentHash"])
    review.setdefault("history", []).append({"attempt": args.attempt, "status": status, "evidence": args.evidence, "areas": args.areas, **snapshot})
    if terminal or status == "blocked":
        record["status"] = "blocked"
        state["status"] = "blocked"
    write_state(run_dir, state)
    (run_dir / "reviews" / f"{args.slice}.json").write_text(json.dumps(review, indent=2) + "\n")


def record_final_validation(args) -> None:
    require_attempt(args.attempt)
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    require_no_writer(run_dir, state)
    require_no_validation(state)
    required_reviews = [
        name for name, review in state["reviews"].items()
        if name not in {"completion", "codex"} and review.get("required", True)
    ]
    if any(state["reviews"][name]["status"] != "pass" for name in required_reviews):
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
    lease = {"phase": "final_validation", "attempt": args.attempt}
    state["validationLease"] = lease
    state["activeOperations"] = [lease]
    write_state(run_dir, state)
    index = len(state.get("finalValidationRuns", [])) + 1
    run = run_with_evidence(
        Path(state["repo"]), command, args.attempt,
        log_path=run_dir / "logs" / f"final-validation-{args.attempt}-{index}.log",
    )
    state.setdefault("finalValidationRuns", []).append(run)
    state["finalValidationAttempts"] = args.attempt
    current = [item for item in state["finalValidationRuns"] if item["attempt"] == args.attempt]
    state["finalValidation"] = "pass" if all(
        item["exitCode"] == 0 and not item["mutatedContent"] for item in current
    ) else "changes_requested"
    state["validationLease"] = None
    state["activeOperations"] = []
    if args.attempt == MAX_ATTEMPTS and state["finalValidation"] != "pass":
        state["finalValidation"] = "blocked"
        state["status"] = "blocked"
    write_state(run_dir, state)
    (run_dir / "evidence" / "final-validation.json").write_text(
        json.dumps(state["finalValidationRuns"], indent=2) + "\n"
    )
    print(json.dumps(run, indent=2))
    if run["exitCode"] or run["mutatedContent"]:
        raise SystemExit(run["exitCode"] or 2)


def set_review(args) -> None:
    require_attempt(args.attempt)
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    if args.name not in state["reviews"]:
        raise SystemExit(f"unknown review: {args.name}")
    require_no_writer(run_dir, state)
    require_no_validation(state)
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
    (run_dir / "reviews" / f"{args.name}.json").write_text(json.dumps(review, indent=2) + "\n")


def record_review_command(args) -> None:
    require_attempt(args.attempt)
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    if args.name not in state["reviews"]:
        raise SystemExit(f"unknown review: {args.name}")
    require_no_writer(run_dir, state)
    require_no_validation(state)
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
    run = run_with_evidence(
        Path(state["repo"]), command, args.attempt, args.sha,
        log_path=run_dir / "logs" / f"{args.name}-command-{args.attempt}.log",
    )
    state["reviews"][args.name].setdefault("commandRuns", []).append(run)
    write_state(run_dir, state)
    print(json.dumps(run, indent=2))
    if run["exitCode"] or run["mutatedContent"]:
        raise SystemExit(run["exitCode"] or 2)


def release_validation(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    lease = state.get("validationLease")
    if not lease:
        raise SystemExit("validation lease is not held")
    if lease.get("slice") in state["slices"]:
        record = state["slices"][lease["slice"]]
        if record["status"] != "blocked":
            record["validation"] = "changes_requested"
            record["phase"] = "validation_interrupted"
    state["validationLease"] = None
    state["activeOperations"] = []
    state.setdefault("recovery", {})["lastAction"] = args.reason
    write_state(run_dir, state)


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
        state["checkpointEvidence"] = artifact_hashes(run_dir)
    else:
        checkpoint = state.get("checkpointSha")
        if not checkpoint:
            raise SystemExit("final commit requires a checkpoint commit")
        if sha != checkpoint:
            try:
                git(repo, "merge-base", "--is-ancestor", checkpoint, sha)
            except subprocess.CalledProcessError:
                raise SystemExit("final repair commit must descend from the reviewed checkpoint") from None
        for name, review in state["reviews"].items():
            if name in {"completion", "codex"} or not review.get("required", True):
                continue
            if review["status"] != "pass" or review.get("contentHash") != snapshot["contentHash"]:
                raise SystemExit(f"final content was not passed by {name} review")
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
        manifest = {
            "schemaVersion": state.get("schemaVersion"),
            "pluginVersion": state.get("pluginVersion"),
            "runId": state["runId"],
            "status": state["status"],
            "checkpointSha": state["checkpointSha"],
            "finalSha": state["finalSha"],
            "contentHash": snapshot["contentHash"],
            "artifacts": artifact_hashes(run_dir),
        }
        manifest_path = run_dir / "evidence" / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        state["evidenceManifestSha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        write_state(run_dir, state)
    print(state["status"])


if __name__ == "__main__":
    handlers = {
        "init": init, "set-slice-status": set_slice_status,
        "record-slice-validation": record_slice_validation, "set-slice-review": set_slice_review,
        "record-final-validation": record_final_validation,
        "set-review": set_review,
        "record-review-command": record_review_command, "acquire-writer": acquire_writer,
        "acquire-finalizer": acquire_finalizer, "release-writer": release_writer,
        "release-validation": release_validation,
        "set-commit": set_commit, "check": check, "resume-status": resume_status,
        "health": health, "self-test": self_test,
    }
    arguments = build_parser(handlers, FINAL_GATES).parse_args()
    if not hasattr(arguments, "function"):
        arguments.command_name, arguments.function = "health", health
    if arguments.command_name == "init":
        verify_policy()
    arguments.function(arguments)
