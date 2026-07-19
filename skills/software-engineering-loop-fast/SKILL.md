---
name: software-engineering-loop-fast
description: Run the complete Codex software engineering loop without bundled loop scripts or durable audit records. Use when the user invokes fast mode and still wants scouting, planning, isolated slices, implementation, concise rationale comments, documentation, validation, debt sweeps, Codex review, wiring reviews, and local commits. Keep workflow state in the active thread, never switch to full mode, and never push.
---

# Software Engineering Loop Fast

Run the complete engineering workflow in the active thread. Never invoke the full skill, run bundled software-engineering-loop scripts, or create `.codex/software-engineering/` records. Run project-owned tests, lint, typechecks, and builds directly. Run native Codex review only as `codex review --commit <checkpoint-sha>` against a clean local commit, never against uncommitted changes.

Keep network access disabled unless the task explicitly requires it. Never push, merge, or open a pull request.

## Agents

- Use read-only `se-scout` agents for repository, test, and risk discovery and one read-only `se-planner` for the sliced dependency plan. Do not add a separate parallelism planner.
- Use writable `se-implementer` agents, configured as `gpt-5.6-sol` with high reasoning, for complete slices: executable code, tests, necessary rationale comments, and maintained documentation. Reuse the same slice agent for repairs.
- Run ready slices with disjoint likely files concurrently only in isolated Git worktrees. Integrate them into the primary worktree one at a time. Run overlapping or dependent slices sequentially.
- Use one read-only Sol/high `se-reviewer` for the unified system gate. Add a read-only specialist only for triggered security, migration, compatibility, concurrency, performance, UX/accessibility, or operations risk. Terra agents may assist only with bounded read-only work and cannot approve gates.
- Prefer installed native profiles. Never invoke `run_profile.py`, a state script, or any other bundled loop script in fast mode, and never mislabel an unconfigured model.
- Keep subagent depth at one. Workers never delegate.

## Workflow

1. Read applicable `AGENTS.md`; inspect the repository, relevant code, conventions, worktree, tests, and build commands.
2. Classify the task. Run repository, test, and relevant risk scouts in parallel, then have the planner produce the smallest slices with scope, acceptance criteria, `depends_on`, likely files, risks, and validation. Keep this plan in the active thread only. Do not generate or refresh a knowledge graph unless the task is broad, the repository is unfamiliar, or the user explicitly requests it.
3. Start every dependency-ready slice whose likely files do not overlap. Give each implementer only its slice, dependency handoffs, and an isolated Git worktree based on the same commit. Make the smallest complete change and keep files below the 500-line design warning unless a justified exception exists. Integrate completed worktrees sequentially; discard or rerun stale work when integration reveals a conflict or changed dependency.
4. After all slices are integrated, complete all acceptance criteria and verify wider-system wiring. Create a local checkpoint commit only when unrelated worktree changes can be excluded safely.
5. Run `codex review --commit <checkpoint-sha>`, one unified system review, and only triggered specialist reviews concurrently against that exact checkpoint. Never substitute `codex review --uncommitted`. Aggregate valid findings into one repair pass with the matching slice implementer.
6. Reuse passing evidence when the content hash is unchanged. After repairs, rerun affected validation, the unified system review, and only affected specialist reviews, with at most two attempts per gate, then commit the repairs as a second local commit.
7. Run the relevant project validation directly against the final content. If reviews made no changes, keep the checkpoint as the final commit.
8. Produce the change explanation below.

Stop as blocked when a required model, agent, command, validation, or review gate is unavailable or fails its retry budget. Never claim a test, review, or commit happened when it did not.

## Change explanation

Have the supervisor finish with a plain-language summary of what changed, why it changed, how it works, validation performed, risks or limitations, deferred work, changed files, local commits, and that nothing was pushed. Do not spawn another agent for this summary.

The implementer must keep rationale comments concise. A paragraph-sized comment is normally a signal to simplify the code or move the explanation into documentation. Comments must never expose private chain-of-thought, narrate edit history, or restate obvious code.
