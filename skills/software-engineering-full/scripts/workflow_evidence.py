"""Git snapshot and command evidence helpers for workflow_state.py."""

from __future__ import annotations

import hashlib
import os
import platform
import shlex
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

EMPTY_DIFF_HASH = hashlib.sha256().hexdigest()
PATHS = ("--", ".", ":(exclude).codex/software-engineering/**")


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True
    ).stdout


def head_sha(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD").decode().strip()


def hash_path(digest: hashlib._Hash, repo: Path, raw_path: bytes) -> None:
    path = repo / os.fsdecode(raw_path)
    digest.update(raw_path)
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        digest.update(b"missing\0")
        return
    digest.update(f"{mode & 0o177777:o}\0".encode())
    if path.is_symlink():
        digest.update(b"link\0" + os.fsencode(os.readlink(path)))
    elif path.is_file():
        digest.update(b"file\0")
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)


def diff_hash(repo: Path) -> str:
    digest = hashlib.sha256()
    digest.update(git(repo, "status", "--porcelain=v1", "-z", *PATHS))
    digest.update(git(repo, "diff", "--binary", "HEAD", *PATHS))
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z", *PATHS)
    for raw_path in filter(None, untracked.split(b"\0")):
        hash_path(digest, repo, raw_path)
    return digest.hexdigest()


def content_hash(repo: Path) -> str:
    digest = hashlib.sha256()
    tracked = git(repo, "ls-files", "--stage", "-z", *PATHS)
    entries = {}
    for entry in filter(None, tracked.split(b"\0")):
        metadata, raw_path = entry.split(b"\t", 1)
        entries[raw_path] = metadata
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z", *PATHS)
    paths = set(entries).union(filter(None, untracked.split(b"\0")))
    for raw_path in sorted(paths):
        if not os.path.lexists(repo / os.fsdecode(raw_path)):
            continue
        metadata = entries.get(raw_path, b"")
        index_mode = metadata.split(b" ", 1)[0]
        if index_mode == b"160000":
            path = repo / os.fsdecode(raw_path)
            try:
                object_id = git(path, "rev-parse", "HEAD").strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                object_id = metadata.split(b" ")[1]
            digest.update(raw_path + b"\0submodule\0" + object_id)
        else:
            hash_path(digest, repo, raw_path)
    return digest.hexdigest()


def non_record_dirty(repo: Path) -> bool:
    return bool(git(repo, "status", "--porcelain=v1", "-z", *PATHS))


def evidence_snapshot(repo: Path) -> dict:
    return {
        "headSha": head_sha(repo),
        "diffHash": diff_hash(repo),
        "contentHash": content_hash(repo),
    }


def run_with_evidence(
    repo: Path, command: list[str], attempt: int, reviewed_sha: str | None = None,
    log_path: Path | None = None,
) -> dict:
    before = evidence_snapshot(repo)
    started_at = datetime.now(UTC)
    started = time.monotonic()
    try:
        result = subprocess.run(command, cwd=repo, capture_output=True)
        output = result.stdout + result.stderr
        sys.stdout.buffer.write(result.stdout)
        sys.stderr.buffer.write(result.stderr)
        exit_code = result.returncode
    except FileNotFoundError as error:
        output = str(error).encode()
        sys.stderr.buffer.write(output + b"\n")
        exit_code = 127
    ended_at = datetime.now(UTC)
    after = evidence_snapshot(repo)
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_bytes(output)
    record = {
        "attempt": attempt,
        "command": shlex.join(command),
        "exitCode": exit_code,
        "startedAt": started_at.isoformat(),
        "endedAt": ended_at.isoformat(),
        "durationMs": round((time.monotonic() - started) * 1000),
        "outputSha256": hashlib.sha256(output).hexdigest(),
        "preContentHash": before["contentHash"],
        "preDiffHash": before["diffHash"],
        "preHeadSha": before["headSha"],
        "mutatedContent": any(before[key] != after[key] for key in ("headSha", "contentHash", "diffHash")),
        "tool": command[0],
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "log": str(log_path) if log_path else None,
        **after,
    }
    if reviewed_sha:
        record["reviewedSha"] = reviewed_sha
    return record
