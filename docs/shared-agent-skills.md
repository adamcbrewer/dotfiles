# Shared agent skills

I keep my skills in `agents/.agents/skills/`. Stow links them into
`~/.agents/skills/`, so Codex and OpenCode use the same files.

## Set up

From this repo:

```sh
mkdir -p ~/.agents/skills ~/.codex ~/.claude ~/.config/opencode
stow --simulate --verbose=2 -t ~ agents
stow -t ~ agents
```

Keep `~/.agents` and `~/.agents/skills` as real directories. Check for clashes
with vendor and Omarchy skill names before adding one.

## Use a skill

- Codex: `$<skill-name> <request>`, or select it from `/skills`.
- OpenCode v2: `@<skill-id> <request>`, or use its `/command` if it has one.

OpenCode commands, agents and settings stay in `opencode/.config/opencode/`.
The skill holds the workflow; commands and agents just load it.

For Rust or Go implementation, review, debugging, planning or explanation, the
agent loads `rust-stack` or `go-stack` first. The stack selects supporting skills,
coordinates the work, verifies it and reports actual skill use. Loading an
individual Rust/Go skill alone does not run the stack.

Ordinary requests such as "fix this Rust borrow error" or "review this Go handler"
can select the matching stack. To choose it directly, use `$rust-stack` / `$go-stack`
in Codex or `@rust-stack` / `@go-stack` in OpenCode. The OpenCode `/rust-stack` and
`/go-stack` wrappers have been removed; no wrapper is needed for skill mentions.

Claude Code uses `~/.claude/skills/` for personal discovery. This Stow package shares
its global instructions, but does not link the shared skill catalog there. Only
Omarchy's `omarchy` and `diagnose-crash` links currently exist there. Reading a skill
by its shared path is different from registering it for automatic discovery or
`/skill-name` invocation.

