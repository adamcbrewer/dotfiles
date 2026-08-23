# Cortana Agent System

Cortana is an explicit-only global OpenCode workflow for implementation work.
Use `/cortana <task>` or select the `cortana` primary agent. It is not the
default agent.

## Architecture

```text
                    +-> Scout when uncertainty warrants
                    |
Cortana -> classify +-> Implementer -> tiered Verifier? -> Reviewer? -> Finalize
          risk      |       ^               |                |
                    +-------+---------------+----------------+
                         corrections and human checkpoints
```

Cortana is the only governor. It owns routing, approvals, handoff state, loop
limits, and finalization. Secondary agents run sequentially for reliable state
transfer; safe tool calls inside one agent may run in parallel.

| Agent | Visibility | Responsibility |
| --- | --- | --- |
| `cortana` | Primary/selectable | Governance and handoff state |
| `cortana-scout` | Hidden subagent | Research and planning |
| `cortana-implementer` | Hidden subagent | Edits, focused checks, commits |
| `cortana-verifier` | Hidden subagent | Baseline/final verification; direct user mentions are report-only |
| `cortana-reviewer` | Hidden subagent | Final substantive review; direct user mentions are report-only |

All `cortana-*` agents are hidden and may only be delegated by the `cortana`
primary agent. You may invoke one directly by naming it; direct sessions are
standalone, report-only modes. They do not edit, delegate, or start remediation
loops.

## Workflow

Cortana scales the workflow to the task:

```text
research          -> Scout
state/admin       -> Implementer -> direct confirmation
docs/metadata     -> Implementer -> Tier 0 Verifier when useful
behavior config  -> Implementer -> Tier 1 Verifier
narrow code       -> Implementer -> Tier 1 Verifier
normal code       -> Scout when needed -> Implementer -> Tier 2 Verifier
high-risk/release -> Scout -> Baseline -> Implementer -> Tier 3 Verifier
```

Reviewer is added for security, authentication, permissions, money, data loss,
migrations, public contracts, shared architecture/dependencies, broad changes,
low confidence, explicit careful/release work, or substantive Verifier risk. It
is skipped for narrow low-risk code that passes focused verification.

All routes still begin with exact acceptance criteria, branch/status/diff
inspection, and ownership protection. Cortana selects the route and verification
tier before delegation, invokes agents sequentially, and finalizes only after
the route's definition of done is met.

Acceptance criteria are a hard contract when supplied. Cortana records them
verbatim and does not invent more. When none are supplied, agents use the
request plus clearly labelled success signals. Ambiguous success is Blocking.

Stage selection is risk-adaptive, not a user-approved shortcut. Cortana skips
unnecessary stages automatically and reports what was skipped and why. User
approval remains required for external effects, risky actions, real tradeoffs,
and unresolved ambiguity, not merely for using a smaller workflow.

## Verification

Baseline verification is need-based. Use it for known/possible flakiness, dirty
or ambiguous health, broad/risky changes, failure attribution, or explicit
careful work. Otherwise verify after implementation. A baseline uses the
cheapest relevant fingerprint rather than the final matrix. Command discovery
order:

1. Project `AGENTS.md`.
2. `README`, `CONTRIBUTING`, and project docs.
3. Package scripts, task runner, and CI configuration.
4. Ecosystem defaults.
5. Human clarification when still unclear.

Scout discovers these commands but does not execute them unless Cortana assigns
one diagnostic probe to resolve a named uncertainty. A related or unclear
baseline failure blocks edits; an unrelated pre-existing failure is recorded
and does not block. A failure the user asked to fix is expected and does not
block.

Verifier uses explicit tiers. Logical validations are counted rather than shell
calls; command chaining does not bypass a budget. Git state, diff, ownership,
and final-state inspection are required hygiene but not acceptance checks.

| Tier | Scope | Soft budget |
| --- | --- | ---: |
| 0 | State, metadata, docs | Direct confirmation; no suite |
| 1 | Narrow code, behavior config | Two logical checks |
| 2 | Subsystem | Four logical checks |
| 3 | Broad, risky, release | Planned comprehensive checks |

Every code or behavior-bearing configuration change receives at least one
independent acceptance-focused Verifier check. Extra Tier 1/2 checks require a
named distinct risk. Tier 3 has no numeric cap, but every check still covers a
distinct risk. Generic confidence does not justify speculative lint, typecheck,
build, or full-suite execution.

Passing evidence records repository state, check, result, scope, producer, and
invalidation conditions. It remains valid while relevant state and inputs are
unchanged. A broader suite subsumes its focused subset in the same phase unless
the focused run is an intentional fast-fail or diagnostic. Repetition requires
concrete flakiness evidence. Corrections rerun the failed check and checks
invalidated by changed paths. If the failed check is not independent and
acceptance-focused, they also run one that is. Wall-clock age alone does not
invalidate evidence.

Project-defined formatters, lint fixes, expected snapshot updates, codegen, and
lockfile refresh
may write mechanically. Any output returns to Implementer for inspection and
commit. Verifier never manually edits, changes logic, weakens tests, or commits.

