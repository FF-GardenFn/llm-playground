# Composition: Higher-Order Components (HOC)

**Pattern**: Function that takes a component and returns a new component with enhanced functionality.

**When to Use**:
- Add behavior to multiple components (auth checks, logging, analytics)
- Cross-cutting concerns (permissions, theming, error boundaries)
- Enhance components without modifying original code
- Legacy codebase using class components (hooks not available)

**When NOT to Use**:
- Simple logic reuse (prefer hooks)
- Only used once (no reuse justifies complexity)
- Hooks can solve the problem (prefer hooks in modern React)
- Props need to be passed down (causes wrapper hell)

---

## Core Principle

**Enhancement**: Wrap component to add functionality without modifying it.

**Example: Loading State**

```tsx
// ❌ WITHOUT HOC: Loading logic duplicated in every component
function UserProfile({ userId }) {
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState(null)

  useEffect(() => {
    fetch(`/api/user/${userId}`)
      .then(res => res.json())
      .then(data => {
        setUser(data)
        setLoading(false)
      })
  }, [userId])

  if (loading) return <Spinner />
  return <div>{user.name}</div>
}

function PostList({ userId }) {
  const [loading, setLoading] = useState(true)
  const [posts, setPosts] = useState([])

  useEffect(() => {
    fetch(`/api/user/${userId}/posts`)
      .then(res => res.json())
      .then(data => {
        setPosts(data)
        setLoading(false)
      })
  }, [userId])

  if (loading) return <Spinner />
  return <ul>{posts.map(post => <li key={post.id}>{post.title}</li>)}</ul>
}
```

```tsx
// ✅ WITH HOC: Loading logic centralized
function withLoading<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  isLoading: (props: P) => boolean
): React.ComponentType<P> {
  return function WithLoadingComponent(props: P) {
    if (isLoading(props)) {
      return <Spinner />
    }
    return <WrappedComponent {...props} />
  }
}

// Original components: Just render data (no loading logic)
function UserProfile({ user }: { user: User }) {
  return <div>{user.name}</div>
}

function PostList({ posts }: { posts: Post[] }) {
  return <ul>{posts.map(post => <li key={post.id}>{post.title}</li>)}</ul>
}

// Enhanced components: Automatically show spinner when loading
const UserProfileWithLoading = withLoading(
  UserProfile,
  (props) => !props.user
)

const PostListWithLoading = withLoading(
  PostList,
  (props) => !props.posts
)
```

**Why Better**:
- Loading logic defined once
- Components focus on rendering data
- Easy to change loading indicator globally
- No duplication

---

## HOC Structure

### Basic HOC Pattern

```typescript
// Generic HOC signature
function withFeature<P extends object>(
  WrappedComponent: React.ComponentType<P>
): React.ComponentType<P> {
  // Return enhanced component
  return function EnhancedComponent(props: P) {
    // Add functionality here
    return <WrappedComponent {...props} />
  }
}
```

### HOC with Additional Props

```typescript
// HOC that injects new props
function withUser<P extends object>(
  WrappedComponent: React.ComponentType<P & { user: User }>
): React.ComponentType<P> {
  return function WithUserComponent(props: P) {
    const user = useContext(UserContext)
    return <WrappedComponent {...props} user={user} />
  }
}

// Usage
interface ProfileProps {
  user: User  // Injected by HOC
  theme: 'light' | 'dark'  // Passed by parent
}

function Profile({ user, theme }: ProfileProps) {
  return <div className={theme}>{user.name}</div>
}

// Wrap component
const ProfileWithUser = withUser(Profile)

// Parent only passes theme (user comes from HOC)
<ProfileWithUser theme="light" />
```

### HOC with Options

```typescript
// HOC configured with options
function withAuth<P extends object>(
  requiredRole: string
) {
  return function (WrappedComponent: React.ComponentType<P>): React.ComponentType<P> {
    return function WithAuthComponent(props: P) {
      const { user } = useAuth()

      if (!user) {
        return <Navigate to="/login" />
      }

      if (user.role !== requiredRole) {
        return <div>Access Denied</div>
      }

      return <WrappedComponent {...props} />
    }
  }
}

// Usage
const AdminDashboard = withAuth('admin')(Dashboard)
const ModeratorPanel = withAuth('moderator')(Panel)
```

---

## Examples: Common HOCs

### Example 1: Authentication

**Problem**: Many components require user to be logged in.

```tsx
function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
): React.ComponentType<P> {
  return function WithAuthComponent(props: P) {
    const { user, loading } = useAuth()

    if (loading) {
      return <Spinner />
    }

    if (!user) {
      return <Navigate to="/login" replace />
    }

    return <WrappedComponent {...props} />
  }
}

// Usage
function Dashboard() {
  return <div>Dashboard content</div>
}

const ProtectedDashboard = withAuth(Dashboard)

// Route
<Route path="/dashboard" element={<ProtectedDashboard />} />
```

