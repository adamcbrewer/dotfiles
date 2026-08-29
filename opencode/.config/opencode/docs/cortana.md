# Cortana Agent System

Cortana is an explicit-only OpenCode workflow for implementation work. Select the `cortana` primary agent or run `/cortana <task>`.

## Source Of Truth

The executable policy lives in [`agents/cortana.md`](../agents/cortana.md). Its frontmatter defines permissions and its body defines routing, approvals, verification, evidence reuse, correction loops, Git ownership, and completion rules.

Role-specific behavior and permissions live in:

- [`agents/cortana-scout.md`](../agents/cortana-scout.md)
- [`agents/cortana-implementer.md`](../agents/cortana-implementer.md)
- [`agents/cortana-verifier.md`](../agents/cortana-verifier.md)
- [`agents/cortana-reviewer.md`](../agents/cortana-reviewer.md)

This document is an overview. Do not duplicate policy details here; update the relevant agent definition instead.

## Architecture

```text
                    +-> Scout when uncertainty warrants
                    |
Cortana -> classify +-> Implementer -> tiered Verifier? -> Reviewer? -> Finalize
          risk      |       ^               |                |
                    +-------+---------------+----------------+
                         corrections and human checkpoints
```

Cortana owns routing, approvals, handoff state, loop limits, and finalization. Secondary agents run sequentially so evidence and ownership transfer explicitly. Safe tool calls within one agent may run in parallel.

## Routes

```text
research          -> Scout
state/admin       -> Implementer -> direct confirmation
docs/metadata     -> Implementer -> Tier 0 Verifier when useful
behavior config  -> Implementer -> Tier 1 Verifier
narrow code       -> Implementer -> Tier 1 Verifier
normal code       -> Scout when needed -> Implementer -> Tier 2 Verifier
high-risk/release -> Scout -> Baseline -> Implementer -> Tier 3 Verifier
```

Reviewer is reserved for material risk such as security, permissions, money, data loss, migrations, public contracts, broad architectural changes, or low confidence.

## Persistent Artifacts

Non-trivial runs use `.opencode/runs/<ticket-or-slug>.md` for handoff state. Completed delegated runs produce one `.opencode/runs/<ticket-or-slug>-agent-flow.svg` during finalization. Both are project-local runtime artifacts and should normally be ignored by Git.

## Operating Principles

- Preserve user and unrelated changes; staged work is user-owned unless explicitly assigned.
- Use the smallest route and verification tier justified by risk.
- Reuse passing evidence while relevant repository state and inputs remain unchanged.
- Route corrections back through Implementer and only rerun invalidated checks.
- Require approval for external effects, destructive actions, worktrees, push, and PR creation as defined by the primary agent policy.
- Never integrate work automatically.

For exact branch rules, worktree protocol, check budgets, approval labels, loop limits, report fields, and SVG requirements, read [`agents/cortana.md`](../agents/cortana.md).
