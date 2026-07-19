from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


STORE = Path(__file__).parents[1] / "skills/software-engineering-loop-full/scripts/workflow_store.py"


def load_store():
    sys.path.insert(0, str(STORE.parent))
    spec = importlib.util.spec_from_file_location("legacy_workflow_store", STORE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class LegacyStateTest(unittest.TestCase):
    def test_legacy_review_gates_migrate_on_read(self) -> None:
        review = {
            "status": "pass", "attempts": 1, "evidence": "ok",
            "reviewedSha": "a", "diffHash": "b", "contentHash": "c",
            "commandRuns": [], "history": [],
        }
        state = {"reviews": {
            "completion": dict(review), "codex": dict(review),
            "lean": dict(review), "tech_debt": dict(review),
            "process_debt": dict(review), "wiring": dict(review),
        }}
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            (run_dir / "state.json").write_text(json.dumps(state))
            migrated = load_store().read_state(run_dir)

        self.assertEqual(migrated["reviews"]["system"]["status"], "pass")
        self.assertEqual(migrated["reviews"]["security"]["status"], "not_required")
        self.assertEqual(set(migrated["legacyReviews"]), {
            "lean", "tech_debt", "process_debt", "wiring",
        })


if __name__ == "__main__":
    unittest.main()
