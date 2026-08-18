# Software Engineering Workflows

This plugin provides one full recordless workflow and its four independently invokable prompt chains.

- `$software-engineering-full`: decides what discovery is useful, diagnoses reported bugs against a runnable failure signal, implements complex or high-risk work in reviewable vertical slices, separately reviews standards and spec conformance at each audit gate, validates the integrated result, retrospectively critiques it, and publishes or updates one pull request.
- `$software-engineering-scout-plan`: scouts, plans, or does both when the task has real uncertainty, using relevant `.understand-anything` graph context for wider-system discovery when available.
- `$software-engineering-implement-integrate`: diagnoses reported bugs when needed, then implements, validates, and integrates a complete change.
- `$software-engineering-audit-fix`: separately checks standards and spec conformance, then audits bugs, security, technical debt, and process debt before fixing and validating confirmed findings.
- `$software-engineering-retrospective`: explains each task commit, its rationale and tradeoffs, then gives an honest verdict and a better approach where warranted.

The full workflow chains the four subprocess skills. They are guidance prompts, not a controller or state machine, so the orchestrator adapts them to the task. Contained, low-risk changes stay in one pass; complex or high-risk changes use relevant knowledge-graph context when available, reviewed slice checkpoint commits, and repeated review/fix gates before integration. The plugin creates no workflow records, reuses one canonical branch and pull request across threads, and never merges without an explicit request.

## Install

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

Merging remains a separate explicit action.
