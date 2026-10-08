# Browser automation

## Preflight once

Before loading a browser workflow or interacting with a page, check the runner:

```bash
command -v agent-browser
agent-browser --version
```

If usable, load `agent-browser` and its version-matched core instructions. Use a
named session for this task. On this machine, the first launch can use the existing
Brave executable, with `URL` set to the user's requested URL:

```bash
SESSION="$(agent-browser session id --scope worktree --prefix task)"
agent-browser --session "$SESSION" --executable-path /usr/bin/brave open "$URL"
```

Pass the same session on subsequent commands. Confirm navigation works before
planning further actions, and close that session when finished.

If the CLI is missing or fails, inspect available browser tools and existing
project-installed Playwright packages. Select a working route and report the
fallback briefly. Check CLI wrappers before invoking them: some provision tools
or change global tool selection on every call. Use a preinstalled pinned runner
where available. Restore/install a missing dependency only as authorised work.

**Done:** a runner and browser session work, or a concrete blocker is reported.

## Keep interactions targeted

- Check the active URL before DOM measurements or actions; explicitly navigate
  when the page is stale or blank.
- Wait for the required rendered state instead of a fixed short sleep.
- Keep bulk export/font/layout verification in an existing local Node/Playwright
  script when an embedded runner cannot import modules or complete the batch.
- Retry unavailable hosts or runners after an observed state change. Preserve
  useful results and local captures when one route fails.

## Check upload capability separately

CLI authentication and browser sign-in are different states. Before a requested
attachment upload, verify the browser's actual authenticated upload route. Report
whether evidence is captured, uploaded and embedded. If upload is unavailable,
retain exact local paths and captions and mark it pending in the handoff.

## Local CLI installation

`~/.local/bin/agent-browser` uses the exact package version in
`~/.local/share/opencode-browser-tools/package.json` and its lockfile. Restore it
with `npm ci --ignore-scripts` in that directory. The package includes its native
CLI; browser selection is checked separately from package installation.

## Tidy up

Always close down sessons and browsers you've finished working with.

This setup uses version pinning, lockfile resolution and disabled lifecycle scripts
from [npm security best practices](https://github.com/lirantal/npm-security-best-practices).
