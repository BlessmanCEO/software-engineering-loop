---
name: software-engineering-loop
description: Run a bounded multi-agent software engineering workflow in Codex for feature work, bug fixes, refactors, integrations, and coding tasks that need planning, isolated slices, debt sweeps, review gates, wider-system verification, and local commits without pushing.
---

# Software Engineering Loop

Use Codex as the supervisor. Use the `se-scout`, `se-planner`, `se-implementer`, and `se-reviewer` profiles for bounded work. The supervisor may directly select `se-terra-helper` for simple read-only subtasks or `se-terra-implementer` for a simple locked slice. Workers never recursively delegate.

Read [workflow.md](references/workflow.md) completely before starting. Read [records.md](references/records.md) when creating the run plan or slice records.

Use `scripts/workflow_state.py` for durable machine-checked state, content-bound evidence, legal transitions, attempt limits, and the single-writer lock. Run `--help` and `self-test` before the first real use after an update.

Use native typed subagents only when the spawn surface exposes an agent-profile selector and the named profiles are installed. Otherwise invoke `scripts/run_profile.py`; it uses the bundled profiles directly, applies their model, reasoning, sandbox, and instructions exactly, and disables multi-agent tools in the worker. This runner path needs no global profile installation. Never label a generic spawned child as a configured profile.

## Start

1. Inspect the repository, applicable `AGENTS.md`, status, tests, and build commands. The profile runner loads the bundled execution policy only inside its isolated worker home.
2. Refuse automatic commits when the worktree is dirty unless the user explicitly identifies which existing changes belong to this task.
3. Initialize the run record:

```bash
python3 <skill-dir>/scripts/workflow_state.py init \
  --repo <repo> --run-id <run-id> --task-class <class> --slices S1 S2
```

For a one-slice task in the current repository, `python3 <helper> init` is sufficient. Use `python3 <helper> resume-status --run-dir <run-dir>` to recover the next legal action. Running the helper with no command performs the installation health check.

4. Store the plan and slice Markdown beside the generated `state.json`.
5. Classify the task and select the route in `workflow.md`.
6. When using native typed subagents, require `agents.max_depth = 1`. The isolated runner is the zero-setup fallback and always disables multi-agent tools in workers. Do not silently replace a requested model or sandbox.

## Control rules

- Treat phases as state transitions. Loop only when a reviewer returns `changes_requested`.
- Use the state helper's attempt number on every gate. Attempt three is rejected; return `blocked` after attempt two fails.
- Run independent `se-scout` specialists in parallel. Acquire the slice or finalizer writer lock before starting one `se-implementer`, and release it before review.
- Use Terra companions only for simple bounded work. Keep Sol/high for architecture, security, persistence, shared contracts, ambiguous failures, and final gate ownership.
- Start the next slice only after validation, tech-debt sweep, and process-debt sweep pass.
- Use structured reviewer output: `pass`, `changes_requested`, or `blocked`, plus concrete findings.
- Run validation through `record-validation`; a passing claim without exit-code, output-digest, diff-hash, and HEAD evidence fails the final check.
- Keep network access disabled unless the task explicitly requires it.
- Never run `git push`, merge, or open a pull request.
- Let the supervisor create local commits only after the required gates pass.

## Codex review

After the checkpoint commit, invoke the non-interactive review command through the evidence recorder:

```bash
python3 <skill-dir>/scripts/workflow_state.py record-review-command \
  --run-dir <run-dir> --name codex --attempt 1 --sha <checkpoint-sha> \
  -- codex review --commit <checkpoint-sha>
```

Do not substitute a normal reviewer prompt while claiming the native Codex review ran. If the command is unavailable or fails, record the gate as `degraded` or `blocked`.

## Finish

After wiring passes, run the relevant commands through `record-final-validation` so final test evidence is bound to the exact reviewed content. Stop only after final state and commit SHAs are recorded. When reviews make no changes, record the checkpoint SHA as the final SHA; do not create an empty commit. Report tests, review results, deferred work, local commits, and the explicit fact that nothing was pushed.

Run the final machine check before reporting success:

```bash
python3 <skill-dir>/scripts/workflow_state.py check --run-dir <run-dir> --final
```
