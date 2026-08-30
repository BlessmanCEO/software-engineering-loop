# Software Engineering Workflows

This Codex plugin and Pi package provide one full recordless workflow and its four independently invocable prompt chains.

- `$software-engineering-full`: chooses low, medium, or high-risk review gates, implements coherent vertical slices, validates and independently reviews only the required diffs, retrospectively critiques substantial work, and publishes or updates one pull request.
- `$software-engineering-scout-plan`: scouts, plans, or does both when the task has real uncertainty, using relevant `.understand-anything` graph context for wider-system discovery when available.
- `$software-engineering-implement-integrate`: implements, validates, and integrates a complete change.
- `$software-engineering-audit-fix`: checks bugs, security, technical debt, and process debt, then fixes and validates confirmed findings.
- `$software-engineering-retrospective`: explains each task commit, its rationale and tradeoffs, then gives an honest verdict and a better approach where warranted.

The full workflow chains only the subprocess skills justified by the task. Low-risk work gets one final independent review, medium-risk work gets slice audits and one cumulative review, and high-risk work adds independent slice reviews. Every reviewer receives the objective, acceptance criteria, constraints, risk, and observed validation results; unchanged diffs are never reviewed twice. The plugin creates no workflow records, reuses one canonical branch and pull request across threads, and never merges without an explicit request.

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

## Evaluation

[`EVALUATION.md`](EVALUATION.md) defines a five-case paired corpus and scorecard for comparing the full workflow with the implementation-only control.

Merging remains a separate explicit action.
