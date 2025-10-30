# React Testing Library Guide

**Testing Philosophy**: Test user behavior, not implementation details.

React Testing Library encourages writing tests that resemble how users interact with your application.

---

## Core Principles

### 1. Test User Behavior, Not Implementation

**Good**:
- User clicks button → modal opens
- User types in search → results appear
- User submits form → success message shows

**Bad**:
- Component state changes
- Internal function called
- Props passed correctly

**Why**: Tests should fail when behavior breaks, not when refactoring.

---

### 2. Query Priorities

Use queries in this order (most to least accessible):

**1. getByRole** (BEST):
```jsx
// ✅ Best: Semantic and accessible
screen.getByRole('button', { name: 'Submit' })
screen.getByRole('textbox', { name: 'Email' })
screen.getByRole('heading', { name: 'Welcome' })
```

**2. getByLabelText** (Forms):
```jsx
// ✅ Good: For form inputs
screen.getByLabelText('Email Address')
screen.getByLabelText('Password')
```

**3. getByPlaceholderText** (Last resort for forms):
```jsx
// ⚠️ OK: When no label available
screen.getByPlaceholderText('Enter your email')
```

**4. getByText** (Non-interactive elements):
```jsx
// ✅ Good: For text content
screen.getByText('Welcome back!')
screen.getByText(/error occurred/i)
```

**5. getByDisplayValue** (Current form values):
```jsx
// ✅ Good: For checking form state
screen.getByDisplayValue('john@example.com')
```

**6. getByAltText** (Images):
```jsx
// ✅ Good: For images
screen.getByAltText('User profile picture')
```

**7. getByTitle** (Tooltips):
```jsx
// ⚠️ OK: For title attributes
screen.getByTitle('Close')
```

**8. getByTestId** (AVOID):
```jsx
// ❌ Last resort: Not visible to users
screen.getByTestId('submit-button')
```

**Why**: Higher priority queries test accessibility automatically.

---

## Basic Setup

### Install Dependencies

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### Setup File (setupTests.js)

```js
// Import jest-dom matchers
import '@testing-library/jest-dom'

// Example: Global test setup
beforeEach(() => {
  // Reset mocks, clear localStorage, etc.
})
```

---

## Basic Test Structure

### Simple Component Test

```jsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Button from './Button'

test('renders button with text', () => {
  render(<Button>Click me</Button>)

  const button = screen.getByRole('button', { name: 'Click me' })
  expect(button).toBeInTheDocument()
})

test('calls onClick when clicked', async () => {
  const user = userEvent.setup()
  const handleClick = jest.fn()

  render(<Button onClick={handleClick}>Click me</Button>)

  const button = screen.getByRole('button', { name: 'Click me' })
  await user.click(button)

  expect(handleClick).toHaveBeenCalledTimes(1)
})
```

---

## Query Variants

### getBy vs queryBy vs findBy

**getBy**: Element MUST exist (throws error if not found)
```jsx
// Throws if not found
const button = screen.getByRole('button')
```

**queryBy**: Element MAY NOT exist (returns null if not found)
```jsx
// Returns null if not found (good for asserting absence)
const button = screen.queryByRole('button')
expect(button).not.toBeInTheDocument()
```

**findBy**: Element WILL APPEAR (async, waits up to 1000ms)
```jsx
// Waits for element to appear
const button = await screen.findByRole('button')
```

### getAllBy vs queryAllBy vs findAllBy

Same concept, but returns array:
```jsx
const buttons = screen.getAllByRole('button')  // Must exist
const buttons = screen.queryAllByRole('button')  // May not exist
const buttons = await screen.findAllByRole('button')  // Will appear
```

---

## Common Patterns

### Form Testing

```jsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginForm from './LoginForm'

test('submits form with user credentials', async () => {
  const user = userEvent.setup()
  const handleSubmit = jest.fn()

  render(<LoginForm onSubmit={handleSubmit} />)

  // Fill out form
  await user.type(screen.getByLabelText('Email'), 'user@example.com')
  await user.type(screen.getByLabelText('Password'), 'password123')

  // Submit
  await user.click(screen.getByRole('button', { name: 'Login' }))

  // Assert
  expect(handleSubmit).toHaveBeenCalledWith({
    email: 'user@example.com',
    password: 'password123'
  })
})

test('shows error when email is invalid', async () => {
  const user = userEvent.setup()

  render(<LoginForm />)

  await user.type(screen.getByLabelText('Email'), 'invalid-email')
  await user.click(screen.getByRole('button', { name: 'Login' }))

  expect(screen.getByText(/valid email/i)).toBeInTheDocument()
})
```

---

### Async Data Fetching

```jsx
import { render, screen, waitFor } from '@testing-library/react'
import UserProfile from './UserProfile'

test('displays user profile after loading', async () => {
  // Mock API
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve({ name: 'John Doe', email: 'john@example.com' })
    })
  )

  render(<UserProfile userId="123" />)

  // Initially shows loading
  expect(screen.getByText(/loading/i)).toBeInTheDocument()

  // Wait for data to load
  const name = await screen.findByText('John Doe')
  expect(name).toBeInTheDocument()

  const email = await screen.findByText('john@example.com')
  expect(email).toBeInTheDocument()
})

test('shows error when fetch fails', async () => {
  global.fetch = jest.fn(() => Promise.reject(new Error('Failed to fetch')))

  render(<UserProfile userId="123" />)

  const error = await screen.findByText(/error occurred/i)
  expect(error).toBeInTheDocument()
})
```

---

### Modal Testing

```jsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Modal from './Modal'

test('opens modal when button clicked', async () => {
  const user = userEvent.setup()

  render(
    <div>
      <button>Open Modal</button>
      <Modal />
    </div>
  )

  // Modal not visible initially
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

  // Click button
  await user.click(screen.getByRole('button', { name: 'Open Modal' }))

  // Modal now visible
  expect(screen.getByRole('dialog')).toBeInTheDocument()
})

test('closes modal when close button clicked', async () => {
  const user = userEvent.setup()

  render(<Modal isOpen={true} onClose={jest.fn()} />)

  expect(screen.getByRole('dialog')).toBeInTheDocument()

  await user.click(screen.getByRole('button', { name: 'Close' }))

  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
})

test('closes modal when escape key pressed', async () => {
  const user = userEvent.setup()
  const handleClose = jest.fn()

  render(<Modal isOpen={true} onClose={handleClose} />)

  await user.keyboard('{Escape}')

  expect(handleClose).toHaveBeenCalled()
})
```

---

### List/Table Testing

```jsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UserTable from './UserTable'

test('renders all users', () => {
  const users = [
    { id: 1, name: 'Alice', email: 'alice@example.com' },
    { id: 2, name: 'Bob', email: 'bob@example.com' }
  ]

  render(<UserTable users={users} />)

  expect(screen.getByText('Alice')).toBeInTheDocument()
  expect(screen.getByText('Bob')).toBeInTheDocument()
})

test('sorts users when column header clicked', async () => {
  const user = userEvent.setup()
  const users = [
    { id: 1, name: 'Bob', email: 'bob@example.com' },
    { id: 2, name: 'Alice', email: 'alice@example.com' }
  ]

  render(<UserTable users={users} />)

  // Click "Name" column header to sort
  await user.click(screen.getByRole('button', { name: 'Name' }))

  const rows = screen.getAllByRole('row')
  expect(rows[1]).toHaveTextContent('Alice')  // First row (after header)
  expect(rows[2]).toHaveTextContent('Bob')
})
```

---

## Mocking

### Mocking Functions

```jsx
test('calls onDelete when delete button clicked', async () => {
  const user = userEvent.setup()
  const handleDelete = jest.fn()

  render(<Item id="123" onDelete={handleDelete} />)

  await user.click(screen.getByRole('button', { name: 'Delete' }))

  expect(handleDelete).toHaveBeenCalledWith('123')
})
```

---

### Mocking API Calls

