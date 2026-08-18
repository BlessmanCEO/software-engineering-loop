---
name: software-engineering-scout-plan
description: Chain focused read-only scouting and planning prompts for a coding task, including relevant Understand Anything knowledge-graph context when available. Use when ownership, callers, tests, conventions, risks, affected components, dependency order, wider system relationships, or safe work slicing are unclear, or when the user explicitly asks to scout or plan before implementation.
---

# Software Engineering Scout And Plan

Use only the prompts that reduce uncertainty. Do not edit or commit.

For complex or cross-cutting work, use `.understand-anything/knowledge-graph.json` when it exists. Read only project metadata, task-relevant nodes matched by name, summary, or tags, their one-hop edges, and their layer context. Compare the graph's `project.gitCommitHash` with `HEAD` and check task-relevant uncommitted changes; if either differs from the graph snapshot, label the affected graph context stale and use it only to guide source inspection. Treat every graph relationship as a lead and verify affected files, callers, consumers, configuration, and tests against the current source. Do not dump the whole graph, rebuild it automatically, or block work when it is absent or has no relevant node.

## Prompt Chain

1. **Scout, if needed:** Read applicable `AGENTS.md`, current source and callers, tests, build configuration, nearby conventions, and repository status. For complex or cross-cutting work, also read the relevant graph context described above and trace beyond the initial code path when graph edges or source evidence identify affected components. Return concise verified facts with file references, runnable validation commands, concrete risks, unknowns, and any graph-staleness warning. Use parallel read-only scouts only for distinct independent questions.
2. **Plan, if needed:** Turn the request and scout findings into the smallest complete implementation route. Prefer one slice for contained, low-risk work. Split complex or high-risk work into the smallest coherent vertical slices that can be validated and adversarially reviewed before the next slice; do not slice merely by file or architectural layer. Note likely writable files, acceptance criteria, validation, integration points, and risks.
3. **Handoff:** Return one compact task packet containing the objective, acceptance criteria, non-goals, relevant files, validation commands, invariants, known risks, and any justified slices.

For a contained task with an obvious code path, say formal scouting or slicing is unnecessary and return only the compact task packet.
