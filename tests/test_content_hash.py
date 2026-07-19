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
        for path in HELPERS:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as directory:
                helper = load_helper(path)
                repo = Path(directory)
                subprocess.run(["git", "init", "-q", str(repo)], check=True)
                (repo / "z.txt").write_text("tracked\n")
                subprocess.run(["git", "-C", str(repo), "add", "z.txt"], check=True)
                subprocess.run([
                    "git", "-C", str(repo), "-c", "user.name=test",
                    "-c", "user.email=test@example.com", "commit", "-qm", "initial",
                ], check=True)

                (repo / "a.txt").write_text("same content\n")
                untracked = helper.content_hash(repo)
                subprocess.run(["git", "-C", str(repo), "add", "a.txt"], check=True)
                self.assertEqual(untracked, helper.content_hash(repo))

                (repo / "z.txt").rename(repo / "y.txt")
                unstaged_rename = helper.content_hash(repo)
                subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
                self.assertEqual(unstaged_rename, helper.content_hash(repo))


if __name__ == "__main__":
    unittest.main()
