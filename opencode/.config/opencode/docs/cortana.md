# Cortana Agent System

Cortana is an explicit-only global OpenCode workflow for implementation work.
Use `/cortana <task>` or select the `cortana` primary agent. It is not the
default agent.

## Architecture

```text
                         blocking finding
                               +-----+
                               |     v
Cortana -> Scout -> Baseline -> Implementer -> Verifier -> Reviewer -> Finalize
   ^                              ^              |          |
   |                              +--------------+----------+
   +--------------- human checkpoints and state ----------------+
```

Cortana is the only governor. It owns routing, approvals, handoff state, loop
limits, and finalization. Secondary agents run sequentially for reliable state
transfer; safe tool calls inside one agent may run in parallel.

| Agent | Visibility | Responsibility |
| --- | --- | --- |
| `cortana` | Primary/selectable | Governance and handoff state |
| `cortana-scout` | Hidden subagent | Research and planning |
| `cortana-implementer` | Hidden subagent | Edits, focused checks, commits |
| `cortana-verifier` | Mentionable subagent | Baseline/final verification |
| `cortana-reviewer` | Mentionable subagent | Final substantive review |

Manual `@cortana-verifier` and `@cortana-reviewer` sessions are standalone,
report-only modes. They do not edit, delegate, or start remediation loops.

## Workflow

The full workflow is the default:

1. Cortana records the request and exact user acceptance criteria.
2. Cortana inspects branch, status, staged/unstaged diffs, and recent history.
3. Scout discovers project rules, architecture, risks, checks, and slices.
4. Verifier runs baseline checks before edits.
5. Implementer completes and commits coherent slices.
6. Verifier runs focused checks per slice and final relevant/full checks.
7. Reviewer assesses the accumulated final change.
8. Blocking findings loop through Implementer, Verifier, and Reviewer.
9. Cortana finalizes only after the definition of done is met.

Acceptance criteria are a hard contract when supplied. Cortana records them
verbatim and does not invent more. When none are supplied, agents use the
request plus clearly labelled success signals. Ambiguous success is Blocking.

### Shortcuts

Cortana may offer a shortcut only before implementation. The Optional prompt
must name every skipped stage, explain why, and retain post-change Verifier.
The user must approve. Once implementation starts, checks may be added but not
removed.

Scout approval is required only for careful mode, low confidence, broad/risky
or destructive work, meaningful architecture tradeoffs, and unclear or
conflicting instructions. Otherwise Scout hands directly to Implementer after
baseline verification.

## Verification

Baseline verification fingerprints existing health so regressions can be
separated from pre-existing failures. Command discovery order:

1. Project `AGENTS.md`.
2. `README`, `CONTRIBUTING`, and project docs.
3. Package scripts, task runner, and CI configuration.
4. Ecosystem defaults.
5. Human clarification when still unclear.

Run cheap authoritative checks first. Scope checks when full runs are
unreasonably expensive. A related or unclear baseline failure blocks edits;
an unrelated pre-existing failure is recorded and does not block. A failure
the user asked to fix is expected and does not block.

Verifier evaluates whole-project state with diff-aware focus. Project-defined
formatters, lint fixes, expected snapshot updates, codegen, and lockfile refresh
may write mechanically. Any output returns to Implementer for inspection and
commit. Verifier never manually edits, changes logic, weakens tests, or commits.

Results use three states:

- `passed`: the check completed successfully.
- `failed`: the check ran and found a real issue.
- `incomplete`: it could not run, timed out, needed a missing service, or was
  omitted for scope/cost.

Final verification is mandatory. The final report lists every check run and
omitted, with reasons. Residual risk requires Blocking human acceptance.

Documented project-local services may be used. The agent records what it starts
and stops only those services. Cloud, staging, production, deployed previews,
GitHub Actions reruns, paid/external services, and anything using secrets need
approval.

## Review

Reviewer runs after all planned work passes verification and reviews the final
accumulated diff, not each small checkpoint. Findings are:

- **Blocking:** substantive, in-scope, introduced/worsened by the change, an
  unmet request/acceptance criterion, or serious immediate risk in touched code.
- **Non-blocking:** useful follow-up, including unrelated pre-existing issues.

