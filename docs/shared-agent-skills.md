# Shared agent skills

I keep one copy of my skills in `agent-skills/.agents/skills/`. Stow links each
folder into `~/.agents/skills/`, so OpenCode and Codex read the same files.

## Set up

Run from the dotfiles repo:

```sh
mkdir -p ~/.agents/skills
stow --simulate --verbose=2 -t ~ agent-skills
stow -t ~ agent-skills
```

Keep `~/.agents` and `~/.agents/skills` as real directories. The skills CLI and
Omarchy have their own entries there too. Before adding a skill, check existing
names, the vendor manifest, lockfile and managed-name state. Stop on a conflict.

## Use a skill

- Codex: type `$<skill-name> <request>` or select it from `/skills`.
- OpenCode: ask to use the skill by name, or use an existing `/command` shortcut.

For redesign, use `$redesign-from-first-principles <request>` in Codex or
`/redesign-from-first-principles <request>` in OpenCode.

For a diff explanation, use `$diff-explainer <PR URL, range, or request>` in
Codex or ask OpenCode's `diff-explainer` agent. The agent loads the shared skill;
diagram rules live in its `references/logic-flow-diagrams.md`. The skill is
explicit-invocation only.

For a project-owned GitHub experiment, see
[mention-triggered Codex explanations](github-diff-explainer.md). Its reusable
workflow forwards a PR mention to Codex; bot-authored requests still need a
live check.

OpenCode commands and agents stay in `opencode/.config/opencode/`. Commands load
shared skills and pass the request. Workflow defaults belong in the skill;
models, permissions and agent roles belong in the tool's own config.

## Update a skill

Edit the whole package here, including its scripts, references and licences.
Keep its source header. Resolve supporting files from the skill's directory,
not the project you're working in. Browser guidance and stack receipts live in
`verify-change/references/`.

Vendor packages stay outside Git and are restored by `sync-opencode-skills`.
Review them before changing a pin. Keep their lockfile and install state outside
Stow too. The pinned setup follows [npm security best practices](https://github.com/lirantal/npm-security-best-practices).

## Manual-only skills

Codex uses `agents/openai.yaml` with `allow_implicit_invocation: false` to keep a
skill available for user mentions without selecting it automatically. A missing
entry in the model's skill list doesn't mean it's missing from `/skills`.

OpenCode v2 and Claude use `disable-model-invocation: true`. OpenCode v1 ignores
that flag, so it relies on the explicit-request wording. That's guidance, not a
hard block. These settings control selection; they don't grant permissions.

Claude can use per-skill links under `~/.claude/skills/` later. OpenCode also reads
that directory, so check for duplicate entries when adding those links.

## Check it works

Check both tools from the repo and another directory. Each shared skill should
appear once, its references should resolve, and an explicit request should work.
For manual-only skills, also check that an ordinary request doesn't select them.

Use `opencode --pure debug skill` for OpenCode's list and `/skills` or app-server
`skills/list` for Codex. Codex 0.161.0 doesn't report invocation policy there;
`codex debug prompt-input "Explain what a symlink is."` shows what the model sees.

Checked on 8 October 2026 with OpenCode 1.18.35 and Codex 0.161.0: all 14 personal
skills were discovered, the writing pilot and redesign requests worked in both.
Stow reported no conflicts, and vendor state was unchanged.
Claude and T3's menu haven't been tested here.

Restart OpenCode after changes, then refresh provider status in T3. Existing
sessions can remember old skill paths.

Docs: [Agent Skills](https://agentskills.io/specification),
[Codex](https://developers.openai.com/codex/build-skills),
[OpenCode v1](https://opencode.ai/docs/skills/),
[OpenCode v2](https://opencode.ai/v2/docs/skills/).
