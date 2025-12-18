# dotfiles

Personal dotfiles managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Requirements

- stow
- fish shell
- starship
- tmux
- zoxide

For fish shell, also install [fisher](https://github.com/jorgebucaran/fisher) + [bass](https://github.com/edc/bass) for nvm compatibility.

## Installation

```sh
# Clone to ~/localhost/dotfiles (or adjust paths)
git clone <repo> ~/localhost/dotfiles
cd ~/localhost/dotfiles

# Install all packages
stow -t ~ fish git tmux vim starship bin claude vscode zed gh
```

## Packages

| Package | Symlinks to |
|---------|------------|
| `fish` | `~/.config/fish/` |
| `git` | `~/.gitconfig`, `~/.editorconfig` |
| `tmux` | `~/.tmux.conf` |
| `vim` | `~/.vimrc`, `~/.vim/` |
| `starship` | `~/.config/starship.toml` |
| `bin` | `~/.local/bin/` |
| `claude` | `~/.claude/CLAUDE.md` |
| `vscode` | `~/.config/Code/User/{settings,keybindings,snippets}` |
| `zed` | `~/.config/zed/{settings,keymap,snippets}` |
| `gh` | `~/.config/gh/config.yml` |

The `_nostow/` directory contains archived configs and reference files that are not stowed:
- `bash/` - old bash config
- `fonts/` - font files
- `gnome/` - GNOME/dconf settings
- `claude-skills/` - Claude Code custom skills
- `flameshot/` - screenshot tool config
- `vscode-ext/` - VS Code extensions list

## Shell Setup

```sh
chsh -s /usr/bin/fish
```

## Git Config

After stowing, set your identity:
```sh
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```