### Example 2: Error Boundary

**Problem**: Catch errors in multiple components.

```tsx
function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  FallbackComponent: React.ComponentType<{ error: Error; resetError: () => void }> = DefaultErrorFallback
): React.ComponentType<P> {
  return class WithErrorBoundary extends React.Component<
    P,
    { hasError: boolean; error: Error | null }
  > {
    constructor(props: P) {
      super(props)
      this.state = { hasError: false, error: null }
    }

    static getDerivedStateFromError(error: Error) {
      return { hasError: true, error }
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
      console.error('Error caught by boundary:', error, errorInfo)
    }

    resetError = () => {
      this.setState({ hasError: false, error: null })
    }

    render() {
      if (this.state.hasError && this.state.error) {
        return <FallbackComponent error={this.state.error} resetError={this.resetError} />
      }

      return <WrappedComponent {...this.props} />
    }
  }
}

// Usage
function Dashboard() {
  // May throw error
  const data = fetchData()
  return <div>{data}</div>
}

const SafeDashboard = withErrorBoundary(Dashboard)
```

### Example 3: Analytics Tracking

**Problem**: Track page views and interactions across components.

```tsx
function withAnalytics<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: {
    trackPageView?: boolean
    trackClicks?: boolean
    pageName: string
  }
): React.ComponentType<P> {
  return function WithAnalyticsComponent(props: P) {
    const analytics = useAnalytics()

    useEffect(() => {
      if (options.trackPageView) {
        analytics.trackPageView(options.pageName)
      }
    }, [])

    const handleClick = (e: React.MouseEvent) => {
      if (options.trackClicks) {
        analytics.trackClick(options.pageName, (e.target as HTMLElement).tagName)
      }
    }

    return (
      <div onClick={handleClick}>
        <WrappedComponent {...props} />
      </div>
    )
  }
}

// Usage
const Dashboard = withAnalytics(DashboardComponent, {
  trackPageView: true,
  trackClicks: true,
  pageName: 'Dashboard',
})

const Profile = withAnalytics(ProfileComponent, {
  trackPageView: true,
  trackClicks: false,
  pageName: 'Profile',
})
```

### Example 4: Theming

**Problem**: Inject theme into multiple components.

```tsx
function withTheme<P extends object>(
  WrappedComponent: React.ComponentType<P & { theme: Theme }>
): React.ComponentType<P> {
  return function WithThemeComponent(props: P) {
    const theme = useContext(ThemeContext)
    return <WrappedComponent {...props} theme={theme} />
  }
}

// Usage
interface ButtonProps {
  theme: Theme  // Injected by HOC
  label: string
}

function Button({ theme, label }: ButtonProps) {
  return (
    <button style={{ backgroundColor: theme.primaryColor }}>
      {label}
    </button>
  )
}

const ThemedButton = withTheme(Button)

// Parent doesn't need to pass theme
<ThemedButton label="Click me" />
```

### Example 5: Data Fetching

**Problem**: Fetch data with loading/error states for multiple components.

```tsx
interface WithDataProps<T> {
  data: T | null
  loading: boolean
  error: Error | null
  refetch: () => void
}

function withData<P extends object, T>(
  WrappedComponent: React.ComponentType<P & WithDataProps<T>>,
  fetcher: (props: P) => Promise<T>
): React.ComponentType<P> {
  return function WithDataComponent(props: P) {
    const [data, setData] = useState<T | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<Error | null>(null)

    const fetchData = useCallback(async () => {
      setLoading(true)
      try {
        const result = await fetcher(props)
        setData(result)
        setError(null)
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }, [props])

    useEffect(() => {
      fetchData()
    }, [fetchData])

    return (
      <WrappedComponent
        {...props}
        data={data}
        loading={loading}
        error={error}
        refetch={fetchData}
      />
    )
  }
}

// Usage
interface UserProfileProps {
  userId: string
  data: User | null
  loading: boolean
  error: Error | null
}

function UserProfile({ data: user, loading, error }: UserProfileProps) {
  if (loading) return <Spinner />
  if (error) return <ErrorMessage error={error} />
  if (!user) return null
  return <div>{user.name}</div>
}

const UserProfileWithData = withData(
  UserProfile,
  async (props) => {
    const res = await fetch(`/api/user/${props.userId}`)
    return res.json()
  }
)

// Parent just passes userId
<UserProfileWithData userId="123" />
```

---

## Composing Multiple HOCs

**Problem**: Component needs multiple enhancements.

