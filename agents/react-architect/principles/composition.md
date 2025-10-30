# Component Composition Principle

**Core Philosophy**: Build complex interfaces from simple, reusable components.

Composition is the foundation of React architecture. Master composition, master React.

---

## The Composition Mindset

### Think in Components

**Break UI into pieces**:
```
Application
├─ Header
│  ├─ Logo
│  ├─ Navigation
│  └─ UserMenu
├─ Main
│  ├─ Sidebar
│  │  ├─ FilterPanel
│  │  └─ CategoryList
│  └─ Content
│     ├─ ProductGrid
│     │  └─ ProductCard (repeated)
│     └─ Pagination
└─ Footer
```

**Each component**:
- Has single responsibility
- Is reusable across app
- Can be tested in isolation
- Is composable with others

---

## Composition Over Inheritance

React uses composition, not inheritance. Components don't extend each other—they compose.

### ❌ Inheritance (Java-style, NOT React)

```jsx
// Bad: Don't do this in React
class Button extends Component {
  render() {
    return <button>{this.props.children}</button>
  }
}

class PrimaryButton extends Button {
  render() {
    return <button className="primary">{this.props.children}</button>
  }
}

class SecondaryButton extends Button {
  render() {
    return <button className="secondary">{this.props.children}</button>
  }
}
```

**Problems**:
- Tight coupling (child depends on parent)
- Hard to change (modifying Button affects all subclasses)
- Limited reusability (can't combine behaviors)

---

### ✅ Composition (React way)

```jsx
// Good: Composition via props
function Button({ variant = 'primary', children, ...props }) {
  return (
    <button className={`btn btn-${variant}`} {...props}>
      {children}
    </button>
  )
}

// Usage: Compose through props, not inheritance
<Button variant="primary">Save</Button>
<Button variant="secondary">Cancel</Button>
<Button variant="danger">Delete</Button>
```

**Benefits**:
- Loose coupling (components independent)
- Easy to change (modify props, not class hierarchy)
- Flexible reusability (combine behaviors via props)

---

## Composition Patterns

### 1. Props Composition

**Pass data and behavior via props**:

```jsx
// Simple prop composition
function Card({ title, content, footer }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <p>{content}</p>
      <div className="card-footer">{footer}</div>
    </div>
  )
}

// Usage
<Card
  title="Welcome"
  content="This is a card"
  footer={<Button>Learn More</Button>}
/>
```

---

### 2. Children Composition

**Nest components inside each other**:

```jsx
// Container component accepts children
function Card({ children }) {
  return <div className="card">{children}</div>
}

// Usage: Compose by nesting
<Card>
  <h2>Welcome</h2>
  <p>This is a card</p>
  <Button>Learn More</Button>
</Card>
```

**Why**: More flexible than props (can pass any JSX).

---

### 3. Containment (Slots)

**Multiple slots for different content areas**:

```jsx
// Component with multiple "slots"
function Dialog({ title, content, actions }) {
  return (
    <div className="dialog">
      <div className="dialog-header">{title}</div>
      <div className="dialog-body">{content}</div>
      <div className="dialog-actions">{actions}</div>
    </div>
  )
}

// Usage
<Dialog
  title={<h2>Confirm Delete</h2>}
  content={<p>Are you sure you want to delete this item?</p>}
  actions={
    <>
      <Button variant="secondary">Cancel</Button>
      <Button variant="danger">Delete</Button>
    </>
  }
/>
```

---

### 4. Specialization

**Create specific variants from generic components**:

```jsx
// Generic Dialog
function Dialog({ title, children, actions }) {
  return (
    <div className="dialog">
      <h2>{title}</h2>
      <div>{children}</div>
      <div className="actions">{actions}</div>
    </div>
  )
}

// Specialized: Confirm Dialog
function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <Dialog
      title="Confirm"
      actions={
        <>
          <Button onClick={onCancel}>Cancel</Button>
          <Button onClick={onConfirm} variant="danger">Confirm</Button>
        </>
      }
    >
      <p>{message}</p>
    </Dialog>
  )
}

// Specialized: Alert Dialog
function AlertDialog({ message, onClose }) {
  return (
    <Dialog
      title="Alert"
      actions={<Button onClick={onClose}>OK</Button>}
    >
      <p>{message}</p>
    </Dialog>
  )
}

// Usage
<ConfirmDialog
  message="Delete this item?"
  onConfirm={handleDelete}
  onCancel={handleCancel}
/>
```

**Why**: Reuse generic logic, customize for specific use cases.

---

## Single Responsibility Principle

**Each component should do ONE thing well.**

### ❌ Bad: Component doing too much

```jsx
// Bad: UserProfile does everything
function UserProfile({ userId }) {
  const [user, setUser] = useState(null)
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => setUser(data))

    fetch(`/api/users/${userId}/posts`)
      .then(res => res.json())
      .then(data => setPosts(data))
      .finally(() => setLoading(false))
  }, [userId])

  if (loading) return <Spinner />

  return (
    <div>
      <img src={user.avatar} alt={user.name} />
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
      <h2>Posts</h2>
      <ul>
        {posts.map(post => (
          <li key={post.id}>
            <h3>{post.title}</h3>
            <p>{post.body}</p>
            <span>{post.date}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
```

**Problems**:
- Fetches user AND posts (two responsibilities)
- Renders profile AND posts (two responsibilities)
- Hard to reuse (tightly coupled)
- Hard to test (too much logic)

---

### ✅ Good: Components with single responsibility

```jsx
// Component 1: Fetch user data
function useUser(userId) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => setUser(data))
      .finally(() => setLoading(false))
  }, [userId])

  return { user, loading }
}

// Component 2: Display user info
function UserInfo({ user }) {
  return (
    <div>
      <img src={user.avatar} alt={user.name} />
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  )
}

// Component 3: Fetch posts
function usePosts(userId) {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/users/${userId}/posts`)
      .then(res => res.json())
      .then(data => setPosts(data))
      .finally(() => setLoading(false))
  }, [userId])

  return { posts, loading }
}

