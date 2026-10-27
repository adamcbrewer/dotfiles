---
name: ux-stack
description: Coordinate UX planning, implementation or review when asked to use the UX stack. Select usability, visual-design and web-interface guidance for the requested stage and return one prioritised result.
metadata:
  source: local
---

# UX Stack

Announce `ux-stack` when requested. Infer the mode from the user's request, then
use the available artifacts to decide which passes are possible. Existing code
does not turn a planning request into an implementation or review request.

## 1. Establish the task

Carry one brief through the work: audience, primary user task, platform, scope,
existing design system, constraints and requested deliverable. Infer settled
details from the conversation and project; ask only when missing information
would materially change a decision. Plans and reviews stay read-only. Apply fixes
only within an implementation or review-and-fix request.

For change reviews, identify the intended base, HEAD and relevant staged,
unstaged and untracked UI changes. Include surrounding screens, components and
states needed to understand the affected user journey. Use the supplied screen,
flow, screenshot or URL for an artifact audit instead. With no explicit target,
review the relevant current branch/local UI changes; ask if the target or base
is genuinely ambiguous. An empty UI diff is a valid result, not a reason to
audit the entire application.

Keep an existing workflow's coordinator when assigned a bounded UX pass. Reuse
its scope and evidence, return findings to it, and avoid starting nested stacks.

**Done:** mode, target, primary task and material constraints are clear.

## 2. Select the guidance

Select from task evidence rather than loading every skill. Briefly state which
passes fit and why. Revisit selection when the task changes.

| Skill | Select when | Timing and limits |
| --- | --- | --- |
| `ux-heuristics-audit` | Evaluating a proposed or existing user flow, feedback, navigation, error prevention or recovery. | After a concrete flow exists; before dependent visual decisions. For new work, first outline the steps and material states. |
| `frontend-design` | Creating or deliberately changing visual hierarchy, composition, typography or identity; critiquing affected visual choices. | After usability constraints, before visual implementation. Preserve existing tokens/components and the brief; novelty alone is not an improvement. Skip for behaviour-only fixes. |
| `web-design-guidelines` | Planning or reviewing web interactions, accessibility, forms, focus, responsiveness or other affected web implementation. | Use relevant rules as planning constraints; run its file-based audit only when source exists. Skip web-specific rules for native UI. |
| `ui-ux-pro-max` | A specific unresolved pattern, chart, palette, typography or platform decision would benefit from reference options. | At the decision it informs, before choosing or building. Use focused local searches; skip when existing requirements or the design system already settle the question. |

Resolve selected skills by name through shared discovery. Read each complete
`SKILL.md` and only the references needed for its assignment. Before applying
vendor guidance or running Pro Max searches, read [review caveats](SETUP.md#review-caveats).
Resolve scripts relative to the installed skill directory, not the working
directory or a presumed harness-specific environment variable.

A missing selected skill leaves that pass incomplete. Continue independent work
and report the gap; use the pinned setup only when installation is authorised.
Do not quietly substitute general knowledge and claim the skill ran.

This stack owns selection, ordering, scope and the combined report. Project rules,
the user's brief and supported platform behaviour govern conflicting vendor
preferences. Preserve the project's copy conventions, tokens and components;
distinguish usability requirements from aesthetic preferences. Vendor references
to other audits or workflows do not add dependencies or permissions.

**Done:** every selected pass has a distinct question and a usable input.

## 3. Work in the requested mode

### Plan

For new work, outline the user journey and material states, then apply the
heuristics audit. For changes to an existing experience, assess the affected
current flow before proposing the revised one. Resolve task blockers and recovery
paths before dependent visual design. Use Pro Max only for an open decision.

Apply frontend guidance where visual work is in scope, then check relevant web
constraints. Revisit the flow if a later constraint changes it. Return the
smallest useful plan with states, decisions, open questions and acceptance checks.
Distinguish proposed behaviour from observed behaviour; a planning pass is not a
completed code or accessibility audit.

### Implement or fix

Reuse settled planning rather than repeating discovery. Follow the relevant plan
route only for unresolved decisions, implement the scoped change, then review the
result using selected guidance. Use `verify-change` for justified checks through
the project's existing tools. Follow its browser preflight before browser work.
Recheck only affected findings after fixes.

### Review

Assess the affected journey with heuristics first, then apply visual critique
where relevant and the web file audit where source is available. Independent
checks can share a stable snapshot; their order must still respect dependencies.
Preserve concrete source locations when combining vendor outputs. Fetch Vercel's
current rules as its skill requires, and report an unavailable fetch as a coverage
limit. Use `verify-change` when execution is justified within the review scope.

Match claims to evidence: a screenshot supports visible observations; source
supports code findings; an exercised flow supports observed behaviour. Name what
was inspected or run and what remains untested. Heuristic judgement is not user
research, and these passes do not certify accessibility compliance.

### Focused request

Keep a named concern narrow: choose only the passes needed to answer it. A focus
bug does not require a palette search or visual redesign. For explanations,
answer the question without manufacturing an audit or implementation task.

**Done:** the requested plan, scoped implementation or review is ready, with
each selected pass completed or its missing evidence stated.

## 4. Combine and report

Return one result, deduplicated by underlying problem and ordered by user impact.
Each finding identifies the affected task/state, evidence and location, relevant
heuristic or rule, and a concrete fix. Use Critical/Major/Minor/Cosmetic for UX
severity, keeping uncertainty separate from impact. Label aesthetic suggestions
as suggestions. Estimate frequency only from available context; do not invent
usage data. Resolve competing recommendations toward the primary task.

Give up to three priorities when findings exist; a clean result needs none.
Include checks actually run, coverage limits and any authorised fixes applied.
Plans list proposed checks explicitly. Finish with a compact **Skills used** table
of actual reads by the coordinator or helpers: skill, stage, and contribution.
Distinguish consulted guidance from applied guidance, and list missing selected
passes separately. Reading instructions is not proof that their checks ran.

**Done:** one report accounts for the requested outcome, skill contributions and
remaining limits. No additional unchanged review is required.