Blocking findings must be fixed or explicitly accepted. Fixes route through
Implementer, then Verifier, then Reviewer. Non-blocking findings appear in the
final summary; issues are not created automatically.

## Git And Ownership

Startup inspection is mandatory: status, staged diff, unstaged diff, recent
log, and current branch.

- Clean tree: proceed.
- Related dirty work: preserve and proceed carefully.
- Unrelated or unclear dirty work: Blocking ownership question.
- `main`, `master`, or `trunk`: Blocking branch question before edits; recommend
  `feat/`, `fix/`, or `chore/`, including a ticket ID when known.
- Staged changes are user-owned by default. Never commit or unstage them without
  explicit approval.
- Separate same-file hunks are allowed. Overlap or unclear ownership blocks.
- Use whole-file staging for Cortana-owned files and non-interactive patch
  staging for mixed files. Inspect staged diff before every commit.
- Commit coherent slices before Verifier or Reviewer handoff.
- Never amend, squash, rebase, reset, force-push, or rewrite history without
  Blocking approval.

Push is Optional by default. PR creation is Blocking unless explicitly
pre-approved because it creates team-visible state.

Authenticated GitHub hosting operations use the `gh` CLI, including issues,
PRs, checks, runs, releases, and repository metadata. Repository transport uses
`git`. Agents do not call the GitHub API with `curl` or manually handle tokens.

## Run Handoffs

Non-trivial runs use project-local `.opencode/runs/<ticket-or-slug>.md`. On
first use, add `.opencode/runs/` to an existing `.gitignore`; ask Optional
before creating a new `.gitignore` when none exists. Handoffs are lean state,
not transcripts:

```md
# Run Handoff

## Task
## Acceptance Criteria
## Success Signals
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

`Worktree Ownership` is conditional. Cortana owns the file structure, workflow
state, shortcuts, loop counts, and outcome. Subagents own the content of their
role reports, which they return to Cortana for recording. Harness improvement
ideas belong in the final summary, not the handoff.

## Loops And Checkpoints

Each correction route has a maximum of five loops. Track routes independently,
for example `Verifier -> Implementer` and `Reviewer -> Implementer`. Pause
before the limit if the same failure repeats twice without meaningful progress.
At the limit, stop and provide route, count, stuck point, attempts, likely
cause, and recommended options.

Confidence drops also require a checkpoint: unclear criteria, risky domains,
missing verification commands, broken environment, real tradeoffs, or inability
to explain correctness. Human prompts are labelled `Blocking` or `Optional`.

## Project Onboarding

The first non-trivial run discovers project type/package manager, rules,
declared checks, CI, run-directory ignore status, naming conventions, and local
service needs. It does not create a permanent profile. At finalization Cortana
may offer to promote genuinely reusable knowledge:

- `AGENTS.md`: repeatable agent rule, command, or gotcha.
- `docs/`: human-facing workflow/domain/onboarding knowledge.
- `docs/adr/`: durable architecture decision or tradeoff.

Ordinary feature summaries, one-off failures, and transcripts are not promoted.

## Definition Of Done

Cortana can finalize only when:

- implementation is committed locally;
- Verifier passed, or residual failures are documented and accepted;
- Reviewer blocking findings are resolved or accepted;
- non-blocking findings and loop counts are recorded;
- checks run and omitted are reported;
- push is offered unless declined;
- PR creation is asked when relevant; and
- reusable knowledge promotion is offered only when valuable.

## Permissions

Permissions reinforce role boundaries:

- Cortana edits only `.opencode/runs/*.md`, invokes only `cortana-*` agents, and
  loads only approved workflow skills. It can inspect Git and GitHub state.
- Scout, Verifier, and Reviewer can run Git and GitHub read/view commands but
  cannot mutate repository or GitHub state.
- Implementer edits and has unrestricted Git/GitHub CLI permissions. Workflow
  approval rules still govern push, PR creation, history rewriting, and other
  external or destructive effects.
- Verifier cannot manually edit or commit; project tooling may still produce
  mechanical changes through shell commands.
- No subagent can invoke another agent, load a skill, or ask the user directly;
  checkpoint requests return to Cortana.

Global Cortana agents, global OpenCode config/skills, and shared workflow policy
need Blocking approval to change. Project-local config follows normal reviewed,
committed project edits.
