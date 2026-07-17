---
name: software-engineering-loop-fast
description: Run the complete Codex software engineering loop without bundled loop scripts or durable audit records. Use when the user invokes fast mode and still wants scouting, planning, isolated slices, implementation, concise rationale comments, documentation, validation, debt sweeps, Codex review, wiring reviews, and local commits. Keep workflow state in the active thread, never switch to full mode, and never push.
---

# Software Engineering Loop Fast

Run the complete engineering workflow in the active thread. Never invoke the full skill, run bundled software-engineering-loop scripts, or create `.codex/software-engineering/` records. Run project-owned tests, lint, typechecks, builds, and direct `codex review` commands when required.

Keep network access disabled unless the task explicitly requires it. Never push, merge, or open a pull request.

## Agents

- Use read-only `se-scout` agents for repository, test, and risk discovery and one read-only `se-planner` for the sliced plan.
- Use one writable `se-implementer`, configured as `gpt-5.6-sol` with high reasoning, for executable code and tests. Reuse it for repairs.
- After each implementation or repair, run writable Sol/high `se-code-commenter` to edit only comments and docstrings, then writable Terra/medium `se-documenter` to edit only maintained documentation. Run these writers sequentially and never concurrently.
- Use read-only Sol/high `se-reviewer` agents for every approval gate. Terra agents may assist only with bounded read-only work and cannot approve gates.
- Prefer installed native profiles. For `se-code-commenter` and `se-documenter`, invoke `codex exec` directly with the exact model, reasoning, sandbox, and instructions in `../software-engineering-loop-full/assets/agents/` when no native profile is installed. Never invoke `run_profile.py`, a state script, or any other bundled loop script in fast mode, and never mislabel an unconfigured model.
- Keep subagent depth at one. Workers never delegate.

## Workflow

1. Read applicable `AGENTS.md`; inspect the repository, relevant code, conventions, worktree, tests, and build commands.
2. Classify the task. Run repository, test, and relevant risk scouts in parallel, then have the planner produce the smallest ordered slices with scope, acceptance criteria, likely files, risks, and validation. Keep this plan in the active thread only.
3. For each slice, give the implementer only the current slice and prior handoff. Make the smallest complete change and keep files below the 500-line design warning unless a justified exception exists. Then run the code commenter and documenter sequentially before validation.
4. Run relevant project validation directly. Then run read-only tech-debt and process-debt reviews in order. Repair with the same implementer, rerun the commenter and documenter when affected, and recheck the gate. Allow at most two attempts per gate; do not start the next slice until both pass.
5. Complete all acceptance criteria and verify wider-system wiring. Create a local checkpoint commit only when unrelated worktree changes can be excluded safely.
6. Run `codex review --commit <checkpoint-sha>` directly. Fix valid findings with the same implementer and rerun relevant validation.
7. Run read-only lean, tech-debt, process-debt, and wider-system wiring reviews in order. Repair and recheck each gate before continuing, with at most two attempts per gate.
8. Run the relevant project validation directly against the final content. Create a final local commit only when review or wiring fixes changed files; otherwise keep the checkpoint as the final commit.
9. Produce the change explanation below.

Stop as blocked when a required model, agent, command, validation, or review gate is unavailable or fails its retry budget. Never claim a test, review, or commit happened when it did not.

## Change explanation

Have the supervisor finish with a plain-language summary of what changed, why it changed, how it works, validation performed, risks or limitations, deferred work, changed files, local commits, and that nothing was pushed. Do not spawn another agent for this summary.

The code commenter must keep rationale concise. A paragraph-sized comment is normally a signal to simplify the code or move the explanation into documentation. Comments must never expose private chain-of-thought, narrate edit history, or restate obvious code.
