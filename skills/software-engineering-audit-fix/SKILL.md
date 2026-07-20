---
name: software-engineering-audit-fix
description: Chain bug, security, technical-debt, process-debt, repair, and validation prompts over a completed code change. Use after implementation, before a release or commit, or whenever the user requests a comprehensive change audit and repair without durable audit records.
---

# Software Engineering Audit And Fix

Audit the completed change plus affected callers and consumers. Keep findings in the active thread; create no records or commits. Adjust depth to the change, but consider every lens.

## Prompt Chain

1. **Bug hunt:** Check requirements, logic, edge cases, error handling, regressions, wiring, compatibility, concurrency, and test gaps.
2. **Security check:** Check trust boundaries, authentication and authorization, validation, injection, secrets, unsafe file/process/network access, dependency risk, and data leakage.
3. **Technical-debt check:** Find unnecessary complexity, duplication, dead code, brittle coupling, maintainability regressions, or shortcuts introduced or materially worsened by the change.
4. **Process-debt check:** Find missing validation, tests, documentation, migrations, rollback handling, generated artifacts, operational readiness, or scope discipline required by the change.
5. **Verify and repair:** Confirm findings against the code, discard false positives and unrelated pre-existing debt, then fix valid in-scope root causes in one consolidated pass.
6. **Validate:** Run targeted checks for repaired areas and an integrated check covering the affected surface.
7. **Handoff:** Report fixed findings, rejected findings with reasons, validation results, and genuine residual risk.

Run the four review prompts as one unified audit by default. Split them into parallel specialists only when change size or risk makes independent review worthwhile.
