# Software Engineering Workflows

This Codex plugin and Pi package provide one full recordless workflow, its four independently invocable prompt chains, and a persistent PR babysitter.

- `$software-engineering-full`: chooses low, medium, or high-risk review gates, implements coherent vertical slices, validates and independently reviews only the required diffs, retrospectively critiques substantial work, and publishes or updates one pull request.
- `$software-engineering-scout-plan`: scouts, plans, or does both when the task has real uncertainty, using relevant `.understand-anything` graph context for wider-system discovery when available.
- `$software-engineering-implement-integrate`: implements, validates, and integrates a complete change.
- `$software-engineering-audit-fix`: checks bugs, security, technical debt, and process debt, then fixes and validates confirmed findings.
- `$software-engineering-retrospective`: explains each task commit, its rationale and tradeoffs, then gives an honest verdict and a better approach where warranted.
- `$pr-babysit`: monitors an existing PR's reviews and CI, verifies feedback, fixes genuine in-scope defects, and publishes only when authorized; never merges.

The full workflow chains only the subprocess skills justified by the task. Low-risk work gets one final independent review, medium-risk work gets slice audits and one cumulative review, and high-risk work adds independent slice reviews. Every reviewer receives the objective, acceptance criteria, constraints, risk, and observed validation results; unchanged diffs are never reviewed twice. The full workflow creates no workflow records, reuses one canonical branch and pull request across threads, and never merges without an explicit request.

## Install in Codex

```bash
codex plugin marketplace add BlessmanCEO/software-engineering-loop
codex plugin add software-engineering-loop@software-engineering-loop
```

Start a new Codex thread and invoke one skill:

```text
Use $software-engineering-full for this coding task.
Use $software-engineering-scout-plan to investigate and plan this task.
Use $software-engineering-implement-integrate to build this task.
Use $software-engineering-audit-fix to audit and repair this change.
Use $software-engineering-retrospective to explain and critique a completed task.
```

## Install in Pi

```bash
pi install git:github.com/BlessmanCEO/software-engineering-loop
```

Start or restart Pi, then invoke one skill:

```text
/skill:software-engineering-full Implement and review this coding task.
/skill:software-engineering-scout-plan Investigate and plan this task.
/skill:software-engineering-implement-integrate Build this coding task.
/skill:software-engineering-audit-fix Audit and repair this change.
/skill:software-engineering-retrospective Explain and critique this completed task.
```

## Babysit an existing PR

The [PR babysitter](skills/pr-babysit/SKILL.md) is also available at
`.agents/skills/pr-babysit/SKILL.md` through a symlink to the packaged skill.
It keeps resumable local state outside the source tree, not committed workflow records.
It requires git, authenticated GitHub CLI (`gh`), network access, and the repo's test toolchain.

In Codex:

```text
$pr-babysit Babysit PR #123 in OWNER/REPO.

You may edit code, run tests, commit, push to the existing PR branch,
reply to review comments, and retrigger the configured bot reviews and CI.

Fix genuine in-scope defects only. Do not implement unrelated improvements
or later-phase architecture. Continue until the current head has a clean
configured review and successful required checks, or an explicit terminal
condition applies. Stop for stalled progress or a required human decision.

Do not merge. Return a summary when the PR is ready or needs my attention.
```

In Pi, use `/skill:pr-babysit` instead of `$pr-babysit`, followed by the same
instructions. Without publishing permission, it prepares verified local fixes
for handoff. Monitoring lasts only while the agent is actually running.

## Evaluation

[`EVALUATION.md`](EVALUATION.md) defines a five-case paired corpus and scorecard for comparing the full workflow with the implementation-only control.

Merging remains a separate explicit action.
