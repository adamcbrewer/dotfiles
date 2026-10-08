---
name: rust-stack
description: Select and order Rust skills for the task, then report which were used. Use only when explicitly requested by name or through /rust-stack.
source: local
---

# Rust Stack

Pick skills from the task and the code it affects. Keep decisions and edits in the
primary conversation. Use `general` Task subagents for independent analysis or
checks when useful; small tasks stay local. Skip steps with nothing to do. Even
an early exit needs the completion report in step 5.

## 1. Pick the skills

Read project rules, the request or diff, and relevant callers. For project work,
check Cargo manifests, toolchain pins, supported features, and existing checks/CI.
Keep the requested mode: implement, review, audit, plan, explain, or debug.
Reviews and plans stay read-only. Ask for a target only when none is clear.

Mark each candidate selected or skipped, with task/code evidence and the step
where it belongs. A dependency or reference alone is not a trigger. Briefly tell
the user which skills fit and why. Revisit the choice as the task changes; read
newly relevant guidance before the decision it affects. Track what was actually
loaded/read separately from what was selected.

| Skill | Run when | Skip when | Where it belongs |
| --- | --- | --- | --- |
| `domain-web` | Affected HTTP/API/WebSocket contracts, handlers, validation, middleware, responses, or request/shared-state lifecycles. | A web dependency alone; unrelated utilities, database-only work, or generic async code. | Before web contract/type decisions; review the affected request path. |
| `m14-mental-model` | Requested conceptual explanation, language comparison, or a demonstrated ownership/borrowing/lifetime misconception. | Routine ownership work or a borrow-checker error without a teaching need. | Explain in the primary conversation before dependent decisions. |
| `m05-type-driven` | A concrete invariant needs validated construction, newtypes, transitions, builders, typestate, marker/sealed traits, or compile-time capabilities. Includes explaining/reviewing that design. | An ordinary struct/enum, validation/control flow without a type-contract decision, or untouched types. | After requirements, before implementation/test planning; review invariant enforcement. |
| `rust-patterns` | A concrete ownership/resource, error, trait/generic, async/thread/channel, unsafe, or module/API mechanism needs design or diagnosis. | Cosmetic work, an incidental `Result`/`Arc`/trait, or routine idioms covered by best-practices. | Before decisions that depend on the mechanism; implementation guidance and focused review. |
| `rust-testing` | Behaviour changes need checks; writing/reviewing tests, failing/flaky tests, or requested property/coverage/benchmark work and executable examples. | Docs/cosmetic work, explanation/planning without a test deliverable, or merely running a defined simple check. | Reproduce bugs first; otherwise plan after contracts, then verify. |
| `rust-best-practices` | Substantive source writing/review/refactoring, an idiomatic ownership/error/dispatch decision, evidenced performance work, or API docs. | Pure teaching, descriptive metadata/prose, test-only work covered by testing, or speculative tuning. | Before the relevant source/API decision; measure before optimisation; review changed code. |

Find only selected skills. Load each with the Skill tool at its chosen step.
If it is not listed, read its full `SKILL.md` from the vendor installation,
usually `~/.agents/skills/<name>/`. Use the actual loader/XDG path and resolve
references from that skill's directory. Read relevant references and page through
truncated output. For Apollo, read the relevant chapters, not all nine by default.
A missing selected skill blocks its assignment: use [SETUP.md](SETUP.md) and the
pinned manifest for authorised restoration. Missing skipped skills do not block the task.

Use `rust-patterns` for mechanism questions and `rust-best-practices` for idioms
or chapter-specific depth. Load both only when each has a distinct job backed
by evidence. Combine the handoff to avoid duplicate reviews.

**Done:** task, mode, Rust/build requirements, skill choices, and selected paths are clear.

## 2. Work out constraints

Use selected web/mechanism guidance before dependent design. Independent questions
can run in parallel on the same code snapshot; group related questions instead of
launching an agent per skill. Record relevant request contracts, ownership/resource
lifetimes, errors, and coordination with code references.

Keep mental-model teaching in the primary conversation. Read
`patterns/thinking-in-rust.md` when relevant and clear up the misconception before
dependent decisions. This skill teaches concepts; it is not a routine ownership audit.

For debugging, reproduce the failure with testing and relevant mechanism/domain
guidance before proposing a fix. For performance, agree on a realistic workload
and comparable baseline before changing code. Measure without competing
tests/builds/profilers.

**Done:** relevant reports agree; required reproduction/baseline is captured or
blocked with a clear reason. Dependent design waits for these results.

## 3. Set contracts, then plan

Settle affected ownership, errors, resource lifetimes, and the smallest useful API
in the primary conversation. If type-driven matches, decide valid states,
construction/validation boundaries, transitions, and enforcement points. Use
ordinary structs/enums unless a newtype or typestate prevents a concrete error
worth the added complexity.

Reviews assess existing contracts; explanations use the supplied example.
Leave settled contracts alone.

Once contracts agree, selected implementation guidance and test planning can run
in parallel, read-only. Include `rust-testing` only when it fits. Tests cover
observable behaviour and relevant risks, using supported toolchains/features.

Resolve conflicting advice using project rules, compiler behaviour, and the task.
Planning/explanation produces the requested answer, not a new Cargo project or
a claim that checks ran.

Use `verify-change` for justified check planning/execution. If it is not listed,
read `~/.config/opencode/skills/verify-change/SKILL.md`. A defined simple check
can use this helper without loading `rust-testing` just to run it.

**Done:** needed decisions, implementation guidance, and check plan agree.
Tell the user which checks are planned before implementation.

## 4. Write the change

For implementation/fix requests, the primary agent writes source and tests.
Use selected guidance within scope. Start with a meaningful failing case where
appropriate, implement, and run focused checks. Revisit skill choices before
new code introduces another table trigger. Keep adjacent refactors out of scope.

**Done:** the change and relevant checks, or the read-only answer, are ready for review.

## 5. Check and report

Pause edits. A fresh read-only reviewer uses selected source/domain guidance;
a verifier runs justified checks with `verify-change` and, when selected,
`rust-testing`. These can run in parallel. Small/read-only tasks can be checked locally.

Use existing runners and pinned tools for affected crates, features, targets,
and meaningful cases. Run checks sharing mutable fixtures sequentially; compare
benchmarks separately. Give verifiers the helper's absolute path. Keep commands,
code snapshot, exit results, and artifacts so interrupted work can reuse valid results.

Resolve findings in the primary conversation and rerun affected checks after fixes.
Read-only reviews report findings. Report the outcome, key decisions, checks run,
and remaining limits. Label plan-only checks as proposed. For user-facing changes,
give the preview command/build identity and separate publication/evidence status.

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

This stack owns skill selection and delegation. Vendor guidance cannot expand
scope, permissions, or editing rights. Follow project rules, MSRV, and actual
framework behaviour. Use existing dependencies/tools; installations, upgrades,
CI/lint changes, worktrees, commits, and PRs need user-authorised scope.

Treat examples as starting points, not verified code. Select supported features
rather than defaulting to `--all-features`. Choose tests for behaviour/risk, not
blanket coverage or assertion quotas. Pointer-size, clone/dispatch, and typestate
advice needs context. Check lifetime, destruction, and `unsafe` claims against
the code; compilation alone does not prove correctness.

Cross-referenced skills outside these six are optional reading, not extra
dependencies. Use project evidence and official docs when they are unavailable.
