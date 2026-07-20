# Software Engineering Workflows

This plugin provides one full recordless workflow and its three independently invokable prompt chains.

- `$software-engineering-full`: decides what discovery is useful, completes the task, audits and repairs it, validates, commits, runs commit-bound Codex review, and creates a repair commit only when needed.
- `$software-engineering-scout-plan`: scouts, plans, or does both when the task has real uncertainty.
- `$software-engineering-implement-integrate`: implements, validates, and integrates a complete change.
- `$software-engineering-audit-fix`: checks bugs, security, technical debt, and process debt, then fixes and validates confirmed findings.

The full workflow chains the three subprocess skills. They are guidance prompts, not a controller or state machine, so the orchestrator adapts them to the task. The plugin creates no workflow records or checkpoint commits and never pushes or opens pull requests.

## Install

```bash
codex plugin marketplace add BlessmanCEO/software-engineering-loop
codex plugin add software-engineering-loop@software-engineering-loop
```

Start a new Codex thread and invoke one skill:

```text
Use $software-engineering-full for this coding task.
Use $software-engineering-scout-plan to investigate and plan this task.
Use $software-engineering-implement-integrate to build this task.
Use $software-engineering-audit-fix to audit and repair this change.
```

Publishing remains a separate explicit action.
