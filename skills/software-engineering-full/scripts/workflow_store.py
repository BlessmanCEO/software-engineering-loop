"""Atomic workflow state storage and single-writer locks."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from workflow_checks import dependencies_complete, require_no_validation, require_no_writer


def write_state(run_dir: Path, state: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    state["revision"] = state.get("revision", 0) + 1
    state["updatedAt"] = datetime.now(UTC).isoformat()
    state.setdefault("recovery", {})["lastRevision"] = state["revision"]
    target = run_dir / "state.json"
    with tempfile.NamedTemporaryFile("w", dir=run_dir, delete=False) as handle:
        json.dump(state, handle, indent=2)
        handle.write("\n")
        temp = Path(handle.name)
    temp.replace(target)


def read_state(run_dir: Path) -> dict:
    return json.loads((run_dir / "state.json").read_text())


def _lock(run_dir: Path, state: dict, payload: dict) -> None:
    lock_path = run_dir / ".writer.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f"writer already locked: {lock_path.read_text().strip()}") from None
    with os.fdopen(descriptor, "w") as handle:
        json.dump(payload, handle)
    state["writerLock"] = payload
    state["writerLease"] = payload
    state["activeOperations"] = [payload]
    state["status"] = "running"
    write_state(run_dir, state)


def acquire_writer(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    if args.slice not in state["slices"]:
        raise SystemExit(f"unknown slice: {args.slice}")
    require_no_writer(run_dir, state)
    require_no_validation(state)
    record = state["slices"][args.slice]
    if record["status"] not in {"planned", "in_progress"}:
        raise SystemExit(f"cannot write a {record['status']} slice")
    if not dependencies_complete(state, args.slice):
        raise SystemExit("slice dependencies are not complete")
    if record.get("validation") != "pass":
        raise SystemExit("slice requires passing worker validation before integration")
    if record["status"] == "in_progress":
        record["validation"] = "changes_requested"
    record["status"] = "in_progress"
    record["phase"] = "integrating"
    state["currentSlice"] = args.slice
    _lock(run_dir, state, {"phase": "slice", "slice": args.slice, "owner": args.owner})


def acquire_finalizer(args) -> None:
    run_dir = Path(args.run_dir)
    state = read_state(run_dir)
    require_no_writer(run_dir, state)
    require_no_validation(state)
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
            state["writerLease"] = None
            state["activeOperations"] = []
            write_state(run_dir, state)
            return
        raise SystemExit("writer lock is not held")
    payload = json.loads(lock_path.read_text())
    if payload["owner"] != args.owner:
        raise SystemExit(f"writer lock belongs to {payload['owner']}")
    lock_path.unlink()
    if payload.get("phase") == "slice":
        state["slices"][payload["slice"]]["phase"] = "integrated"
    state["writerLock"] = None
    state["writerLease"] = None
    state["activeOperations"] = []
    write_state(run_dir, state)
