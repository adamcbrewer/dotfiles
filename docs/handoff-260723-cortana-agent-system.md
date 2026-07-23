# Handoff: Cortana OpenCode Agent System

## Context

User wants to build a global reusable OpenCode agent system called Cortana in this dotfiles repo. It should live under the stowed OpenCode config at `opencode/.config/opencode/` and be usable across projects. Project-specific overrides should remain project-local.

Source conversation reviewed: <https://chatgpt.com/share/6a61c75a-57bc-83eb-a0ec-01e5f6034d6b>

Current repo observations:

- Global OpenCode config exists at `opencode/.config/opencode/opencode.json`.
- Global OpenCode rules exist at `opencode/.config/opencode/AGENTS.md`.
- Global skills already exist under `opencode/.config/opencode/skills/`.
- No Cortana agents or commands have been created yet.

## Skills To Use Next

- `customize-opencode`: required when implementing OpenCode agents, commands, config, permissions, or skills.
- `simplify`: useful after drafting agent prompts to reduce bloat.
- `verify`: useful before committing/pushing if requested.

## Target Files To Create

```text
opencode/.config/opencode/
  agents/
    cortana.md
    cortana-scout.md
    cortana-implementer.md
    cortana-verifier.md
    cortana-reviewer.md
  commands/
    cortana.md
  docs/
    cortana.md
```

Do not make Cortana the default agent. It should be explicit-only via `/cortana` or TUI primary-agent selection.

## Agent Names And Visibility

Use namespaced agents:

```text
cortana
cortana-scout
cortana-implementer
cortana-verifier
cortana-reviewer
```

Visibility policy:

- `cortana`: primary, visible/selectable.
- `cortana-scout`: subagent, hidden.
- `cortana-implementer`: subagent, hidden.
- `cortana-verifier`: subagent, visible via `@mention`.
- `cortana-reviewer`: subagent, visible via `@mention`.

Manual `@cortana-verifier` and `@cortana-reviewer` must be report-only standalone modes: no edits, no loops, no handoff to Implementer. They should suggest `/cortana` if governed remediation is needed.

## Slash Command

Create `/cortana` as natural-language only. No formal flags initially.

Behavior:

```text
/cortana <task>
```

- Forces/uses the `cortana` agent.
- Starts the governed workflow.
- Natural language can express intent like “quickly”, “be careful”, “do not push”, or “prepare for PR”.

## Core Architecture

Cortana is the orchestrator/governor. It controls routing, loops, approvals, handoff state, finalization, and human checkpoints.

Subagents are sequential secondary agents, not a parallel worker pool:

```text
Cortana
  |
  v
Scout
  |
  v
Baseline Verifier
  |
  v
Implementer
  |
  v
Verifier
  |
  v
Reviewer
  |
  +-- blocking findings -> Implementer -> Verifier -> Reviewer
  |
  v
Finalize
```

Secondary agent pipeline must be sequential for reliability. Tool calls inside each agent may be parallelized where safe.

Only Cortana may invoke secondary agents or specialized workflow skills. Subagents may use basic tools for their own work but must request escalation through Cortana.

## Existing Skill Usage

Cortana may intentionally use existing global skills, governed by Cortana only.

Likely routing:

- `verify`: verification strategy/checks.
- `test-analyzer`: failing tests.
- `code-review`: reviewer behavior.
- `simplify`: cleanup after implementation if useful.
- `frontend-design`, `react-best-practices`, `web-interface`: relevant frontend/UI work.

Subagents should not independently trigger workflow skills unless Cortana directs them.

## Workflow Defaults

Default is full workflow.

Shortcuts:

- Cortana may suggest shortcuts only before implementation starts.
- Shortcut prompts must name exact skipped steps.
- User must approve shortcuts.
- Post-change verification is never silently skipped.
- After implementation starts, Cortana may only add checks, not remove them.

Example shortcut prompt:

```text
Optional:
Fast path available: skip Scout deep-dive + Reviewer, still run Verifier. Proceed?
```

## Baseline Verification

Baseline verification is default and uses `cortana-verifier`.

Purpose: fingerprint current repo health before edits to separate pre-existing failures from agent-introduced regressions.

Policy:

- Discover verification commands before implementation.
- Run cheapest authoritative checks first.
- Scope checks for large/expensive projects.
- Record pass/fail in handoff if a handoff exists.
- If baseline fails and failure is clearly unrelated, continue and record it as pre-existing.
- If baseline fails and is related or unclear, block implementation and ask the user.
- If baseline failure matches a user request like “fix failing checkout tests”, continue.

Verifier command discovery order:

```text
1. Project AGENTS.md
2. README / CONTRIBUTING / docs
3. package scripts / task runner / CI config
4. ecosystem defaults
5. ask human if unclear
```

## Verification Policy

Verifier checks whole project state with diff-aware focus.

Verifier may run write-producing commands only when they exist within project tooling and are mechanical:

- project formatter
- project lint fix
- snapshot updates when expected
- project codegen
- lockfile refresh caused by project tooling

