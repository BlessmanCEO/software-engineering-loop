---
name: software-engineering-full
description: Orchestrate a complete coding task without durable workflow records by chaining focused scout/plan, implement/integrate, and audit/fix prompts, then validating, committing, running commit-bound Codex review, and making a repair commit when needed. Use when the user requests the full software-engineering workflow or wants an end-to-end implementation with review and local commits.
---

# Software Engineering Full

Act as the orchestration agent and own the task through reviewed local commits. This is a prompt chain, not a state machine: combine, adapt, or skip process steps when evidence says they add no value. The user request and repository instructions always win.

Do not create workflow records, controller state, evidence manifests, or checkpoint commits. Preserve unrelated changes. Never push, merge, or open a pull request.

## Prompt Chain

1. **Orchestrate:** Read applicable `AGENTS.md`, inspect the worktree and immediate code path, and define the objective, acceptance criteria, constraints, affected surface, and done condition.
2. **Scout and plan when useful:** Invoke `$software-engineering-scout-plan` only when ownership, callers, tests, risks, dependencies, or implementation order are genuinely unclear. Let that skill decide whether scouting, planning, both, or neither is warranted.
3. **Implement and integrate:** Invoke `$software-engineering-implement-integrate` to complete the entire task, including required tests, documentation, wiring, and validation.
4. **Audit and repair:** Invoke `$software-engineering-audit-fix` on the completed uncommitted change. Ensure bugs, security, technical debt, and process debt are considered at a depth proportional to the change. Fix verified in-scope findings and validate the repairs.
5. **Commit:** Inspect the final diff and status, run `git diff --check`, and create the first local commit. This is the completed audited change, not a checkpoint.
6. **Codex review:** Run `codex review --commit <commit-sha>`. If it finds valid issues, fix them in one pass, rerun affected validation, and create one second local commit. Do not create an empty second commit or restart the whole workflow.
7. **Report:** Summarize the completed behavior, checks, audit, Codex review, residual risks, commit hashes, and that nothing was pushed.

If a required implementation, validation, commit, or review cannot run, report the exact blocker without pretending the chain completed.
