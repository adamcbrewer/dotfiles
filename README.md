# dotfiles

Personal dotfiles managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Dependencies

Install these before stowing:

```sh
# Core
sudo apt install stow fish tmux vim zoxide

# Starship prompt
curl -sS https://starship.rs/install.sh | sh

# GitHub CLI
sudo apt install gh

# NVM (for Node.js version management)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# Optional Node package install hardening tools
npm install -g npq sfw
```

Optional (for respective packages):
- [VS Code](https://code.visualstudio.com/)
- [Zed](https://zed.dev/)
- [Claude Code](https://claude.ai/code)
- [OpenCode](https://opencode.ai)

## Installation

```sh
# Clone
git clone <repo> ~/localhost/dotfiles
cd ~/localhost/dotfiles

# Stow all packages
stow -t ~ fish git tmux vim starship bin node claude vscode zed gh opencode
```

## Post-Install Setup

### Fish Shell

```sh
# Set as default shell
chsh -s /usr/bin/fish

# Install fisher (plugin manager)
fish -c "curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher"

# Install plugins from fish_plugins manifest
fish -c "fisher update"
```

### Tmux

```sh
# Install TPM (plugin manager)
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# Start tmux, then press: prefix + I (Ctrl-s + I) to install plugins
```

### Git

```sh
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### Node Security

See [`docs/node-security.md`](docs/node-security.md) for npm, pnpm, and Yarn supply-chain hardening defaults. The policy follows [npm Security Best Practices](https://github.com/lirantal/npm-security-best-practices).

If `stow -t ~ node` reports conflicts, move existing package-manager config files aside first and preserve any auth tokens outside this repo. Do not use `stow --adopt` on token-bearing npm/pnpm config files.

### OpenCode Skills

Install or refresh vendor-managed skills after stowing `bin` and `opencode`:

```sh
sync-opencode-skills
```

Custom skills remain stowed from `opencode/.config/opencode/skills/`. Vendor skills and their update metadata live under `~/.agents/`.

### VS Code Extensions (optional)

```sh
cat _nostow/vscode-ext/extensions.txt | xargs -L 1 code --install-extension
```

## Packages

| Package | Symlinks to |
|---------|-------------|
| `fish` | `~/.config/fish/{config.fish,fish_plugins}` |
| `git` | `~/.gitconfig`, `~/.editorconfig` |
| `tmux` | `~/.tmux.conf` |
| `vim` | `~/.vimrc`, `~/.vim/` |
| `starship` | `~/.config/starship.toml` |
| `bin` | `~/.local/bin/` |
| `node` | `~/.npmrc`, `~/.yarnrc`, `~/.config/pnpm/rc` |
| `claude` | `~/.claude/{CLAUDE.md,settings.json,skills/,hooks/,statusline.sh}` |
| `vscode` | `~/.config/Code/User/{settings,keybindings,snippets}` |
| `zed` | `~/.config/zed/{settings,keymap,snippets}` |
| `gh` | `~/.config/gh/config.yml` |
| `opencode` | `~/.config/opencode/{opencode.json,agents/,plugins/,skills/}` |

## _nostow (Reference/Backup)

Not stowed. Manual restore if needed:

| Dir | Restore Command |
|-----|-----------------|
| `fonts/` | `cp -r _nostow/fonts/* ~/.local/share/fonts/ && fc-cache -fv` |
| `gnome/` | `dconf load / < _nostow/gnome/<file>` |
| `flameshot/` | `cp _nostow/flameshot/* ~/.config/flameshot/` |
| `claude-skills/` | `cp -r _nostow/claude-skills/* ~/.claude/skills/` |
| `vscode-ext/` | See "VS Code Extensions" above |
| `bash/` | Archived, not used |
| `software/` | Reference notes |

## Theme

Catppuccin Mocha across starship and tmux.
