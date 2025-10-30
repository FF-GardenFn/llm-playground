# Composition: Render Props

**Pattern**: Pass a function as a prop to control what a component renders, enabling flexible component reuse with different rendering logic.

**When to Use**:
- Component logic is reusable but UI varies
- Need to share stateful logic between components
- Child component needs access to parent's state/methods
- Custom rendering per use case

**When NOT to Use**:
- Simple static rendering (use regular composition)
- Logic + UI always used together (no need for flexibility)
- Performance-critical (render props can cause extra re-renders)
- Hooks can solve the problem (prefer hooks for logic reuse)

---

## Core Principle

**Separation**: Logic in parent, UI controlled by caller.

**Example: Mouse Position Tracker**

```tsx
// ❌ BAD: Logic + UI tightly coupled
function MousePosition() {
  const [position, setPosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMove)
    return () => window.removeEventListener('mousemove', handleMove)
  }, [])

  return <div>X: {position.x}, Y: {position.y}</div>
}
```

**Problem**: UI is hardcoded. Can't reuse logic for different rendering.

```tsx
// ✅ GOOD: Logic separated from UI via render prop
interface MouseTrackerProps {
  render: (position: { x: number; y: number }) => React.ReactNode
}

function MouseTracker({ render }: MouseTrackerProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMove)
    return () => window.removeEventListener('mousemove', handleMove)
  }, [])

  return <>{render(position)}</>
}

// Usage 1: Simple text
<MouseTracker render={({ x, y }) => <div>X: {x}, Y: {y}</div>} />

// Usage 2: Crosshair
<MouseTracker
  render={({ x, y }) => (
    <div
      style={{
        position: 'fixed',
        top: y,
        left: x,
        width: 20,
        height: 20,
        borderRadius: '50%',
        border: '2px solid red',
        pointerEvents: 'none',
      }}
    />
  )}
/>

// Usage 3: Tooltip that follows mouse
<MouseTracker
  render={({ x, y }) => (
    <Tooltip x={x + 10} y={y + 10}>
      Position: {x}, {y}
    </Tooltip>
  )}
/>
```

**Why Better**:
- Logic reused with different UIs
- Caller controls rendering
- No need for multiple specialized components (MousePositionText, MousePositionCrosshair, etc.)

---

## Pattern Variations

### Variation 1: Render Prop (Function as Prop)

**Pattern**: Pass function as named prop.

```tsx
interface DataFetcherProps<T> {
  url: string
  render: (data: T | null, loading: boolean, error: Error | null) => React.ReactNode
}

function DataFetcher<T>({ url, render }: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err)
        setLoading(false)
      })
  }, [url])

  return <>{render(data, loading, error)}</>
}

// Usage
<DataFetcher<User>
  url="/api/user"
  render={(user, loading, error) => {
    if (loading) return <Spinner />
    if (error) return <ErrorMessage error={error} />
    if (!user) return null
    return <div>Welcome, {user.name}!</div>
  }}
/>
```

### Variation 2: Children as Function

**Pattern**: Pass function as `children` prop.

```tsx
interface ToggleProps {
  children: (isOn: boolean, toggle: () => void) => React.ReactNode
}

function Toggle({ children }: ToggleProps) {
  const [isOn, setIsOn] = useState(false)
  const toggle = () => setIsOn(prev => !prev)

  return <>{children(isOn, toggle)}</>
}

// Usage
<Toggle>
  {(isOn, toggle) => (
    <div>
      <button onClick={toggle}>Toggle</button>
      <p>The switch is {isOn ? 'ON' : 'OFF'}</p>
    </div>
  )}
</Toggle>
```

**When to Use Children vs Named Prop**:
- **Children**: Single render function (more common)
- **Named prop**: Multiple render functions (e.g., `renderHeader`, `renderBody`)

### Variation 3: Multiple Render Props

**Pattern**: Multiple rendering areas controlled by caller.

```tsx
interface ListProps<T> {
  items: T[]
  renderHeader: () => React.ReactNode
  renderItem: (item: T, index: number) => React.ReactNode
  renderEmpty: () => React.ReactNode
  renderFooter: () => React.ReactNode
}

function List<T>({ items, renderHeader, renderItem, renderEmpty, renderFooter }: ListProps<T>) {
  return (
    <div className="list">
      {renderHeader()}
      {items.length === 0 ? (
        renderEmpty()
      ) : (
        <ul>
          {items.map((item, index) => (
            <li key={index}>{renderItem(item, index)}</li>
          ))}
        </ul>
      )}
      {renderFooter()}
    </div>
  )
}

// Usage
<List
  items={users}
  renderHeader={() => <h2>Users ({users.length})</h2>}
  renderItem={(user, index) => (
    <div>
      <strong>{user.name}</strong> - {user.email}
    </div>
  )}
  renderEmpty={() => <p>No users found</p>}
  renderFooter={() => <button>Load More</button>}
/>
```

