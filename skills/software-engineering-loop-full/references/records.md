# Durable records

Store run artifacts under `.codex/software-engineering/<run-id>/` so a human or a later Codex thread can resume without reconstructing hidden context.

## `state.json`

Required fields:

```json
{
  "runId": "se-YYYYMMDD-HHMMSS",
  "taskClass": "small_edit|bug_fix|medium_component|large_component|refactor|integration",
  "status": "planning|running|blocked|degraded|passed",
  "planId": "plan-id",
  "currentSlice": "S1",
  "maxAttempts": 2,
  "writerLock": null,
  "checkpointSha": null,
  "finalSha": null,
  "finalValidation": "pending|pass|changes_requested|blocked",
  "finalValidationAttempts": 0,
  "pushed": false
}
```

## `plan.md`

Record objective, in/out scope, current system context, risks, acceptance criteria, ordered slices, review gates, and the local-only commit policy.

## `slices/<slice-id>.md`

Record:

- slice ID and parent plan ID
- objective and scope boundaries
- acceptance criteria
- likely and changed files
- implementer thread ID
- implementation notes
- validation commands, attempt, exit codes, output SHA-256, diff hash, stable content hash, and HEAD SHA
- tech-debt sweep result and fixes
- process-debt sweep result and fixes
- handoff notes
- terminal status

Update records after each state transition, not only at the end.

The state helper rejects illegal phase order, a third gate attempt, a second slice/finalization writer, a passing validation without matching machine-run content evidence, and final success while either lock representation remains held. Gate histories preserve prior findings. Each final review records its evidence, reviewed SHA, diff hash, and stable content hash. Native Codex review additionally requires the exact command and its exit evidence against the checkpoint SHA. Final success requires a clean non-record worktree at the recorded final HEAD, final reviews bound to that content, and passing final-validation command evidence for the same content.

## Reviewer result

All machine-consumed reviewers return:

```json
{
  "status": "pass|changes_requested|blocked",
  "summary": "short result",
  "findings": [
    {
      "severity": "high|medium|low",
      "location": "path:line or workflow record",
      "problem": "concrete issue",
      "requiredChange": "smallest acceptable correction"
    }
  ]
}
```

Ignore style preferences that do not affect correctness, maintainability, scope, or the explicit workflow policy.
