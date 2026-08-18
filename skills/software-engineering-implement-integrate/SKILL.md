---
name: software-engineering-implement-integrate
description: Chain implementation, targeted validation, and integration prompts to complete an approved coding change or one reviewable vertical slice. Use when a task or slice is understood and needs executable code, tests, required documentation, wiring, cleanup, and safe integration without running the separate audit workflow.
---

# Software Engineering Implement And Integrate

Make the smallest complete change that satisfies the assigned task or vertical slice. Keep the branch coherent and runnable at a slice boundary. A single coherent change needs one implementer and no integration ceremony.

## Prompt Chain

1. **Implement:** Read applicable `AGENTS.md`, the assigned task or slice, relevant source, and callers of shared code being changed. Reuse repository patterns and installed dependencies. Include required code, focused tests, documentation, wiring, and cleanup directly caused by this scope; do not pull later slices forward.
2. **Validate:** Run the cheapest relevant tests, lint, typecheck, or build. Fix failures caused by the change.
3. **Integrate, if needed:** Use multiple implementers only for independent slices with disjoint writable files. Keep all work on the canonical branch and shared worktree selected by the invoking workflow; do not create branches, worktrees, or pull requests here. Reject stale or unrelated changes and rerun affected checks after integration.
4. **Handoff:** Report changed files, behavior, validation results, integration decisions, remaining known risks, and whether the assigned slice is ready for adversarial review.

Leave the completed task or slice ready for audit. Do not commit unless the invoking workflow or user asks, and never push, merge, or open a pull request.
