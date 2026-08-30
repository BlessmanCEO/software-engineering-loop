# Workflow Evaluation

This small corpus checks whether `software-engineering-full` improves delivered quality over `software-engineering-implement-integrate` without buying that quality through redundant review.

## Paired protocol

For each case:

1. Export the base commit into two fresh repositories and initialize new Git histories so the agent cannot inspect later oracle commits.
2. Copy and load only the candidate skill directories from the checkout under evaluation. Disable fixture-local skill discovery, and do not expose this file or the source repository's Git history to the task agent.
3. Run the control with `software-engineering-implement-integrate` and the treatment with `software-engineering-full`, using the same model, reasoning level, task prompt, and starting snapshot.
4. Tell both arms to work locally and stop before push or pull-request creation.
5. Keep the target commit hidden until scoring. It is a reference solution, not an exact-diff requirement.
6. Have one independent adjudicator inspect both final diffs against the task and acceptance checks.

Run each pair once initially. Repeat only a case whose outcome is close enough to change the decision.

## Scorecard

Record:

| Case | Arm | Acceptance misses | Escaped blockers | Independent reviews | Accepted / rejected findings | Repair rounds | Task commits | Wall time / tokens |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
|  | Control |  |  |  |  |  |  |  |
|  | Full |  |  |  |  |  |  |  |

A rejected finding is a reviewer finding the adjudicator confirms was false, out of scope, or merely a preference. Compare acceptance misses and escaped blockers first; when quality ties, fewer reviews, repairs, commits, and tokens wins.

## Corpus

### L1 — Recursive reviewer guard

- **Profile:** Low
- **Base:** `7ae9551dc4bbcd4b23080816081e4aff9f1f406a`
- **Reference:** `db155fdca09ed34257827d91595a7dc87d5b9af1`
- **Task:** Prevent a process launched as an independent reviewer by the full workflow from recursively launching another reviewer. Make the smallest complete change.
- **Acceptance:** The full skill explicitly returns findings to its caller when already acting as the independent reviewer, with no unrelated workflow changes.
- **Expected treatment budget:** One final independent review.

### M1 — Pi chaining and read-only review isolation

- **Profile:** Medium
- **Base:** `d6955664e23bc1dbb4c7db6803394e4cb7adcf74`
- **Reference:** `7ae9551dc4bbcd4b23080816081e4aff9f1f406a`
- **Task:** Fix Pi support in the full workflow. Chained skills must be loaded in a way that works from inside another Pi skill, and independent Pi reviews must receive the exact commit or branch diff in a fresh process with only read-only tools. Preserve the Codex path.
- **Acceptance:** Pi reads sibling skill files instead of emitting an unexpanded slash command; commit and base reviews receive their intended diffs; Pi review subprocesses have no session, extensions, skills, or mutation tools; Codex review remains supported.
- **Expected treatment budget:** One cumulative independent review.

### H1 — Working-tree hashes and legacy workflow state

- **Profile:** High
- **Base:** `006a5ffab06aa0a0aff3c0467fcd6d194a7c598f`
- **Reference:** `05997dc3c164bd30f8377b0476f22ab61a9cc495`
- **Task:** Fix the duplicated workflow implementations so their working-tree content hash is unchanged by staging and does not fail on a staged rename or deletion. Preserve old runs when legacy review gates are loaded after the unified-review migration. Add focused regression tests.
- **Acceptance:** Both hash helpers handle tracked, untracked, renamed, and missing paths consistently; staging alone does not alter the hash; legacy review evidence is retained; the unified gate passes only when all required legacy gates passed against one content hash; new optional specialist gates default safely; regression tests exercise the failures.
- **Expected treatment budget:** At most one review per coherent slice plus one cumulative review; skip an identical final diff.

### H2 — Cross-platform review command hardening

- **Profile:** High
- **Base:** `db155fdca09ed34257827d91595a7dc87d5b9af1`
- **Reference:** `7800876eed121f7021a9d503ff8286279191dfc5`
- **Task:** Harden the full workflow's independent review commands for untrusted or invalid revision input and cross-platform execution. Preserve exact diffs, UTF-8 output, read-only Pi isolation, and both POSIX and PowerShell support.
- **Acceptance:** Revision candidates are verified before use and replaced with full commit IDs; Git writes exact diffs directly to temporary files; argument boundaries are explicit; POSIX cleanup is reliable; PowerShell checks Git and Pi exit codes and removes temporary files; invalid refs cannot be presented as successful reviews.
- **Expected treatment budget:** One review if delivered as one coherent slice; never repeat the identical final diff.

### H3 — Remove stateful workflow machinery

- **Profile:** High
- **Base:** `05997dc3c164bd30f8377b0476f22ab61a9cc495`
- **Reference:** `50327f56e73672f8f97ad1fecf9b969af920f5d0`
- **Task:** Replace the duplicated stateful fast/full workflow implementations with one recordless full workflow and focused independently invocable prompt-chain skills. Delete scripts, records, agent profiles, and tests that exist only for the removed state machinery while preserving installation metadata and clear usage documentation.
- **Acceptance:** One full orchestrator composes focused scout/plan, implementation, audit/fix, and retrospective skills; obsolete state machinery and duplicate workflow variants are removed; surviving metadata and documentation point only to real skills; the repository contains no dangling references to deleted runtime assets.
- **Expected treatment budget:** At most one review per coherent slice plus one cumulative review; skip an identical final diff.
