---
name: verify
description: Run all verification checks before committing or pushing. Use when the user asks to "verify", "check everything", "run all tests", or before committing/pushing code. Runs prettier, lint, unit tests, build, and e2e tests in sequence, stopping on first failure.
---

# Verify

## Skills

Review the code as per the user's instructions, be that a PR or, by default if no instructions, the current branch against the primary branch for the project.

Run any/all of the skills below in subagents. Keep track of progress and exec order in order to address feedback If any questions or actions are required by the user. Do not make assumptions if a review or suggestions functionality changes the implementation.

- Always run the code simplify skill after edits are done
- If meaningful react files have changed run the `react-best-practices` skill
- If meaningful next files have changed run the `next-best-practices` skill
- If meaningful test files have changed or new tests added run the `test-analyzer` skill
- If a meaningful amount of file have changes overall run the `code-review` skill. This should be the final skill run once all other skill and skill subagents have completed and any change suggesations have been implemented.

## CI Checks

Run these checks only once no more changes are required and all subagent skills have finished. Run these in order, stopping on first failure.

Checks will differ between projects. Only run if a suitable script or check exists which are relevant to the files changed.

### Execution Order

1. prettier
2. lint - Static analysis (0 errors required, warnings OK)
3. unit tests
4. build

### Behavior

- Stop immediately on any failure
- Report which step failed
- On success, confirm all checks passed

## Output

Always report which skills and CI checks were run when all tasks have finished.