---

## Examples: Common Use Cases

### Example 1: Data Fetching

**Problem**: Fetch data, handle loading/error, render UI differently per use case.

```tsx
interface FetchProps<T> {
  url: string
  children: (state: {
    data: T | null
    loading: boolean
    error: Error | null
    refetch: () => void
  }) => React.ReactNode
}

function Fetch<T>({ url, children }: FetchProps<T>) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = useCallback(() => {
    setLoading(true)
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err)
        setLoading(false)
      })
  }, [url])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return <>{children({ data, loading, error, refetch: fetchData })}</>
}

// Usage 1: User profile
<Fetch<User> url="/api/user">
  {({ data: user, loading, error }) => {
    if (loading) return <Spinner />
    if (error) return <ErrorMessage error={error} />
    if (!user) return null
    return (
      <div>
        <h1>{user.name}</h1>
        <p>{user.email}</p>
      </div>
    )
  }}
</Fetch>

// Usage 2: Product list
<Fetch<Product[]> url="/api/products">
  {({ data: products, loading, error, refetch }) => {
    if (loading) return <Skeleton count={5} />
    if (error) return <ErrorBanner error={error} onRetry={refetch} />
    if (!products) return null
    return (
      <ProductGrid products={products} />
    )
  }}
</Fetch>
```

### Example 2: Form State Management

**Problem**: Manage form state, validation, submission - but UI varies.

```tsx
interface FormState<T> {
  values: T
  errors: Partial<Record<keyof T, string>>
  touched: Partial<Record<keyof T, boolean>>
  isSubmitting: boolean
  handleChange: (field: keyof T, value: any) => void
  handleBlur: (field: keyof T) => void
  handleSubmit: (e: React.FormEvent) => void
}

interface FormProps<T> {
  initialValues: T
  validate: (values: T) => Partial<Record<keyof T, string>>
  onSubmit: (values: T) => Promise<void>
  children: (state: FormState<T>) => React.ReactNode
}

function Form<T extends Record<string, any>>({
  initialValues,
  validate,
  onSubmit,
  children,
}: FormProps<T>) {
  const [values, setValues] = useState<T>(initialValues)
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({})
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (field: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [field]: value }))
  }

  const handleBlur = (field: keyof T) => {
    setTouched(prev => ({ ...prev, [field]: true }))
    const newErrors = validate(values)
    setErrors(newErrors)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const newErrors = validate(values)
    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      setIsSubmitting(true)
      try {
        await onSubmit(values)
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  return (
    <>
      {children({
        values,
        errors,
        touched,
        isSubmitting,
        handleChange,
        handleBlur,
        handleSubmit,
      })}
    </>
  )
}

// Usage: Login form
interface LoginValues {
  email: string
  password: string
}

<Form<LoginValues>
  initialValues={{ email: '', password: '' }}
  validate={values => {
    const errors: Partial<Record<keyof LoginValues, string>> = {}
    if (!values.email.includes('@')) errors.email = 'Invalid email'
    if (values.password.length < 8) errors.password = 'Password must be 8+ characters'
    return errors
  }}
  onSubmit={async values => {
    await fetch('/api/login', {
      method: 'POST',
      body: JSON.stringify(values),
    })
  }}
>
  {({ values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit }) => (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={values.email}
        onChange={e => handleChange('email', e.target.value)}
        onBlur={() => handleBlur('email')}
      />
      {touched.email && errors.email && <span>{errors.email}</span>}

      <input
        type="password"
        value={values.password}
        onChange={e => handleChange('password', e.target.value)}
        onBlur={() => handleBlur('password')}
      />
      {touched.password && errors.password && <span>{errors.password}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  )}
</Form>
```

### Example 3: Pagination

**Problem**: Manage pagination state, but table/grid rendering varies.

