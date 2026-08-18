---
name: software-engineering-audit-fix
description: Chain standards, spec, bug, security, technical-debt, process-debt, repair, and validation prompts over a completed change, reviewable slice, or cumulative branch diff. Use during iterative implementation, before a release or commit, or whenever the user requests a comprehensive change audit and repair without durable audit records.
---

# Software Engineering Audit And Fix

Audit the supplied slice or cumulative change plus affected callers and consumers. Keep findings in the active thread; create no records or commits. Adjust depth to the scope and risk, but consider every lens.

## Prompt Chain

1. **Pin the review:** Identify the exact slice or branch diff, its commits, and the originating request, acceptance criteria, linked issue, or supplied spec. For a branch comparison, resolve the base and review its merge-base diff with `HEAD`; stop if the ref is invalid or the expected diff is empty. Treat the user request as the spec when no separate artifact exists, and state when no spec is available.
2. **Standards review:** Compare the diff with applicable `AGENTS.md`, contributing guides, coding standards, and nearby established conventions. Cite documented-rule violations. Also scan for possible Fowler smells—unclear names, duplication, feature envy, data clumps, primitive obsession, repeated switches, shotgun surgery, divergent change, speculative generality, message chains, middle men, and refused bequests—as judgement calls only. Repository rules override this baseline; skip checks already enforced by tooling.
3. **Spec review:** Independently compare the diff with the spec. Cite the requirement behind each finding and report missing or partial requirements, unrequested scope, and implementations that appear present but behave incorrectly. If no spec is available, report that this axis was skipped.
4. **Bug hunt:** Check requirements, logic, edge cases, error handling, regressions, wiring, compatibility, concurrency, and test gaps.
5. **Security check:** Check trust boundaries, authentication and authorization, validation, injection, secrets, unsafe file/process/network access, dependency risk, and data leakage.
6. **Technical-debt check:** Find unnecessary complexity, duplication, dead code, brittle coupling, maintainability regressions, or shortcuts introduced or materially worsened by the change.
7. **Process-debt check:** Find missing validation, tests, documentation, migrations, rollback handling, generated artifacts, operational readiness, or scope discipline required by the change.
8. **Verify and repair:** Confirm findings against the code and discard false positives and unrelated pre-existing debt. For a reported or non-obvious runtime or performance bug, require a red-capable command that reproduces the exact symptom before repairing it; request a redacted artifact, missing environment access, or targeted instrumentation when that is impossible. Fix valid in-scope root causes and recheck repaired areas until no verified blocker remains.
9. **Validate:** Run targeted checks for repaired areas and an integrated check covering the affected surface. For bug repairs, re-run the original reproduction and its regression test when one exists, then remove temporary harnesses and diagnostic instrumentation.
10. **Handoff:** Keep Standards and Spec findings separate, with a count and worst issue for each axis. Then report fixed findings, rejected findings with reasons, validation results, and genuine residual risk.

Keep the Standards and Spec passes independent so one cannot mask the other. Run the review prompts as one unified audit by default; split independent axes or lenses into parallel specialists only when change size or risk justifies the overhead.
