# Stack skill-use receipt

End every Go/Rust stack run with a short **Skills used** table. Include blocked,
no-change, review, planning, and explanation runs.

| Skill used | Why it ran | Where used |
| --- | --- | --- |
| `<actual skill name>` | `<request phrase or affected file:line matching the routing rule>` | `<stage; primary or subagent; consulted/applied>` |

Track actual use separately from the selection plan. Count a skill after a Skill
call or a full `SKILL.md` read. Include subagent use and helpers such as
`verify-change` when read. Leave the current stack itself out of the sub-skill table.

Ask subagents for skill names/paths, references read, stages, trigger evidence,
and whether guidance was applied or only consulted. They use assigned skills;
new triggers go back to the primary agent before adding skills. Check their
reports against actual calls/reads before claiming completion.

Use one row per skill, combining stages/agents if reused. Leave out skills that
were only mentioned, planned, skipped, unavailable, or assigned but not read.
If none ran, say **No sub-skills were loaded.** List missing selected skills as blockers.

If a skill was read unnecessarily or turned out not to fit, still list it:
**consulted, not applied**, with the original reason and failed match. Do not
call it skipped after reading it. Report check commands/results separately;
reading a skill does not prove its checks ran. Label proposed checks as planned.
