## Overview

- Personal dotfiles managed with GNU Stow.
- Each package directory mirrors the target structure in `$HOME`.
- Making changes to files stowed in this project should be done within this project, not in the user's home directory (because the files are symlinked).

## Structure

```
dotfiles/
├── fish/           # -> ~/.config/fish/{config.fish,fish_plugins}
├── git/            # -> ~/.gitconfig, ~/.editorconfig, ~/.gitignore, ~/.gitattributes
├── tmux/           # -> ~/.tmux.conf
├── vim/            # -> ~/.vimrc, ~/.vim/
├── starship/       # -> ~/.config/starship.toml
├── bin/            # -> ~/.local/bin/
├── node/           # -> ~/.npmrc, ~/.yarnrc, ~/.bunfig.toml, ~/.config/{pnpm/config.yaml,aube/config.toml}
├── mise/           # -> ~/.config/mise/config.toml
├── vscode/         # -> ~/.config/Code/User/{settings,keybindings,snippets}
├── zed/            # -> ~/.config/zed/{settings,keymap,snippets}
├── gh/             # -> ~/.config/gh/config.yml
├── agents/         # -> ~/.agents/{AGENTS.md,skills/} and harness instruction links
├── opencode/       # -> ~/.config/opencode/{opencode.json,cli.json,agents/,commands/,plugins/}
├── herdr/          # -> ~/.config/herdr/config.toml
├── omarchy/        # -> ~/.config/omarchy/shell.json
├── hypr/           # -> ~/.config/hypr/{hyprland.lua,looknfeel.lua}
├── hypr-desktop/   # -> ~/.config/hypr/input.lua
├── hypr-laptop/    # -> ~/.config/hypr/input.lua
└── _nostow/        # NOT stowed (backups, reference files)
```

## Dependencies

- stow, fish, tmux, vim, zoxide, starship, gh, mise
- Optional Node security tools: npq, sfw
- Optional: VS Code, Zed, Claude Code, OpenCode, Herdr

## Stow Commands

```sh
cd ~/localhost/dotfiles

# Install packages without generated runtime state
stow -t ~ git tmux vim starship bin node mise vscode zed opencode

# Share instructions and personal skills; keep discovery directories real
mkdir -p ~/.agents/skills ~/.codex ~/.claude ~/.config/opencode
stow -t ~ agents

# Keep generated Fish, GitHub CLI, Herdr, Omarchy, and Hyprland state outside the repository
mkdir -p ~/.config/{fish,gh,herdr,hypr,omarchy}
stow --no-folding -t ~ fish gh herdr

# Share shell settings; plugins are stowed from the private omarchy-plugins repo
stow --no-folding -t ~ omarchy

# Machine-specific settings plus portable Hyprland overrides
stow --no-folding -t ~ hypr hypr-laptop

# Remove a package
stow -t ~ -D fish

# Dry run
stow -t ~ -n -v fish
```

## Post-Install

- Fish: Install fisher, then `fisher update` to install plugins
- Tmux: Clone TPM to `~/.tmux/plugins/tpm`, then `prefix + I`
- Git: Set user.name and user.email
- Mise: Run `mise install` after stowing `mise`
- Shared skills: Run `sync-opencode-skills` after stowing `bin` and `agents`; stow `opencode` for its native commands and agents
- Herdr: Install Herdr and OpenCode, then run `herdr integration install opencode` after stowing `opencode`

## Theme

Catppuccin Mocha across starship and tmux.

## Omarchy And Hyprland Ownership

`hypr` owns portable `hyprland.lua` and `looknfeel.lua` overrides.
`hypr-desktop` owns the desktop's `input.lua`; `hypr-laptop` owns this laptop's
`input.lua`. Leave `monitors.lua` unmanaged and local to each machine.

The `omarchy` package owns the shared `~/.config/omarchy/shell.json` and the
`hooks/post-boot.d/10-audio-volume` hook, which sets the active output to 10% at login.
All user plugins belong in the separate private `~/localhost/omarchy-plugins`
repository. Its `omarchy` Stow package owns the complete
`~/.config/omarchy/plugins/` directory using regular Stow folding. Never add
plugin source to this public repository. Plugin IDs may remain in `shell.json`
when the plugins are absent; keep direct Hyprland plugin loads optional.
Plugin settings can be persisted into the public `shell.json`, so keep secrets
and private data out of those settings and out of both repositories.

Omarchy defaults under `/usr/share/omarchy`, generated state under
`~/.local/state/omarchy`, and cache data under `~/.cache/omarchy` remain outside
Git. Keep `~/.config/hypr` and `~/.config/omarchy` as real directories. Use
`--no-folding` for this repository's `omarchy` and Hyprland packages. Omarchy
updates and refreshes may modify repository files through links or replace
links; inspect Git and simulate a restow after each update.

