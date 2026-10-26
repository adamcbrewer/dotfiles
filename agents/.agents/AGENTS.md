## Conventions

- Be concise in planning and output. Use plain English by default; explain necessary technical terms.
- Answer questions directly before making changes. Lead with the outcome; use a concrete example when it helps.
- Keep your tone casual and friendly. Don't be obsequious or pandering.
- If asked to reclarify or explain in more detail explain it to me like I'm a junior in this area.
- Correct me if I'm wrong and highlight when I'm contradicting myself or making an obvious error.
- Questions, suggestions, emojies and insights are encouraged.
- Prefer SVG images for diagrams such as data flows, state machines, dependency graphs, processing pipelines, and decision trees. Use ASCII diagrams only when the output format is restricted to text.
- Important: Avoid adding comments unless otherwise specified or when code clarity is insufficient or to explain non-standard solutions (like using any) or hard to read / understand code sections. 

- Browser automation: follow [browser preflight](~/.agents/skills/verify-change/references/browser-automation.md) before choosing a runner, measuring a page, or uploading evidence.

## Shared Skills

- Repository-owned skills live under `~/.agents/skills/`. Load permitted skills by name; resolve supporting paths from the loaded skill's directory.
- For Rust or Go implementation, review, debugging, planning or explanation, load `rust-stack` or `go-stack` first. Each stack selects its supporting skills.

## Git

- Before drafting, revising, or posting a commit message, PR, issue, or comment on an external service, load and follow the `author-git-content` skill, even when the writing arises during other work.
- Subject line: concise and specific
- Description: blank line after subject, explain what/why not how
- Branch naming: `feat/`, `fix/`, `chore/` prefixes. Include issue number if exists (e.g., `feat/123-dark-mode`).
- Ensure commits include any tickets referenced or resolved by an implementation.

## Security

- When changing security settings or documenting new installs and setup, consult and cite https://github.com/lirantal/npm-security-best-practices.


## Behavioral guidelines

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

- No features beyond what was asked.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.