```tsx
interface PaginationState {
  currentPage: number
  totalPages: number
  pageSize: number
  goToPage: (page: number) => void
  nextPage: () => void
  previousPage: () => void
}

interface PaginationProps<T> {
  items: T[]
  pageSize: number
  children: (paginatedItems: T[], state: PaginationState) => React.ReactNode
}

function Pagination<T>({ items, pageSize, children }: PaginationProps<T>) {
  const [currentPage, setCurrentPage] = useState(0)

  const totalPages = Math.ceil(items.length / pageSize)
  const startIndex = currentPage * pageSize
  const paginatedItems = items.slice(startIndex, startIndex + pageSize)

  const goToPage = (page: number) => {
    setCurrentPage(Math.max(0, Math.min(page, totalPages - 1)))
  }

  const nextPage = () => goToPage(currentPage + 1)
  const previousPage = () => goToPage(currentPage - 1)

  return (
    <>
      {children(paginatedItems, {
        currentPage,
        totalPages,
        pageSize,
        goToPage,
        nextPage,
        previousPage,
      })}
    </>
  )
}

// Usage 1: Table
<Pagination items={users} pageSize={10}>
  {(paginatedUsers, { currentPage, totalPages, nextPage, previousPage }) => (
    <div>
      <table>
        <tbody>
          {paginatedUsers.map(user => (
            <tr key={user.id}>
              <td>{user.name}</td>
              <td>{user.email}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div>
        <button onClick={previousPage} disabled={currentPage === 0}>
          Previous
        </button>
        <span>
          Page {currentPage + 1} of {totalPages}
        </span>
        <button onClick={nextPage} disabled={currentPage === totalPages - 1}>
          Next
        </button>
      </div>
    </div>
  )}
</Pagination>

// Usage 2: Grid
<Pagination items={products} pageSize={12}>
  {(paginatedProducts, { currentPage, totalPages, goToPage }) => (
    <div>
      <div className="grid">
        {paginatedProducts.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
      <div className="pagination-dots">
        {Array.from({ length: totalPages }, (_, i) => (
          <button
            key={i}
            onClick={() => goToPage(i)}
            className={i === currentPage ? 'active' : ''}
          >
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  )}
</Pagination>
```

### Example 4: Dropdown/Menu

**Problem**: Manage open/close state, keyboard navigation - but menu content varies.

```tsx
interface DropdownState {
  isOpen: boolean
  open: () => void
  close: () => void
  toggle: () => void
}

interface DropdownProps {
  children: (state: DropdownState) => React.ReactNode
}

function Dropdown({ children }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const open = () => setIsOpen(true)
  const close = () => setIsOpen(false)
  const toggle = () => setIsOpen(prev => !prev)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        close()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close()
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [])

  return <div ref={dropdownRef}>{children({ isOpen, open, close, toggle })}</div>
}

// Usage 1: User menu
<Dropdown>
  {({ isOpen, toggle, close }) => (
    <>
      <button onClick={toggle}>
        <Avatar user={currentUser} />
      </button>
      {isOpen && (
        <div className="menu">
          <MenuItem onClick={close}>Profile</MenuItem>
          <MenuItem onClick={close}>Settings</MenuItem>
          <MenuItem onClick={() => { close(); logout(); }}>Logout</MenuItem>
        </div>
      )}
    </>
  )}
</Dropdown>

// Usage 2: Filter menu
<Dropdown>
  {({ isOpen, toggle, close }) => (
    <>
      <button onClick={toggle}>
        Filters {activeFilters.length > 0 && `(${activeFilters.length})`}
      </button>
      {isOpen && (
        <div className="filter-panel">
          <FilterGroup title="Category">
            <Checkbox label="Electronics" />
            <Checkbox label="Books" />
          </FilterGroup>
          <FilterGroup title="Price">
            <RangeSlider min={0} max={1000} />
          </FilterGroup>
          <button onClick={close}>Apply</button>
        </div>
      )}
    </>
  )}
</Dropdown>
```

---

## Testing Render Props

### Unit Tests

**Pattern**: Test logic component with mock render function.

