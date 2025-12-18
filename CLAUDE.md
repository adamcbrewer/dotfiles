# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Overview

Personal dotfiles managed with GNU Stow. Each package directory mirrors the target structure in `$HOME`.

## Structure

```
dotfiles/
├── fish/           # -> ~/.config/fish/{config.fish,fish_plugins}
├── git/            # -> ~/.gitconfig, ~/.editorconfig
├── tmux/           # -> ~/.tmux.conf
├── vim/            # -> ~/.vimrc, ~/.vim/
├── starship/       # -> ~/.config/starship.toml
├── bin/            # -> ~/.local/bin/
├── claude/         # -> ~/.claude/CLAUDE.md
├── vscode/         # -> ~/.config/Code/User/{settings,keybindings,snippets}
├── zed/            # -> ~/.config/zed/{settings,keymap,snippets}
├── gh/             # -> ~/.config/gh/config.yml
└── _nostow/        # NOT stowed (backups, reference files)
```

## Dependencies

- stow, fish, tmux, vim, zoxide, starship, gh, nvm
- Optional: VS Code, Zed, Claude Code

## Stow Commands

```sh
cd ~/localhost/dotfiles

# Install all packages
stow -t ~ fish git tmux vim starship bin claude vscode zed gh

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

## Git Aliases

Common shortcuts in `git/.gitconfig`:
- `g` → git
- `s` → status -sb
- `co` → checkout
- `cm` → commit -m
- `go <branch>` → checkout or create branch
