# Shared agent skills

I keep my skills in `agent-skills/.agents/skills/`. Stow links them into
`~/.agents/skills/`, so Codex and OpenCode use the same files.

## Set up

From this repo:

```sh
mkdir -p ~/.agents/skills
stow --simulate --verbose=2 -t ~ agent-skills
stow -t ~ agent-skills
```

Keep `~/.agents` and `~/.agents/skills` as real directories. Check for clashes
with vendor and Omarchy skill names before adding one.

## Use a skill

- Codex: `$<skill-name> <request>`, or select it from `/skills`.
- OpenCode: ask for the skill by name, or use its `/command` if it has one.

OpenCode commands, agents and settings stay in `opencode/.config/opencode/`.
The skill holds the workflow; commands and agents just load it.

## Keep them up to date

- Edit my skills here, including supporting files. Keep their source and licence.
- Stow shares those edits with both tools. There's no separate sync step.
- `sync-opencode-skills` restores reviewed, pinned vendor skills. Keep vendor files and their install state outside Git.
- Restart OpenCode and refresh provider status in T3 after changes.

## Explicit-only skills

- Codex: set `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.
- OpenCode v2: set `disable-model-invocation: true` in `SKILL.md`. OpenCode v1 ignores this flag, so keep the explicit-request wording too.

These settings control automatic selection. You can still request the skill by name.

## Quick check

Use `opencode --pure debug skill` in OpenCode or `/skills` in Codex. Check from
this repo and another directory: each skill should appear once, its references
should work, and an explicit request should load it.

See the [GitHub diff-explainer experiment](github-diff-explainer.md) for PR mentions.
Setup follows [npm security best practices](https://github.com/lirantal/npm-security-best-practices).
