---
name: software-engineering-implement-integrate
description: Chain implementation, targeted validation, and integration prompts to complete an approved coding change. Use when a task is understood and needs executable code, tests, required documentation, wiring, cleanup, and safe integration without running the separate audit workflow.
---

# Software Engineering Implement And Integrate

Make the smallest complete change that satisfies the request. Adapt the chain to the task; a single coherent change needs one implementer and no integration ceremony.

## Prompt Chain

1. **Implement:** Read applicable `AGENTS.md`, the task packet or request, relevant source, and callers of shared code being changed. Reuse repository patterns and installed dependencies. Include required code, focused tests, documentation, wiring, and cleanup directly caused by the change.
2. **Validate:** Run the cheapest relevant tests, lint, typecheck, or build. Fix failures caused by the change.
3. **Integrate, if needed:** Use multiple implementers only for independent slices with disjoint writable files, isolating concurrent work in Git worktrees. Integrate sequentially, reject stale or unrelated changes, and rerun affected checks after integration.
4. **Handoff:** Report changed files, behavior, validation results, integration decisions, and remaining known risks.

Leave the completed change ready for audit. Do not commit unless the invoking workflow or user asks, and never push, merge, or open a pull request.