```tsx
// Component
function Dashboard() {
  return <div>Dashboard</div>
}

// Apply multiple HOCs
const EnhancedDashboard = withAuth(
  withErrorBoundary(
    withAnalytics(Dashboard, { trackPageView: true, pageName: 'Dashboard' })
  )
)

// OR: Use compose utility
function compose(...fns: Function[]) {
  return (x: any) => fns.reduceRight((acc, fn) => fn(acc), x)
}

const EnhancedDashboard = compose(
  withAuth,
  withErrorBoundary,
  (Component) => withAnalytics(Component, { trackPageView: true, pageName: 'Dashboard' })
)(Dashboard)
```

**Result**: Dashboard now has auth check, error boundary, and analytics.

**Warning**: Deep nesting can make debugging hard. Consider hooks or render props if too complex.

---

## Testing HOCs

### Test HOC in Isolation

```tsx
describe('withAuth HOC', () => {
  test('redirects to login if not authenticated', () => {
    const MockComponent = () => <div>Protected Content</div>
    const ProtectedComponent = withAuth(MockComponent)

    // Mock useAuth to return no user
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({ user: null, loading: false })

    render(<ProtectedComponent />)

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
    // Verify redirect (depends on router)
  })

  test('renders component if authenticated', () => {
    const MockComponent = () => <div>Protected Content</div>
    const ProtectedComponent = withAuth(MockComponent)

    // Mock useAuth to return user
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({
      user: { id: '1', name: 'Alice' },
      loading: false,
    })

    render(<ProtectedComponent />)

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  test('shows spinner while loading', () => {
    const MockComponent = () => <div>Protected Content</div>
    const ProtectedComponent = withAuth(MockComponent)

    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({ user: null, loading: true })

    render(<ProtectedComponent />)

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })
})
```

### Test Wrapped Component

```tsx
describe('Dashboard (without HOC)', () => {
  test('renders dashboard content', () => {
    render(<Dashboard />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})

describe('Dashboard (with HOC)', () => {
  test('protected dashboard requires auth', () => {
    const ProtectedDashboard = withAuth(Dashboard)

    // Not authenticated
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({ user: null, loading: false })
    const { rerender } = render(<ProtectedDashboard />)
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()

    // Authenticated
    jest.spyOn(AuthContext, 'useAuth').mockReturnValue({
      user: { id: '1', name: 'Alice' },
      loading: false,
    })
    rerender(<ProtectedDashboard />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})
```

---

## Performance Considerations

### 1. Avoid Creating HOCs Inside Render

**Problem**: HOC created on every render.

```tsx
// ❌ BAD: New HOC on every render
function Parent() {
  const EnhancedChild = withAuth(Child)  // New component each render!
  return <EnhancedChild />
}
```

**Solution**: Define HOC outside render.

```tsx
// ✅ GOOD: HOC defined once
const EnhancedChild = withAuth(Child)

function Parent() {
  return <EnhancedChild />
}
```

### 2. Forward Refs

**Problem**: HOC breaks ref forwarding.

```tsx
// ❌ BAD: Ref doesn't reach wrapped component
function withLogging<P extends object>(WrappedComponent: React.ComponentType<P>) {
  return function WithLoggingComponent(props: P) {
    console.log('Rendering:', WrappedComponent.name)
    return <WrappedComponent {...props} />
  }
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>((props, ref) => {
  return <button ref={ref}>{props.label}</button>
})

const LoggedButton = withLogging(Button)

// Ref doesn't work!
<LoggedButton ref={buttonRef} label="Click" />
```

**Solution**: Forward ref through HOC.

```tsx
// ✅ GOOD: Forward ref to wrapped component
function withLogging<P extends object, R = any>(
  WrappedComponent: React.ComponentType<P & { ref?: React.Ref<R> }>
) {
  const WithLoggingComponent = React.forwardRef<R, P>((props, ref) => {
    console.log('Rendering:', WrappedComponent.name)
    return <WrappedComponent {...props} ref={ref} />
  })

  WithLoggingComponent.displayName = `withLogging(${WrappedComponent.displayName || WrappedComponent.name})`

  return WithLoggingComponent
}

const LoggedButton = withLogging(Button)

// Ref works now!
<LoggedButton ref={buttonRef} label="Click" />
```

### 3. Display Name for DevTools

**Problem**: HOCs create generic "Unknown" components in DevTools.

