---
name: software-engineering-retrospective
description: Produce an evidence-based retrospective of completed engineering work by explaining every task commit, the rationale and tradeoffs behind it, what held up, what fell short, and what should be done differently. Use after substantial or long-running coding tasks, before final delivery, or whenever the user asks for an honest commit-by-commit explanation or self-critique.
---

# Software Engineering Retrospective

Inspect the completed work and give the user the candid engineering judgment that is usually lost in a completion summary. Treat this as a read-only assessment unless the user or invoking workflow explicitly requests repair.

## Evidence

1. Reconstruct the original objective, constraints, and acceptance criteria from the request.
2. Identify only the commits belonging to the task. Inspect each commit's full diff and message, the final worktree, validation results, audit findings, and review output. Do not attribute pre-existing or unrelated changes to the task.
3. Distinguish observed facts from inferred rationale. Never claim a check passed unless its result is available.
4. Compare the final behavior with the whole request path. Call out mitigations presented as fixes, symptom patches that leave shared causes intact, shifted costs, and new operational or user-facing tradeoffs.

## Assessment

Report in this order:

1. **Verdict:** State plainly whether the work fully solves the problem, partially solves it, or should not ship, and why.
2. **Each task commit:** For every commit, name its hash and subject, then explain:
   - what behavior or architecture changed;
   - why that decision was reasonable with the evidence available at the time;
   - what was done well;
   - what was incomplete, mistaken, or harder to review than necessary.
3. **What to keep and what to change:** Separate durable decisions from temporary mitigations or regrettable choices.
4. **If starting again:** Give the smallest concrete alternative sequence and explain why it is better. Include commit boundaries when the original work was too broad.
5. **Evidence and residual risk:** List the checks actually observed and the remaining uncertainty.

Be specific without manufacturing regret. Do not defend a decision merely because it is already implemented, and do not propose a rewrite when the existing approach is sound. Prefer a precise qualitative verdict over an arbitrary score.

If the assessment reveals a verified correctness, security, data-loss, or acceptance-criteria failure, label it as a delivery blocker. In an orchestrated workflow, return it to the existing audit-and-repair step and repeat the retrospective after the repair; otherwise report it without silently changing the work.
