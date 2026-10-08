---
description: Verify a change with scoped checks, progress updates and a completion receipt.
agent: build
---

Load and follow the `verify-change` skill for the request below.

Use arguments as the verification target and mode. With no arguments, verify the
current task's changes; otherwise inspect uncommitted changes or the current branch
against its known base. Keep a verification-only request read-only. If no change
can be identified, report that; ask when the target or base is genuinely ambiguous.

$ARGUMENTS
