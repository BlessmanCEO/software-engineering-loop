# Software Engineering Loop

Two explicit Codex skills for implementing, validating, reviewing, and locally committing software changes. Neither skill silently switches to the other.

- `$software-engineering-loop-fast`: the complete engineering workflow without bundled loop scripts or durable audit records. Planning, slices, validation, debt sweeps, Codex review, lean review, wiring review, and local commits still run.
- `$software-engineering-loop-full`: the same engineering workflow with durable state, machine-bound audit evidence, and script-enforced transitions.

Both modes use a Sol/high `se-implementer` for the complete slice, including necessary rationale comments and maintained documentation. Independent read-only work runs in parallel. Independent writable slices may run in parallel only in isolated Git worktrees and are integrated sequentially. Workers never recursively delegate, and neither skill pushes, merges, or opens pull requests.

Slices contain only implementation and integration. Validation, debt review, Codex review, and wiring review run after every slice is integrated.

Native Codex review always targets a clean local checkpoint commit. Review repairs are committed separately; neither mode uses an uncommitted Codex review.

Both skills end with a supervisor-written explanation of what changed, why, how it works, validation, risks, files, and commits. They add code comments only for non-obvious reasoning or constraints.

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

Fast mode never uses the isolated runner or state helper. It requires the current session or a selectable native writer profile to be Sol/high. Full mode can use the isolated runner and state helper without copying agent profiles into `~/.codex`.

## Check the installation

For full mode, run `workflow_state.py` with no arguments. It reports whether the isolated runner is ready and whether optional native profiles are available. Fast mode has no workflow health command.

## Requirements

- Codex CLI authenticated on the machine
- Python 3.11 or newer
- Access to the configured Sol and Terra models

The workflow creates local commits only when permitted. Publishing them is always a separate, explicit action.