Verifier must not manually edit source, change business logic, rewrite tests to pass, or commit.

Verifier-created changes must be handed to Implementer for inspection and commit.

Verifier may install declared project deps or fetch/download deps needed by existing project tooling. It must ask before package additions/upgrades, global tools, or system packages.

Final verification is mandatory. It should run the strongest relevant subset by default and all checks when reasonable. Final summary must list what ran, what did not run, and why.

Verifier must distinguish:

- `failed`: command ran and found a real issue.
- `incomplete`: command could not run, timed out, required missing service, or was skipped due to cost/scope.

Residual risk requires explicit human acceptance before completion.

## Local Services Policy

Verifier may use project-documented local services:

- local dev server
- Docker Compose
- local database
- browser tests against localhost
- project-owned services started by repo scripts

Ask first for:

- cloud/staging/prod APIs
- deployed preview URLs
- GitHub Actions reruns
- paid/external services
- anything using secrets

If Verifier starts local services, it must record them and clean up only services it started. It must not stop services it did not start.

## Reviewer Policy

Reviewer checks whole project state with diff-aware focus.

Reviewer runs after all planned implementation work passes verification. It reviews the final accumulated diff/commit batch, not every tiny checkpoint.

Reviewer findings must be split:

- Blocking
- Non-blocking

Blocking findings must be fixed or explicitly accepted by the user. Reviewer-driven changes route back to Implementer, then Verifier reruns, then Reviewer re-checks if needed.

Reviewer blocks only in-scope substantive issues:

- introduced by this change
- made worse by this change
- prevents task/request/ACs from being satisfied
- serious immediate risk in touched path

Out-of-scope findings become non-blocking follow-ups unless introduced or made worse by the task.

Non-blocking findings are listed in final summary only. Do not create issues by default.

## Acceptance Criteria

Acceptance criteria are a hard contract when provided.

Policy:

- Do not invent ACs.
- If ACs are provided, record and verify exactly.
- If ACs are missing, proceed from the user’s instruction and objective success signals where enough.
- If success is ambiguous, raise a Blocking clarification.
- Distinguish ACs from agent-derived success signals.

Example handoff wording:

```md
## Acceptance Criteria

User-provided: none

## Success Signals

- Requested behavior implemented
- Relevant checks pass
- No obvious regression in touched area
```

## Scout And Planning

Scout is default in the full workflow but can be skipped for tiny/obvious tasks only with Optional approval.

Scout approval is required only in:

- careful mode
- low-confidence cases
- risky/destructive/broad changes
- meaningful architecture tradeoffs
- unclear/conflicting instructions

Otherwise Scout hands off directly to Implementer.

For larger tasks, Scout may identify natural slices. Slicing approval follows the same careful/low-confidence rules.

## Task Slicing

Cortana supports task slicing when natural.

Good slicing examples:

- backend endpoint
- UI integration
- tests/docs

Bad slicing: splitting one tiny bug fix into artificial commits.

Implementer may refine slices during implementation. Verifier checks each slice enough to keep repo stable. Final Verifier runs relevant/full checks before Reviewer.

## Loop Limits And Human Checkpoints

Loop limits:

- Max 5 loops per correction route.
- Track loop counts by route, e.g. `Verifier -> Implementer`, `Reviewer -> Implementer`.
- Final summary must report loop counts.

Cortana must pause before the limit if the same failure repeats twice with no meaningful progress.

At max loop count, Cortana must stop, produce a mini-postmortem, and ask the user.

Mini-postmortem should include:

- route
- loops used
- what got stuck
- attempts made
- likely cause
- recommended options

Confidence-drop triggers also require human checkpoint:

- unclear ACs
- risky files/domains touched
- repeated same failure
- missing verifier commands
- broken environment
- real implementation tradeoffs
- agent cannot explain why fix is correct

Human prompts should be labelled:

- Blocking
- Optional

PR creation is Blocking. Push is Optional. Residual risk acceptance is Blocking.

## Git And Worktree Policy

Startup worktree check is mandatory before implementation:

- `git status`
- staged diff
- unstaged diff
- `git log --oneline -10`

Dirty changes policy:

- Clean tree: proceed.
- Dirty related changes: proceed carefully and preserve user work.
- Dirty unrelated or unclear changes: Blocking prompt.
- If in doubt, recommend new branch from default branch.

Branch policy:

- Work on current branch if it looks intentional and suitable.
- If on `main`, `master`, or `trunk`, ask before implementation and recommend creating a branch.
- If current branch is unsuitable or unclear, ask and recommend new branch from default.
- Branch naming follows existing convention: `feat/`, `fix/`, `chore/`, include ticket if known.

Staging policy:

- Staged changes are user-owned by default.
- Never commit user-staged changes without explicit approval.
- Never unstage user-staged changes without explicit approval.
- Hunk staging is allowed.
- Interactive git staging is banned by default.
- Use whole-file staging for clearly Cortana-owned files.
- Use non-interactive patch-based hunk staging for mixed files.
- Inspect staged diff before every commit.

