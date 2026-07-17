"""Terminal gate checks and their focused self-test."""

from __future__ import annotations

import json
import shlex
from pathlib import Path

from workflow_evidence import EMPTY_DIFF_HASH

FINAL_GATES = (
    "completion", "codex", "system", "security", "migration", "compatibility",
    "concurrency", "performance", "ux_accessibility", "operations", "premortem", "recovery",
)
MAX_ATTEMPTS = 2


def lock_problem(run_dir: Path, state: dict) -> str | None:
    lock_path = run_dir / ".writer.lock"
    if state.get("writerLock") != state.get("writerLease"):
        return "writer lock and lease disagree"
    if lock_path.exists() != bool(state.get("writerLock")):
        return "writer lock file and state disagree"
    if lock_path.exists() and json.loads(lock_path.read_text()) != state["writerLock"]:
        return "writer lock file and state payloads disagree"
    return "writer lock is still held" if lock_path.exists() else None


def require_no_writer(run_dir: Path, state: dict) -> None:
    issue = lock_problem(run_dir, state)
    if issue:
        raise SystemExit(issue)


def require_no_validation(state: dict) -> None:
    if state.get("validationLease"):
        raise SystemExit("validation lease is still held")


def dependencies_complete(state: dict, slice_id: str) -> bool:
    return all(
        state["slices"][dependency]["status"] == "complete"
        for dependency in state["slices"][slice_id].get("dependsOn", [])
    )


def evidence_complete(record: dict) -> bool:
    return all(
        record.get(key) not in (None, "")
        for key in ("command", "outputSha256", "diffHash", "contentHash", "headSha")
    )


def problems(state: dict, final: bool, run_dir: Path | None = None, snapshot: dict | None = None) -> list[str]:
    issues: list[str] = []
    lock_issue = lock_problem(run_dir, state) if run_dir else ("writer lock is still held" if state.get("writerLock") else None)
    if lock_issue:
        issues.append(lock_issue)
    if state.get("validationLease"):
        issues.append("validation lease is still held")
    for slice_id, record in state["slices"].items():
        if record["status"] == "complete":
            if record.get("validation") != "pass":
                issues.append(f"{slice_id}: validation is {record.get('validation', 'missing')}")
            if record.get("review", {}).get("status") != "pass":
                issues.append(f"{slice_id}: unified review is {record.get('review', {}).get('status', 'missing')}")
            if record.get("proofStatus") != "pass":
                issues.append(f"{slice_id}: proof obligations are {record.get('proofStatus', 'missing')}")
            if not record.get("closedSnapshot"):
                issues.append(f"{slice_id}: closing snapshot is missing")
        elif final:
            issues.append(f"{slice_id}: status is {record['status']}")
    if final:
        for name, review in state["reviews"].items():
            allowed = {"not_required"} if not review.get("required", True) else {"pass", "degraded"} if name == "codex" else {"pass"}
            if review["status"] not in allowed:
                issues.append(f"review {name}: {review['status']}")
            if review["status"] == "not_required":
                continue
            if not all(review.get(key) for key in ("evidence", "reviewedSha", "diffHash", "contentHash")):
                issues.append(f"review {name}: incomplete evidence")
            if not 1 <= review.get("attempts", 0) <= MAX_ATTEMPTS:
                issues.append(f"review {name}: invalid attempt count")
        codex = state["reviews"]["codex"]
        if codex["status"] == "pass":
            attempt = codex.get("attempts", 0)
            runs = [item for item in codex.get("commandRuns", []) if item.get("attempt") == attempt]
            if not runs or any(item.get("exitCode") != 0 or not evidence_complete(item) for item in runs):
                issues.append("review codex: native command evidence missing or failed")
            if any(item.get("reviewedSha") != state.get("checkpointSha") for item in runs):
                issues.append("review codex: command did not review checkpoint commit")
            expected = ["codex", "review", "--commit", state.get("checkpointSha")]
            if any(shlex.split(item.get("command", "")) != expected for item in runs):
                issues.append("review codex: command was not codex review --commit <checkpoint>")
        if not state.get("checkpointSha"):
            issues.append("checkpoint commit is missing")
        if not state.get("finalSha"):
            issues.append("final commit is missing")
        if state.get("pushed") is not False:
            issues.append("pushed must remain false")
        final_attempt = state.get("finalValidationAttempts", 0)
        final_runs = [
            item for item in state.get("finalValidationRuns", [])
            if item.get("attempt") == final_attempt
        ]
        if state.get("finalValidation") != "pass":
            issues.append(f"final validation: {state.get('finalValidation', 'missing')}")
        if not 1 <= final_attempt <= MAX_ATTEMPTS:
            issues.append("final validation: invalid attempt count")
        if not final_runs or any(item.get("exitCode") != 0 or not evidence_complete(item) for item in final_runs):
            issues.append("final validation: passing machine evidence missing")
        if snapshot:
            if state.get("finalSha") != snapshot["headSha"]:
                issues.append("final commit is not current HEAD")
            if snapshot["diffHash"] != EMPTY_DIFF_HASH:
                issues.append("non-record worktree is not clean")
            for name, review in state["reviews"].items():
                if name in {"completion", "codex"} or review["status"] == "not_required":
                    continue
                if review.get("contentHash") != snapshot["contentHash"]:
                    issues.append(f"review {name}: content does not match final content")
            if any(item.get("contentHash") != snapshot["contentHash"] for item in final_runs):
                issues.append("final validation: content does not match final content")
    return issues


def self_test(_: object) -> None:
    evidence = {"attempt": 1, "command": "true", "exitCode": 0, "outputSha256": "x", "diffHash": "y", "contentHash": "c", "headSha": "z"}
    state = {
        "writerLock": None, "writerLease": None, "validationLease": None,
        "slices": {"S1": {"status": "complete", "validation": "pass", "review": {"status": "pass"}, "proofStatus": "pass", "closedSnapshot": {"contentHash": "c"}}},
        "reviews": {name: {"status": "pass", "required": True, "attempts": 1, "evidence": "ok", "reviewedSha": "a", "diffHash": "b", "contentHash": "c", "commandRuns": []} for name in FINAL_GATES},
        "checkpointSha": "a", "finalSha": "b", "pushed": False,
        "finalValidation": "pass", "finalValidationAttempts": 1,
        "finalValidationRuns": [dict(evidence)],
    }
    state["reviews"]["codex"]["commandRuns"] = [{**evidence, "command": "codex review --commit a", "reviewedSha": "a"}]
    for name in FINAL_GATES[3:]:
        state["reviews"][name].update(status="not_required", required=False, attempts=0, evidence="", reviewedSha=None, diffHash=None, contentHash=None)
    assert problems(state, True) == []
    state["slices"]["S1"]["closedSnapshot"] = None
    assert problems(state, True) == ["S1: closing snapshot is missing"]
    print("self-test passed")
