# CLAUDE global context

## Conversation tone and style

- Be extremely concise. Sacrifice grammar for the sake of concision.
- Keep your tone casual and friendly.
- Don't be obsequious or pandering.
- Correct me if I'm wrong and highlight when I'm contradicting myself or making an obvious error.
- Questions, suggestions and insights are encouraged.
- Emojies are welcome.


## Git

- NEVER commit unless requested to do so.
- Subject line: concise and specific
- Description: blank line after subject, explain what/why not how

**Branch naming:** `feat/`, `fix/`, `chore/` prefixes. Include issue number if exists (e.g., `feat/123-dark-mode`).


## Hard Guidence

- Important: Avoid adding comments unless otherwise specified or when code clarity is insufficient or to explain non-standard solutions (like using any) or hard to read / understand code sections. If code doesn't include comments, DO NOT add comments unless otherwise asked to do so.
- Files/Components: PascalCase for components, camelCase for utils/hooks
- Types: Strict typing, descriptive generics, no implicit any unless a type cannot be easily inferred, named prop interfaces
- ALWAYS respect how things are written in the existing project
- STRICTLY follow the existing style of tests, resolvers, functions, and arguments
- Before creating a new file, ALWAYS examine a similar file and follow its style.
- Follow the exact format of error handling, variable naming, and code organization used in similar files


## Plan Mode

- Make the plan extremely concise. Sacrifice grammar for the sake of concision.
- At the end of each plan, give me a list of unresolved questions to answer, if any.
