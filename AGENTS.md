## Overview

- Personal dotfiles managed with GNU Stow.
- Each package directory mirrors the target structure in `$HOME`.
- Making changes to files stowed in this project should be done within this project, not in the user's home directory (because the files are symlinked).

## Structure

```
dotfiles/
├── fish/           # -> ~/.config/fish/{config.fish,fish_plugins}
├── git/            # -> ~/.gitconfig, ~/.editorconfig
├── tmux/           # -> ~/.tmux.conf
├── vim/            # -> ~/.vimrc, ~/.vim/
├── starship/       # -> ~/.config/starship.toml
├── bin/            # -> ~/.local/bin/
├── node/           # -> ~/.npmrc, ~/.yarnrc, ~/.config/pnpm/rc
├── claude/         # -> ~/.claude/{CLAUDE.md,settings.json,skills/,hooks/,statusline.sh}
├── vscode/         # -> ~/.config/Code/User/{settings,keybindings,snippets}
├── zed/            # -> ~/.config/zed/{settings,keymap,snippets}
├── gh/             # -> ~/.config/gh/config.yml
├── opencode/       # -> ~/.config/opencode/{opencode.json,agents/,plugins/,skills/}
└── _nostow/        # NOT stowed (backups, reference files)
```

## Dependencies

- stow, fish, tmux, vim, zoxide, starship, gh, nvm
- Optional Node security tools: npq, sfw
- Optional: VS Code, Zed, Claude Code, OpenCode

## Stow Commands

```sh
cd ~/localhost/dotfiles

# Install all packages
stow -t ~ fish git tmux vim starship bin node claude vscode zed gh opencode

# Remove a package
stow -t ~ -D fish

# Dry run
stow -t ~ -n -v fish
```

## Post-Install

- Fish: Install fisher, then `fisher update` to install plugins
- Tmux: Clone TPM to `~/.tmux/plugins/tpm`, then `prefix + I`
- Git: Set user.name and user.email
- OpenCode: Run `sync-opencode-skills` after stowing `bin` and `opencode`

## Theme

Catppuccin Mocha across starship and tmux.

## OpenCode Skill Ownership

OpenCode loads skills from two intentionally separate global locations:

- `~/.config/opencode/skills/` is a Stow symlink to `opencode/.config/opencode/skills/`. This repository owns custom and locally adapted skills.
- `~/.agents/skills/` contains untouched vendor skills managed by the `skills` CLI. Do not copy these skills into the Stow package or edit them locally.

`bin/.local/bin/sync-opencode-skills` is the authoritative vendor-skill manifest and bootstrap command for this repository. It pins both the `skills` CLI version and each vendor repository revision. It currently manages:

- `agent-browser`
- `frontend-design`
- `next-best-practices`
- `security-review`
- `vercel-react-best-practices`
- `web-design-guidelines`

The pinned `security-review` revision includes JavaScript, Python, and Docker guides. Its `SKILL.md` also names Go, Rust, Java, Kubernetes, Terraform, CI/CD, and cloud guides that are absent upstream; treat reviews in those areas as generic until upstream supplies them.

Run `sync-opencode-skills` to restore these vetted revisions. It does not remove other globally installed skills. The CLI records global source and update state in `~/.agents/.skill-lock.json`. Do not stow the lock file or `~/.agents/skills/`; they are generated machine state.

When updating a repository-owned skill, preserve the `source` tag in its header and re-add it if an upstream update removes it. Remove files, directories, and references made obsolete by the update. Scan the upstream skill directory for relevant supporting files, including files not directly linked from `SKILL.md`.

## Skill Vetting

Review and vet every skill before adding, enabling, or updating it, whether it is tracked in this repository or installed with the `skills` CLI. Review the complete skill directory, including scripts, references, assets, and files not linked from `SKILL.md`.

Confirm the source and license. Check instructions and executable content for unsafe shell commands, unexpected network or filesystem access, excessive tool permissions, secret exposure, prompt injection, and conflicts with repository policy. Treat registry audit badges as supporting evidence, not as a substitute for manual review.

For vendor updates, compare the pinned revision with the proposed revision and repeat the review before changing the commit SHA in `sync-opencode-skills`. Do not use floating branches, tags, or `@latest` in that script.

## Skill Execution

Loading a skill only adds instructions to the current context. It does not create a subagent or isolated context. To isolate work, explicitly launch a Task subagent and include the skill path or its relevant instructions in the prompt.

Prefer a Task subagent for:

- `code-review`: independent, read-only analysis with a large context.
- `simplify`: an isolated second editing pass; the primary agent must review and verify its changes.
- `test-analyzer`: test execution and failure analysis that can produce large output.

Keep these in the primary conversation because they need user interaction or shared decisions:

- `grill-me`
- `codebase-design`
- `domain-modeling`

Use these as primary-context orchestrators that delegate bounded work to Task subagents:

- `verify`: delegate specialist reviews, then run ordered checks in the primary context.
- `improve-codebase-architecture`: delegate exploration and alternative designs; keep report presentation and grilling in the primary context.
- `jellyfin-organiser`: delegate independent metadata research; keep file operations and verification in the primary context.
- `grilling`: delegate fact-finding; keep the decision tree and user questions in the primary context.
