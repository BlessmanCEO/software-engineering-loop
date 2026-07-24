---
name: software-engineering-full
description: Orchestrate a complete coding task without durable workflow records by chaining focused scout/plan, implement/integrate, audit/fix, and retrospective prompts, then validating, committing, running commit-bound Codex review, and publishing or updating exactly one pull request. Use when the user requests the full software-engineering workflow or wants an end-to-end implementation with review, honest self-assessment, and PR delivery.
---

# Software Engineering Full

Act as the orchestration agent and own the task through one reviewed pull request. This is a prompt chain, not a state machine: combine, adapt, or skip process steps when evidence says they add no value. The user request and repository instructions always win.

Do not create workflow records, controller state, evidence manifests, or checkpoint commits. Preserve unrelated changes. One task gets one canonical branch and one pull request. Before creating or switching branches, inspect the current branch, remote branches, and open pull requests; continue a clear match, and ask the user when ownership is ambiguous instead of creating a duplicate. Never use additional worktrees or merge the pull request unless the user explicitly asks.

## Prompt Chain

1. **Orchestrate:** Read applicable `AGENTS.md`, inspect the worktree and immediate code path, and define the objective, acceptance criteria, constraints, affected surface, and done condition. Establish the canonical delivery branch: keep a matching current branch, resume a clearly matching open pull request or remote branch, or create one task branch only when no match exists.
2. **Scout and plan when useful:** Invoke `$software-engineering-scout-plan` only when ownership, callers, tests, risks, dependencies, or implementation order are genuinely unclear. Let that skill decide whether scouting, planning, both, or neither is warranted.
3. **Implement and integrate:** Invoke `$software-engineering-implement-integrate` to complete the entire task, including required tests, documentation, wiring, and validation.
4. **Audit and repair:** Invoke `$software-engineering-audit-fix` on the completed uncommitted change. Ensure bugs, security, technical debt, and process debt are considered at a depth proportional to the change. Fix verified in-scope findings and validate the repairs.
5. **Commit:** Inspect the final diff and status, run `git diff --check`, and create the first local commit. This is the completed audited change, not a checkpoint.
6. **Codex review:** Run `codex review --commit <commit-sha>`. If it finds valid issues, fix them in one pass, rerun affected validation, and create one second local commit. Do not create an empty second commit or restart the whole workflow.
7. **Retrospect:** Invoke `$software-engineering-retrospective` against every task commit and the final validated state. Require a candid verdict, commit-by-commit explanation and rationale, what held up or fell short, and what should be done differently. If it finds a verified delivery blocker, return once to audit and repair, validate and review the repair, then repeat the retrospective.
8. **Publish and report:** Push the canonical branch, update its existing pull request or open one when none exists, and never create a second pull request for the task. Leave it open for review. Include the retrospective with the completed behavior, checks, audit, Codex review, residual risks, commit hashes, and pull request URL.

If a required implementation, validation, commit, review, push, or pull request operation cannot run, report the exact blocker without pretending the chain completed.
