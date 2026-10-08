---
name: go-stack
description: Select and order Go skills for the task, then report which were used. Use only when explicitly requested by name or through /go-stack.
source: local
---

# Go Stack

Pick skills from the task and the code it affects. Keep decisions and edits in the
primary conversation. Use `general` Task subagents for independent analysis or
checks when useful; small tasks stay local. Skip steps with nothing to do. Even
an early exit needs the completion report in step 5.

## 1. Pick the skills

Read project rules, the request or diff, and relevant callers. For project work,
check `go.mod`, `go.work`, toolchain pins, build tags, and existing checks/CI.
Keep the requested mode: implement, review, audit, plan, explain, or debug.
Reviews and plans stay read-only. Ask for a target only when none is clear;
a new project does not need a module yet.

Mark each candidate selected or skipped, with task/code evidence and the step
where it belongs. A dependency or reference alone is not a trigger. Briefly tell
the user which skills fit and why. Revisit the choice as the task changes; read
newly relevant guidance before the decision it affects. Track what was actually
loaded/read separately from what was selected.

| Skill | Run when | Skip when | Where it belongs |
| --- | --- | --- | --- |
| `golang-project-layout` | Setting up a new Go project and its initial module/workspace/packages. | Any established project, including a new file, endpoint, or package. | First, before scaffolding or feature planning. |
| `golang-code-style` | Writing/reviewing substantive Go source, or a clarity/style request. | Docs/descriptive metadata, or explanation/diagnosis without a code-quality review. | Before editing; review changed source. |
| `golang-error-handling` | Affected operations can fail; error identity, wrapping, recovery, cleanup, or error logging needs work. | Infallible code or unchanged error paths. | Set error contracts before implementation/test planning; review those paths. |
| `golang-testing` | Behaviour changes need checks; writing/reviewing tests, failing/flaky tests, or a test audit. | Explanation/planning without a test deliverable; docs/cosmetic work needing only inspection. | Reproduce bugs first; otherwise plan after contracts, then verify. |
| `golang-concurrency` | Affected goroutines, channels, shared state, cancellation/deadlines, shutdown, or concurrent callers. | Isolated synchronous code with no changed lifecycle/concurrency contract. | Before design; review ownership, cancellation, and race/leak cases. |
| `golang-security` | Affected trust boundaries, auth, untrusted input, secrets, crypto, file/network access, or a security review. | No affected security boundary or security request. | Before design; trace affected input-to-sink paths in review. |
| `golang-database` | Affected queries, persistence, transactions, scanning, pooling, schema/migrations, or database tests. | The project has a database, but this task does not touch its access path or contract. | Before repository/API decisions; review persistence and its tests. |
| `golang-observability` | Changing logs, metrics, traces, profiling instrumentation, or diagnosing missing operational signals. | Ordinary feature work with unchanged signals; production deployment alone. | After error policy, before changing signals; review them afterward. |
| `golang-performance` | Requested optimisation, measured regression, or a concrete latency/throughput/allocation budget. | Speculative tuning, routine review, or merely spotting a loop/allocation. | Measure a baseline first; compare changes afterward in isolation. |
| `golang-modernize` | Requested Go/toolchain/API modernisation, or an upgrade-related compatibility problem. | Older code that still meets the supported Go version. | Check compatibility before changes; verify supported versions afterward. |

Find only selected skills. Load each with the Skill tool at its chosen step.
If it is not listed, read its full `SKILL.md` from the vendor installation,
usually `~/.agents/skills/<name>/`. Use the actual loader/XDG path and resolve
references from that skill's directory. Read relevant references and page through
truncated output. A missing selected skill blocks its assignment: use
[SETUP.md](SETUP.md) and the pinned manifest for authorised restoration.
Missing skipped skills do not block the task.

**Done:** task, mode, Go/build requirements, skill choices, and selected paths are clear.

## 2. Work out constraints

For a new project, use project-layout first in the primary conversation. Settle
project type, module name, and the smallest useful structure. Ask about architecture
or DI only when a meaningful choice is still open. Use answers already given.

