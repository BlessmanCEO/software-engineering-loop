from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
HELPERS = (
    ROOT / "skills/software-engineering-full/scripts/workflow_evidence.py",
    ROOT / "skills/software-engineering-loop-full/scripts/workflow_evidence.py",
)


def load_helper(path: Path):
    spec = importlib.util.spec_from_file_location(path.parent.parent.name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class ContentHashTest(unittest.TestCase):
    def test_staging_does_not_change_working_tree_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "z.txt").write_text("tracked\n")
            subprocess.run(["git", "-C", str(repo), "add", "z.txt"], check=True)
            (repo / "a.txt").write_text("same content\n")

            for path in HELPERS:
                helper = load_helper(path)
                untracked = helper.content_hash(repo)
                subprocess.run(["git", "-C", str(repo), "add", "a.txt"], check=True)
                staged = helper.content_hash(repo)
                subprocess.run(["git", "-C", str(repo), "rm", "--cached", "-q", "a.txt"], check=True)
                self.assertEqual(untracked, staged, path)


if __name__ == "__main__":
    unittest.main()
