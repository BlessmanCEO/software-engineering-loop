#!/usr/bin/env python3
"""Run one bounded Codex worker with an exact bundled agent profile."""

from __future__ import annotations

import argparse
import json
import os
import signal
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

from workflow_policy import bundled_policy, verify_policy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.profile.replace("-", "").isalnum():
        raise SystemExit("profile name may contain only letters, numbers, and hyphens")
    profile_path = Path(__file__).parent.parent / "assets" / "agents" / f"{args.profile}.toml"
    if not profile_path.is_file():
        raise SystemExit(f"unknown bundled profile: {args.profile}")
    profile = tomllib.loads(profile_path.read_text())
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--json",
        "--disable",
        "multi_agent",
        "--disable",
        "apps",
        "--disable",
        "plugins",
        "--model",
        profile["model"],
        "--sandbox",
        profile["sandbox_mode"],
        "-c",
        'approval_policy="never"',
        "-c",
        "sandbox_workspace_write.network_access=false",
        "-c",
        f"model_reasoning_effort={json.dumps(profile['model_reasoning_effort'])}",
        "-c",
        f"developer_instructions={json.dumps(profile['developer_instructions'])}",
        "-C",
        str(Path(args.repo).resolve()),
        "--",
        args.prompt,
    ]
    if args.dry_run:
        print(json.dumps({"profile": profile["name"], "command": command}, indent=2))
        return
    policy = bundled_policy()
    verify_policy(policy)
    print(
        json.dumps(
            {
                "type": "profile.started",
                "profile": profile["name"],
                "model": profile["model"],
                "reasoning": profile["model_reasoning_effort"],
                "sandbox": profile["sandbox_mode"],
                "delegation": "disabled",
            }
        ),
        flush=True,
    )
    with tempfile.TemporaryDirectory(prefix="codex-se-worker-") as directory:
        worker_home = Path(directory)
        rules = worker_home / "rules"
        rules.mkdir()
        shutil.copy2(policy, rules / policy.name)
        user_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
        auth = user_home / "auth.json"
        if auth.is_file():
            shutil.copy2(auth, worker_home / "auth.json")
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(worker_home)
        child = subprocess.Popen(
            command, env=environment, stdin=subprocess.DEVNULL, start_new_session=True
        )

        def forward(signum, _frame):
            try:
                os.killpg(child.pid, signum)
            except ProcessLookupError:
                pass

        forwarded = [signal.SIGINT, signal.SIGTERM]
        if hasattr(signal, "SIGHUP"):
            forwarded.append(signal.SIGHUP)
        previous = {signum: signal.signal(signum, forward) for signum in forwarded}
        try:
            raise SystemExit(child.wait())
        finally:
            for signum, handler in previous.items():
                signal.signal(signum, handler)


if __name__ == "__main__":
    main()