```tsx
describe('MouseTracker', () => {
  test('calls render with initial position', () => {
    const render = jest.fn(() => null)
    render(<MouseTracker render={render} />)

    expect(render).toHaveBeenCalledWith({ x: 0, y: 0 })
  })

  test('updates position on mouse move', () => {
    const render = jest.fn(() => null)
    render(<MouseTracker render={render} />)

    fireEvent.mouseMove(window, { clientX: 100, clientY: 200 })

    expect(render).toHaveBeenCalledWith({ x: 100, y: 200 })
  })
})

describe('Toggle', () => {
  test('provides initial state', () => {
    const children = jest.fn(() => null)
    render(<Toggle>{children}</Toggle>)

    expect(children).toHaveBeenCalledWith(false, expect.any(Function))
  })

  test('toggle function changes state', () => {
    let capturedToggle: (() => void) | null = null
    render(
      <Toggle>
        {(isOn, toggle) => {
          capturedToggle = toggle
          return <div>{isOn ? 'ON' : 'OFF'}</div>
        }}
      </Toggle>
    )

    expect(screen.getByText('OFF')).toBeInTheDocument()

    act(() => {
      capturedToggle!()
    })

    expect(screen.getByText('ON')).toBeInTheDocument()
  })
})
```

### Integration Tests

**Pattern**: Test full usage with real render function.

```tsx
describe('DataFetcher Integration', () => {
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({ name: 'Alice', email: 'alice@example.com' }),
      })
    ) as jest.Mock
  })

  test('renders loading state initially', () => {
    render(
      <DataFetcher url="/api/user">
        {({ loading }) => (loading ? <div>Loading...</div> : <div>Loaded</div>)}
      </DataFetcher>
    )

    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  test('renders data after fetch', async () => {
    render(
      <DataFetcher url="/api/user">
        {({ data, loading }) => {
          if (loading) return <div>Loading...</div>
          return <div>{data.name}</div>
        }}
      </DataFetcher>
    )

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument()
    })
  })

  test('renders error on fetch failure', async () => {
    global.fetch = jest.fn(() => Promise.reject(new Error('Network error')))

    render(
      <DataFetcher url="/api/user">
        {({ error, loading }) => {
          if (loading) return <div>Loading...</div>
          if (error) return <div>Error: {error.message}</div>
          return null
        }}
      </DataFetcher>
    )

    await waitFor(() => {
      expect(screen.getByText('Error: Network error')).toBeInTheDocument()
    })
  })
})
```

---

## Performance Considerations

### 1. Inline Functions Cause Re-Renders

**Problem**: Inline render functions are recreated on every render.

```tsx
// ❌ BAD: New function on every parent render
function App() {
  return (
    <MouseTracker
      render={({ x, y }) => <div>X: {x}, Y: {y}</div>}
    />
  )
}
```

**Solution**: Extract function or use useCallback.

```tsx
// ✅ GOOD: Stable function reference
const renderMousePosition = ({ x, y }: { x: number; y: number }) => (
  <div>X: {x}, Y: {y}</div>
)

function App() {
  return <MouseTracker render={renderMousePosition} />
}

// OR: useCallback
function App() {
  const renderMousePosition = useCallback(
    ({ x, y }: { x: number; y: number }) => <div>X: {x}, Y: {y}</div>,
    []
  )
  return <MouseTracker render={renderMousePosition} />
}
```

### 2. Render Props vs Hooks

**When to Use Hooks Instead**:

```tsx
// Render prop approach
<MouseTracker render={({ x, y }) => <div>X: {x}, Y: {y}</div>} />

// Hook approach (simpler for logic reuse)
function useMousePosition() {
  const [position, setPosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMove)
    return () => window.removeEventListener('mousemove', handleMove)
  }, [])

  return position
}

// Usage
function App() {
  const { x, y } = useMousePosition()
  return <div>X: {x}, Y: {y}</div>
}
```

**Rule**: If you only need logic (no UI component), prefer hooks. If logic is tied to a UI container, use render props.

---

## Accessibility

### 1. Preserve Semantic Structure

**Pattern**: Render props should not break HTML semantics.

```tsx
// ❌ BAD: Render prop breaks list structure
<ul>
  <Pagination items={users} pageSize={5}>
    {(paginatedUsers) =>
      paginatedUsers.map(user => <li key={user.id}>{user.name}</li>)
    }
  </Pagination>
</ul>

// Result: <ul><div><li>...</li></div></ul> (invalid)

// ✅ GOOD: Render prop doesn't insert wrapper
<Pagination items={users} pageSize={5}>
  {(paginatedUsers) => (
    <ul>
      {paginatedUsers.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  )}
</Pagination>
```

### 2. Pass Accessibility Props Through Render Function

**Pattern**: Provide ARIA attributes via render function.