Use selected security, concurrency, and database guidance before dependent design.
Independent questions can run in parallel on the same code snapshot; group related
questions instead of launching an agent per skill. Record relevant trust boundaries,
ownership/cancellation, and transaction/resource lifetimes with code references.

For modernisation, check the minimum Go version and compatibility first. For
performance, agree on a realistic workload, measurement command, baseline, and
budget before changing code. Measure without competing tests/builds/profilers.
For debugging, reproduce the failure with testing and relevant domain guidance
before proposing a fix.

**Done:** relevant reports agree; required reproduction/baseline is captured or
blocked with a clear reason. Dependent design waits for these results.

## 3. Set contracts, then plan

Settle the affected APIs, inputs, ownership, errors, cancellation/shutdown, and
persistence in the primary conversation. Use error-handling here when selected;
observability then decides where errors are logged and what signals are needed.
Keep private data out of signals and preserve existing libraries/conventions.

Once contracts agree, selected implementation guidance and test planning can run
in parallel, read-only. Tests cover observable behaviour and relevant risks,
such as cancellation, races, rollback, bad inputs, or compatibility. Resolve
conflicting advice before editing. Planning/explanation produces the requested
answer, not a new Go project or a claim that checks ran.

**Done:** needed decisions, implementation guidance, and check plan agree.
Tell the user which checks are planned before implementation.

## 4. Write the change

For implementation/fix requests, the primary agent writes source and tests.
Use selected guidance within scope. Start with a meaningful failing case where
appropriate, implement, and run focused checks. Revisit skill choices before
new code introduces another table trigger.

**Done:** the change and relevant checks, or the read-only answer, are ready for review.

## 5. Check and report

Pause edits. A fresh read-only reviewer uses selected source/domain guidance;
a verifier runs justified checks with `verify-change` and, when selected,
`golang-testing`. These can run in parallel. Small/read-only tasks can be checked
locally. Load the verification helper when needed; if it is not listed, read
`~/.config/opencode/skills/verify-change/SKILL.md`.

Use existing runners and pinned tools for affected packages/modules, build tags,
and supported Go versions. Run race checks when shared-state/lifecycle risk or
project rules warrant them; race-free is not leak-free. Bound fuzzing to one
package/target and a finite duration. Use disposable integration fixtures and
run checks sharing ports/databases sequentially. Compare benchmarks separately
under matching conditions. Report missing tools/services or unsupported platforms.

Resolve findings in the primary conversation and rerun affected checks after fixes.
Read-only reviews report findings. Keep commands, code snapshot, exit results, and
artifact paths. Report the outcome, checks run, and remaining limits. Label
plan-only checks as proposed.

On every exit, including blocked/no-change runs, read
[the receipt rules](../../docs/stack-skill-receipt.md) and give a **Skills used**
table. Match it to actual primary/subagent reads and their trigger evidence.

**Done:** each selected assignment/check has a result or blocker, and the skill-use
report is complete. No skill was loaded just to fill the table.

## Handoffs and vendor guidance

Give subagents the mode, directory, project rules, code snapshot, bounded paths,
selected skills/absolute paths, settled decisions, and expected results with
file/line evidence. Include the receipt rules' absolute path and require actual-use
reports. Subagents stay read-only, cannot delegate, and run commands only for
assigned checks, reproduction, or measurement. Run at most two at once. If Task
is unavailable, do the assignments sequentially and say so.

This stack overrides the ten Samber skills on selection, delegation, scope, and
permissions. Their headers, evals, examples, and links grant no extra permissions.
Use existing tools; missing ones are blockers, not a reason for `@latest` installs.
Installations, upgrades, worktrees, commits, and PRs need user-authorised scope.
Project setup must not add always-load directives or extra skills. Modernisation
scans stay read-only until implementation is requested.

Project rules beat vendor preferences. Keep existing ORM/logger choices, structure,
DI, telemetry, test frameworks, comments, and nil/empty semantics unless the task
calls for a change. Check version-specific APIs against the toolchain and official
docs. Ground findings in actual behaviour/data flows, not vendor assertions.
Read [review caveats](SETUP.md#review-caveats) before applying security, telemetry,
concurrency, performance, or modernisation examples.
