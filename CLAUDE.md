# CLAUDE global context

## General

- Always exclude node_modules for searching and indexing

## Git

This applies to all git operations, especially commits.

### Commits

#### Commit messages

##### Subject line (first line)

- 50 characters max length
- Pluralise verb (adds, fixes, improves, removes, changes, etc.)
- Be specific and descriptive

##### Body (optional)

- Leave a blank line between the subject and the body
- Explain what and why vs. how
- Never include claude code attribution to any commit messages
- Append 🤖 to the end of the message on a newline with a space above.


##### Commit message examples

```
Adds login form
```

```
Fixes api endpoints

Api endpoint misspelled and response was not parsed as json
```

```
Fixes date utils function

Undefined/null dates were not being parsed correctly and tests cases weren't covered for these cases.
```

## Style Guidelines

- Always avoid comments for lower level functions.
- Include comments for higher level functions which perform more than 3 tasks/functions. Keep comments simple.
- Don't use JSDoc style function header comments
- Add comments when code clarity is insufficient or to explain non-standard solutions (like using any) or hard to read / understand code sections
- Files/Components: PascalCase for components, camelCase for utils/hooks
- Types: Strict typing, descriptive generics, no implicit any unless a typoe cannot be easily inferred, named prop interfaces
- Type Naming: Function types use FunctionNameArgs, class options use ClassNameOptions, hook args use UseHookNameArgs, React component props use ComponentNameProps
- ALWAYS respect how things are written in the existing project
- DO NOT invent your own approaches or innovations
- STRICTLY follow the existing style of tests, resolvers, functions, and arguments
- Before creating a new file, ALWAYS examine a similar file and follow its style exactly
- If code doesn't include comments, DO NOT add comments unless otherwise asked to do so.
- Follow the exact format of error handling, variable naming, and code organization used in similar files
- if a project has any kind of prettier config  file always run prettier formatting for changed files.

## Permissions

- If user modifies a file between reads, assume the change is intentional
- Always use flamboyant emojis. More emojis the better.
- Always keep the tone of Claude Code friendly, casual
- Favour sarcasm and being funny over being serious or formal


## MCP

### Playwright
When taking screenshots with Playwright copy the screenshot to `~/Pictures/Screenshots/<filename>.<ext>`. Prefix the filename with YYYY-MM-DDTHH:MM:SS timestamp.  Do not try to create the directory.

When using playwright, always clode the browser once the task or screenshot has finished.
