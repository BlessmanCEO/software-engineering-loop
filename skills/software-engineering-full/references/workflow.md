# Full workflow

Use this workflow for high-risk, large, regulated, security-sensitive, or operationally important work. It includes the useful fast-mode practices plus durable state, formal evidence, specialist review, recovery, and stricter transitions.

## 1. Formal task contract

Record the objective, business or technical reason, in-scope work, explicit non-goals, acceptance criteria, invariants, constraints, risk classification, rollback expectations, and definition of done in `plan.md`.

## 2. Durable run initialization

Create:

```text
.codex/software-engineering/<run-id>/
  state.json
  plan.md
  slices/
  evidence/
  reviews/
  logs/
```

State records schema and plugin versions, run ID, task class, status, revision, slice dependencies, active operations, writer and validation leases, checkpoint and final SHAs, review and validation status, timestamps, and recovery information.

## 3. Parallel specialist inspection

Run repository, test, and risk scouts in parallel. Add the reusable `se-specialist` only when triggered:

| Trigger | Specialist role |
| --- | --- |
| Authentication, permissions, secrets | Security |
| Database or schema changes | Migration and rollback |
| Public APIs, events, shared types | Compatibility |
| Jobs, queues, async state | Concurrency |
| Performance-sensitive paths | Performance |
| User-facing workflows | UX/accessibility |
| Deployment or configuration | Operations |

## 4. Resolve uncertainty

Classify unanswered questions in `plan.md`:

```yaml
uncertainties:
  - question:
    status: repository_resolvable | safe_assumption | product_decision | blocked
    resolution:
```

Resolve repository-answerable questions before planning. Do not silently invent important product or governance decisions.

## 5. Define proof obligations

Map every acceptance criterion to implementation and evidence:

```yaml
proof_obligations:
  - criterion:
    implementation_surface:
    required_test:
    required_review:
    status:
```

Do not finish until every criterion is proven or explicitly deferred.

## 6. Build the dependency-aware plan

For every slice record its ID, objective, scope, acceptance criteria, `depends_on`, likely writable files, invariants, validation commands, specialist triggers, rollback considerations, and handoff requirements.

Reject cycles, concurrent writable overlap, slices that cannot be tested independently, and acceptance criteria that belong to no slice.

## 7. Prepare slices durably

Prepare independent slices concurrently only in isolated worktrees. Record base SHA and content hash, worktree identifier, implementer identity, declared and actual files, patch hash, timestamps, validation evidence, and current phase. Prepared work must be resumable.

## 8. Validate in each worker

Before integration, run targeted validation in the prepared worktree. Capture command, exit code, start and end time, duration, stdout/stderr logs, output hash, pre/post content hashes, tool versions, and environment metadata. Fail validation if the command unexpectedly mutates repository content.

## 9. Integrate under lease

Integrate one slice at a time under the exclusive repository writer lease. Verify completed dependencies, unchanged base assumptions, patch hash, declared scope, no stale or overlapping work, and unchanged content since validation.

## 10. Record one formal slice review

Use one structured reviewer call covering correctness, acceptance criteria, regression risk, tests, technical and process debt, triggered security and compatibility concerns, wiring, documentation, and scope control. Record the entire round atomically so later findings are not lost when an earlier area fails.

## 11. Repair and revalidate

Aggregate findings into one repair pass for the original implementer. Rerun affected validation and review areas, preserve findings and resolutions, and stop after two failed rounds.

## 12. Close the slice

Close only when acceptance criteria and proof obligations pass, validation and review evidence match current content, handoff notes are complete, and dependents can safely consume it.

## 13. Run completion review

After every slice closes, check acceptance criteria, proof obligations, hidden TODOs, unresolved assumptions, documentation, migrations, rollback readiness, operational impact, cross-slice wiring, and deferred work.

## 14. Commit the checkpoint

Create a clean local checkpoint commit. Record commit, content, plan, records, and evidence-manifest hashes. Never run native Codex review against uncommitted changes.

## 15. Run final reviews in parallel

Against the exact checkpoint, run:

- `codex review --commit <checkpoint-sha>`
- one unified system review
- triggered specialist reviews

The unified review covers lean implementation, cross-system wiring, maintainability, compatibility, test sufficiency, operational readiness, acceptance criteria, and proof obligations.

## 16. Add a pre-mortem for critical work

For authentication, permissions, persistence, migrations, governance, queues/concurrency, or destructive operations, ask: assume this caused a production incident; identify likely causes and whether the implementation prevents or detects them.

## 17. Review observability and recovery

For production-impacting work, verify detection, logs, metrics, tracing, alerts, retries, idempotency, partial failure handling, feature disablement, rollback, and operator recovery instructions.

## 18. Run one final repair round

Aggregate valid final findings for the relevant original implementer. Rerun affected specialist and unified reviews. Keep native Codex review attached to the checkpoint. Record which findings were fixed or rejected.

## 19. Validate the exact final content

Choose the appropriate unit, integration, contract, migration, rollback, concurrency, security, build/package, and smoke checks. All evidence must match the final content hash.

## 20. Commit and bundle the audit

Create a separate final local commit when content changed after checkpoint. Produce an evidence manifest containing the plan, slice records, validation logs, reviewer results, proof obligations, commit SHAs, content hashes, tool versions, risks, deferred work, and rollback instructions. Run the final machine check before reporting success.

## Outcomes

- `passed`: every required gate passed and local commits are recorded.
- `blocked`: a required action cannot continue safely or exhausted two repair rounds.
- `degraded`: work is otherwise complete but a named review or validation surface was unavailable; never report full success.

## State command outline

```bash
python3 <helper> init --repo <repo> --run-id <run-id> --task-class <class> --slices S1 S2
python3 <helper> resume-status --run-dir <run-dir>
python3 <helper> release-validation --run-dir <run-dir> --reason <interruption-summary>
python3 <helper> record-slice-validation --run-dir <run-dir> --slice S1 \
  --worktree <worktree> --attempt 1 -- <test-command>
python3 <helper> acquire-writer --run-dir <run-dir> --slice S1 --owner <thread-id>
python3 <helper> release-writer --run-dir <run-dir> --owner <thread-id>
python3 <helper> set-slice-review --run-dir <run-dir> --slice S1 --attempt 1 \
  --status pass --areas <areas> --evidence <review-json>
python3 <helper> set-slice-status --run-dir <run-dir> --slice S1 --status complete \
  --proof-status pass --handoff <summary>
python3 <helper> record-review-command --run-dir <run-dir> --name codex \
  --attempt 1 --sha <checkpoint-sha> -- codex review --commit <checkpoint-sha>
python3 <helper> record-final-validation --run-dir <run-dir> --attempt 1 -- <test-command>
python3 <helper> check --run-dir <run-dir> --final
```
