# Full workflow

Use one scope-limited Sol/high `se-implementer` for the complete slice, including executable code, tests, necessary rationale comments, and maintained documentation. `se-reviewer` is Sol/high and read-only; every Terra profile is read-only. The supervisor may directly create and update only `plan.md` and `slices/*.md`, plus mechanically apply a verified implementer patch from an isolated worktree; mutate `state.json` only through `workflow_state.py`.

## Worker execution

Use native typed agents when the spawn surface supports the installed profiles. Otherwise run the same profile through:

```bash
python3 <skill-dir>/scripts/run_profile.py \
  --profile se-implementer --repo <repo> --prompt <bounded-task>
```

The isolated runner applies the profile's exact model, reasoning, sandbox, and bundled execution policy, and disables recursive delegation. Never silently substitute a model or sandbox. Keep `agents.max_depth = 1` for native workers. Never run more than one writable worker in a working tree. Parallel implementers require separate temporary Git worktrees based on the same integration HEAD.

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

Planning and finalization are the agent feedback loops. Classification, state changes, validation commands, commits, and stopping are supervisor actions.

Parallelize independent worker calls through the available execution tool, not shell background tricks. Read-only Terra workers cannot approve implementation output; required gates use `se-reviewer`.

## 1. Planning loop

Use the planning loop. A bounded task can use one slice, but it still keeps the full state-and-evidence workflow.

Do not generate or refresh a knowledge graph unless the task is broad, the repository is unfamiliar, or the user explicitly requests it. Prefer direct source inspection for contained work.

Run these read-only `se-scout` specialists in parallel, with the listed role in each prompt:

- `repo-scout`: map relevant modules, conventions, integration points, and likely files.
- `test-scout`: find validation commands, existing coverage, edge cases, and likely regression tests.
- `risk-scout`: inspect security, persistence, public contracts, deployment, and migration risk when relevant.

Give their outputs to one `se-planner`. The planner produces the objective, scope, acceptance criteria, slices, `depends_on` for each slice, likely files, validation, risks, and commit metadata. Do not add another agent call to plan parallelism. For a bug, produce one bug-fix mini-plan and normally one slice.

The supervisor rejects a plan that has missing acceptance criteria, speculative future architecture, invalid dependencies, overlapping files among concurrently ready slices, or slices that cannot be validated independently. Repair at most twice.

## 2. Slice loop

Compute the ready set from completed dependencies. Start ready slices concurrently only when their likely writable files are disjoint. Each `se-implementer` receives only the parent plan, its slice, dependency handoffs, specialist findings, and an isolated temporary Git worktree based on the same integration HEAD. If isolation is unavailable, run slices sequentially.

Parallel workers prepare changes only. After they finish, integrate one slice at a time into the primary worktree under the durable writer lock by applying the verified worker diff without committing it. Declare slices in topological integration order because the state helper enforces that order. Reject or rerun a prepared slice when its patch conflicts, its dependency changed, or it touches an undeclared file that overlaps another ready slice. Remove temporary worktrees after their changes are safely integrated; do not delete a worktree containing unintegrated changes.

For each slice:

1. Reuse planning scout findings. Run new read-only scouts only when findings are missing or an integrated dependency changed the relevant boundary.
2. Let each ready implementer make the smallest complete slice change in its isolated worktree. It owns executable code, tests, concise non-obvious rationale comments, and required maintained documentation.
3. Integrate one prepared slice into the primary worktree under `acquire-writer`, inspect its actual changed files against the plan, then release the lock.
4. Record the handoff, close the slice, and release newly ready dependents. Validation and review wait until every slice is integrated.

Never run slice implementers concurrently in one working tree. `.writer.lock` protects primary-worktree integration and repair; a second primary integration acquisition is a machine failure.

### Tech-debt gate

Check file size, responsibilities, readability, names, duplication, error states, edge cases, contracts, tests, dependencies, dead code, configuration, and repository conventions. Treat 500 lines as a design warning; record justified generated/static/framework exceptions. Prefer a split plan when adding logic to a file over 450 lines.

### Process-debt gate

Check plan alignment, scope drift, acceptance criteria, recorded validation, assumptions, risks, docs, deferred work, and next-slice handoff. Do not hide unresolved items.

## 3. Finalization loop

After all slices are integrated:

1. Run a completion check across acceptance criteria, tests, hidden TODOs, records, and system wiring.
2. Create a clean local checkpoint commit. Never run native Codex review against uncommitted changes.
3. Concurrently run `codex review --commit <checkpoint-sha>`, one unified system review, and only triggered specialist reviews against that exact checkpoint. Record their results sequentially through the state helper after all calls finish.
4. Aggregate valid findings into one repair set. Acquire `acquire-finalizer`, route it to the relevant `se-implementer`, then release the lock before re-reviewing.
5. After repairs, reuse passing evidence when the content hash is unchanged. When content changes, rerun affected validation, the unified system review, and only the specialist reviews whose scopes the repair touched. The checkpoint-bound Codex review remains attached to the checkpoint.
6. Run the relevant commands through `record-final-validation`, binding passing machine evidence to the reviewed content.
7. When review or wiring fixes changed files, create a second local commit and record it as final. Otherwise record the checkpoint SHA as the final SHA.

The wiring gate checks exports, imports, routes, handlers, UI entry points, jobs, configuration, migrations, build/test scripts, docs, and orphaned components as applicable.

### Outcomes

- `passed`: all required gates passed and local commits are recorded.
- `blocked`: a required action cannot continue safely or a repair budget is exhausted.
- `degraded`: work is otherwise complete but a named review/validation surface was unavailable; never report full completion without disclosing it.

## Non-negotiable policy

- Never push, merge, or open a pull request.
- Never release a slice before its dependencies are integrated.
- Never let more than one writer mutate the same working tree.
- Never let an implementer exceed its assigned slice or working tree.
- Never claim a command, test, review, or commit happened without captured evidence.
- Never initialize a run when the bundled execution policy fails its negative probes; load it only in isolated worker homes. Check every recorded external command against the policy, but do not rerun the full probe suite for state-only transitions.
- Never create package/domain/application/infrastructure/UI folders merely to match a template; use the repository's current structure and split only when responsibilities require it.

### State command sequence

```bash
# Health, easy start, and resume
python3 <helper>
python3 <helper> init
python3 <helper> resume-status --run-dir <run-dir>

# One writer only
python3 <helper> acquire-writer --run-dir <run-dir> --slice S1 --owner <thread-id>
python3 <helper> release-writer --run-dir <run-dir> --owner <thread-id>

# Locked post-checkpoint repairs, followed by validation of the final reviewed content
python3 <helper> acquire-finalizer --run-dir <run-dir> --owner <thread-id>
python3 <helper> release-writer --run-dir <run-dir> --owner <thread-id>
python3 <helper> record-final-validation --run-dir <run-dir> --attempt 1 -- <test-command>

# Close each slice immediately after integration
python3 <helper> set-slice-status --run-dir <run-dir> --slice S1 --status complete
```
