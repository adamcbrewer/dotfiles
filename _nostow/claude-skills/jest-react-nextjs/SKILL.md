---
name: jest-react-nextjs
description: Write Jest unit tests for React and Next.js applications. Use when creating test files or improving test coverage. Triggers on requests like "write tests for", "add unit tests", "test this component", or "improve test coverage".
---

# Jest Unit Tests for React & Next.js

## Philosophy

- **Brevity over verbosity** - Condense and combine related assertions where logically possible; try to avoid too granular tests
- **Key functionality first** - Prioritize critical paths and edge cases over 100% coverage
- **Type safety** - Use proper TS types; use `as` assertions only for partial mock data

## Workflow

1. **Explore patterns** - Find existing `__tests__/` directories, custom render wrappers, mock conventions
2. **Read source** - Identify key behaviors, edge cases, dependencies to mock
3. **Write tests** - Follow structure below
4. **Run tests** - Verify passing
5. **Review & optimize** - Re-read all written tests; look for duplication, overly verbose assertions, tests that can be combined, unnecessary mocks, and simplification opportunities. Refactor as needed.
6. **Verify with project tools** - Run project-specific TypeScript (`tsc --noEmit` or similar) and lint commands (check `package.json` scripts for `lint`, `typecheck`, etc.) to ensure test files are clean and error-free. Fix any issues found.

## Test Structure

```typescript
// Mocks BEFORE imports
jest.mock('dependency', () => ({ fn: jest.fn() }))

import { fn } from 'dependency'
import { Component } from '../component'

const mockFn = fn as jest.MockedFunction<typeof fn>

const makeMockItem = (overrides = {}) => ({ id: '1', ...overrides })

describe('Component', () => {
  beforeEach(() => jest.clearAllMocks())

  it('renders correctly with expected behavior', () => {
    // Combine related assertions
  })
})
```

## Condensing Tests

❌ Too granular:
```typescript
it('renders name', () => {})
it('renders link', () => {})
it('renders status', () => {})
```

✅ Condensed:
```typescript
it('renders row with name link, status, and data', () => {})
```

Use `it.each()` for symmetric behavior:
```typescript
it.each([
  { from: 'A', to: 'X', button: 'Switch to X' },
  { from: 'X', to: 'A', button: 'Switch to A' },
])('switches from $from to $to', async ({ from, to, button }) => {
  // test logic
})
```

## TypeScript Patterns

Proper mock typing:
```typescript
jest.mock('module', () => ({ fn: jest.fn() }))
import { fn } from 'module'
const mockFn = fn as jest.MockedFunction<typeof fn>
```

Partial mock data:
```typescript
mockApi.mockResolvedValue({
  items: [{ id: '1' }],
} as Awaited<ReturnType<typeof apiFunction>>)
```

Inline prop types (avoid `any`):
```typescript
// ❌ ({ children }: any)
// ✅ ({ children }: { children: React.ReactNode })
```

## Common Patterns

See [references/patterns.md](references/patterns.md) for:
- Next.js server component redirect testing
- Hook testing with `renderHook`
- External library mocking
- Render helper functions

## What NOT to Test

- Simple prop pass-through
- Third-party library internals
- Implementation details
- Already-covered behavior in parent tests

## After Writing

1. **Run tests**: `npm test -- --testPathPattern="<file>"` or project-specific test command
2. **Review & optimize**: Re-read all tests looking for:
   - Duplicate setup/assertions that can be extracted
   - Tests that can be combined (related assertions in one `it()`)
   - Overly verbose mocks or unnecessary mocking
   - Opportunities to use `it.each()` for similar test cases
   - Dead code or commented-out tests to remove
3. **Run project TS/lint checks**: Check `package.json` for scripts like `lint`, `typecheck`, `type-check`, or run:
   - `npx tsc --noEmit` (or project's typecheck script)
   - `npx eslint <file>` (or project's lint script)
   - `npx prettier --write <file>` (or project's format script)
4. **Fix all errors** before considering tests complete

Common lint fixes:
- `no-explicit-any` → Use proper types or `unknown`
- `no-require-imports` → Use ES imports after `jest.mock()`
- `simple-import-sort` → Run `--fix`
