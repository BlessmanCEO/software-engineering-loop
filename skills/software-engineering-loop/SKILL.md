---
name: software-engineering-loop
description: Run a bounded Codex software engineering workflow for feature work, bug fixes, refactors, integrations, and other coding tasks. Default to a fast implement-validate-review flow for low-risk work, and use the full state-and-evidence flow only for the listed elevated-risk cases or an explicit request. Commit locally when permitted and never push.
---

# Software Engineering Loop

Use Codex as the supervisor. Default bounded, low-risk coding tasks to fast mode. Select full mode only for security, authentication, permissions, persistence, migrations, data-loss risk, architecture, shared or public contracts, deployment or build behavior, multiple dependent slices, ambiguous failures, or an explicit user request for full mode.

Read [workflow.md](references/workflow.md) completely before starting. Read [records.md](references/records.md) when creating the run plan or slice records.

The only writable worker in either mode is `se-implementer` (`gpt-5.6-sol`, high reasoning). It performs every task and source file edit. `se-reviewer` is Sol/high and read-only. Every Terra worker is read-only. In full mode, the supervisor may directly create and update only `plan.md` and `slices/*.md`; mutate `state.json` only through `scripts/workflow_state.py`. Workers never recursively delegate.

Use native typed subagents only when the spawn surface exposes an agent-profile selector and the named profiles are installed. Otherwise invoke `scripts/run_profile.py`; it uses the bundled profiles directly, applies their model, reasoning, sandbox, and instructions exactly, and disables multi-agent tools in the worker. This runner path needs no global profile installation. Never label a generic spawned child as a configured profile.

Keep network access disabled unless the task explicitly requires it. Never push, merge, or open a pull request.

## Fast mode

1. Inspect the repository, applicable `AGENTS.md`, status, tests, and build commands. The profile runner loads the bundled execution policy only inside its isolated worker home.
2. Refuse automatic commits when the worktree is dirty unless the user explicitly identifies which existing changes belong to this task.
3. Scope the task directly. Never run `se-scout` or `se-planner` in fast mode.
4. Start one `se-implementer` and let it make the smallest complete change.
5. Run every applicable validation command directly. Stop as blocked if any command fails.
6. Run one read-only `se-reviewer`.
7. Stop as blocked if the initial review returns `blocked`. If it returns `changes_requested`, return the findings to the same implementer for the only repair round, rerun every applicable validation command, and run one re-review. Stop as blocked if validation fails or the re-review does not return `pass`.
8. Create one local commit when permitted only after every applicable validation command passes and the final `se-reviewer` returns `pass`. Never create checkpoint and final commits for fast mode.

Fast mode does not create workflow-state records, use scouts or a planner, run separate debt reviews, invoke native Codex review, repeat broad test runs, or create checkpoint/final double commits.

## Full mode

Inspect the repository and worktree as in fast mode, then initialize the durable state-and-evidence workflow:

```bash
python3 <skill-dir>/scripts/workflow_state.py init \
  --repo <repo> --run-id <run-id> --task-class <class> --slices S1 S2
```

For a one-slice task in the current repository, `python3 <helper> init` is sufficient. Use `python3 <helper> resume-status --run-dir <run-dir>` to recover the next legal action. Running the helper with no command performs the installation health check.

The supervisor may directly create and update `plan.md` and `slices/*.md` beside `state.json`. Use `scripts/workflow_state.py` for all `state.json` mutations, content-bound evidence, legal transitions, attempt limits, and the single-writer lock. Run `--help` and `self-test` before the first real use after an update. When using native typed subagents, require `agents.max_depth = 1`. The isolated runner is the zero-setup fallback and always disables multi-agent tools in workers. Do not silently replace a requested model or sandbox.

Follow the complete planning, slice, review, validation, checkpoint, finalization, and record sequence in `workflow.md`.

## Full-mode control rules

- Treat phases as state transitions. Loop only when a reviewer returns `changes_requested`.
- Use the state helper's attempt number on every gate. Attempt three is rejected; return `blocked` after attempt two fails.
- Run independent `se-scout` specialists in parallel. Acquire the slice or finalizer writer lock before starting one `se-implementer`, and release it before review.
- Keep every Terra worker read-only. Use only Sol/high `se-implementer` for edits and repairs.
- Start the next slice only after validation, tech-debt sweep, and process-debt sweep pass.
- Use structured reviewer output: `pass`, `changes_requested`, or `blocked`, plus concrete findings.
- Run validation through `record-validation`; a passing claim without exit-code, output-digest, diff-hash, and HEAD evidence fails the final check.
- Let the supervisor create local commits only after the required gates pass.

### Codex review

After the checkpoint commit, invoke the non-interactive review command through the evidence recorder:

```bash
python3 <skill-dir>/scripts/workflow_state.py record-review-command \
  --run-dir <run-dir> --name codex --attempt 1 --sha <checkpoint-sha> \
  -- codex review --commit <checkpoint-sha>
```

Do not substitute a normal reviewer prompt while claiming the native Codex review ran. If the command is unavailable or fails, record the gate as `degraded` or `blocked`.

### Finish

After wiring passes, run the relevant commands through `record-final-validation` so final test evidence is bound to the exact reviewed content. Stop only after final state and commit SHAs are recorded. When reviews make no changes, record the checkpoint SHA as the final SHA; do not create an empty commit. Report tests, review results, deferred work, local commits, and the explicit fact that nothing was pushed.

Run the final machine check before reporting success:

```bash
python3 <skill-dir>/scripts/workflow_state.py check --run-dir <run-dir> --final
```
