---
name: software-engineering-loop-full
description: Run the durable, audited software engineering workflow for high-risk, large, regulated, security-sensitive, or operationally important coding work. Use when the user invokes full mode or needs formal task contracts, dependency-aware slices, content-bound validation evidence, triggered specialist reviews, recovery, commit-bound Codex review, rollback planning, and local audit records. Never push or silently switch modes.
---

# Software Engineering Loop Full

Stay in full mode for the entire task. Read [workflow.md](references/workflow.md) completely before starting and [records.md](references/records.md) before creating records. Keep network access disabled unless the task requires it. Never push, merge, or open a pull request.

## Roles

- Run repository, test, and risk scouts in parallel.
- Use the read-only `se-specialist` only for triggered security, migration and rollback, compatibility, concurrency, performance, UX/accessibility, or operations work.
- Use one read-only `se-planner` for the dependency-aware plan.
- Use one Sol/high `se-implementer` per slice for code, tests, targeted validation, concise rationale comments, and maintained documentation.
- Use one Sol/high `se-reviewer` for each unified slice or final review round. Do not split technical-debt and process-debt into separate calls.
- Reuse the original implementer for repairs. Workers never delegate.

Use native typed agents only when the required installed profiles are selectable. Otherwise invoke `scripts/run_profile.py` with the matching bundled profile; it applies the exact model, reasoning, sandbox, and instructions while disabling worker delegation.

## Durable controller

Initialize the versioned run after inspecting applicable `AGENTS.md`, the repository, relevant code, tests, build commands, and worktree:

```bash
python3 <skill-dir>/scripts/workflow_state.py init \
  --repo <repo> --run-id <run-id> --task-class <class> --slices S1 S2
```

Use `scripts/workflow_state.py` for state mutations, evidence, attempt limits, commit binding, and leases. The supervisor may directly maintain `plan.md` and `slices/*.md`; do not hand-edit `state.json`. Run `--help` and `self-test` before the first real use after an update. Use `resume-status` to recover the next legal action.

## Controls

- Resolve repository-answerable uncertainty before planning. Surface product or governance decisions instead of inventing them.
- Map every acceptance criterion to implementation and evidence.
- Run independent writable slices concurrently only in isolated worktrees. Integrate one at a time under the repository writer lease.
- Run targeted validation in the worker before integration and bind evidence to that prepared content.
- Record one atomic structured review round per slice or batch. Aggregate findings into one repair prompt and stop after two failed rounds.
- Close a slice only when its criteria, proof obligations, validation, unified review, and handoff pass against matching content.
- After every slice closes, create a clean checkpoint commit before native Codex review.
- Run native review only as `codex review --commit <checkpoint-sha>`, never against uncommitted changes.
- Run unified and triggered final reviews against the checkpoint. For critical work, add the pre-mortem and observability/recovery checks described in the workflow.
- Commit repaired content separately; a changed final commit must descend from the reviewed checkpoint.
- Never claim a command, test, review, commit, or evidence artifact that was not captured.

## Finish

Run relevant final validation against the exact reviewed content, record the final commit, produce the evidence manifest, and run:

```bash
python3 <skill-dir>/scripts/workflow_state.py check --run-dir <run-dir> --final
```

Report the change, reason, behavior, validation, reviews, risks, limitations, deferred work, files, local commits, rollback notes when relevant, and that nothing was pushed. Do not spawn a reporting agent.
