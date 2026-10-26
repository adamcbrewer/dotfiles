# Agent session review

Collect and analyse retained local agent history. The reviewing agent uses its
current model; `--source` selects whose history to inspect.

## Sources

| Source | Supported input | Limits |
| --- | --- | --- |
| Codex | Local rollout JSONL in `$CODEX_HOME/sessions` and `archived_sessions` | No cloud/deleted history; observed local record formats only |
| OpenCode | SQLite v1 and v2 tables, including mixed migrated databases | Current stored state may include changes after the review cutoff |
| T3 metadata | Optional `--t3-db` with either source | Supplies parent/root/project links, not another transcript source |

The adapters share a manifest/chunk format. Additional providers can add an
adapter without changing session distillation or pattern analysis. Run collection
separately for each source when comparing providers; preserve the source label.

## Use

This skill is explicit-only. Select it in the skill picker or invoke
`$agent-session-review` in Codex, or `@agent-session-review` in OpenCode.
Ordinary wording and plain-text mentions do not activate it. OpenCode also has
these manual commands:

```text
/agent-session-review Codex sessions from 2026-10-19 through 2026-10-25
/agent-session-review OpenCode sessions from yesterday
```

The old skill and command names are retired. Refresh skill discovery or restart
the harness after the rename.

## Collect without AI

```bash
python3 ~/.agents/skills/agent-session-review/scripts/collect.py --source codex --date yesterday
python3 ~/.agents/skills/agent-session-review/scripts/collect.py --source codex --start-date 2026-10-19 --end-date 2026-10-25 --timezone Europe/London
python3 ~/.agents/skills/agent-session-review/scripts/collect.py --source opencode --date yesterday
```

Date ranges include both local calendar dates and handle daylight-saving changes.
The default is yesterday. Collection selects activity, including sessions created
before the range. It reads history without changing it and writes a new run under
`$XDG_DATA_HOME/agent-session-review/<source>/<dates>/`.

Options:

- `--db PATH`: OpenCode database override. Find the configured path using
  `opencode debug paths`. The collector detects available v1/v2 table sets.
- `--sessions-dir PATH`: Codex directory override; repeat to include multiple
  locations. Continuation files with the same session ID are merged.
- `--t3-db PATH`: optional T3 SQLite database, opened read-only. On this machine,
  `~/.t3/userdata/statev2.sqlite` contains the relevant lineage projections.
- `--project PATH`: exact root-session working directory, applied after lineage
  enrichment. Missing parent metadata can make this filter incomplete.
- `--output PATH`: new output directory; an existing directory is refused.
- `--tool-chars N`: characters per tool input/output/error field; default 2,000.
  Both ends are retained with an explicit omission count.
- `--chunk-chars N`: approximate compact-JSON character budget; default 30,000.
  This is not a token limit; pretty-printed files are larger.

The script prints the manifest path and coverage. It collects, not analyses.
Give an existing manifest to the skill to resume analysis using saved digests.

## Outputs and interpretation

```text
manifest.json         source, dates, diagnostics, coverage and session/chunk index
chunks/*.json         normalised entries with source message IDs and references
evidence.json         indexed media, PR links and reported tool results
digests/*.json        one AI digest per session, checked against input hashes
report.md             patterns, counterexamples, limits and up to three actions
```

Adapters return session records with parent/root/project identity, directory,
message counts, input hash and bounded `chunks` of `entries`. The shared CLI
writes schema-version-2 manifests. Digests retain extraction version 1; reuse
requires matching input hashes and chunk lists. Historical manifests are not
rewritten by a rename.

Codex retains user/assistant text, bounded tool calls and results, model labels,
CLI version, available usage snapshots and turn timing. Response items are used
instead of their mirrored event messages. The first file header owns session
identity; inherited parent headers cannot replace it. Duplicate records across
continuations are collapsed, while distinct messages with identical text remain.

Both sources retain up to four preceding messages as context. Child briefs,
synthetic continuations and copied history are not fresh human corrections.
T3's parent links are important: external delegates can otherwise look like
independent root conversations. Without T3, projects use native metadata (Codex
uses the root working directory). T3 roots titled `[session-review]` are excluded;
OpenCode also supports this exclusion through its native root titles. Codex
without T3 has no dependable title-based exclusion.

Coverage is complete only for the collected, readable input. Deleted history,
other devices, unsupported schemas and malformed records limit that claim.
Media paths/URLs are indexed with local availability where possible. The
collector does not decode images or videos; the reviewer selectively inspects
them using [the evidence workflow](references/evidence.md). Embedded media data
is not copied. Reasoning, injected instructions and compaction replacement
history are omitted. Tool excerpts are not full logs;
Codex nested tools inside `exec` are not counted separately. SQLite records show
current stored state rather than a point-in-time snapshot.

Cumulative token snapshots must not be summed. Turn durations include waiting
and do not measure human effort. Comparing model performance needs comparable
tasks and confirmed outcomes, not just model labels or token totals.

OpenCode v2 embeds content and tool states inside message records. The adapter
retains text, tool results, media references, model and per-message usage data,
and marks stored state updated after the cutoff. Mixed databases deduplicate
matching session/message IDs while retaining messages unique to either schema.

The evidence index preserves tool-reported process exits, test-summary lines and
structured PR states where present, before excerpting output. These are review
candidates, not automatic confirmation. The reviewer pairs results with calls,
checks test scope and ties PR checks to the relevant head. Fresh read-only PR
lookups are labelled with their lookup time, separately from historical state.
Neither collection nor evidence review reruns historical commands.

Evidence lists share an approximate 3,000-character budget per entry; PR check
lists have a 1,000-character budget within that. Fields ending in `_omitted`
count excluded items. Retrieve the original record when a relevant reference or
result is omitted. These budgets keep large tool results from flooding chunks.

Remaining gaps include deleted sessions, missing media, unavailable service
access and the instruction/skill versions active at the time. Retrieve only
evidence relevant to a suspected pattern; distinguish unavailable evidence from
a negative result. Raw excerpts can contain private data, so keep review
artifacts out of published repositories.

## Maintenance and checks

This is a local personal skill; the original package has no separate licence
file. No vendor implementation is bundled. It uses Python 3.9+ and the standard
library, with no package installation. This keeps dependencies minimal, following
[the repository's dependency guidance](https://github.com/lirantal/npm-security-best-practices#14-reduce-your-package-dependency-tree).

```bash
python3 -B -m unittest discover -s ~/.agents/skills/agent-session-review/scripts -p 'test_*.py' -v
```

Fixtures cover source preservation, cutoff/context behavior, daylight saving,
continuations, native and T3 child grouping, inherited headers, synthetic text,
long text/tool excerpts, malformed records, mixed v1/v2 migrations, media and
outcome provenance, metadata and the CLI contract.
