---
name: software-engineering-full
description: Orchestrate a complete coding task without durable workflow records by chaining focused scout/plan, risk-adjusted implementation and independent review, audit/fix, retrospective when useful, and delivery through exactly one pull request. Use when the user requests the full software-engineering workflow or wants an end-to-end implementation with review gates proportional to risk, honest self-assessment, and PR delivery.
---

# Software Engineering Full

Act as the orchestration agent and own the task through one reviewed pull request. The user request and repository instructions always win.

Load each chained skill before following it. In Codex, invoke `$skill-name`. In Pi, read the sibling `../<skill-name>/SKILL.md` relative to this skill because `/skill:name` is expanded only from user input.

## Gate profile

Classify the task after initial inspection and escalate whenever later evidence raises the risk:

- **Low:** contained, reversible work with a small affected surface and no trust-boundary, data-loss, schema, public-compatibility, concurrency, or production-operations risk.
- **Medium:** meaningful regression or integration risk across callers or slices without a high-risk trigger.
- **High:** security or authorization, money, destructive data or migrations, concurrency, public compatibility, infrastructure, irreversible operations, or broad cross-cutting change.

Use one slice for contained work. For multiple slices, use the smallest coherent vertical slices that leave the branch runnable; never slice merely by file or architectural layer.

| Profile | Slice gate | Final gate |
| --- | --- | --- |
| Low | Targeted validation only | One independent review |
| Medium | Audit each completed slice | One cumulative independent review |
| High | Audit and independently review each completed slice | One cumulative independent review |

A clean independent review covers any later gate aimed at the exact same final diff. Never review unchanged content twice.

Do not create workflow records, controller state, or evidence manifests. Preserve unrelated changes. Create checkpoint commits only at coherent review boundaries, never as save points. Keep one canonical branch and pull request. Before switching or creating a branch, inspect the current branch, base, remotes, and open pull requests; continue a clear match and ask when ownership is ambiguous. Never create another worktree or merge unless the user explicitly asks.

## Prompt Chain

1. **Orchestrate:** Read applicable `AGENTS.md`, inspect the worktree and immediate code path, and create a compact task packet containing the objective, acceptance criteria, non-goals, constraints, affected surface, invariants, validation commands, done condition, gate profile, canonical branch, and base commit. Keep a matching branch or pull request; create one task branch only when no match exists.
2. **Scout and plan when useful:** Load and invoke `software-engineering-scout-plan` when ownership, callers, tests, risks, dependencies, order, or slice boundaries are unclear. Also invoke it for complex or high-risk work when `.understand-anything/knowledge-graph.json` exists. Merge verified findings into the task packet.
3. **Implement one slice:** Load and invoke `software-engineering-implement-integrate` for the current slice, including required tests, documentation, wiring, and validation. Stop at the coherent slice boundary.
4. **Validate, audit, and checkpoint the slice:** For medium- or high-risk work, load and invoke `software-engineering-audit-fix` on the uncommitted slice and affected callers, supplying the task packet; low-risk work keeps the targeted validation from implementation. Validate repairs, inspect the diff and status, run `git diff --check`, and commit the coherent slice. For a high-risk task, read [REVIEW.md](REVIEW.md), update its temporary review packet with observed validation, and independently review the slice commit. Fix verified in-scope blockers, validate, amend the unpublished checkpoint when it is still the latest commit, and rerun the changed commit review. Use a separate repair commit only when history is already shared or the repair spans earlier commits. Stop and report blocked after two failed repair/re-review rounds.
5. **Repeat:** For multiple slices, start the next only after the current slice gate in the table passes.
6. **Integrate and review the final diff:** Run integrated validation. For medium- or high-risk work, invoke `software-engineering-audit-fix` on the cumulative diff only when conflict resolution, final wiring, or later repairs introduced behavior not covered by slice audits; low-risk work adds no separate audit unless evidence escalates its profile. Read [REVIEW.md](REVIEW.md), refresh its temporary packet with the final validation evidence, and run the final independent review required by the table unless an earlier clean review covered the exact final diff. Verify findings, repair blockers in one consolidated pass, rerun affected validation and audit scopes, commit using the history rule above, and review only the changed final diff. Stop and report blocked after two failed repair/re-review rounds.
7. **Retrospect when useful:** Load and invoke `software-engineering-retrospective` for high-risk, substantial, long-running, multi-commit, or materially repaired work. For straightforward low- or medium-risk work, put a concise verdict in the final report instead. If a retrospective finds a delivery blocker, return through step 6 once; report blocked if it remains.
8. **Publish and report:** Push the canonical branch, update its existing pull request or open one when none exists, and leave it open. Report completed behavior, checks, audits, independent reviews, retrospective or concise verdict, residual risks, commit hashes, and pull request URL.

If a required implementation, validation, commit, review, push, or pull request operation cannot run, report the exact blocker without claiming the chain completed.
