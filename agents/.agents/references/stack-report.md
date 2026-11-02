# Completion report

When a workflow points here, read this before starting work. Track the work as
you go, then give one combined report, even if nothing changed or work is blocked.
Planning and explanation runs need a report too. Helpers return their results to
the agent assembling the report.

Keep the report in the conversation. Temporary notes are fine when useful. Save
long-term records only when requested or required by the project. This file is a
shared reference, not another skill to run.

## What to track

Include every skill fully read by you or a helper, including any workflow skills.
Say whether it was applied or just consulted. List missing or unrun
assignments separately; selecting a skill doesn't mean it ran.

Ask helpers which skills and paths they read, what they did, how many passes they
completed, what they found and rechecked, and what remains uncertain. Keep the
evidence behind findings. Reuse shared work without counting it twice.

## What the numbers mean

- **Passes:** completed rounds of work using a skill. Each assignment or stage
  counts once; a focused recheck after a fix adds a pass. Two independent reviewers
  using the same skill count as two passes. Reading instructions, tool calls,
  messages and resuming interrupted work don't add passes. Coordinating one workflow
  run counts as one pass.
- **Findings:** confirmed issues, counted once per underlying problem. Credit the
  skill that first established the issue with evidence. Mention other skills that
  confirmed it in their contribution. Leave rejected concerns, unresolved questions
  and aesthetic suggestions out of the count.
- **Fixed:** those findings repaired and verified during this task, by a relevant
  check or inspection. Keep credit with the skill that found the issue; say who
  repaired or verified it in the contribution. Suggestions and unchecked edits
  aren't fixes. Rechecking an issue doesn't make it a new finding.

Use `0` for none, `n/a` when a finding or fix count doesn't apply, and `unknown`
when there's not enough evidence to count. Mark unfinished or failed assignments
incomplete, showing any passes already completed. Don't guess missing counts or
treat the numbers as quality or confidence scores.

## What to report

Lead with the result, then findings or fixes, checks performed and anything still
unverified. Keep proposed checks separate from checks actually run. Finish with
one **Skills used** table, one row per skill:

| Skill | Passes | Findings | Fixed | Contribution / limits |
| --- | --- | --- | --- | --- |
| `<name>` | `<count>` | `<count or n/a>` | `<count or n/a>` | `<what it contributed, where used and any limits>` |

Skills only consulted get zero passes and `n/a` for findings and fixes. Briefly
explain shared findings and unknown counts. Give unique finding and fix totals
where relevant. Mention unresolved questions and incomplete coverage even when
there are no confirmed findings.
