# Common Test Patterns

## Table of Contents
- [Next.js Server Component Redirects](#nextjs-server-component-redirects)
- [Hook Testing](#hook-testing)
- [MUI/External Library Mocking](#muiexternal-library-mocking)
- [Render Helper Functions](#render-helper-functions)
- [Context Provider Mocking](#context-provider-mocking)
- [Factory Functions for Mock Data](#factory-functions-for-mock-data)

## Next.js Server Component Redirects

Next.js `redirect()` throws internally. Simulate this in tests:

```typescript
const mockRedirect = jest.fn()

jest.mock('next/navigation', () => ({
  redirect: (...args: unknown[]) => mockRedirect(...args),
}))

// In test - redirect throws, component should reject
it('redirects on error', async () => {
  mockApi.mockRejectedValue(new Error('Not found'))
  mockRedirect.mockImplementation(() => {
    throw new Error('NEXT_REDIRECT')
  })

  await expect(ServerComponent({ params })).rejects.toThrow('NEXT_REDIRECT')
  expect(mockRedirect).toHaveBeenCalledWith('/not-found')
})
```

## Hook Testing

```typescript
import { renderHook, act } from '@testing-library/react'
import { useCustomHook } from '../use-custom-hook'

it('updates state correctly', () => {
  const { result } = renderHook(() => useCustomHook())

  act(() => {
    result.current.doSomething()
  })

  expect(result.current.value).toBe('expected')
})
```

With wrapper for context:
```typescript
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <Provider value={mockValue}>{children}</Provider>
)

const { result } = renderHook(() => useHook(), { wrapper })
```

## MUI/External Library Mocking

```typescript
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  useTheme: jest.fn(() => ({
    breakpoints: { down: jest.fn(() => '(max-width: 768px)') },
  })),
  useMediaQuery: jest.fn(() => false),
}))

const mockUseMediaQuery = useMediaQuery as jest.MockedFunction<typeof useMediaQuery>

beforeEach(() => {
  mockUseMediaQuery.mockReturnValue(false) // desktop
})

it('renders mobile view', () => {
  mockUseMediaQuery.mockReturnValue(true)
  // test mobile behavior
})
```

## Render Helper Functions

Extract repeated render logic:

```typescript
const renderComponent = (overrides = {}) =>
  render(
    <Component
      defaultProp="value"
      requiredProp="required"
      {...overrides}
    />,
  )

it('handles case A', () => {
  renderComponent({ propA: 'a' })
})

it('handles case B', () => {
  renderComponent({ propB: 'b' })
})
```

With user events (from custom render):
```typescript
const renderWithUser = (props = {}) => {
  const result = render(<Component {...props} />)
  return { ...result, user: userEvent.setup() }
}

it('handles click', async () => {
  const { user } = renderWithUser()
  await user.click(screen.getByRole('button'))
})
```

## Context Provider Mocking

Mock context hooks while preserving other exports:

```typescript
jest.mock('@/components', () => {
  const actual = jest.requireActual('@/components')
  return {
    ...actual,
    useAppContext: () => ({
      user: { id: '1', name: 'Test User' },
      settings: { theme: 'light' },
    }),
  }
})
```

Or mock the provider wrapper:
```typescript
jest.mock('@/providers/auth', () => ({
  useAuth: () => ({ isAuthenticated: true, user: mockUser }),
}))
```

## Factory Functions for Mock Data

Keep mock data DRY with factory functions:

```typescript
const makeMockUser = (overrides = {}) => ({
  id: '1',
  name: 'John Doe',
  email: 'john@example.com',
  status: 'active',
  ...overrides,
})

const makeMockFirm = (name: string, code = 'F1') => ({
  personCode: code,
  name,
  type: 'FIRM',
})

// Usage
const users = [
  makeMockUser({ id: '1', name: 'Alice' }),
  makeMockUser({ id: '2', name: 'Bob', status: 'inactive' }),
]

const firms = [
  makeMockFirm('Alpha Corp', 'F1'),
  makeMockFirm('Beta Inc', 'F2'),
]
```
