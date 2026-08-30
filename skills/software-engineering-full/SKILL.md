---
name: software-engineering-full
description: Orchestrate a complete coding task without durable workflow records by chaining focused scout/plan, iterative implementation and adversarial review, audit/fix, retrospective, and delivery through exactly one pull request. Use when the user requests the full software-engineering workflow or wants an end-to-end implementation with early review gates, honest self-assessment, and PR delivery.
---

# Software Engineering Full

Act as the orchestration agent and own the task through one reviewed pull request. This is a prompt chain, not a state machine: combine, adapt, or skip process steps when evidence says they add no value. The user request and repository instructions always win.

Load each chained skill before following it. In Codex, invoke `$skill-name`. In Pi, read the sibling `../<skill-name>/SKILL.md` relative to this skill because `/skill:name` is only expanded from user input.

Use one implementation slice for contained, low-risk work. For complex or high-risk work, use the smallest vertical slices that leave the branch coherent and can be validated and adversarially reviewed before the next slice. Do not slice merely by file or architectural layer.

Do not create workflow records, controller state, or evidence manifests. Preserve unrelated changes. Slice checkpoint commits are allowed on the canonical branch only at coherent review boundaries; do not create speculative or save-point commits. One task still gets one canonical branch and one pull request. Before creating or switching branches, inspect the current branch, its base branch, remote branches, and open pull requests; continue a clear match, and ask the user when ownership is ambiguous instead of creating a duplicate. Never use additional worktrees or merge the pull request unless the user explicitly asks.

Run independent reviews in a fresh, read-only process for the active harness:

- Codex commit/base review: `codex review --commit <commit-sha>` or `codex review --base <base-branch>`.
- Pi commit review: `git show --format=fuller --stat --patch <commit-sha> | pi -p --no-session --no-extensions --no-skills --tools read,grep,find,ls "Review the supplied commit diff. Do not modify the repository. Return only verified findings, ordered by severity."`
- Pi base review: `git diff --stat --patch <base-branch>...HEAD | pi -p --no-session --no-extensions --no-skills --tools read,grep,find,ls "Review the supplied branch diff. Do not modify the repository. Return only verified findings, ordered by severity."`

If the current process was itself launched as an independent reviewer, return findings to its caller; never launch another review process.

## Prompt Chain

1. **Orchestrate:** Read applicable `AGENTS.md`, inspect the worktree and immediate code path, and define the objective, acceptance criteria, constraints, affected surface, done condition, canonical branch, and base branch. Keep a matching current branch, resume a clearly matching open pull request or remote branch, or create one task branch only when no match exists.
2. **Scout and plan when useful:** Load and invoke the `software-engineering-scout-plan` skill when ownership, callers, tests, risks, dependencies, implementation order, or safe slice boundaries are genuinely unclear. Also invoke it for complex or high-risk work whenever `.understand-anything/knowledge-graph.json` exists, so the wider affected system informs slice boundaries before implementation. Let that skill decide whether other scouting or planning is warranted.
3. **Implement one slice:** Load and invoke the `software-engineering-implement-integrate` skill for the current slice, including its required tests, documentation, wiring, and validation. Do not start the next slice yet.
4. **Audit, checkpoint, and review the slice:** Load and invoke the `software-engineering-audit-fix` skill on the current uncommitted slice and its affected callers. Validate repairs, inspect the diff and status, run `git diff --check`, and commit the reviewed slice. Run the active harness's commit review command above. Fix every verified in-scope blocker and validate and commit the repair. After a repair, or always for a multi-slice task, run the active harness's base review command to review the cumulative branch. Repeat repair, validation, commit, and cumulative review until no verified blocker remains. A clean commit review completes this gate for a one-slice low-risk task. Do not force findings into one pass or create empty commits.
5. **Repeat:** For a multi-slice task, return to implementation only after the current slice passes its review gate.
6. **Integrate and review the whole change:** After all slices, run integrated validation and load and invoke the `software-engineering-audit-fix` skill against the cumulative branch diff and affected integration surface. Commit any validated repairs, then run the active harness's base review command. Repeat repair, validation, commit, and cumulative review until no verified blocker remains. For a one-slice low-risk task with no changes after its clean slice review, that review may serve as this final gate.
7. **Retrospect:** Load and invoke the `software-engineering-retrospective` skill against every task commit and the final validated state. Require a candid verdict, commit-by-commit explanation and rationale, what held up or fell short, and what should be done differently. If it finds a verified delivery blocker, return to audit and repair, validate, commit, and repeat cumulative review and retrospective until the blocker is resolved.
8. **Publish and report:** Push the canonical branch, update its existing pull request or open one when none exists, and never create a second pull request for the task. Leave it open for review. Include the retrospective with the completed behavior, checks, audit, independent review, residual risks, commit hashes, and pull request URL.

If a required implementation, validation, commit, review, push, or pull request operation cannot run, report the exact blocker without pretending the chain completed.