// Component 4: Display post
function PostItem({ post }) {
  return (
    <li>
      <h3>{post.title}</h3>
      <p>{post.body}</p>
      <span>{post.date}</span>
    </li>
  )
}

// Component 5: Display posts list
function PostsList({ posts }) {
  return (
    <ul>
      {posts.map(post => (
        <PostItem key={post.id} post={post} />
      ))}
    </ul>
  )
}

// Component 6: Compose everything
function UserProfile({ userId }) {
  const { user, loading: userLoading } = useUser(userId)
  const { posts, loading: postsLoading } = usePosts(userId)

  if (userLoading || postsLoading) return <Spinner />

  return (
    <div>
      <UserInfo user={user} />
      <h2>Posts</h2>
      <PostsList posts={posts} />
    </div>
  )
}
```

**Benefits**:
- Each piece has ONE responsibility
- Easy to reuse (UserInfo, PostsList used elsewhere)
- Easy to test (test each piece separately)
- Easy to modify (change posts without touching user logic)

---

## Lifting State (When to Compose State)

**Share state by lifting to common ancestor**:

```jsx
// ❌ Bad: Duplicate state
function SearchInput() {
  const [query, setQuery] = useState('')
  return <input value={query} onChange={e => setQuery(e.target.value)} />
}

function SearchResults() {
  const [query, setQuery] = useState('')  // Duplicate!
  const { data } = useFetch(`/api/search?q=${query}`)
  return <Results data={data} />
}

// ✅ Good: Lift state to common ancestor
function SearchPage() {
  const [query, setQuery] = useState('')  // Single source of truth

  return (
    <>
      <SearchInput query={query} onQueryChange={setQuery} />
      <SearchResults query={query} />
    </>
  )
}

function SearchInput({ query, onQueryChange }) {
  return (
    <input
      value={query}
      onChange={e => onQueryChange(e.target.value)}
    />
  )
}