Results use three states:

- `passed`: the check completed successfully.
- `failed`: the check ran and found a real issue.
- `incomplete`: it could not run, timed out, needed a missing service, or was
  omitted for scope/cost.

Required route verification is mandatory. The final report lists the tier,
checks run and omitted, retained evidence, budget exceptions, skipped stages,
and reasons. Residual risk requires Blocking human acceptance.

Dev servers/processes and any package install require approval; do not open UI,
and use scripts for verification when possible. The agent records what it starts
and stops only those services. Cloud, staging, production, deployed previews,
GitHub Actions reruns, paid/external services, and anything using secrets need
approval.

Any env file setup/template/placeholder creation requires approval. Agents do
not read, copy, or parse real `.env` files. Secrets, cloud, and production
services require approval.

## Worktrees

Worktrees are allowed only when the user explicitly asks, or when Cortana
suggests one and receives Blocking approval first. They are not allowed for
visual checks, local test confirmation, or agent convenience.

Strict rules:

- Worktrees are AFK lanes. Main checkout remains untouched.
- User PR review is required; agents do not self-review/integrate worktree work.
- Default maximum is one worktree. Cortana asks before increasing it.
- Directory format: sibling `../<original-dir>-<slug-or-issue>/`.
- Branching: create from the default branch on a new task branch.
- Feedback, handoffs, and subagent reports include the worktree banner below.
- After verification Cortana asks whether to push/create a PR. No automatic
  integration.
- Cortana always asks before cleanup and verifies cleanup after removal.
- If a task does not fit the protocol, Cortana stops and asks.

```text
WORKTREE LANE ACTIVE
path: <absolute worktree path>
branch: <task branch>
base: <default branch>
main checkout: untouched at <absolute original path>
integration: no push/PR/merge without approval; user PR review required
```

## Review

When routed, Reviewer runs after all planned work passes verification and
reviews the final accumulated diff, not each small checkpoint. On every
invocation it loads only
the `code-review` skill, then runs two sequential passes: the standard
skill-backed review followed by an independent adversarial review. Supplied
scope, base, and acceptance criteria override skill fallbacks. When no base is
supplied, Reviewer discovers the repository default branch and uses it instead
of the skill's `main` fallback. Reviewer overrides all skill skip conditions;
both passes run for every invocation, including closed PRs, trivial changes, and
manual contexts.

Reviewer trusts fresh Verifier evidence against unchanged relevant state. It
does not routinely run tests, lint, typecheck, build, format, or validation. A
command is allowed only to prove or disprove a concrete suspected defect after
the Reviewer states that hypothesis. Read-only Git and GitHub commands needed to
establish scope, base, and diff are exempt.

The adversarial pass challenges assumptions and seeks counterexamples, hidden
interactions, edge and failure cases, rollback and data-loss risks, security
risks, acceptance-criteria loopholes, and false confidence from tests. The
Reviewer records each pass's outcome, then deduplicates findings into:

- **Blocking:** substantive, in-scope, introduced/worsened by the change, an
  unmet request/acceptance criterion, or serious immediate risk in touched code.
- **Non-blocking:** useful follow-up, including unrelated pre-existing issues.

Blocking findings must be fixed or explicitly accepted. Fixes route through
Implementer and scoped Verifier, then Reviewer when the risk still warrants
re-review. Non-blocking findings appear in the final summary; issues are not
created automatically.

## Git And Ownership

Startup inspection is mandatory: status, staged diff, unstaged diff, recent
log, and current branch.

- Clean tree: proceed only after branch/worktree rules are satisfied.
- Related dirty work: preserve and proceed carefully.
- Unrelated or unclear dirty work: Blocking ownership question.
- Always work from a new branch off the default branch. Ask Blocking before
  creating it unless the user explicitly named/approved it. Cortana may run
  branch creation itself, such as `git switch -c <branch>`.
- Staged changes are user-owned by default. Never commit or unstage them without
  explicit approval.
- Separate same-file hunks are allowed. Overlap or unclear ownership blocks.
- Use whole-file staging for Cortana-owned files and non-interactive patch
  staging for mixed files. Inspect staged diff before every commit.
- Commit coherent slices before Verifier or Reviewer handoff.
- Never amend, squash, rebase, reset, force-push, or rewrite history without
  Blocking approval.

Push is Optional by default after verification. PR creation is Blocking unless
explicitly pre-approved because it creates team-visible state. No automatic
merge, integration, or cleanup.

Authenticated GitHub hosting operations use the `gh` CLI, including issues,
PRs, checks, runs, releases, and repository metadata. Repository transport uses
`git`. Agents do not call the GitHub API with `curl` or manually handle tokens.

## Run Handoffs

Non-trivial runs use project-local `.opencode/runs/<ticket-or-slug>.md`
regardless of ignore status. Cortana does not edit `.gitignore` or ask about it
for this purpose. Handoffs are lean state, not transcripts:

