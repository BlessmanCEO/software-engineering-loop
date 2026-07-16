# Workflow

## State flow

```text
classify
  -> planning loop
  -> slice loop x N
  -> completion check
  -> checkpoint commit
  -> Codex review gate
  -> finalization loop
  -> final local commit
  -> stop
```

Only three parts are agent feedback loops. Classification, state changes, validation commands, commits, and stopping are supervisor actions.

When native spawn supports typed custom agents, select the named profile directly. When it does not, run the same profile through:

```bash
python3 <skill-dir>/scripts/run_profile.py \
  --profile se-scout --repo <repo> --prompt <bounded-task>
```

The runner starts an isolated Codex worker with the profile's exact model and sandbox and disables recursive delegation. Parallelize independent runner calls through the available execution tool, not shell background tricks.

For simple work, the supervisor may directly launch:

- `se-terra-helper` (`gpt-5.6-terra`, high, read-only) for bounded scouting, plan checks, and review triage.
- `se-terra-implementer` (`gpt-5.6-terra`, high, workspace-write) for a low-risk slice while the normal writer lock is held.

These are companions, not nested agents. They cannot approve their own output. Use the Sol/high planner, implementer, and reviewer for architecture, security, persistence, shared contracts, ambiguous failures, and final gate decisions.

## 1. Planning loop

Use for bug fixes and medium or large work. A small edit can skip to a single implicit slice unless it changes architecture, security, data flow, multiple files, or public behavior.

Run these read-only `se-scout` specialists in parallel, with the listed role in each prompt:

- `repo-scout`: map relevant modules, conventions, integration points, and likely files.
- `test-scout`: find validation commands, existing coverage, edge cases, and likely regression tests.
- `risk-scout`: inspect security, persistence, public contracts, deployment, and migration risk when relevant.

Give their outputs to one `se-planner`. The planner produces the objective, scope, acceptance criteria, ordered slices, likely files, validation, risks, and commit metadata. For a bug, produce one bug-fix mini-plan and normally one slice.

The supervisor rejects a plan that has overlapping slices, missing acceptance criteria, speculative future architecture, or slices that cannot be validated independently. Repair at most twice.

## 2. Slice loop

Create one writable `se-implementer` thread for the current slice. It receives only the parent plan, current slice, relevant prior handoff, and specialist findings.

For each slice:

1. Reuse the planning scout findings for the first slice. Run new read-only `se-scout` code/test passes only when findings are missing or a completed slice changed the relevant boundary.
2. Acquire the writer lock for the implementer thread, let it make the smallest complete change, then release the lock.
3. Run each validation command through `record-validation`, using the same attempt number for commands in one validation round.
4. Run `se-reviewer` with the `tech-debt-reviewer` role read-only.
5. If changes are requested, return findings to the same implementer thread, validate again, and rerun the tech gate.
6. Run `se-reviewer` with the `process-debt-reviewer` role only after the tech gate passes.
7. If changes are requested, repair the record or implementation as appropriate, then rerun affected gates.
8. Record the handoff and close the slice.

Never run slice implementers concurrently in one working tree. The supervisor must hold `.writer.lock` for the active implementer; a second acquisition is a machine failure.

### Tech-debt gate

Check file size, responsibilities, readability, names, duplication, error states, edge cases, contracts, tests, dependencies, dead code, configuration, and repository conventions. Treat 500 lines as a design warning; record justified generated/static/framework exceptions. Prefer a split plan when adding logic to a file over 450 lines.

### Process-debt gate

Check plan alignment, scope drift, acceptance criteria, recorded validation, assumptions, risks, docs, deferred work, and next-slice handoff. Do not hide unresolved items.

## 3. Finalization loop

After all slices pass:

1. Run a completion check across acceptance criteria, tests, hidden TODOs, records, and system wiring.
2. Create a local checkpoint commit.
3. Run `codex review --commit <checkpoint-sha>` through `record-review-command`, then record the interpreted result with `set-review` against that SHA.
4. Acquire `acquire-finalizer`, send valid findings to one `se-implementer`, then release the lock before re-reviewing.
5. Run `se-reviewer` for these read-only gates in order, repairing and rechecking each before continuing:
   - lean review
   - tech-debt review
   - process-debt review
   - wider-system wiring review
6. Run the relevant commands through `record-final-validation`, binding passing machine evidence to the reviewed content.
7. Create a final local commit only when review or wiring fixes changed files. Otherwise record the checkpoint SHA as the final SHA.

The wiring gate checks exports, imports, routes, handlers, UI entry points, jobs, configuration, migrations, build/test scripts, docs, and orphaned components as applicable.

## Outcomes

- `passed`: all required gates passed and local commits are recorded.
- `blocked`: a required action cannot continue safely or a repair budget is exhausted.
- `degraded`: work is otherwise complete but a named review/validation surface was unavailable; never report full completion without disclosing it.

## Non-negotiable policy

- Never push, merge, or open a pull request.
- Never let a later slice start while the current slice has a failed gate.
- Never let more than one writer mutate the same working tree.
- Never claim a command, test, review, or commit happened without captured evidence.
- Never continue when the bundled execution policy fails its negative probes; load it only in isolated worker homes.
- Never create package/domain/application/infrastructure/UI folders merely to match a template; use the repository's current structure and split only when responsibilities require it.

## State command sequence

```bash
# Health, easy start, and resume
python3 <helper>
python3 <helper> init
python3 <helper> resume-status --run-dir <run-dir>

# One writer only
python3 <helper> acquire-writer --run-dir <run-dir> --slice S1 --owner <thread-id>
python3 <helper> release-writer --run-dir <run-dir> --owner <thread-id>

# Machine-run validation; repeat commands with the same attempt for one round
python3 <helper> record-validation --run-dir <run-dir> --slice S1 --attempt 1 -- <test-command>

# Locked post-checkpoint repairs, followed by validation of the final reviewed content
python3 <helper> acquire-finalizer --run-dir <run-dir> --owner <thread-id>
python3 <helper> release-writer --run-dir <run-dir> --owner <thread-id>
python3 <helper> record-final-validation --run-dir <run-dir> --attempt 1 -- <test-command>

# Agent-reviewed gates; attempt must be 1 or 2
python3 <helper> set-slice-gate --run-dir <run-dir> --slice S1 \
  --gate techDebt --status pass --attempt 1 --evidence <summary>
python3 <helper> set-slice-status --run-dir <run-dir> --slice S1 --status complete
```
