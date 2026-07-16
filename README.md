# Software Engineering Loop

Two explicit Codex skills for implementing, validating, reviewing, and locally committing software changes. Neither skill silently switches to the other.

- `$software-engineering-loop-fast`: script-free implement, validate, and review flow. It creates no workflow-state records and runs no bundled loop scripts. Relevant project test/build scripts are still allowed.
- `$software-engineering-loop-full`: durable planning, state, audit evidence, debt gates, native Codex review, and wider-system wiring checks.

Fast mode permits exactly one Sol/high writer. Full mode permits only its Sol/high `se-implementer` to edit task files. All Terra agents are read-only, workers never recursively delegate, and neither skill pushes, merges, or opens pull requests.

## Install

```bash
codex plugin marketplace add BlessmanCEO/software-engineering-loop
codex plugin add software-engineering-loop@software-engineering-loop
```

Start a new Codex thread, then invoke the workflow you want:

```text
Use $software-engineering-loop-fast for this task.
Use $software-engineering-loop-full for this task.
```

Fast mode never uses the isolated runner. It requires the current session or a selectable native writer profile to be Sol/high. Full mode can use the isolated runner without copying agent profiles into `~/.codex`.

## Check the installation

For full mode, run `workflow_state.py` with no arguments. It reports whether the isolated runner is ready and whether optional native profiles are available. Fast mode has no workflow health command.

## Requirements

- Codex CLI authenticated on the machine
- Python 3.11 or newer
- Access to the configured Sol and Terra models

The workflow creates local commits only when permitted. Publishing them is always a separate, explicit action.
