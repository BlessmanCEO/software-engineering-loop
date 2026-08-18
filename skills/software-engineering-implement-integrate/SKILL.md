---
name: software-engineering-implement-integrate
description: Chain focused bug diagnosis when needed, implementation, targeted validation, and integration to complete an approved coding change or one reviewable vertical slice. Use when a task or slice needs executable code, tests, required documentation, wiring, cleanup, and safe integration without running the separate audit workflow.
---

# Software Engineering Implement And Integrate

Make the smallest complete change that satisfies the assigned task or vertical slice. Keep the branch coherent and runnable at a slice boundary. A single coherent change needs one implementer and no integration ceremony.

## Prompt Chain

1. **Diagnose reported bugs and regressions:** Before fixing, build and run one fast, deterministic, agent-runnable command that exercises the real path and fails on the user's exact symptom. Prefer an existing test, then the smallest test or harness at the correct seam. For a hard or non-obvious bug, minimise the reproduction, rank falsifiable hypotheses, and change one variable per probe; for performance work, capture a baseline measurement and profile or bisect instead of adding broad logs. If no red-capable loop is possible, request the missing environment, a redacted captured artifact, or permission for targeted instrumentation rather than guessing. Never expose secrets in commands, output, or artifacts.
2. **Implement:** Read applicable `AGENTS.md`, `CONTEXT.md` and relevant ADRs when present, the assigned task or slice, relevant source, and callers of shared code being changed. Reuse repository patterns and installed dependencies. For a bug, fix the shared root cause and turn the minimal reproduction into a regression test before the fix when a correct seam exists; otherwise document why it cannot be locked down. Include required code, focused tests, documentation, wiring, and cleanup directly caused by this scope; do not pull later slices forward.
3. **Validate:** For a bug, re-run the original feedback command and regression test when one exists. Then run the cheapest relevant lint, typecheck, build, or integration check, fix failures caused by the change, and remove temporary harnesses and tagged diagnostic instrumentation.
4. **Integrate, if needed:** Use multiple implementers only for independent slices with disjoint writable files. Keep all work on the canonical branch and shared worktree selected by the invoking workflow; do not create branches, worktrees, or pull requests here. Reject stale or unrelated changes and rerun affected checks after integration.
5. **Handoff:** Report changed files, behavior, validation results, integration decisions, remaining known risks, and whether the assigned slice is ready for adversarial review. For a bug or regression, include the redacted feedback command and its before-and-after result.

Leave the completed task or slice ready for audit. Do not commit unless the invoking workflow or user asks, and never push, merge, or open a pull request.
