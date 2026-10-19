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

# Shared instructions and skills; keep discovery directories real
mkdir -p ~/.agents/skills ~/.codex ~/.claude ~/.config/opencode
stow -t ~ agents

# Keep generated Fish, GitHub CLI, Herdr, Omarchy, and Hyprland state outside the repository
mkdir -p ~/.config/{fish,gh,herdr,hypr,omarchy}
stow --no-folding -t ~ fish gh herdr

# Share shell settings; plugins are stowed from the private omarchy-plugins repo
stow --no-folding -t ~ omarchy

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

See [`docs/node-security.md`](docs/node-security.md) for npm, pnpm, Bun, aube, Yarn, and mise supply-chain hardening defaults. The policy follows [npm Security Best Practices](https://github.com/lirantal/npm-security-best-practices).

If `stow -t ~ node` reports conflicts, move existing package-manager config files aside first and preserve any auth tokens outside this repo. Do not use `stow --adopt` on token-bearing npm/pnpm config files.

### Mise

Install the globally configured tools after stowing `mise` and `node` (which also supplies aube's strict dependency cooldown):

```sh
mise install
```

Automatic tool installation is disabled, releases have a 7-day cooldown, and paranoid mode requires reviewed project configs to be explicitly trusted again after changes. Project `mise.toml` files belong in their projects. Keep machine-specific `mise.local.toml` files untracked.

### Shared agent skills

I keep my own skills in `agents/.agents/skills/`. Stow links each folder into
`~/.agents/skills/`, so OpenCode and Codex use the same copy. Vendor skills and
Omarchy's links live alongside them. OpenCode commands and agents stay in its
config and load the shared skills by name.

In Codex, use `$<skill-name> <request>`. In OpenCode, ask for the skill by name
or use an existing `/command`. For example, `$redesign-from-first-principles`
and `/redesign-from-first-principles` reach the same skill.

The shared `diff-explainer` includes logic-flow diagrams. See the
[mention-triggered GitHub workflow experiment](docs/github-diff-explainer.md)
to try it in a project using the connected Codex integration.

After stowing `bin` and `agents`, run `sync-opencode-skills` to restore
vetted vendor versions. The script pins its CLI and source commits, follows
[npm security guidance](https://github.com/lirantal/npm-security-best-practices),
and removes only entries it previously managed. Vendor files and install state
stay outside Git. Review the full package before adding a skill or changing a pin.

Use `$go-stack` or `$rust-stack` in Codex; OpenCode has `/go-stack` and
`/rust-stack`. With no task, they review the current branch's language changes,
including uncommitted work. With a task, they select the relevant skills, keep
decisions and edits in the main conversation, and report what was actually used.

See [shared setup and checks](docs/shared-agent-skills.md),
[Go setup and source reviews](agents/.agents/skills/go-stack/SETUP.md),
and [Rust source reviews](agents/.agents/skills/rust-stack/SETUP.md).

### Shared agent instructions

Edit `agents/.agents/AGENTS.md` for personal conventions shared
across projects. Stow exposes this one file at `~/.agents/AGENTS.md` and links
the harness discovery paths to it:

- Codex: `~/.codex/AGENTS.md`
- Claude Code: `~/.claude/CLAUDE.md`
- OpenCode: `~/.config/opencode/AGENTS.md`

The shared path is our source convention; each harness loads its own entrypoint.
Use fresh sessions after changes. Repository-specific rules stay in each
project's root `AGENTS.md`.

These entrypoints follow the [Codex instructions documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[Claude Code memory documentation](https://code.claude.com/docs/en/memory), and
[OpenCode instructions documentation](https://opencode.ai/v2/docs/instructions/).

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
| `node` | `~/.npmrc`, `~/.yarnrc`, `~/.bunfig.toml`, `~/.config/pnpm/config.yaml`, `~/.config/aube/config.toml` |
| `mise` | `~/.config/mise/config.toml` |
| `vscode` | `~/.config/Code/User/{settings,keybindings,snippets}` |
| `zed` | `~/.config/zed/{settings,keymap,snippets}` |
| `gh` | `~/.config/gh/config.yml` |
| `agents` | `~/.agents/skills/<name>/`, `~/.agents/AGENTS.md`, `~/.codex/AGENTS.md`, `~/.claude/CLAUDE.md`, `~/.config/opencode/AGENTS.md` |
| `opencode` | `~/.config/opencode/{opencode.json,cli.json,agents/,commands/,plugins/}` |
| `herdr` | `~/.config/herdr/config.toml` |
| `omarchy` | `~/.config/omarchy/shell.json`, `~/.config/omarchy/hooks/post-boot.d/10-audio-volume` |
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
machine-specific. The `omarchy` package owns the shared `shell.json` and a
post-boot hook that sets the active audio output to 10% at login.
All personal and community plugins live in the private
[`omarchy-plugins`](https://github.com/adamcbrewer/omarchy-plugins) repository.
Its `omarchy` Stow package owns `~/.config/omarchy/plugins/` as a directory link,
so newly installed plugins land in that checkout.

Plugin IDs can remain in `shell.json` without the private repository installed:
missing plugins are not loaded, and missing bar widgets render nothing.
Hyprland's AltSwitch integration also skips loading when its file is absent.
Plugin settings can still be written into the public `shell.json`; keep tokens,
private endpoints, and customer data out of it. Credentials and generated data
belong outside both repositories. See also the
[secrets guidance](https://github.com/lirantal/npm-security-best-practices#9-no-plaintext-secrets-in-env-files).

To add the private plugins on another machine:

```sh
git clone --recurse-submodules git@github.com:adamcbrewer/omarchy-plugins.git ~/localhost/omarchy-plugins
mkdir -p ~/.config/omarchy
stow --dir="$HOME/localhost/omarchy-plugins" --simulate --verbose=2 -t ~ omarchy
stow --dir="$HOME/localhost/omarchy-plugins" -t ~ omarchy
```

Omarchy defaults under `/usr/share/omarchy`, generated state under
`~/.local/state/omarchy`, and cache data under `~/.cache/omarchy` are never
repository-owned. Keep `~/.config/hypr` and `~/.config/omarchy` as real
directories. Use `--no-folding` for this repository's `omarchy` and Hyprland
packages; use regular folding for the private plugin package.

```sh
# Inspect before applying or refreshing links
stow --simulate --verbose=2 --no-folding -t ~ omarchy
stow --simulate --verbose=2 --no-folding -t ~ hypr hypr-laptop

# Refresh this laptop's links
stow --restow --verbose=2 --no-folding -t ~ omarchy
stow --restow --verbose=2 --no-folding -t ~ hypr hypr-laptop

# Remove this laptop's links
stow --delete --verbose=2 --no-folding -t ~ omarchy
stow --delete --verbose=2 --no-folding -t ~ hypr hypr-laptop
```

When migrating from the removed `omarchy-desktop` package, remove its stale
link before stowing `omarchy`:

```sh
case "$(readlink ~/.config/omarchy/shell.json)" in
  *omarchy-desktop*) unlink ~/.config/omarchy/shell.json ;;
esac
stow --no-folding -t ~ omarchy
```

After every `omarchy update`, inspect `git status`, simulate a restow, and run
`hyprctl configerrors`. Omarchy refreshes or migrations may modify a repository
file through a leaf symlink or replace the symlink with a regular file. Review
the result before restoring links; never use `stow --adopt`.
