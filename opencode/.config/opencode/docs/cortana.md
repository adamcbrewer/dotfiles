# Cortana Agent System

Cortana is an explicit-only OpenCode workflow for implementation work. Select the `cortana` primary agent or run `/cortana <task>`.

## Source Of Truth

Coordination policy lives in [`agents/cortana.md`](../agents/cortana.md): routing, approvals, handoffs, correction limits, and completion.

Role-specific behavior and permissions live in:

- [`agents/cortana-scout.md`](../agents/cortana-scout.md)
- [`agents/cortana-implementer.md`](../agents/cortana-implementer.md)
- [`agents/cortana-verifier.md`](../agents/cortana-verifier.md)
- [`agents/cortana-reviewer.md`](../agents/cortana-reviewer.md)

This document is an overview. Do not duplicate policy details here; update the relevant agent definition instead.

## How It Works

Cortana chooses the smallest useful sequence of agents. Scout resolves uncertainty, Implementer owns changes, Verifier independently checks behavior, and Reviewer investigates material risks. Agents run sequentially; safe tool calls within an agent may run in parallel.

Verifier owns check selection and evidence-reuse details. It uses check-only modes and returns fixes to Implementer. Required domain skills can be loaded without starting nested agent workflows; skills outside explicit allowlists require approval.

Cortana assesses the evidence after each handoff and records a brief retrospective at completion: what the result proves, remaining uncertainty, avoidable work, and any useful adjustment for next time. The final response focuses on the outcome, verification limits, and next decision.

## Persistent Artifacts

Non-trivial runs keep decisions, evidence, and the retrospective in `.opencode/runs/<ticket-or-slug>.md`. An agent-flow SVG is optional and created only when requested. These are project-local runtime artifacts, not implementation changes to commit by default.

Research requires no branch setup. Editing follows the branch policy in the primary agent. Commits, pushes, and PRs follow explicit user intent rather than being automatic completion steps.