```tsx
// ❌ BAD: Shows as "Unknown" in DevTools
function withAuth<P extends object>(WrappedComponent: React.ComponentType<P>) {
  return function (props: P) {
    return <WrappedComponent {...props} />
  }
}

// ✅ GOOD: Shows as "withAuth(Dashboard)" in DevTools
function withAuth<P extends object>(WrappedComponent: React.ComponentType<P>) {
  const WithAuthComponent = (props: P) => {
    return <WrappedComponent {...props} />
  }

  WithAuthComponent.displayName = `withAuth(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`

  return WithAuthComponent
}
```

---

## Accessibility

### 1. Preserve ARIA Attributes

**Pattern**: Don't override wrapped component's ARIA attributes.

```tsx
function withTooltip<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  tooltip: string
): React.ComponentType<P> {
  return function WithTooltipComponent(props: P) {
    return (
      <div title={tooltip}>
        <WrappedComponent {...props} />
      </div>
    )
  }
}

// Wrapped component has ARIA attributes
<button aria-label="Close">✕</button>

// HOC preserves them
const TooltipButton = withTooltip(Button, 'Close this window')
<TooltipButton aria-label="Close" />  // aria-label preserved
```

### 2. Focus Management

**Pattern**: Don't break keyboard navigation.

```tsx
function withClickOutside<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  onClickOutside: () => void
): React.ComponentType<P> {
  return function WithClickOutsideComponent(props: P) {
    const wrapperRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
      const handleClick = (e: MouseEvent) => {
        if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
          onClickOutside()
        }
      }
      document.addEventListener('mousedown', handleClick)
      return () => document.removeEventListener('mousedown', handleClick)
    }, [])

    return (
      <div ref={wrapperRef}>
        <WrappedComponent {...props} />
      </div>
    )
  }
}

// Wrapped component still focusable
<input /> → <div><input /></div>  // Input still keyboard-accessible
```

---

## Anti-Patterns

### 1. Mutating Wrapped Component

**Problem**: Modifying original component.

```tsx
// ❌ BAD: Mutates original component
function withFeature(WrappedComponent) {
  WrappedComponent.prototype.componentDidMount = function() {
    console.log('Mounted')
  }
  return WrappedComponent
}

// ✅ GOOD: Return new component, don't mutate
function withFeature(WrappedComponent) {
  return class extends React.Component {
    componentDidMount() {
      console.log('Mounted')
      super.componentDidMount?.()
    }
    render() {
      return <WrappedComponent {...this.props} />
    }
  }
}
```

### 2. Using HOCs Inside render()

**Problem**: Creates new component on every render (performance issue).

```tsx
// ❌ BAD
function Parent() {
  const Enhanced = withAuth(Child)
  return <Enhanced />
}

// ✅ GOOD
const Enhanced = withAuth(Child)
function Parent() {
  return <Enhanced />
}
```

### 3. Not Copying Static Methods

**Problem**: Static methods lost after wrapping.

```tsx
function Child() {
  return <div>Child</div>
}
Child.staticMethod = () => 'static'

// ❌ BAD: Static method lost
const Enhanced = withAuth(Child)
Enhanced.staticMethod()  // undefined

// ✅ GOOD: Copy static methods
import hoistNonReactStatics from 'hoist-non-react-statics'

function withAuth(WrappedComponent) {
  const WithAuthComponent = (props) => <WrappedComponent {...props} />
  hoistNonReactStatics(WithAuthComponent, WrappedComponent)
  return WithAuthComponent
}

const Enhanced = withAuth(Child)
Enhanced.staticMethod()  // 'static'
```

---

## HOCs vs Hooks vs Render Props

### When to Use Each

| Pattern | Use When | Example |
|---------|----------|---------|
| **HOC** | Cross-cutting concern applied to many components. Legacy class components. | Auth check, error boundary, analytics |
| **Hook** | Logic reuse in function components. No UI wrapper needed. | `useAuth()`, `useWindowSize()` |
| **Render Prop** | UI rendering varies per use case. Logic + UI container combined. | `<Fetch>{data => ...}</Fetch>` |

### Migration Example

**HOC (Legacy)**:
```tsx
const UserProfile = withUser(Profile)
```

**Hook (Modern)**:
```tsx
function Profile() {
  const user = useUser()
  return <div>{user.name}</div>
}
```

**When Hooks Can't Replace HOCs**:
- Need to wrap component without modifying code (HOC)
- Error boundaries (no error boundary hook exists)
- Class components (no hooks in classes)

---

## Summary

**HOC Pattern**:
- Function that takes component, returns enhanced component
- Add behavior without modifying original
- Cross-cutting concerns (auth, logging, theming)

**Structure**:
```typescript
function withFeature<P>(Component: React.ComponentType<P>): React.ComponentType<P> {
  return function Enhanced(props: P) {
    // Add functionality
    return <Component {...props} />
  }
}
```

**Common HOCs**:
- `withAuth`: Require authentication
- `withErrorBoundary`: Catch errors
- `withAnalytics`: Track events
- `withTheme`: Inject theme
- `withData`: Fetch data

**Best Practices**:
- Forward refs
- Set display name for DevTools
- Don't create HOCs in render
- Don't mutate wrapped component
- Copy static methods (use `hoist-non-react-statics`)

**Result**: Reusable component enhancements without code modification.