Same-file overlap policy:

- Same file, separate clear hunks: allowed.
- Overlapping hunks, unclear ownership, or user-staged changes near Cortana edits: Blocking prompt.

Commit policy:

- Many small local commits are encouraged.
- Implementer must commit before handoff to Verifier or Reviewer.
- Commit after coherent slices/checkpoints.
- WIP/checkpoint commits are allowed if clearly labelled when blocked.
- Do not squash, rebase, amend, reset, force-push, or rewrite history without explicit Blocking approval.
- Local commit history may be noisy; PR merge can squash later.

Push/PR policy:

- Push is Optional human prompt by default.
- PR creation is Blocking human prompt always unless explicitly pre-approved.
- PRs are team-visible and should not be created silently.

## Run Handoff Files

Run handoff files are project-local only:

```text
.opencode/runs/<ticket-or-slug>.md
```

Create only for non-trivial runs. Include ticket/issue ID in filename when provided.

When first creating `.opencode/runs/*.md`:

- If `.gitignore` exists and lacks `.opencode/runs/`, add it automatically.
- If no `.gitignore` exists, ask Optional before creating one.

Handoff files should be lean and execution-focused. They are not logs.

Suggested sections:

```md
# Run Handoff

## Task

## Workflow State

## Loop Counts

## Worktree Ownership

## Scout

## Baseline Verification

## Implementation

## Verification

## Review

## Finalization
```

`Worktree Ownership` is conditional and should appear only when dirty/staged/pre-existing changes exist.

Section ownership:

- Cortana owns structure, workflow state, shortcut decisions, loop counts, final outcome.
- Scout owns findings, risks, AC notes, implementation guidance.
- Implementer owns changed files, implementation notes, blockers.
- Verifier owns baseline status, commands, results, unresolved failures.
- Reviewer owns findings, required changes, residual risks.

Cortana may compress/clean sections during finalization. Subagents must not rewrite another subagent’s section.

Harness improvement suggestions must not go in handoff files. They belong only in the final user summary.

## Project Onboarding

First non-trivial Cortana run in a repo includes lightweight onboarding:

- project type/package manager
- declared verification commands
- CI config
- AGENTS.md/project rules
- `.opencode/runs/` gitignore status
- ticket/branch naming conventions
- obvious local service requirements

Do not create a permanent project profile by default. Rediscover by default. At finalization, offer promotion to `AGENTS.md`, `docs/`, or `docs/adr/` only when genuinely useful.

Promotion targets:

- `AGENTS.md`: repeatable agent/project rule, verification command, known gotcha.
- `docs/`: human-facing workflow/domain/onboarding knowledge.
- `docs/adr/`: durable architecture decision/tradeoff.

Do not promote ordinary feature summaries, bug fix details with no reusable lesson, noisy transcripts, or one-off failures.

## Definition Of Done

Cortana cannot finalize until this checklist is satisfied or explicitly documented:

- implementation committed locally
- Verifier passed, or residual failures documented and user-accepted
- Reviewer blocking findings resolved or user-accepted
- non-blocking findings listed
- loop counts recorded
- final summary prepared
- optional push offered unless user said not to
- PR creation asked as Blocking if relevant
- valuable knowledge promotion offered only when genuinely reusable

## Permission Intent

Exact OpenCode permission frontmatter still needs implementation/validation.

Intent:

- `cortana`: no general code edits; may create/update `.opencode/runs/*.md`; may read/search/run safe checks; may invoke only Cortana subagents and approved skills.
- `cortana-scout`: no edits; research/planning only.
- `cortana-implementer`: edits project files; commits; normal dev/test/git-local commands allowed; risky commands ask; destructive commands require explicit approval.
- `cortana-verifier`: checks/reporting; may run project-defined mechanical write-producing tooling; no manual edits or commits.
- `cortana-reviewer`: read/review/report; no edits.

Global harness edits require Blocking approval:

- global Cortana agents
- global OpenCode config
- global skills
- shared workflow policy
- dotfiles-managed OpenCode files

Project-local config edits are normal project edits because they are visible and reversible via commits.

## Suggested Next Steps

1. Load `customize-opencode` skill.
2. Fetch/verify OpenCode config schema if permission shapes are uncertain.
3. Create the agent, command, and design doc files listed above.
4. Keep prompts concise; avoid over-documenting inside operational agent prompts.
5. Use the design doc for full policy detail and agent prompts for role-specific behavior.
6. Validate frontmatter fields against OpenCode docs/schema.
7. Inspect resulting file tree.
8. Tell user to restart OpenCode because agents/config are loaded at startup.

## Open Questions For Implementation

- Exact frontmatter permission patterns for restricting Cortana edits only to `.opencode/runs/*.md` may require schema/docs validation.
- The `/cortana` command frontmatter should force the `cortana` agent; confirm command field shape before writing.
- Decide whether to include model overrides per agent or let subagents inherit the primary/global model. Current preference appears to be no special model overrides initially.
