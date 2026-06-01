# Security

## Node Supply Chain

User-level defaults live in the `node` stow package:

```sh
stow -t ~ node
```

These defaults are intentionally conservative:

- npm: disable lifecycle scripts. Release-age and git-dependency blocking are documented below, but are not enabled by default because npm 11.6.1 warns that those config keys are unknown.
- pnpm: disable lifecycle scripts and avoid versions published in the last 7 days.
- Yarn v1: disable lifecycle scripts.

If `stow -t ~ node` conflicts with existing files, move them aside and manually copy only safe settings into this repo. Avoid `stow --adopt` for package-manager configs because it can accidentally import registry tokens.

## Project Defaults

For pnpm projects, add these settings to `pnpm-workspace.yaml` and adjust `allowBuilds` per project:

```yaml
minimumReleaseAge: 10080
trustPolicy: no-downgrade
strictDepBuilds: true
blockExoticSubdeps: true

allowBuilds:
  esbuild: true
  sharp: true
  rolldown: true
  unrs-resolver: true
```

Only allow build scripts after reviewing why the package needs them. Common legitimate examples are native packages or bundler binaries such as `esbuild`, `sharp`, `rolldown`, and `unrs-resolver`.

For npm projects, prefer deterministic installs in automation:

```sh
npm ci
```

When your installed npm supports these keys, add them to the project or user `.npmrc`:

```ini
min-release-age=7
allow-git=none
```

For pnpm projects:

```sh
pnpm install --frozen-lockfile
```

For Yarn v1 projects:

```sh
yarn install --frozen-lockfile
```

For Yarn modern projects:

```sh
yarn install --immutable
```

## Ad-hoc Installs

Use explicit hardened install commands when trying new packages:

```sh
npqi express
npqp fastify
pnpmf
```

The aliases are intentionally explicit instead of replacing `npm`, `pnpm`, or `yarn`, so scripts and existing workflows keep normal package-manager behavior.

## New Dependencies

Before adopting a new package:

- Prefer packages with a small dependency tree.
- Check package health in Snyk, Socket, npm provenance, or another package security tool.
- Avoid unpinned `npx` execution for tools that access the filesystem or secrets.
- Prefer pre-installed, lockfile-backed tools for MCP servers and agent integrations.
- Use scoped private package names and per-scope registry config to avoid dependency confusion.
