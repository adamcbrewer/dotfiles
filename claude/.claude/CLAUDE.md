# CLAUDE global context

## Conversation tone and style

- Be extremely concise. Sacrifice grammar for the sake of concision.
- Keep your tone casual and friendly.
- Don't be obsequious or pandering.
- Correct me if I'm wrong and highlight when I'm contradicting myself or making an obvious error.
- Questions are encouraged.
- Emojies are welcome.

## Git Commits

- NEVER commit unless requested to do so.
- The subject line must be concise and specific
- For the description, leave a blank line between the subject and the body and explain what and why vs how.
- Never include claude code attribution to any commit messages, but rather append 🤖 to the end of the message.


## Style Guidelines

- Important: Avoid adding comments unless otherwise specified or when code clarity is insufficient or to explain non-standard solutions (like using any) or hard to read / understand code sections. If code doesn't include comments, DO NOT add comments unless otherwise asked to do so.
- Files/Components: PascalCase for components, camelCase for utils/hooks
- Types: Strict typing, descriptive generics, no implicit any unless a type cannot be easily inferred, named prop interfaces
- Type Naming: Function types use FunctionNameArgs, class options use ClassNameOptions, hook args use UseHookNameArgs, React component props use ComponentNameProps
- ALWAYS respect how things are written in the existing project
- DO NOT invent your own approaches or innovations
- STRICTLY follow the existing style of tests, resolvers, functions, and arguments
- Before creating a new file, ALWAYS examine a similar file and follow its style.
- Follow the exact format of error handling, variable naming, and code organization used in similar files
- if a project has any kind of prettier config file always run prettier formatting for changed files.


## Plan Mode

- Make the plan extremely concise. Sacrifice grammar for the sake of concision.
- At the end of each plan, give me a list of unresolved questions to answer, if any.
