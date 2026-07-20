---
name: software-engineering-scout-plan
description: Chain focused read-only scouting and planning prompts for a coding task. Use when ownership, callers, tests, conventions, risks, affected components, dependency order, or safe work slicing are unclear, or when the user explicitly asks to scout or plan before implementation.
---

# Software Engineering Scout And Plan

Use only the prompts that reduce uncertainty. Do not edit or commit.

## Prompt Chain

1. **Scout, if needed:** Read applicable `AGENTS.md`, relevant source and callers, tests, build configuration, nearby conventions, and repository status. Return concise facts with file references, runnable validation commands, concrete risks, and unknowns. Use parallel read-only scouts only for distinct independent questions.
2. **Plan, if needed:** Turn the request and scout findings into the smallest complete implementation route. Prefer one slice. Split only for real dependency order or independently deliverable work, and note likely writable files, acceptance criteria, validation, integration points, and risks.
3. **Handoff:** Return one compact task packet containing the objective, acceptance criteria, non-goals, relevant files, validation commands, invariants, known risks, and any justified slices.

For a contained task with an obvious code path, say formal scouting or slicing is unnecessary and return only the compact task packet.
