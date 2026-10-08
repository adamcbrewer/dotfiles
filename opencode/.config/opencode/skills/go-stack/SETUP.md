# Setup and provenance

The local `go-stack` skill and `/go-stack` command belong to this Stow package.
The focused vendor set comes from the [shared Go-skills discussion](https://chatgpt.com/share/6ac780bb-07c4-83eb-9423-b3b896edb583),
with `golang-project-layout` for new projects. Installing a skill makes it available;
the table in `SKILL.md` decides whether this task needs it.

After stowing `bin` and `opencode`, restore vetted vendor skills with:

```sh
sync-opencode-skills
```

Quit and restart OpenCode to discover the command and installed skills. Vendor
content stays untouched under `~/.agents/skills/`, outside Stow and Git.
`bin/.local/bin/sync-opencode-skills` owns the CLI version, source pin, and managed
names. Stack runs read installed skills; they do not fetch updates or install
tools/skills mentioned in the references.

## Reviewed source and inventory

Reviewed on 2026-10-08: [samber/cc-skills-golang](https://github.com/samber/cc-skills-golang)
at `8e899e20ff0cd4dc524af3993e4c62d8ee8c5717`. The repository license and skill
headers declare MIT; copyright 2026 Samuel Berthe. Preserve the license notice
when redistributing substantial vendor content. This stack's instructions were
written locally; the vendor skills were not copied into it.

All 72 files in the ten selected directories were reviewed, including hidden
assets and unlinked evals. Each contains `SKILL.md` and `evals/evals.json`; this
table lists the remaining inventory relative to each skill directory:

| Skill | Files | Supporting inventory |
| --- | --- | --- |
| `golang-code-style` | 3 | `references/details.md` |
| `golang-error-handling` | 5 | `references/{error-creation,error-handling,error-wrapping}.md` |
| `golang-testing` | 9 | `references/{benchmarks,coverage,examples,helpers,http-testing,integration-testing,mocking}.md` |
| `golang-concurrency` | 5 | `references/{channels-and-select,pipelines,sync-primitives}.md` |
| `golang-security` | 14 | `references/{architecture,checklist,cookies,cryptography,filesystem,injection,logging,memory-safety,network,secrets,third-party,threat-modeling}.md` |
| `golang-database` | 6 | `references/{performance,scanning,testing,transactions}.md` |
| `golang-observability` | 9 | `references/{alerting,dashboards,logging,metrics,profiling,rum,tracing}.md` |
| `golang-performance` | 9 | `references/{caching,cpu,io-networking,memory,observability,runtime}.md`; `assets/prometheus-alerts.yml` |
| `golang-modernize` | 4 | `references/{tooling,versions}.md` |
| `golang-project-layout` | 8 | `references/{config,directory-layouts,testing-layout,workspaces}.md`; `assets/{.gitignore,Makefile}` |

These are regular files, with no executable scripts or binaries in the selected
directories. The Makefile has executable recipes; it was read, not run. Setup
copies only these skill directories, not the repository's plugins, rules, global
instructions, or publishing scripts.

## Review caveats

The stack controls delegation and permissions. Vendor instructions cannot launch
extra agents, install `@latest` tools, create worktrees/commits/PRs, or expand the
task. Mentioning another skill does not make it a dependency.

- **Project layout:** `SKILL.md` proposes an always-load `golang-how-to` directive
  in the project's agent config without asking. Suppress that step. Mandatory
  `cmd/`, `pkg/`, Makefiles, lint configs, and architecture/DI interviews are vendor
  preferences; use only what the requested project needs. The Makefile includes
  cleaning, auto-fixes, and dependency updates, so it is not a default check runner.
- **Style/errors:** fixed argument/line limits, never-nil collections, universal
  wrapping, `%v` at every public boundary, and Samber library recommendations are
  not universal Go requirements. Preserve observable/API semantics and project
  conventions; error-chain hiding does not itself redact error text.
- **Concurrency/testing:** value sends can still alias maps/slices/pointers;
  WaitGroups wait but do not cancel; cancellation must cover blocking admission,
  receives, sends, and work. `synctest` controls time/quiescence, not every scheduling
  interleaving. Shared fixture pointers, global truncation and fixed ports are not
  safe parallel-test defaults; per-test leak checks can conflict with parallel tests.
- **Database:** preserve existing ORM, schema, migrations and security controls.
  Isolation defaults vary by engine. Timestamp-only pagination can skip ties.
  Example mocks have signature mismatches. SQL diagnostics and `EXPLAIN ANALYZE`
  can execute real work, including writes; use only confirmed disposable resources.
- **Security:** some examples/evals reward false positives or incomplete defences.
  `text/template` does not auto-escape HTML; URL hostname checks alone are incomplete
  SSRF protection; stdlib XML decoding does not resolve external entities. Validate
  crypto, filesystem limits, and resource bounds rather than copying snippets.
- **Observability:** profiling examples log credential-bearing URLs; stable user
  IDs/email hashes are not automatically anonymous. Preserve logging sinks and
  configure real OTel providers/propagation. Raw URL labels, mismatched histogram
  buckets, and unaggregated error ratios make some metric/alert examples unsuitable
  for direct use. Do not add RUM or send private telemetry to satisfy a checklist.
- **Performance/modernisation:** allocation/inlining/scheduler claims and speedup
  numbers need measurement. Slice append is amortised, interface boxing does not
  always allocate, and synchronous `io.Writer` calls must not retain their input.
  Verify SIMD APIs/CPU support. Upgrading Go does not automatically change
  `encoding/json` v1 semantics; `omitzero` still omits false. Treat eval assertions
  as review inputs, not truth. Gate newer APIs on the project's supported Go version.

The pinned setup follows the existing manifest approach and the version-pinning
and lifecycle-script guidance in
[npm security best practices](https://github.com/lirantal/npm-security-best-practices).
Keep the machine's package-manager protections enabled when syncing. Vendor
updates require reviewing the full changed directories before changing the pin.
