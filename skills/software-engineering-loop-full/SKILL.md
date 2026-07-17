---
name: software-engineering-loop-full
description: Run the explicit full Codex software engineering loop for coding work that needs durable plans, isolated slices, concise rationale comments, maintained documentation, machine-bound validation evidence, debt gates, native Codex review, wiring review, and local commits. Use only when the user invokes full mode or requests the audited state-and-evidence workflow. Never push.
---

# Software Engineering Loop Full

Stay in full mode for the entire task. Do not switch to the fast skill. Use Codex as the supervisor and keep the durable state-and-evidence workflow active even for a one-slice task.

Read [workflow.md](references/workflow.md) completely before starting. Read [records.md](references/records.md) when creating the run plan or slice records.

Use three scope-limited writers sequentially: `se-implementer` (Sol/high) edits executable code and tests, `se-code-commenter` (Sol/high) edits only comments and docstrings, and `se-documenter` (Terra/medium) edits only maintained documentation. Never run writers concurrently. `se-reviewer` is Sol/high and read-only; all other Terra workers are read-only. The supervisor may directly create and update only `plan.md` and `slices/*.md`; mutate `state.json` only through `scripts/workflow_state.py`. Workers never recursively delegate.

Use native typed subagents only when the spawn surface exposes an agent-profile selector and the named profiles are installed. Otherwise invoke `scripts/run_profile.py`; it uses the bundled profiles directly, applies their model, reasoning, sandbox, and instructions exactly, and disables multi-agent tools in the worker. This runner path needs no global profile installation. Never label a generic spawned child as a configured profile.

Keep network access disabled unless the task explicitly requires it. Never push, merge, or open a pull request.

## Start

Inspect applicable `AGENTS.md`, the repository, relevant code, tests, build commands, and worktree. Refuse automatic commits when unrelated worktree changes cannot be safely excluded. Then initialize the durable state-and-evidence workflow:

```bash
python3 <skill-dir>/scripts/workflow_state.py init \
  --repo <repo> --run-id <run-id> --task-class <class> --slices S1 S2
```

For a one-slice task in the current repository, `python3 <helper> init` is sufficient. Use `python3 <helper> resume-status --run-dir <run-dir>` to recover the next legal action. Running the helper with no command performs the installation health check.

The supervisor may directly create and update `plan.md` and `slices/*.md` beside `state.json`. Use `scripts/workflow_state.py` for all `state.json` mutations, content-bound evidence, legal transitions, attempt limits, and the single-writer lock. Run `--help` and `self-test` before the first real use after an update. When using native typed subagents, require `agents.max_depth = 1`. The isolated runner is the zero-setup fallback and always disables multi-agent tools in workers. Do not silently replace a requested model or sandbox.

Follow the complete planning, slice, review, validation, checkpoint, finalization, and record sequence in `workflow.md`.

## Control rules

- Treat phases as state transitions. Loop only when a reviewer returns `changes_requested`.
- Use the state helper's attempt number on every gate. Attempt three is rejected; return `blocked` after attempt two fails.
- Run independent `se-scout` specialists in parallel. Acquire and release the writer lock separately for `se-implementer`, `se-code-commenter`, and `se-documenter`; run them in that order and never concurrently.
- Use Sol/high `se-implementer` for executable code and tests, Sol/high `se-code-commenter` only for comments and docstrings, and Terra/medium `se-documenter` only for maintained documentation. Keep every other Terra worker read-only.
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

## Change explanation

Have the supervisor finish with a plain-language summary of what changed, why it changed, how it works, validation performed, risks or limitations, deferred work, changed files, local commits, and that nothing was pushed. Do not spawn another agent for this summary.

The code commenter must keep rationale concise. A paragraph-sized comment is normally a signal to simplify the code or move the explanation into documentation. Comments must never expose private chain-of-thought, narrate edit history, or restate obvious code.
