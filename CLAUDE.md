# CLAUDE global context

## Git best practices

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
