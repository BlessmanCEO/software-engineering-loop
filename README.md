# Software Engineering Workflows

This plugin provides two original loop skills and two newer delivery workflows. Each is explicitly invoked and never silently switches to another.

## Original loop skills

- `$software-engineering-loop-fast`: the original complete workflow without durable audit scripts or records.
- `$software-engineering-loop-full`: the original durable state-and-evidence workflow.

## New workflow skills

- `$software-engineering-fast`: a lightweight workflow for contained small and medium tasks, with optional scouts, a reusable context packet, targeted worker validation, unified review, and no durable records.
- `$software-engineering-full`: a high-risk or governed workflow with a formal task contract, proof obligations, triggered specialists, durable recovery, content-bound evidence, and an audit manifest.

All four use Sol/high implementers, allow isolated parallel work only for independent slices, integrate sequentially, keep workers from recursively delegating, create local commits only when permitted, and never push or open pull requests. Native Codex review always targets a clean checkpoint commit.

## Install

```bash
codex plugin marketplace add BlessmanCEO/software-engineering-loop
codex plugin add software-engineering-loop@software-engineering-loop
```

Start a new Codex thread and invoke one skill:

```text
Use $software-engineering-loop-fast for this task.
Use $software-engineering-loop-full for this audited task.
Use $software-engineering-fast for this task.
Use $software-engineering-full for this high-risk task.
```

The full skills include their own controller and isolated runner. Run their `workflow_state.py` without arguments for an installation health check.

## Requirements

- Authenticated Codex CLI
- Python 3.11 or newer
- Access to the configured Sol and Terra models

Publishing remains a separate explicit action.
