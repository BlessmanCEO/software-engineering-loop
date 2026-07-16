# Software Engineering Loop

A bounded Codex workflow for planning, implementing, reviewing, validating, and committing software changes locally. It uses isolated worker profiles, permits only one writer at a time, and never pushes, merges, or opens pull requests from inside the coding loop.

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

The workflow creates local commits only. Publishing those commits is always a separate, explicit action.
