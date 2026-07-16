"""One-command installation health check for the software-engineering loop."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tomllib
from pathlib import Path

from workflow_policy import bundled_policy, verify_policy


def health(_: object = None) -> None:
    skill = Path(__file__).parent.parent
    code_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    checks: dict[str, object] = {
        "codex": bool(shutil.which("codex")),
        "globalPolicyAbsent": not (code_home / "rules" / bundled_policy().name).exists(),
    }
    try:
        verify_policy()
        checks["bundledPolicy"] = True
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError, SystemExit):
        checks["bundledPolicy"] = False

    try:
        config = tomllib.loads((code_home / "config.toml").read_text())
        checks["maxDepthOne"] = config.get("agents", {}).get("max_depth") == 1
    except (OSError, tomllib.TOMLDecodeError):
        checks["maxDepthOne"] = False

    profiles = {}
    for source in sorted((skill / "assets" / "agents").glob("*.toml")):
        try:
            profile = tomllib.loads(source.read_text())
            installed = code_home / "agents" / source.name
            profiles[profile["name"]] = {
                "model": profile["model"],
                "reasoning": profile["model_reasoning_effort"],
                "sandbox": profile["sandbox_mode"],
                "bundled": True,
                "installed": installed.is_file() and installed.read_bytes() == source.read_bytes(),
            }
        except (KeyError, OSError, tomllib.TOMLDecodeError):
            profiles[source.stem] = {"bundled": False, "installed": False}
    checks["profiles"] = profiles
    checks["mode"] = (
        "native-profiles"
        if checks["maxDepthOne"] and all(item.get("installed") is True for item in profiles.values())
        else "isolated-runner"
    )
    passed = all(checks[key] is True for key in ("codex", "globalPolicyAbsent", "bundledPolicy")) and all(
        item.get("bundled") is True for item in profiles.values()
    )
    print(json.dumps({"status": "pass" if passed else "fail", "checks": checks}, indent=2))
    if not passed:
        raise SystemExit(1)
