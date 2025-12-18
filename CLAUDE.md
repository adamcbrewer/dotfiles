# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal dotfiles for shell and terminal environment configuration. Files are meant to be symlinked to home directory.

## Dependencies

- zsh or fish shell
- starship prompt
- tmux (with tpm plugin manager)
- zoxide (z command for directory jumping)
- nvm (node version manager)

For fish: also install fisher + bass plugins for nvm compatibility.

## Key Files

| File | Purpose |
|------|---------|
| `.zshrc` | Primary shell config, plugins in `~/.zsh-plugins/` |
| `config.fish` | Fish shell config (alt shell) |
| `.tmux.conf` | Tmux config, prefix is `C-s`, uses tpm |
| `starship.toml` | Prompt config, lives at `~/.config/starship.toml` |
| `.gitconfig` | Git aliases and settings |
| `.vimrc` | Vim config |

## Theme

Catppuccin Mocha is used consistently across starship and tmux.

## Git Aliases

Common shortcuts defined in `.gitconfig`:
- `g` → git
- `s` → status -sb
- `co` → checkout
- `cm` → commit -m
- `lg` / `l` → pretty log graphs
- `go <branch>` → checkout or create branch

## Installation

Symlink files to home directory:
```sh
ln -s ~/localhost/dotfiles/.zshrc ~/.zshrc
ln -s ~/localhost/dotfiles/.tmux.conf ~/.tmux.conf
ln -s ~/localhost/dotfiles/starship.toml ~/.config/starship.toml
# etc.
```

Set default shell:
```sh
chsh -s /usr/bin/zsh   # or /usr/bin/fish
```