```tsx
interface DropdownState {
  isOpen: boolean
  toggle: () => void
  triggerProps: {
    'aria-haspopup': 'true'
    'aria-expanded': boolean
    'aria-controls': string
  }
  menuProps: {
    id: string
    role: 'menu'
  }
}

function Dropdown({ children }: { children: (state: DropdownState) => React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  const menuId = useId()

  const state: DropdownState = {
    isOpen,
    toggle: () => setIsOpen(prev => !prev),
    triggerProps: {
      'aria-haspopup': 'true',
      'aria-expanded': isOpen,
      'aria-controls': menuId,
    },
    menuProps: {
      id: menuId,
      role: 'menu',
    },
  }

  return <>{children(state)}</>
}

// Usage: ARIA attributes automatically applied
<Dropdown>
  {({ isOpen, toggle, triggerProps, menuProps }) => (
    <>
      <button onClick={toggle} {...triggerProps}>Menu</button>
      {isOpen && (
        <div {...menuProps}>
          <div role="menuitem">Item 1</div>
          <div role="menuitem">Item 2</div>
        </div>
      )}
    </>
  )}
</Dropdown>
```

---

## Anti-Patterns

### 1. Too Many Render Props

**Problem**: Overusing render props for every component.

```tsx
// ❌ BAD: Render prop for simple button
<Button render={({ onClick }) => <button onClick={onClick}>Click me</button>} />

// ✅ GOOD: Just use regular composition
<Button>Click me</Button>
```

### 2. Render Props for Static Content

**Problem**: Using render prop when content doesn't vary.

```tsx
// ❌ BAD: Render prop returns same content always
<Card
  renderTitle={() => <h3>Title</h3>}
  renderBody={() => <p>Body text</p>}
/>

// ✅ GOOD: Use regular children
<Card>
  <CardTitle>Title</CardTitle>
  <CardBody>Body text</CardBody>
</Card>
```

### 3. Deeply Nested Render Props

**Problem**: Multiple render props create "callback hell".

```tsx
// ❌ BAD: Nested render props
<Fetch url="/api/user">
  {({ data: user }) => (
    <Fetch url={`/api/user/${user.id}/posts`}>
      {({ data: posts }) => (
        <Pagination items={posts} pageSize={5}>
          {(paginatedPosts) => (
            <div>
              {paginatedPosts.map(post => <Post key={post.id} post={post} />)}
            </div>
          )}
        </Pagination>
      )}
    </Fetch>
  )}
</Fetch>

// ✅ GOOD: Extract to separate component or use hooks
function UserPosts({ userId }: { userId: string }) {
  const { data: posts } = useFetch(`/api/user/${userId}/posts`)
  const paginatedPosts = usePagination(posts, 5)

  return (
    <div>
      {paginatedPosts.map(post => <Post key={post.id} post={post} />)}
    </div>
  )
}

<Fetch url="/api/user">
  {({ data: user }) => <UserPosts userId={user.id} />}
</Fetch>
```

---

## Migration: Render Props → Hooks

**When**: Hooks are simpler for most logic reuse cases.

**Before (Render Prop)**:
```tsx
<WindowSize>
  {({ width, height }) => (
    <div>
      Window: {width} x {height}
    </div>
  )}
</WindowSize>
```

**After (Hook)**:
```tsx
function useWindowSize() {
  const [size, setSize] = useState({ width: window.innerWidth, height: window.innerHeight })

  useEffect(() => {
    const handleResize = () => {
      setSize({ width: window.innerWidth, height: window.innerHeight })
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return size
}

// Usage
function App() {
  const { width, height } = useWindowSize()
  return <div>Window: {width} x {height}</div>
}
```

**When to Keep Render Props**:
- Logic is tied to a UI container (e.g., Dropdown has both logic + wrapper div)
- Need to support class components (no hooks)
- Multiple render areas (e.g., List with renderHeader, renderItem, renderFooter)

---

## Summary

**Render Props Pattern**:
- Pass function as prop to control rendering
- Logic in parent, UI controlled by caller
- Enable flexible component reuse

**When to Use**:
- Reusable logic with variable UI
- Share stateful logic between components
- Custom rendering per use case

**Variations**:
- Named prop: `render={(data) => <UI />}`
- Children as function: `{(data) => <UI />}`
- Multiple render props: `renderHeader`, `renderItem`, `renderFooter`

**Performance**:
- Extract render functions or use useCallback
- Prefer hooks for simple logic reuse

**Result**: Flexible, reusable component logic with caller-controlled UI.
