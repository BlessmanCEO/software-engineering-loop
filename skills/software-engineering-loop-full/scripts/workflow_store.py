"""Atomic workflow state storage and single-writer locks."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from workflow_checks import previous_slices_complete, require_no_writer

LEGACY_GATES = ("lean", "tech_debt", "process_debt", "wiring")
SPECIALIST_GATES = (
    "security", "migration", "compatibility", "concurrency", "performance",
    "ux_accessibility", "operations", "premortem", "recovery",
)


def upgrade_reviews(state: dict) -> dict:
    reviews = state.get("reviews", {})
    if "system" in reviews or not any(name in reviews for name in LEGACY_GATES):
        return state
    legacy = {name: reviews[name] for name in LEGACY_GATES if name in reviews}
    passed = len(legacy) == len(LEGACY_GATES) and all(
        review.get("status") == "pass" for review in legacy.values()
    )
    content_hashes = {review.get("contentHash") for review in legacy.values()}
    passed = passed and len(content_hashes) == 1 and None not in content_hashes
    template = next(iter(legacy.values()), {})
    reviews = {name: reviews[name] for name in ("completion", "codex") if name in reviews}
    reviews["system"] = {
        **template,
        "status": "pass" if passed else "pending",
        "required": True,
        "attempts": max((review.get("attempts", 0) for review in legacy.values()), default=0) if passed else 0,
        "evidence": "Migrated passing legacy review gates" if passed else "",
        "contentHash": next(iter(content_hashes)) if passed else None,
    }
    reviews.update({
        name: {
            "status": "not_required", "required": False, "attempts": 0,
            "evidence": "", "reviewedSha": None, "diffHash": None,
            "contentHash": None, "commandRuns": [], "history": [],
        }
        for name in SPECIALIST_GATES
    })
    state["legacyReviews"] = legacy
    state["reviews"] = reviews
    return state


def write_state(run_dir: Path, state: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    target = run_dir / "state.json"
    with tempfile.NamedTemporaryFile("w", dir=run_dir, delete=False) as handle:
        json.dump(state, handle, indent=2)
        handle.write("\n")
        temp = Path(handle.name)
    temp.replace(target)


def read_state(run_dir: Path) -> dict:
    return upgrade_reviews(json.loads((run_dir / "state.json").read_text()))


def _lock(run_dir: Path, state: dict, payload: dict) -> None:
    lock_path = run_dir / ".writer.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f"writer already locked: {lock_path.read_text().strip()}") from None
    with os.fdopen(descriptor, "w") as handle:
        json.dump(payload, handle)
    state["writerLock"] = payload
    state["status"] = "running"
    write_state(run_dir, state)


def acquire_writer(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    if args.slice not in state["slices"]:
        raise SystemExit(f"unknown slice: {args.slice}")
    require_no_writer(run_dir, state)
    record = state["slices"][args.slice]
    if record["status"] not in {"planned", "in_progress"}:
        raise SystemExit(f"cannot write a {record['status']} slice")
    if not previous_slices_complete(state, args.slice):
        raise SystemExit("previous slice is not complete")
    record["status"] = "in_progress"
    state["currentSlice"] = args.slice
    _lock(run_dir, state, {"phase": "slice", "slice": args.slice, "owner": args.owner})


def acquire_finalizer(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    require_no_writer(run_dir, state)
    if not state.get("checkpointSha") or any(item["status"] != "complete" for item in state["slices"].values()):
        raise SystemExit("finalization requires a checkpoint and complete slices")
    state["finalSha"] = None
    state["finalValidation"] = "pending"
    _lock(run_dir, state, {"phase": "finalization", "owner": args.owner})


def release_writer(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    lock_path = run_dir / ".writer.lock"
    if not lock_path.exists():
        if (state.get("writerLock") or {}).get("owner") == args.owner:
            state["writerLock"] = None
            write_state(run_dir, state)
            return
        raise SystemExit("writer lock is not held")
    payload = json.loads(lock_path.read_text())
    if payload["owner"] != args.owner:
        raise SystemExit(f"writer lock belongs to {payload['owner']}")
    lock_path.unlink()
    state["writerLock"] = None
    write_state(run_dir, state)