See the official [Codex](https://learn.chatgpt.com/docs/build-skills),
[OpenCode v2](https://opencode.ai/v2/docs/skills/) and
[Claude Code](https://code.claude.com/docs/en/skills) discovery rules.

## Invocation list

- **Eligible:** the agent can select it when the task matches its description.
- **On request:** ordinary wording requesting that activity is enough; naming the
  skill or using a command is optional. The agent should not initiate the activity.
- **Explicit-only:** select the skill directly, using `$name` in Codex or `@name`
  in OpenCode. These skills are omitted from the model's automatic-selection list.

Eligible and on-request skills both allow model invocation; on-request limits
live in their descriptions and instructions. Eligibility is permission to select
a skill, not proof it ran. Eligible and on-request skills accept a prose request.
Explicit-only skills require the harness's skill picker, registered mention or
command; a plain-text name does not activate them.

This list covers the shared personal, pinned vendor and Omarchy skills. Built-in
and plugin skills have their own catalogs and policies.

| Skill | Invocation | Matching task |
| --- | --- | --- |
| `agent-browser` | Eligible | Browser interaction and app testing |
| `author-git-content` | Eligible | Commit, PR, issue and comment wording |
| `code-review` | Eligible | Branch/local or explicit-target review; assigned review step; before merging |
| `diagnose-crash` | Eligible | Local application crashes |
| `diff-explainer` | Explicit-only | Explain a diff or PR as semantic chapters |
| `domain-web` | Eligible | Rust web services, selected by `rust-stack` |
| `frontend-design` | Eligible | Build or reshape a UI |
| `go-stack` | Eligible | Entry point for Go work; selects supporting skills |
| `golang-code-style` | Eligible | Go source style and clarity |
| `golang-concurrency` | Eligible | Go goroutines, channels and shared state |
| `golang-database` | Eligible | Go database access |
| `golang-error-handling` | Eligible | Go errors and logging |
| `golang-modernize` | Eligible | Go modernization and upgrades |
| `golang-observability` | Eligible | Go metrics, tracing and production logs |
| `golang-performance` | Eligible | Go optimization with evidence |
| `golang-project-layout` | Eligible | New Go projects only, per repository rules |
| `golang-security` | Eligible | Go security and trust boundaries |
| `golang-testing` | Eligible | Write or review Go tests |
| `grill-me` | On request | Asked to be grilled or interviewed; loads `grilling` |
| `grilling` | Eligible | Stress-test an idea or plan |
| `improve-codebase-architecture` | On request | Requested architecture review |
| `jellyfin-organiser` | Eligible | Organize Jellyfin media |
| `m05-type-driven` | Eligible | Rust types enforcing an invariant |
| `m14-mental-model` | Eligible | Teach Rust concepts and ownership |
| `my-voice` | On request | Requested writing in Adam's voice |
| `next-best-practices` | Eligible | Next.js implementation and review |
| `omarchy` | Eligible | Linux desktop and Omarchy customization |
| `agent-session-review` | Explicit-only | Select the skill or command to review Codex/OpenCode sessions |
| `redesign-from-first-principles` | On request | Requested first-principles redesign or rethink |
| `retro` | Explicit-only | Session retrospective |
| `review-completeness` | Eligible | Feature outcomes and missing changes across components |
| `review-failure-paths` | Eligible | Errors, retries and fallbacks that hide failure |
| `review-findings` | Eligible | Validate supplied suspected bugs |
| `review-security-history` | Eligible | Changed safeguards and security regressions in local history |
| `review-stack` | On request | Review branch or feature changes with automatic specialist selection |
| `rust-best-practices` | Eligible | Substantive Rust source work |
| `rust-patterns` | Eligible | Rust ownership, errors, traits and concurrency |
| `rust-stack` | Eligible | Entry point for Rust work; selects supporting skills |
| `rust-testing` | Eligible | Write or review Rust tests |
| `security-review` | Eligible | Requested security audit or review |
| `simplify` | On request | Requested cleanup or assigned simplification pass |
| `test-analyzer` | Eligible | Requested test analysis or failure diagnosis |
| `unslop` | On request | Requested prose polishing or humanizing |
| `vercel-react-best-practices` | Eligible | React and Next.js performance |
| `verify-change` | Eligible | Requested verification or a verification stage |
| `wat` | Eligible | Confusion about the last reply or a simpler explanation |
| `web-design-guidelines` | Eligible | Requested UI, UX or accessibility review |
| `writing-for-agents` | Eligible | Write skills or agent instructions |

The language stacks choose only the supporting skills justified by the task.
In Claude Code, `user-invocable: false` hides the direct command while keeping
model selection available. The vendor skills `domain-web`, `m05-type-driven`,
`m14-mental-model` and `next-best-practices` use this field. It does not make them
explicit-only in Codex or OpenCode.

## Keep them up to date

- Edit my skills here, including supporting files. Keep their source and licence.
- Stow shares those edits with both tools. There's no separate sync step.
- `sync-opencode-skills` restores reviewed, pinned vendor skills. Keep vendor files and their install state outside Git.
- The sync script overrides `grill-me`'s description and invocation flags in the
  pinned checkout before installation, preserving its on-request mode on refresh.
  Its two-file alias package and repository MIT license were reviewed at
  `f6abdeb8dd2a9be64f924ab44c7af374cb76726d`; its workflow still loads `grilling`.
- Restart OpenCode and refresh provider status in T3 after changes.

## Explicit-only skills

- Codex: set `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.
- OpenCode v2 and Claude Code: set `disable-model-invocation: true` in `SKILL.md`.

Use both switches for shared explicit-only skills. For eligible or on-request
skills, allow Codex invocation and omit `disable-model-invocation`; keep their
descriptions and opening instructions consistent with the intended trigger.

## Quick check

In OpenCode v2, use `@<skill-id>` to load a skill explicitly and
`opencode api GET /api/command` to list available commands. Use `/skills` in
Codex. Check from this repo and another directory: each skill should appear
once, its references should work, and an explicit request should load it. For
each language stack, also try a matching task without naming the skill and confirm
the agent announces the stack and finishes its skill-use report. A task in another
language should not select either stack.

See the [GitHub diff-explainer experiment](github-diff-explainer.md) for PR mentions.
Setup follows [npm security best practices](https://github.com/lirantal/npm-security-best-practices).
