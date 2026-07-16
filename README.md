# Software Engineering Loop

A bounded Codex workflow for implementing, validating, reviewing, and locally committing software changes. Fast mode is the default for low-risk work; full mode adds durable planning, state, evidence, and review gates for the listed elevated-risk cases.

Fast mode uses one Sol/high `se-implementer`, relevant validation once, and one Sol/high read-only `se-reviewer`. It permits at most one repair and re-review before one local commit. Full mode is reserved for security, authentication, permissions, persistence, migrations, data-loss risk, architecture, shared or public contracts, deployment or build behavior, multiple dependent slices, ambiguous failures, or an explicit request.

Only `se-implementer` may edit task files in either mode. All Terra agents are read-only. Workers run without recursive delegation. The loop never pushes, merges, or opens pull requests.

## Install

```bash
codex plugin marketplace add BlessmanCEO/software-engineering-loop
codex plugin add software-engineering-loop@software-engineering-loop
```

Start a new Codex thread, then ask:

```text
Run the software engineering loop for this task.
```

The isolated runner works without copying agent profiles into `~/.codex`. If compatible named profiles are already installed and Codex exposes profile selection, the loop can use them directly.

## Check the installation

Run the plugin's `workflow_state.py` with no arguments. It reports whether the isolated runner is ready and whether optional native profiles are available.

## Requirements

- Codex CLI authenticated on the machine
- Python 3.11 or newer
- Access to the configured Sol and Terra models

The workflow creates local commits only when permitted. Publishing them is always a separate, explicit action.
