# Setup and provenance

The local skill and `/rust-workflow` command are owned by this Stow package.
Untouched vendor skills live outside the repository and are restored with:

```sh
sync-opencode-skills
```

Stow `bin` and `opencode` first if they are not already linked. Quit and restart
OpenCode after setup so it discovers the command and all six dependencies.

The authoritative CLI version, upstream commit pins, and managed-skill list are in
`bin/.local/bin/sync-opencode-skills` in the dotfiles repository. Normal workflow
invocations read installed skills and do not run `npx skills use` or access the
network to refresh guidance. Updates require reviewing the complete changed
skill directories before changing pins.

## Reviewed sources

| Source | Skills | Complete reviewed inventory | License |
| --- | --- | --- | --- |
| [affaan-m/ecc](https://github.com/affaan-m/ecc) | `rust-patterns`, `rust-testing` | One `SKILL.md` per skill | MIT, repository license |
| [actionbook/rust-skills](https://github.com/actionbook/rust-skills) | `domain-web`, `m05-type-driven`, `m14-mental-model` | Each `SKILL.md`, plus `m14-mental-model/patterns/thinking-in-rust.md` | MIT declared in metadata and README; no standalone license file at the reviewed revision |
| [apollographql/skills](https://github.com/apollographql/skills) | `rust-best-practices` | `SKILL.md` and `references/chapter_01.md` through `chapter_09.md` | MIT, repository license and skill header |

All files in these six directories were reviewed, including unlinked supporting
files. They contain prose and examples, with no bundled executables. Apollo's
`allowed-tools` header is upstream metadata, not permission to expand this
workflow's tool access. Installation selects only these directories, not the
repositories' agents, hooks, routers, or setup scripts.

The Actionbook license declaration lacks a standalone grant text; preserve that
provenance caveat when updating or redistributing it. The workflow installs vendor
content separately rather than copying it into this public repository.

Known content caveats are handled under **Applying upstream guidance** in
`SKILL.md`: overly broad test quotas and style rules, examples needing adaptation,
toolchain-version inconsistencies, and simplified ownership/lifetime explanations.

Authoring guidance came from Matt Pocock's
[`writing-great-skills`](https://github.com/mattpocock/skills/tree/9c32629965586e75a9d2206922dccec91e19f2f2/skills/productivity/writing-great-skills),
including its glossary and invocation metadata. Upstream renamed it to
`writing-for-agents`; it is authoring reference, not a runtime dependency.
OpenCode uses the explicit command file and a discoverable skill description;
the guide's Claude-specific invocation mechanics are not assumed to apply.

The pinned setup follows the existing manifest approach and the version-pinning
and lifecycle-script guidance in
[npm security best practices](https://github.com/lirantal/npm-security-best-practices).
Preserve the machine's npm security settings when running the bootstrap command.
