# Node Supply-Chain Security

These defaults follow [npm Security Best Practices](https://github.com/lirantal/npm-security-best-practices). Consult and cite that reference when changing security settings or documenting Node installation and setup.

## User Defaults

The `node` Stow package installs conservative defaults for every local project:

```sh
stow -t ~ node
```

- npm disables lifecycle scripts, blocks Git dependencies, and delays new releases for 30 days.
- pnpm delays new releases for 30 days, rejects reduced package trust, fails on unapproved dependency builds, and blocks exotic transitive dependencies.
- Yarn v1 disables lifecycle scripts. Yarn v1 has no release-age setting.

pnpm 10 already blocks dependency lifecycle scripts by default. The `~/.local/bin/pnpm` wrapper overrides npm's inherited `ignore-scripts=true`; otherwise pnpm would also block project scripts and prevent project `allowBuilds` approvals from working. The wrapper delegates version selection to Corepack.

Projects can override user defaults when a reviewed dependency or urgent security fix requires an exception. If Stow reports conflicts, move existing package-manager config files aside and preserve authentication tokens outside this repository. Do not use `stow --adopt` on token-bearing config files.

## Project Policy

Commit security policy to each project so CI and other contributors use it too. For pnpm projects, use `pnpm-workspace.yaml`:

```yaml
minimumReleaseAge: 43200
trustPolicy: no-downgrade
strictDepBuilds: true
blockExoticSubdeps: true

allowBuilds:
  esbuild: true
```

Treat `allowBuilds` as a reviewed exception list, not a standard package list. Pin an allowed package version when practical.

Use deterministic installs in automation:

```sh
npm ci
pnpm install --frozen-lockfile
yarn install --frozen-lockfile # Yarn v1
yarn install --immutable --immutable-cache # Modern Yarn
bun install --frozen-lockfile
```

Commit the lockfile. npm and Yarn projects that accept external contributions should also validate lockfile hosts and HTTPS with a project dependency such as `lockfile-lint`.

For private packages, use scoped names and commit only the scope-to-registry mapping. Keep registry tokens in user config or injected environment variables.

## Ad-Hoc Installs

The Fish config provides explicit hardened commands:

```sh
npqi express
npqp fastify
pnpmf
```

`npq` and Socket Firewall (`sfw`) are optional pre-install checks. Their direct forms are `npq install <package>` and `sfw <package-manager> install <package>`.

Do not run unpinned `npx` commands that can access files or secrets. Prefer a reviewed, lockfile-backed local dependency. For unattended tools such as MCP servers, use a pre-installed workspace and run `npx` with `--no --offline`.

## Dependency Review

Before adopting or upgrading a package:

- Review dependency and lockfile changes instead of applying blind upgrades.
- Prefer a small dependency tree and maintained packages.
- Check Snyk, Socket, provenance, signatures, and published tarball contents.
- Use a cooldown exception only after reviewing an urgent security fix.
- Use OIDC trusted publishing, 2FA, and provenance when maintaining npm packages.
- Keep secrets out of committed files and avoid exposing host secrets to dependency scripts.