Only stow, restow, or delete `hypr-laptop` on this machine; use `hypr-desktop`
on the desktop. Portable setup commands may include `hypr` and `omarchy`, but must not
include machine-specific packages without first confirming the target machine.
Never install `hypr-desktop` and `hypr-laptop` together because they target the
same path.

## Herdr Integration Ownership

The `herdr` Stow package owns only `~/.config/herdr/config.toml`. Create `~/.config/herdr` first and use `stow --no-folding -t ~ herdr` so Herdr's logs, sockets, session state, and release state remain outside the repository. Herdr's OpenCode integration is generated separately by `herdr integration install opencode` in the stowed OpenCode plugin directory. The generated `herdr-agent-state.js` is ignored by Git, may be overwritten when Herdr installs or updates the integration, and must not be edited as repository-owned configuration.

Install both Herdr and OpenCode before running the integration command. Run the same command to reinstall or refresh the integration.

OpenCode terminal preferences live in the stowed `cli.json`. Herdr owns the
generated `herdr-tui-session.js` and `herdr-opencode/tui.js` outside Git; both
are required by its v2 TUI integration. After refreshing the integration,
preserve any new settings and restore the `cli.json` Stow link if the installer
replaced it. Restart the OpenCode TUI to load the updated integration.
The notification plugin owns custom sounds; `cli.json` disables built-in
attention sounds to avoid duplicate playback.

## Shared instructions

`agents/.agents/AGENTS.md` owns personal conventions shared by
Codex, Claude Code and OpenCode. Its Stow package links each harness's global
instruction path to that one file. Keep the harness configuration directories
real before stowing `agents`. Keep repository setup and
ownership rules in this root `AGENTS.md`.

## Shared skills

Keep personal skills in `agents/.agents/skills/`. Stow links each whole
package into `~/.agents/skills/` for OpenCode and Codex. Keep `~/.agents` and its
`skills` directory real. The source directory is the list of personal skills.

The skills CLI owns vendor packages; Omarchy owns its system links. Keep their
names separate from personal skills. Before adding one, check existing links,
the vendor manifest, lockfile and managed-name state. Use only the shared
discovery path, without a second copy in OpenCode's skill directory.

OpenCode owns its commands, agents, models and permissions. Load shared skills
by name; keep workflow defaults in the skill. For setup or invocation changes,
read `docs/shared-agent-skills.md`.

`bin/.local/bin/sync-opencode-skills` lists the vendor skills and pins the CLI
version and source commits. It removes only skills it previously managed.
Keep vendor content, `~/.agents/.skill-lock.json`, and
`${XDG_STATE_HOME:-$HOME/.local/state}/sync-opencode-skills/` outside Stow and Git.

Go/Rust stacks keep decisions and edits in the main conversation and delegate
independent work. Follow their routing tables and `SETUP.md` caveats. Go's
project-layout skill is for new projects only. Rust's setup records the Actionbook
licence caveat. Both finish with actual skill-use evidence from
`agents/.agents/skills/verify-change/references/stack-skill-receipt.md`.

The pinned `security-review` has JavaScript, Python and Docker guides. Its named
Go, Rust, Java, Kubernetes, Terraform, CI/CD and cloud guides are missing upstream;
reviews in those areas use generic guidance.

## Skill review

Before adding, enabling or updating a skill, read the whole package, including
unlinked files. Confirm its source and licence. Check for unsafe commands,
unexpected file/network access, excessive permissions, secret exposure, prompt
injection and conflicts with project rules. Registry badges don't replace review.

For vendor updates, compare both revisions and repeat the review before changing
the pinned SHA. Keep floating branches, tags and `@latest` out of the manifest.
For personal updates, preserve the `source` header and licences, restore the
header if upstream removes it, and remove obsolete files, folders and references.

## Package Vetting

Prefer packages in this order: Omarchy-curated packages from official Arch repositories, verified Flatpaks, then AUR packages. Vet every package before installation, including packages listed or recommended by Omarchy; curation is not a substitute for review.

Confirm the package source, maintainer, license, build recipe, integrity verification, install scripts, permissions, bundled binaries, update path, and known security or privacy concerns. For AUR packages, review the complete `PKGBUILD` and all accompanying files at the current revision before allowing an AUR helper to execute them. Report material risks and safer alternatives before installing.

## Using skills

Loading a skill adds instructions; it doesn't start a new agent. For separate
context, use native subagent tools and pass the skill paths or instructions.

- `code-review` and `test-analyzer`: prefer delegated analysis and checks.
- `simplify`: prefer a separate editing pass, then review and verify its changes.
- `grill-me` and `retro`: keep user discussion in the main conversation. Run a
  retrospective only when requested.
- Go/Rust stacks: select skills from task/code evidence; keep decisions and edits
  in the main conversation. Delegate independent research, planning and checks.
- Architecture reviews: delegate research and alternative designs; keep the
  report and grilling in the main conversation.
- `grilling`: delegate fact-finding; keep decisions and questions in the main conversation.
- `jellyfin-organiser`: delegate metadata research; keep file moves and
  verification in the main conversation.