```md
# Run Handoff

## Task
## Acceptance Criteria
## Success Signals
## Workflow State
## Interaction Flow
## Loop Counts
## Worktree Ownership
## Scout
## Baseline Verification
## Implementation
## Verification
## Review
## Finalization
```

`Worktree Ownership` is conditional. Cortana owns the file structure, workflow
state, route/tier decisions, evidence, loop counts, and outcome. Subagents own
the content of their role reports, which they return to Cortana for recording.
Harness improvement ideas belong in the final summary, not the handoff.

`Interaction Flow` is a live ASCII sequence diagram. Cortana initializes it at
task start, adds a numbered outbound arrow marked `pending` immediately before
each subagent invocation, then completes that arrow and adds the numbered return
when the report arrives. It records actual interactions only; repeated arrows
preserve correction loops as they happen.

```text
Cortana +--[01 discover route]--> Scout
Cortana <--[02 route ready]------+ Scout
Cortana +--[03 implement slice]--> Implementer (pending)
```

Labels remain short and numbering never changes. This live diagram is the source
for the final interaction SVG, but no SVG is generated during the task.

## Agent Interaction Map

Each complete task flow that invoked subagents produces exactly one standalone
SVG at `.opencode/runs/<ticket-or-slug>-agent-flow.svg`. Cortana creates it only after
all subagents and correction loops have finished and the final report and
suggestions have been assembled. It is not generated after individual agent
invocations or at interim checkpoints.

The map is generated from the completed ASCII interaction flow rather than the
planned route. It places Cortana at the center, includes only participating
agents, preserves delegation/report numbering, and ends with Cortana's final
outcome and suggestions. Arrow labels summarize the purpose and outcome, so
correction loops remain visible without implying that subagents delegated
directly to each other.

The SVG uses a responsive `viewBox`, accessible contrast, a title, description,
and legend. It contains no scripts, foreign objects, external assets, or raw
project content. Cortana records its path in the handoff and both embeds and
links it in the final response, allowing the link to act as a fallback when the
client cannot render SVG inline.

## Loops And Checkpoints

Each correction route has a maximum of five loops. Track routes independently,
for example `Verifier -> Implementer` and `Reviewer -> Implementer`. Pause
before the limit if the same failure repeats twice without meaningful progress.
At the limit, stop and provide route, count, stuck point, attempts, likely
cause, and recommended options.

Each loop records which evidence the correction invalidated. Unaffected passing
evidence is retained.

Confidence drops also require a checkpoint: unclear criteria, risky domains,
missing verification commands, broken environment, real tradeoffs, or inability
to explain correctness. Human prompts are labelled `Blocking` or `Optional`.

## Project Onboarding

The first non-trivial run discovers project type/package manager, rules,
declared checks, CI, naming conventions, and local service needs. It does not
create a permanent profile. At finalization Cortana may offer to promote
genuinely reusable knowledge:

- `AGENTS.md`: repeatable agent rule, command, or gotcha.
- `docs/`: human-facing workflow/domain/onboarding knowledge.
- `docs/adr/`: durable architecture decision or tradeoff.

Ordinary feature summaries, one-off failures, and transcripts are not promoted.

## Definition Of Done

Cortana can finalize only when the selected route's requirements are met:

- tracked implementation is committed locally when files changed;
- required route confirmation/Verifier passed, or residual failures are
  documented and accepted;
- any required Reviewer blocking findings are resolved or accepted;
- non-blocking findings and loop counts are recorded;
- checks run and omitted are reported;
- when subagents were invoked, one final agent interaction SVG is generated
  after the report and suggestions are assembled;
- push is offered unless declined;
- PR creation is asked when relevant; and
- reusable knowledge promotion is offered only when valuable.

## Permissions

Permissions and role rules reinforce boundaries:

- Cortana edits only `.opencode/runs/*.md` and generated
  `.opencode/runs/*-agent-flow.svg` files, invokes only `cortana-*` agents, and
  loads only approved workflow skills. It can inspect Git/GitHub state, create
  approved branches, push and create PRs with approval, and manage approved
  worktree setup/removal.
- Scout, Verifier, Reviewer, and Implementer can run project scripts and Git or
  GitHub commands without routine permission prompts. Role rules still keep
  report-only agents from making changes.
- Direct destructive commands require confirmation. Agents must also request
  approval before destructive scripts whose effects permissions cannot inspect.
- Implementer edits and has unrestricted Git/GitHub CLI permissions. Workflow
  approval rules still govern push, PR creation, history rewriting, and other
  external or destructive effects.
- Verifier cannot manually edit or commit; project tooling may still produce
  mechanical changes through shell commands.
- No subagent can invoke another agent or ask the user directly. Reviewer must
  load only `code-review` for its two-pass review; other subagents cannot load
  skills. Checkpoint requests return to Cortana.

Global Cortana agents, global OpenCode config/skills, and shared workflow policy
need Blocking approval to change. Project-local config follows normal reviewed,
committed project edits.