**Option 1: Mock fetch globally**
```jsx
beforeEach(() => {
  global.fetch = jest.fn()
})

test('fetches user data', async () => {
  global.fetch.mockResolvedValueOnce({
    json: async () => ({ name: 'John' })
  })

  render(<UserProfile userId="123" />)

  expect(await screen.findByText('John')).toBeInTheDocument()
})
```

**Option 2: Use MSW (Mock Service Worker) - Recommended**
```jsx
import { rest } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  rest.get('/api/users/:id', (req, res, ctx) => {
    return res(ctx.json({ name: 'John', email: 'john@example.com' }))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

test('displays user data', async () => {
  render(<UserProfile userId="123" />)

  expect(await screen.findByText('John')).toBeInTheDocument()
})
```

---

### Mocking Context

```jsx
import { render, screen } from '@testing-library/react'
import { AuthContext } from './AuthContext'
import Dashboard from './Dashboard'

test('shows admin panel for admin users', () => {
  const mockUser = { name: 'Admin', role: 'admin' }

  render(
    <AuthContext.Provider value={{ user: mockUser }}>
      <Dashboard />
    </AuthContext.Provider>
  )

  expect(screen.getByText('Admin Panel')).toBeInTheDocument()
})

test('hides admin panel for regular users', () => {
  const mockUser = { name: 'User', role: 'user' }

  render(
    <AuthContext.Provider value={{ user: mockUser }}>
      <Dashboard />
    </AuthContext.Provider>
  )

  expect(screen.queryByText('Admin Panel')).not.toBeInTheDocument()
})
```

---

## Custom Render Function

Create custom render with providers:

```jsx
// test-utils.js
import { render } from '@testing-library/react'
import { AuthProvider } from './AuthProvider'
import { ThemeProvider } from './ThemeProvider'

function AllProviders({ children }) {
  return (
    <AuthProvider>
      <ThemeProvider>
        {children}
      </ThemeProvider>
    </AuthProvider>
  )
}

function customRender(ui, options) {
  return render(ui, { wrapper: AllProviders, ...options })
}

export * from '@testing-library/react'
export { customRender as render }

// Usage in tests
import { render, screen } from './test-utils'

test('my component', () => {
  render(<MyComponent />)  // Automatically wrapped with providers
})
```

---

## Accessibility Testing

### Check ARIA Attributes

```jsx
test('button has accessible name', () => {
  render(<Button aria-label="Close modal">X</Button>)

  const button = screen.getByRole('button', { name: 'Close modal' })
  expect(button).toBeInTheDocument()
})

test('modal is accessible', () => {
  render(<Modal isOpen={true} />)

  const dialog = screen.getByRole('dialog')
  expect(dialog).toHaveAttribute('aria-modal', 'true')
})
```

### Use jest-axe for Automated Checks

```jsx
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import LoginForm from './LoginForm'

expect.extend(toHaveNoViolations)

test('has no accessibility violations', async () => {
  const { container } = render(<LoginForm />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

---

## Common Matchers

### jest-dom Matchers

```jsx
// Visibility
expect(element).toBeInTheDocument()
expect(element).toBeVisible()
expect(element).not.toBeInTheDocument()

// Content
expect(element).toHaveTextContent('Hello')
expect(element).toHaveTextContent(/hello/i)  // Case insensitive

// Attributes
expect(element).toHaveAttribute('disabled')
expect(element).toHaveAttribute('aria-label', 'Close')
expect(element).toHaveClass('active')

// Forms
expect(input).toHaveValue('user@example.com')
expect(input).toBeDisabled()
expect(input).toBeEnabled()
expect(checkbox).toBeChecked()

// Focus
expect(element).toHaveFocus()
```

---

## Best Practices

### 1. Use userEvent Over fireEvent

```jsx
// ✅ Good: userEvent (more realistic)
import userEvent from '@testing-library/user-event'

test('types in input', async () => {
  const user = userEvent.setup()
  render(<input />)

  await user.type(screen.getByRole('textbox'), 'hello')
  expect(screen.getByRole('textbox')).toHaveValue('hello')
})

