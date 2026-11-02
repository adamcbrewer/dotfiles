---
name: verify-change
description: Plan or execute scoped checks and return verification evidence. Use for requested verification, readiness checks, or a stack's verification handoff.
---

# Verify change

Use this as the common verification handoff from Go, Rust, UX and review stacks,
or for a standalone verification request. The existing coordinator owns scope,
skill selection, repairs and the final report. An assigned verifier returns its
results to that coordinator without starting another stack or invoking analysis
helpers. Report deeper diagnostic needs for the coordinator to assign separately.

## 1. Accept the handoff

Reuse the supplied task, applicable project rules, affected paths, current code
revision and local edits, requested behaviour, proposed checks and valid earlier
results. Ask only for material missing information. For standalone use, establish
these from the current task or relevant branch/local changes; an empty scope is
a valid result.

Choose the requested mode:

- **Execute:** run justified checks using existing project tools. Verification-only
  requests and assigned verifier passes keep source read-only. The coordinator
  applies already-authorised repairs and hands back the affected reruns. During
  standalone implementation work, the same agent may perform both roles.
- **Plan:** propose cases and commands, without claiming execution.

Match checks to the required behaviour and project rules, using language/testing
guidance already selected by the coordinator. Prose or cosmetic changes may need
only inspection. State the scope before expensive checks. Pause edits to affected
inputs while checking them; changed inputs invalidate only dependent results.

**Done:** target, mode, expected behaviour and justified checks are clear.

## 2. Check the runner

Use existing runners and pinned tools. Inspect commands and targets before
execution, including scripts that update snapshots or mutate data. Use disposable
fixtures for mutating checks; installs, live migrations and automatic source or
snapshot updates require scope beyond verification alone.

Check prerequisites in the process that will execute the checks. Apply the
project's GUI/display, container and environment requirements where relevant.
Browser work follows [browser preflight](references/browser-automation.md).
Report missing prerequisites and use an available supported route when permitted.

**Done:** each check has a usable execution path or a concrete blocker.

## 3. Run and summarise

Run the scoped checks and retain commands, meaningful selection counts where
available, exit results and relevant output in the conversation. A successful
command with zero relevant inputs or skipped required checks is insufficient.
Separate confirmed defects, runner/environment failures and unresolved causes.

Use temporary logs only when needed for long output, diagnosis or an interrupted
run. Existing runner artifacts can be reused. No receipt files, content snapshots
or long-term archive are required by default. After an interruption, inspect
available completion evidence; reuse it only while relevant inputs and environment
still match. Unknown completion is not a pass.

Give progress updates for long checks and report failures or blockers promptly.
Return the smallest supported diagnosis and affected rerun scope to the coordinator.
After each repair, rerun the failing case and the smallest set of affected caller
or regression tests, plus relevant targeted lint or type checks. Refresh only the
review conclusions affected by the edit. Reuse independent passing results; each
specialist does not need its own repeat of the same checks.

Reserve full test/lint suites for the configured final gate, such as a pre-push
hook, final local check or CI. Confirm what that gate actually covers and reuse
its results when they match the final inputs. A future hook or pending CI is
pending evidence, not a pass. Run missing required final checks once at completion
when within scope; do not duplicate a valid gate simply to produce a receipt.
Earlier broad reruns need a concrete cross-cutting impact, new failure evidence,
an explicit request or a project requirement. Explain that reason before running.

Finish once scoped checks pass or remaining failures, blockers and pending final
gates are explicit; a clean result creates no extra gate.

**Done:** every planned check has a result or blocker, and each rerun has a reason.

## 4. Return the verification handoff

Return a compact result in the conversation:

- Target and relevant revision/local-edit qualification.
- Checks performed, commands and meaningful results, including reused results.
- Confirmed issues, unresolved failures, omitted checks and coverage limits.
- When relevant, the exact preview command and how to identify the running build.
- Publication/evidence status only when requested; verification grants no publishing
  permission.

Plan-only handoffs contain proposed checks and rationale. Include actual skill use
and completed passes for the coordinator's [stack report](../../references/stack-report.md).
The coordinator incorporates this handoff into its final answer without a second
receipt. Standalone verification ends with this compact result; no stack table is
required unless a stack ran.

**Done:** the user or coordinator can tell what was checked and what remains uncertain.
