---
description: Run the six-skill Rust design, implementation, testing, and review workflow.
agent: build
---

Load and follow the `rust-workflow` skill for the request below.

If no arguments are provided, review the Rust changes on the current Git branch.
Determine its intended base branch from repository context and review changes
since their merge base, including uncommitted changes. Keep the review read-only.
If the base is ambiguous, ask which branch to compare against. If there are no
Rust changes, report that rather than asking for a task.

When arguments are provided, use them as the request instead of this default.

$ARGUMENTS
