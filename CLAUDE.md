# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal dotfiles managed with GNU Stow. Each package directory mirrors the target structure in `$HOME`.

## Dependencies

- GNU stow
- fish shell
- starship prompt
- tmux (with tpm plugin manager)
- zoxide (z command for directory jumping)
- nvm (node version manager)

For fish: also install fisher + bass plugins for nvm compatibility.

## Structure

```
dotfiles/
├── fish/           # -> ~/.config/fish/
├── git/            # -> ~/.gitconfig, ~/.editorconfig
├── tmux/           # -> ~/.tmux.conf
├── vim/            # -> ~/.vimrc, ~/.vim/
├── starship/       # -> ~/.config/starship.toml
├── bin/            # -> ~/.local/bin/
└── _nostow/        # NOT stowed (bash archive, fonts, gnome)
```

## Stow Commands

```sh
cd ~/localhost/dotfiles

# Install all packages
stow -t ~ fish git tmux vim starship bin

# Remove a package
stow -t ~ -D fish

# Dry run
stow -t ~ -n -v fish
```

## Theme

Catppuccin Mocha is used consistently across starship and tmux.

## Git Aliases

Common shortcuts defined in `git/.gitconfig`:
- `g` → git
- `s` → status -sb
- `co` → checkout
- `cm` → commit -m
- `lg` / `l` → pretty log graphs
- `go <branch>` → checkout or create branch
