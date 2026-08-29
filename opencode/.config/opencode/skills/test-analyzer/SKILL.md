---
name: test-analyzer
description: Analyze test failures, coverage gaps, and test quality. Use when the user asks to analyze or review tests, debug failing tests, or check test edge cases.
---

Analyze tests using the repository's framework, conventions, and available commands.

## Core Responsibilities

1. **Comprehensive Test Analysis**: Examine existing tests for coverage gaps, edge cases, and quality issues
2. **Failure Investigation**: When tests fail, systematically investigate recent changes to identify root causes
3. **Edge Case Discovery**: Identify and test boundary conditions, error states, and unexpected inputs
4. **Test Quality Enhancement**: Suggest improvements for test structure, readability, and maintainability
5. **Change Impact Assessment**: Analyze how recent code changes affect test validity and coverage

## Investigation Methodology

When tests are failing:

- First examine the failing test output and error messages
- Review recent changes to the tested functions/components
- Compare current implementation with test expectations
- Identify if tests need updating or if code introduced bugs
- Highlight non-trivial changes that require attention
- Provide clear recommendations on whether to fix code or update tests

## Edge Case Coverage

Consider these when relevant to the behavior under test:

- Null/undefined inputs
- Empty arrays/objects
- Boundary values (min/max)
- Network failures and timeouts
- Permission/authentication edge cases
- Race conditions and async edge cases
- Invalid data formats
- Error states and exception handling

## Test Quality Standards

- Use descriptive test names that explain the scenario
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies appropriately
- Test behavior, not implementation details
- Ensure tests are isolated and deterministic
- Use appropriate matchers for clear assertions

## Analysis Output Format

1. **Test Status Summary**: Overview of current test state
2. **Failure Analysis**: Detailed investigation of any failing tests
3. **Recent Changes Impact**: Summary of how recent code changes affect tests
4. **Edge Cases Assessment**: Identified gaps in edge case coverage
5. **Improvement Recommendations**: Specific suggestions for enhancement
6. **Priority Actions**: What should be addressed first

## Project Context Awareness

- Discover the test framework, commands, file layout, and conventions from the repository
- Respect existing mock patterns and test structure
- Follow the project's formatting and type-safety rules
- Put tests where the repository's existing conventions require

Provide specific recommendations tied to observed behavior and repository evidence.
