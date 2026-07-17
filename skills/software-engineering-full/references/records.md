# Durable records

Store resumable artifacts under `.codex/software-engineering/<run-id>/`:

```text
state.json
plan.md
slices/
evidence/
reviews/
logs/
```

## State

`state.json` records `schemaVersion`, `pluginVersion`, monotonic `revision`, run and plan IDs, task class, status, timestamps, active operations, writer and validation leases, recovery state, slice dependencies and phases, validation and review status, checkpoint/final SHAs, and final evidence status.

Only `workflow_state.py` mutates state. Its atomic writer increments the revision and update timestamp on every write. A persisted lease makes interrupted work visible to `resume-status` instead of silently losing the active operation.

## Plan

In `plan.md`, record the formal task contract, uncertainties and their resolution, proof obligations, dependency-aware slices, specialist triggers, rollback expectations, risks, and local-only commit policy. Assign every acceptance criterion to at least one slice.

## Slice records

For each `slices/<slice-id>.md`, record:

- objective, scope, criteria, invariants, dependencies, and proof obligations
- likely and actual files
- base SHA/content hash, worktree, implementer, and patch hash
- targeted validation commands and results
- one complete structured review round and finding resolutions
- comments and maintained documentation changed, or why neither was needed
- repair attempts, handoff, rollback notes, and terminal status

Keep these human-readable records current after each transition. Machine evidence is also written to `evidence/`, `reviews/`, and `logs/`.

## Evidence

Worker and final validation capture command, exit code, timestamps, duration, output hash and log, pre/post content and diff hashes, mutation detection, tool name, environment metadata, and HEAD SHA. A worker validation that changes tracked or untracked repository content fails.

Native Codex review must exactly execute `codex review --commit <checkpoint-sha>`. A changed final commit must descend from that checkpoint. Final success requires a clean non-record worktree, passing required reviews and validation bound to final content, no live lease, and `pushed: false`.

The final machine check writes `evidence/manifest.json` with the schema/plugin versions, commit SHAs, final content hash, and hashes of recorded artifacts.

## Structured review result

Return one complete result per slice, batch, final system review, or triggered specialty:

```json
{
  "status": "pass|changes_requested|blocked",
  "summary": "short result",
  "areasChecked": ["correctness", "tests", "wiring"],
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

Record all findings atomically. Ignore preferences that do not affect correctness, maintainability, scope, risk, or policy.
