#!/usr/bin/env python3
"""Command-line parser for the software-engineering workflow controller."""

from __future__ import annotations

import argparse
from collections.abc import Callable


def build_parser(handlers: dict[str, Callable], final_gates: tuple[str, ...]) -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command_name")

    command = commands.add_parser("init")
    command.add_argument("--repo", default=".")
    command.add_argument("--run-id")
    command.add_argument("--task-class", default="small_edit")
    command.add_argument("--plan-id")
    command.add_argument("--slices", nargs="+", default=["S1"])
    command.add_argument("--dependencies-json", default="{}")
    command.add_argument("--allow-dirty", action="store_true")

    command = commands.add_parser("set-slice-status")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--slice", required=True)
    command.add_argument("--status", required=True)
    command.add_argument("--proof-status", choices=("pass", "deferred"))
    command.add_argument("--handoff", default="")

    command = commands.add_parser("record-slice-validation")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--slice", required=True)
    command.add_argument("--worktree", required=True)
    command.add_argument("--attempt", required=True, type=int)
    command.add_argument("command", nargs=argparse.REMAINDER)

    command = commands.add_parser("set-slice-review")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--slice", required=True)
    command.add_argument("--status", required=True)
    command.add_argument("--attempt", required=True, type=int)
    command.add_argument("--areas", default="")
    command.add_argument("--evidence", default="")

    command = commands.add_parser("record-final-validation")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--attempt", required=True, type=int)
    command.add_argument("command", nargs=argparse.REMAINDER)

    command = commands.add_parser("set-review")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--name", required=True, choices=final_gates)
    command.add_argument("--status", required=True)
    command.add_argument("--attempt", required=True, type=int)
    command.add_argument("--sha")
    command.add_argument("--evidence", default="")

    command = commands.add_parser("record-review-command")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--name", required=True, choices=final_gates)
    command.add_argument("--attempt", required=True, type=int)
    command.add_argument("--sha", required=True)
    command.add_argument("command", nargs=argparse.REMAINDER)

    command = commands.add_parser("acquire-writer")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--slice", required=True)
    command.add_argument("--owner", required=True)

    command = commands.add_parser("acquire-finalizer")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--owner", required=True)

    command = commands.add_parser("release-writer")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--owner", required=True)

    command = commands.add_parser("release-validation")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--reason", required=True)

    command = commands.add_parser("set-commit")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--kind", required=True, choices=("checkpoint", "final"))
    command.add_argument("--sha", required=True)

    command = commands.add_parser("check")
    command.add_argument("--run-dir", required=True)
    command.add_argument("--final", action="store_true")

    command = commands.add_parser("resume-status")
    command.add_argument("--run-dir", required=True)

    commands.add_parser("health")
    commands.add_parser("self-test")
    for name, handler in handlers.items():
        commands.choices[name].set_defaults(function=handler)
    return root
