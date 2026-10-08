---
name: verify-change
description: Verify a change with risk-based checks and a clear completion receipt. Use when asked to verify changes, check readiness, or plan/run a workflow's verification stage.
---

# Verify change

Choose checks from the requested behaviour and project rules. Preserve the distinction
between finding a defect, proving a fix, and handing over a usable build.

## 1. Bound the task

Read applicable project instructions, the change, affected callers, existing check
commands and relevant CI configuration. Establish the required outcome and mode:

- **Execute:** run the justified existing checks. For verification-only requests,
  keep source read-only and report defects; an implementation request permits
  in-scope repairs followed by affected-check reruns.
- **Plan:** select cases and exact commands without reporting them as executed.

Identify the snapshot: repository/worktree, HEAD and uncommitted changes, or the
equivalent inputs outside Git. Reuse results only when their inputs and environment
still match. Pause source edits while checking that snapshot.

State the planned checks and their scope before expensive work. Use the project's
escalation rules; broader checks need a concrete impact/coverage reason or an
explicit request. Reversible prose or cosmetic edits may need inspection rather
than new tests. An unclear target or genuinely ambiguous requirement needs a
specific question.

**Done:** target, mode, snapshot, required behaviour and justified checks are known.

## 2. Check the execution environment

Use existing project runners and pinned toolchains. Check prerequisites inside the
process that will execute the checks, including child shells, panes and containers.

- GUI checks use the project's private display/bus and required test settings.
- Browser checks follow [browser preflight](../../docs/browser-automation.md).
- Confirm the selected tests are non-empty and exercise relevant behaviour.
- Preserve the runner's image provenance, accounts, caches and Python environment.

When a prerequisite is missing, report the blocker and use a supported available
runner if project rules allow it. Repeat an unavailable route when its state has
changed. Treat tool installation as separate work governed by the user's request.

**Done:** each planned check has a usable execution path or an explicit blocker.

## 3. Run and retain results

Run the selected checks against the identified snapshot. Record exact commands,
selection counts where available, exit status and relevant summaries. A successful
command that scanned zero inputs or skipped required checks is insufficient.

For long checks, preserve logs and completion status in session-owned scratch or
the runner's existing artifact location. Inspect those receipts after a handoff
interruption before deciding a rerun is needed. Keep task evidence out of tracked
source unless the project explicitly maintains that artifact.

Give updates when a check finishes, fails, blocks, or changes scope. If a long check
has no milestone for several minutes, briefly report what is running and what its
latest output establishes. Keep pending results and estimates clearly qualified.

**Done:** every planned check has a result or blocker traceable to this snapshot.

## 4. Investigate failures and close verification

Reproduce an isolated failure with the exact failing case. Check both the product
and the test-driving conditions: actual page/build, visible input target, captured
text, readiness, timing and environment. Use `test-analyzer` for non-trivial failure
analysis or test-quality questions.

Separate confirmed defects from environment/harness failures and unresolved causes.
Where repairs are authorised, fix the cause and rerun the failing case plus affected
callers/regressions. Document which earlier results remain valid after the edit.
Broaden coverage when new evidence or project rules require it, stating why first.

Finish when all justified checks pass or an unresolved failure/blocker is reported.
A clean result alone is not a reason to launch another suite or repeat the same
unchanged checks. Independent review findings may create new, bounded obligations.

**Done:** outcomes are resolved or explicitly reported; each rerun has a reason.

## 5. Hand over a usable result

Keep the completion receipt short:

- **Change/build:** what changed, worktree/revision and dirty-state qualification.
- **Checks:** exact commands, meaningful results and log paths when needed.
- **Limits:** failed, blocked, intentionally omitted or still-unconfirmed behaviour.
- **Preview, when relevant:** exact build/launch command and how to identify that
  build in the running app. Account for singleton forwarding and stale dev servers.
- **Publication, when requested:** actual commit/push/PR status and whether evidence
  is attached or pending. Verification itself does not authorise publication.

Plan-only results provide proposed checks and rationale instead of a pass receipt.
Respect project-specific PR formats; put detailed local receipts in the handoff
when the PR template does not call for them.

**Done:** the user can distinguish tested code, a running preview, and published work.
