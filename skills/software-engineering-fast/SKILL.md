---
name: software-engineering-fast
description: Run the lightweight software engineering workflow for small and medium coding tasks with contained risk, targeted validation, optional scouting, light slicing, unified review, commit-bound Codex review, and local commits. Use when the user invokes fast mode or requests the normal-delivery workflow without durable audit records. Never silently switch to full mode or push.
---

# Software Engineering Fast

Keep workflow state in the active thread. Do not run full-mode scripts or create `.codex/software-engineering/` records. Keep network access disabled unless the task requires it. Never push, merge, open a pull request, or run native Codex review against uncommitted changes.

## 1. Define the task

Create a compact brief containing the objective, acceptance criteria, non-goals, constraints, expected files or components, and definition of done.

## 2. Inspect only as needed

For a very small task, let the implementer inspect the relevant code directly. Otherwise run only the necessary read-only scouts in parallel for repository structure, tests and validation commands, and risk or integration points.

## 3. Confirm the route

Stop fast mode and recommend restarting with full mode if inspection reveals authentication or authorization work, migrations, destructive data operations, a major public API change, infrastructure, security-sensitive code, complex concurrency, a large cross-package refactor, or formal audit requirements. Never switch modes silently.

## 4. Make the smallest plan

Let the implementer keep a short internal plan for a small task. For a medium task, use one planner to define the smallest useful slices, dependencies, likely writable files, per-slice acceptance criteria, and targeted validation. Do not add a scheduling or parallelism agent.

## 5. Reuse one context packet

Give every worker the same packet instead of making each rediscover the repository:

```yaml
objective:
acceptance_criteria:
non_goals:
relevant_files:
architecture_notes:
repository_conventions:
validation_commands:
invariants:
known_risks:
```

## 6. Implement

Use one Sol/high implementer per slice. It owns executable code, tests, necessary rationale comments, required documentation, and cleanup directly caused by the change. Independent slices with disjoint writable files may run concurrently only in isolated Git worktrees. Run dependent or overlapping slices sequentially. Workers never delegate.

## 7. Validate in the worker

Before integration, have the same implementer run the cheapest relevant unit tests, affected-file lint, package typecheck, or component build in its worktree. Do not integrate a slice whose targeted checks fail.

## 8. Integrate sequentially

Integrate prepared slices into the primary worktree one at a time. Confirm actual files match scope, no undeclared overlap or unrelated changes exist, dependency assumptions remain valid, and the patch is not stale.

## 9. Review once per slice or batch

Use one Sol/high reviewer call for a slice or integration batch. In one result, check acceptance criteria, correctness, regression risk, tests, wiring, maintainability, scope drift, and process issues. Do not split technical-debt and process-debt review into separate agents.

## 10. Repair once

Aggregate valid findings into one prompt for the original implementer. Rerun affected tests and recheck only affected review areas. Allow at most two repair rounds.

## 11. Review a committed checkpoint

When the task is complete and the non-record worktree is clean, create a local checkpoint commit. Concurrently run:

- `codex review --commit <checkpoint-sha>`
- one unified system reviewer against the same checkpoint

Never use `codex review --uncommitted`. The unified reviewer checks end-to-end wiring, acceptance criteria, hidden TODOs, orphaned components, compatibility, documentation, and simplicity.

## 12. Validate the final surface

Choose validation by impact: targeted tests for a local change, affected package tests for shared code, dependent package tests for cross-package work, and wider builds or suites only for major integration changes. Do not run the entire repository suite by default.

## 13. Commit and report

If review repairs changed the checkpoint, create a second local commit after affected validation passes. Otherwise keep the checkpoint as final.

Report what changed, why, how it works, tests, review results, risks, limitations, deferred work, files, local commits, and that nothing was pushed. Do not spawn a reporting agent.

Stop as blocked when a required model, command, validation, or review is unavailable or two repair rounds fail. Never claim work or evidence that did not happen.
