---
name: software-engineering-loop-fast
description: Run the explicit fast, script-free Codex software engineering loop for bounded coding tasks. Use when the user invokes fast mode or asks for the quick implement-validate-review workflow. Never switch to the full loop, create durable workflow records, or run bundled loop scripts. Run relevant project validation directly, allow one repair round, commit locally when permitted, and never push.
---

# Software Engineering Loop Fast

Stay in fast mode for the entire task. Never invoke the full skill, run any bundled software-engineering-loop script, create `.codex/software-engineering/` records, or run native `codex review`. Project-owned test, lint, typecheck, and build scripts are allowed when directly relevant.

Keep network access disabled unless the task explicitly requires it. Never push, merge, or open a pull request.

## Writer and reviewer

- Permit exactly one writer.
- Use a native `se-implementer` only when that installed profile is selectable and configured as `gpt-5.6-sol` with high reasoning. Otherwise let the current supervisor write only when the current session is already Sol/high; if that cannot be established, stop and ask the user to switch models. Never run a profile fallback script.
- Use one native read-only reviewer after validation. Prefer an installed Sol/high `se-reviewer`; otherwise use a read-only native subagent that inherits the current Sol/high session. Never let the reviewer edit or delegate.
- Keep subagent depth at one and reuse the same writer for the only repair round.

## Workflow

1. Read applicable `AGENTS.md`, inspect the relevant code and repository conventions, and check the worktree.
2. Scope the smallest complete change. Do not launch scouts or a planner.
3. Implement with the single writer.
4. Run each directly relevant project validation command once. Stop as blocked on failure.
5. Run one read-only review for correctness, scope, regressions, and maintainability.
6. On `changes_requested`, perform one repair with the same writer, rerun the relevant validation, and re-review once. Stop as blocked if validation fails or the re-review does not pass.
7. Create one local commit only when validation and review pass and unrelated worktree changes can be excluded safely. Otherwise hand back the completed change uncommitted.
8. Report changed files, validation, review result, commit status, and that nothing was pushed.

Do not add planning records, debt-gate records, audit evidence, checkpoint commits, finalization commits, or repeated broad test runs.
