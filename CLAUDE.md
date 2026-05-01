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
├── claude/         # -> ~/.claude/{CLAUDE.md,settings.json,skills/,hooks/,statusline.sh}
├── vscode/         # -> ~/.config/Code/User/{settings,keybindings,snippets}
├── zed/            # -> ~/.config/zed/{settings,keymap,snippets}
├── gh/             # -> ~/.config/gh/config.yml
├── opencode/       # -> ~/.config/opencode/opencode.json
└── _nostow/        # NOT stowed (backups, reference files)
```

## Dependencies

- stow, fish, tmux, vim, zoxide, starship, gh, nvm
- Optional: VS Code, Zed, Claude Code, OpenCode

## Stow Commands

```sh
cd ~/localhost/dotfiles

# Install all packages
stow -t ~ fish git tmux vim starship bin claude vscode zed gh opencode

# Remove a package
stow -t ~ -D fish

# Dry run
stow -t ~ -n -v fish
```

## Post-Install

- Fish: Install fisher, then `fisher update` to install plugins
- Tmux: Clone TPM to `~/.tmux/plugins/tpm`, then `prefix + I`
- Git: Set user.name and user.email

## Theme

Catppuccin Mocha across starship and tmux.

## Updating agent skills

When updating agent skills, use the `source` tag in the skill's header and re-add it if it's removed during the update.
