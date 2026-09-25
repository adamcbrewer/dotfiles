---
name: rust-workflow
description: Rust workflow combining six skills for design, implementation, testing, and review. Use only when explicitly requested by name or through /rust-workflow.
source: local
---

# Rust Workflow

Orchestrate all six skills below. Keep decisions and edits in the primary
conversation; use `general` Task subagents for bounded analysis and verification.
Loading a skill supplies instructions, not an isolated agent.

## 1. Establish scope and dependencies

Read project instructions, the requested code or diff, Cargo manifests, toolchain
pins, and relevant CI commands. Establish whether the request is implementation,
review, planning, or explanation. Preserve that mode throughout: review and
planning produce findings or a plan, rather than edits. If no target can be inferred
from the request or conversation, ask for one before launching agents.

Resolve these installed vendor skills:

- `domain-web`
- `m14-mental-model`
- `m05-type-driven`
- `rust-patterns`
- `rust-testing`
- `rust-best-practices`

Load each with the Skill tool in its assigned stage. If it is not advertised,
read its complete `SKILL.md` from the vendor installation, normally
`~/.agents/skills/<name>/`. Use the loader's actual location when XDG paths differ.
Resolve supporting paths relative to that skill's directory, not the project.
Read complete outputs, paging through any truncation.

If dependencies are missing, read [SETUP.md](SETUP.md) and report the missing
names. Restore them through the pinned manifest before claiming a complete run;
never silently substitute remembered guidance or fetch floating upstream skills.

**Done:** a bounded task, operating mode, affected paths, toolchain constraints,
and the location of all six dependencies are known.

## 2. Establish constraints — parallel

Launch two read-only analyses against the same task and code snapshot:

| Subagent skill | Assignment | Required result |
| --- | --- | --- |
| `domain-web` | Identify applicable HTTP, validation, shared-state, async, and request-lifecycle constraints. For non-web work, assess applicability without adding web architecture. | Concrete constraints with code references, or an explicit not-applicable reason. |
| `m14-mental-model` | Identify ownership, borrowing, lifetime, and concurrency assumptions. Read `patterns/thinking-in-rust.md` when explaining those concepts. | Owners and resource lifetimes relevant to the task; misconceptions or uncertainty needing resolution. |

Reconcile their results before designing types. Keep mental-model explanations
brief unless teaching is the user's goal.

**Done:** both reports received; conflicting assumptions resolved or a precise
question raised with the user. Record the agreed constraints for downstream work.

## 3. Design types — sequential

In the primary conversation, load `m05-type-driven` and apply it to the agreed
constraints. Identify valid states, validation boundaries, fallible transitions,
and the smallest useful public API. Prefer ordinary structs and enums unless a
newtype or typestate prevents a concrete error worth its complexity.

For review, assess the existing types; for explanation, use the supplied example.

**Done:** every task-relevant invariant has a proposed or existing enforcement
point, with ownership and error behavior clear enough to plan implementation and
tests. Record unresolved design choices rather than inventing requirements.

## 4. Plan implementation and tests — parallel

Send the agreed constraints and type decisions to two read-only subagents:

| Subagent skills | Assignment | Required result |
| --- | --- | --- |
| `rust-patterns` + `rust-best-practices` | Load both skills; read all relevant Apollo chapters in parallel. Check ownership, error handling, async behavior, interfaces, and project idioms. | Minimal implementation guidance, or concrete review findings, citing affected code and reference chapters. |
| `rust-testing` | Identify observable behavior, failure paths, and existing test seams. Select meaningful unit, integration, async, property, or doc tests as appropriate. | Test cases tied to requirements and exact verification commands using the project's toolchain and feature matrix. |

Reconcile duplicate or conflicting advice using project instructions, compiler
behavior, and the task's requirements. See **Applying upstream guidance** below.

**Done:** all six skills have been consulted; implementation guidance and test
cases agree on the same API and behavior. Every recommendation is accepted,
rejected with a reason, or raised as an unresolved decision.

## 5. Implement — single writer

For implementation requests, the primary agent owns source and test edits. Use
the agreed test plan: establish a meaningful failing test for changed behavior
where appropriate, implement, then refactor while keeping it passing. Run focused
checks as needed. For review, planning, or explanation, retain the corresponding
output instead of implementing.

**Done:** the requested changes and appropriate tests are ready for verification,
or the requested read-only deliverable is ready for its final consistency check.

## 6. Review and verify — parallel, then reconcile

On a stable snapshot, launch:

- A fresh read-only reviewer using `rust-best-practices`, with the original task,
  constraints, type decisions, and final diff or deliverable. Read relevant
  chapters before assessing concrete correctness and maintainability issues.
- A verifier using `rust-testing`, with the agreed test plan. For code tasks,
  execute applicable project checks and return exact commands, results, and
  blockers. For planning or explanation, check the proposed tests and examples
  without inventing a Cargo project or claiming execution.

Keep edits paused until both finish. Resolve findings in the primary conversation;
after changes, rerun affected checks and re-review affected findings. For review
requests, report findings rather than fixing them. Avoid unrelated test expansion
once relevant checks pass.

**Done:** each finding is resolved or reported, every planned check has a result
or explicit blocker, and all six skills have an application or not-applicable
record. Finish with the outcome, key decisions/findings, checks actually run,
and any remaining limitations. Never equate skill loading with verification.

## Subagent handoff

Each dispatch must include the task and operating mode, project directory,
applicable project instructions, bounded file scope, exact skill names and
absolute paths, prior stage decisions, and the required result above. Require
agents to load/read their assigned skills and applicable supporting files; a name
alone is not enough. Ask for file/line evidence, uncertainties, and commands run.

Subagents do not edit source, install tools, or delegate further. The verifier may
run checks that generate ordinary build artifacts. Run at most two subagents at
once. If Task is unavailable, perform the same assignments sequentially and
disclose that fallback; preserve every stage's completion criterion.

## Applying upstream guidance

Project instructions, scope, MSRV, and actual framework behavior govern application
of the upstream references. Their examples are illustrative, not verified code.
Use existing dependencies and approved tooling; upstream examples are not requests
to install packages, update Rust, change CI, or add lints.

Select supported feature combinations instead of blindly using `--all-features`.
Choose tests for behavior and risk rather than a blanket coverage quota or
one-assertion rule. Treat pointer-size thresholds, clone/dispatch advice, and
typestate as context-dependent. Verify lifetime, destruction, and `unsafe` claims
against the actual code; compilation alone is not proof of correctness.

Cross-referenced skills outside these six are optional further reading, not hidden
dependencies to download. Use project evidence and Rust/framework documentation
when those references are needed but unavailable.