function SearchResults({ query }) {
  const { data } = useFetch(`/api/search?q=${query}`)
  return <Results data={data} />
}
```

**Why**: Single source of truth, components stay in sync.

---

## Component Categories

### Presentational Components (Dumb)

**Characteristics**:
- Focused on rendering (UI only)
- Receive data via props
- No state (or minimal UI state)
- No data fetching
- Highly reusable

**Example**:
```jsx
// Pure presentational component
function Button({ variant, children, onClick, ...props }) {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  )
}

function Card({ title, content, footer }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <p>{content}</p>
      <div className="footer">{footer}</div>
    </div>
  )
}
```

---

### Container Components (Smart)

**Characteristics**:
- Manage state and logic
- Fetch data from APIs
- Pass data to presentational components
- Coordinate interactions

**Example**:
```jsx
// Container component
function UserProfileContainer({ userId }) {
  const { data, loading, error } = useFetch(`/api/users/${userId}`)

  if (loading) return <Spinner />
  if (error) return <Error message={error.message} />

  return <UserProfile user={data} />
}

// Presentational component
function UserProfile({ user }) {
  return (
    <div>
      <Avatar src={user.avatar} alt={user.name} />
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  )
}
```

**Why**: Separation of concerns—logic separate from presentation.

---

## Composition Anti-Patterns

### ❌ Anti-Pattern 1: Prop Drilling (Too Deep)

```jsx
// Bad: Passing theme through 5 levels
<App theme={theme}>
  <Layout theme={theme}>
    <Sidebar theme={theme}>
      <Menu theme={theme}>
        <MenuItem theme={theme} />
      </Menu>
    </Sidebar>
  </Layout>
</App>

// Good: Context for deeply nested props
<ThemeProvider value={theme}>
  <App>
    <Layout>
      <Sidebar>
        <Menu>
          <MenuItem />  {/* Accesses theme via useContext */}
        </Menu>
      </Sidebar>
    </Layout>
  </App>
</ThemeProvider>
```

**Rule**: If prop drilling >3 levels, use Context.

---

### ❌ Anti-Pattern 2: Monolithic Components

```jsx
// Bad: 500-line component doing everything
function Dashboard() {
  // 50 lines of state
  // 100 lines of data fetching
  // 200 lines of event handlers
  // 150 lines of JSX
  return (/* huge JSX */)
}

// Good: Composed from smaller components
function Dashboard() {
  return (
    <>
      <DashboardHeader />
      <DashboardMetrics />
      <DashboardCharts />
      <DashboardActivity />
    </>
  )
}
```

**Rule**: If component >200 lines, break into smaller components.

---

### ❌ Anti-Pattern 3: Unnecessary Wrapper Components

```jsx
// Bad: Wrapper adds no value
function UserNameDisplay({ user }) {
  return <UserName user={user} />
}

function UserName({ user }) {
  return <span>{user.name}</span>
}

// Good: Skip unnecessary wrapper
function UserName({ user }) {
  return <span>{user.name}</span>
}
```

**Rule**: Every component should add value (state, logic, or meaningful abstraction).

---

## Composition Checklist

Before claiming component design complete:

- [ ] Each component has single responsibility?
- [ ] Components are composable (can combine easily)?
- [ ] Props API is clear and minimal?
- [ ] State lifted to appropriate level (not too high, not too low)?
- [ ] Presentational components separated from containers?
- [ ] No prop drilling >3 levels (use Context if needed)?
- [ ] Components are reusable across application?
- [ ] Components can be tested in isolation?

**If any unchecked, composition incomplete.**

---

## Summary

**Component composition principles**:
- Build complex from simple (composition over inheritance)
- Single responsibility (each component does ONE thing)
- Containment (nest components, use children prop)
- Specialization (generic → specific variants)
- Lift state to common ancestor (single source of truth)
- Separate presentation from logic (dumb vs smart components)

**Composition is React's superpower. Master it.**
