"""Execution-policy verification for the software engineering loop."""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path


def bundled_policy() -> Path:
    return Path(__file__).parent.parent / "assets" / "software-engineering-loop.rules"


def policy_decision(command: list[str], policy: Path | None = None) -> str | None:
    result = subprocess.run(
        ["codex", "execpolicy", "check", "--pretty", "--rules", str(policy or bundled_policy()), "--", *command],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout).get("decision")


def verify_policy(policy: Path | None = None) -> None:
    for command in (
        ["git", "push"],
        ["/usr/bin/git", "push"],
        ["git", "-C", ".", "push"],
        ["git", "--literal-pathspecs", "push"],
        ["git", "-C.", "push"],
        ["git", "-cx=y", "push"],
        ["git", "--exec-path=/tmp", "push"],
        ["/usr/bin/env", "git", "push"],
        ["git", "send-pack", "origin", "main"],
        ["git", "merge", "x"],
        ["git", "pull"],
        ["git", "--no-pager", "merge", "x"],
        ["gh", "pr", "create"],
        ["gh", "--repo", "x", "pr", "create"],
        ["gh", "-R", "x", "pr", "create"],
        ["gh", "api", "repos/x/y/pulls"],
        ["git", "reset", "--hard"],
        ["git", "-c", "x=y", "reset", "--hard"],
        ["git", "restore", "x"],
    ):
        if policy_decision(command, policy) != "forbidden":
            raise SystemExit(f"execution policy does not forbid: {shlex.join(command)}")


def check_command_policy(command: list[str]) -> None:
    name = Path(command[0]).name
    args = command[1:]
    forbidden = (
        name == "git"
        and (
            any(item in args for item in ("push", "send-pack", "merge", "pull", "restore"))
            or ("reset" in args and "--hard" in args)
        )
    ) or (name == "gh" and ("api" in args or ("pr" in args and "create" in args)))
    if forbidden or policy_decision(command) == "forbidden":
        raise SystemExit(f"execution policy forbids: {shlex.join(command)}")