// ❌ Bad: fireEvent (low-level)
import { fireEvent } from '@testing-library/react'

test('types in input', () => {
  render(<input />)

  fireEvent.change(screen.getByRole('textbox'), { target: { value: 'hello' } })
  expect(screen.getByRole('textbox')).toHaveValue('hello')
})
```

**Why**: userEvent simulates real user interactions (focus, blur, etc.).

---

### 2. Don't Test Implementation Details

```jsx
// ❌ Bad: Testing state
test('increments count state', () => {
  const { result } = renderHook(() => useState(0))
  const [count, setCount] = result.current

  act(() => setCount(1))
  expect(result.current[0]).toBe(1)  // Testing state directly
})

// ✅ Good: Testing user behavior
test('increments count when button clicked', async () => {
  const user = userEvent.setup()
  render(<Counter />)

  await user.click(screen.getByRole('button', { name: 'Increment' }))
  expect(screen.getByText('Count: 1')).toBeInTheDocument()
})
```

---

### 3. Use findBy for Async Elements

```jsx
// ❌ Bad: Manual waiting
test('shows data after loading', async () => {
  render(<UserProfile />)

  await waitFor(() => {
    expect(screen.getByText('John')).toBeInTheDocument()
  })
})

// ✅ Good: findBy waits automatically
test('shows data after loading', async () => {
  render(<UserProfile />)

  expect(await screen.findByText('John')).toBeInTheDocument()
})
```

---

### 4. Test Accessibility

```jsx
// ✅ Good: Query by role (tests accessibility)
test('button is accessible', () => {
  render(<button>Click me</button>)

  const button = screen.getByRole('button', { name: 'Click me' })
  expect(button).toBeInTheDocument()
})

// ❌ Bad: Query by test ID (doesn't test accessibility)
test('button exists', () => {
  render(<button data-testid="my-button">Click me</button>)

  const button = screen.getByTestId('my-button')
  expect(button).toBeInTheDocument()
})
```

---

## Common Mistakes

### ❌ Mistake 1: Using getBy for Async Elements

```jsx
// Bad: getBy throws immediately
test('shows data after loading', () => {
  render(<UserProfile />)

  const name = screen.getByText('John')  // ❌ Fails immediately
  expect(name).toBeInTheDocument()
})

// Good: findBy waits
test('shows data after loading', async () => {
  render(<UserProfile />)

  const name = await screen.findByText('John')  // ✅ Waits up to 1000ms
  expect(name).toBeInTheDocument()
})
```

---

### ❌ Mistake 2: Not Awaiting userEvent

```jsx
// Bad: Not awaiting userEvent
test('types in input', () => {
  const user = userEvent.setup()
  render(<input />)

  user.type(screen.getByRole('textbox'), 'hello')  // ❌ Missing await
  expect(screen.getByRole('textbox')).toHaveValue('hello')  // May fail
})

// Good: Await userEvent
test('types in input', async () => {
  const user = userEvent.setup()
  render(<input />)

  await user.type(screen.getByRole('textbox'), 'hello')  // ✅
  expect(screen.getByRole('textbox')).toHaveValue('hello')
})
```

---

### ❌ Mistake 3: Querying Outside screen

```jsx
// Bad: Querying from container
test('renders button', () => {
  const { container } = render(<button>Click</button>)
  const button = container.querySelector('button')  // ❌ Not accessible query
  expect(button).toBeInTheDocument()
})

// Good: Use screen queries
test('renders button', () => {
  render(<button>Click</button>)
  const button = screen.getByRole('button', { name: 'Click' })  // ✅
  expect(button).toBeInTheDocument()
})
```

---

## Summary

**React Testing Library enforces**:
- Test user behavior, not implementation
- Use accessible queries (getByRole, getByLabelText)
- userEvent for realistic interactions
- findBy for async elements
- Avoid testing internal state

**Query priority**: getByRole > getByLabelText > getByText > getByTestId

**Test what users do, not how code works.**
