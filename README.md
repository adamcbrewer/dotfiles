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

# Omarchy includes Mise for Node.js and tool version management

# Optional Node package install hardening tools
npm install -g npq sfw
```

Optional (for respective packages):
- [VS Code](https://code.visualstudio.com/)
- [Zed](https://zed.dev/)
- [Claude Code](https://claude.ai/code)
- [OpenCode](https://opencode.ai)
- [Herdr](https://herdr.dev) (required for the `herdr` package and agent integrations)

## Installation

```sh
# Clone
git clone <repo> ~/localhost/dotfiles
cd ~/localhost/dotfiles

# Stow packages without generated runtime state
stow -t ~ git tmux vim starship bin node mise vscode zed opencode

# Keep generated Fish, GitHub CLI, Herdr, Omarchy, and Hyprland state outside the repository
mkdir -p ~/.config/{fish,gh,herdr,hypr,omarchy}
stow --no-folding -t ~ fish gh herdr

# Own the complete user plugin directory, including plugins added later
stow -t ~ omarchy

# This laptop's settings plus shared Hyprland overrides
stow --no-folding -t ~ hypr hypr-laptop
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

### Mise

Install the globally configured tools after stowing `mise`:

```sh
mise install
```

Project `mise.toml` files belong in their projects. Keep machine-specific `mise.local.toml` files untracked.

### OpenCode Skills

Install or refresh vendor-managed skills after stowing `bin` and `opencode`:

```sh
sync-opencode-skills
```

Custom skills remain stowed from `opencode/.config/opencode/skills/`. Vendor skills and their update metadata live under `~/.agents/`. The sync script pins vetted CLI and source revisions and removes only skills recorded as managed by its state file. Review all skill files before adding a skill or updating a pin.

### Herdr

Install Herdr and OpenCode before setting up the integration. The `herdr` Stow package manages only Herdr's `config.toml`; use `stow --no-folding -t ~ herdr` so runtime state stays outside the repository. Install or reinstall the separate Herdr-generated OpenCode integration after stowing `opencode`:

```sh
herdr integration install opencode
```

This command generates `herdr-agent-state.js` in OpenCode's plugin directory. Herdr owns and may overwrite that file, so it is ignored by Git and should not be edited as repository-owned configuration.

### VS Code Extensions (optional)

```sh
cat _nostow/vscode-ext/extensions.txt | xargs -L 1 code --install-extension
```

## Packages

| Package | Symlinks to |
|---------|-------------|
| `fish` | `~/.config/fish/{config.fish,fish_plugins}` |
| `git` | `~/.gitconfig`, `~/.editorconfig`, `~/.gitignore`, `~/.gitattributes` |
| `tmux` | `~/.tmux.conf` |
| `vim` | `~/.vimrc`, `~/.vim/` |
| `starship` | `~/.config/starship.toml` |
| `bin` | `~/.local/bin/` |
| `node` | `~/.npmrc`, `~/.yarnrc`, `~/.config/pnpm/rc` |
| `mise` | `~/.config/mise/config.toml` |
| `vscode` | `~/.config/Code/User/{settings,keybindings,snippets}` |
| `zed` | `~/.config/zed/{settings,keymap,snippets}` |
| `gh` | `~/.config/gh/config.yml` |
| `opencode` | `~/.config/opencode/{opencode.json,agents/,plugins/,skills/}` |
| `herdr` | `~/.config/herdr/config.toml` |
| `omarchy` | `~/.config/omarchy/{plugins/,shell.json}` |
| `hypr` | `~/.config/hypr/{hyprland.lua,looknfeel.lua}` |
| `hypr-desktop` | `~/.config/hypr/input.lua` |
| `hypr-laptop` | `~/.config/hypr/input.lua` |

## _nostow (Reference/Backup)

Not stowed. Manual restore if needed:

| Dir | Restore Command |
|-----|-----------------|
| `fonts/` | `cp -r _nostow/fonts/* ~/.local/share/fonts/ && fc-cache -fv` |
| `gnome/` | `dconf load / < _nostow/gnome/<file>` |
| `flameshot/` | `cp _nostow/flameshot/* ~/.config/flameshot/` |
| `vscode-ext/` | See "VS Code Extensions" above |
| `bash/` | Archived, not used |
| `software/` | Reference notes |

## Theme

Catppuccin Mocha across starship and tmux.

## Omarchy And Hyprland

`hypr` owns portable Hyprland overrides. `hypr-desktop` owns the desktop's
keyboard and pointer settings; `hypr-laptop` owns this laptop's settings. Never
stow both machine packages on one machine because they target the same
`input.lua`.
`monitors.lua` remains local and unmanaged because display layouts are
machine-specific. The `omarchy` package owns the complete user plugin directory
and shared shell layout and plugin settings.
Plugins added under `~/.config/omarchy/plugins/` therefore become repository
changes automatically.

Omarchy defaults under `/usr/share/omarchy`, generated state under
`~/.local/state/omarchy`, and cache data under `~/.cache/omarchy` are never
repository-owned. Keep `~/.config/hypr` and `~/.config/omarchy` as real
directories. Use regular Stow folding for `omarchy` so it owns `plugins/` as a
directory link; use `--no-folding` for the other packages.

```sh
# Inspect before applying or refreshing links
stow --simulate --verbose=2 -t ~ omarchy
stow --simulate --verbose=2 --no-folding -t ~ hypr hypr-laptop

# Refresh this laptop's links
stow --restow --verbose=2 -t ~ omarchy
stow --restow --verbose=2 --no-folding -t ~ hypr hypr-laptop

# Remove this laptop's links
stow --delete --verbose=2 -t ~ omarchy
stow --delete --verbose=2 --no-folding -t ~ hypr hypr-laptop
```

When migrating from the removed `omarchy-desktop` package, remove its stale
link before stowing `omarchy`:

```sh
case "$(readlink ~/.config/omarchy/shell.json)" in
  *omarchy-desktop*) unlink ~/.config/omarchy/shell.json ;;
esac
stow -t ~ omarchy
```

After every `omarchy update`, inspect `git status`, simulate a restow, and run
`hyprctl configerrors`. Omarchy refreshes or migrations may modify a repository
file through a leaf symlink or replace the symlink with a regular file. Review
the result before restoring links; never use `stow --adopt`.
