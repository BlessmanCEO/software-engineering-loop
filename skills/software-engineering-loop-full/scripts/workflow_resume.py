"""Read-only next-action guidance for an existing workflow run."""

from __future__ import annotations

import json
from pathlib import Path

from workflow_store import read_state


def resume_status(args) -> None:
    state = read_state(Path(args.run_dir))
    current = state.get("currentSlice")
    blocked = next(
        (f"slice {name}" for name, item in state["slices"].items() if item["status"] == "blocked"),
        None,
    ) or next(
        (f"review {name}" for name, item in state["reviews"].items() if item["status"] == "blocked"),
        None,
    )
    if state.get("finalValidation") == "blocked":
        blocked = "final validation"
    if blocked or state["status"] == "blocked":
        next_action = f"blocked: {blocked or 'workflow'}; user intervention required"
    elif state.get("writerLock"):
        next_action = f"continue or release {state['writerLock']['phase']} writer"
    else:
        incomplete = next(
            ((name, item) for name, item in state["slices"].items() if item["status"] != "complete"),
            None,
        )
        if incomplete:
            name, record = incomplete
            current = name
            if record["status"] == "planned":
                next_action = f"acquire-writer {name}"
            else:
                next_action = next(
                    (gate for gate in ("validation", "techDebt", "processDebt") if record[gate] != "pass"),
                    f"complete {name}",
                )
        elif state["reviews"]["completion"]["status"] != "pass":
            next_action = "completion review"
        elif not state.get("checkpointSha"):
            next_action = "record checkpoint commit"
        else:
            next_action = next(
                (f"{name} review" for name, item in state["reviews"].items() if item["status"] not in {"pass", "degraded"}),
                "final validation" if state.get("finalValidation") != "pass" else "record final commit" if not state.get("finalSha") else "final check",
            )
    print(json.dumps({
        "runId": state["runId"], "status": state["status"], "currentSlice": current,
        "writerLock": state.get("writerLock"), "nextAction": next_action,
    }, indent=2))
