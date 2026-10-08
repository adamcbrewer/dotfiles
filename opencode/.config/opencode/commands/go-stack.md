---
description: Pick and order the right Go skills, then report what was used.
agent: build
---

Load `go-stack` for the request below. Follow its skill-selection and handoff rules,
then finish with the actual-skills-used report.

If no arguments are provided, review the Go changes on the current Git branch.
Determine its intended base branch from repository context and review changes
since their merge base, including uncommitted changes. Keep the review read-only.
If the base is ambiguous, ask which branch to compare against. If there are no
Go changes, report that rather than asking for a task.

When arguments are provided, use them as the request instead of this default.

$ARGUMENTS
