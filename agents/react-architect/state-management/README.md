# State Management Decision Tree

**Purpose**: Choose the right state management approach for your React application.

State management is not one-size-fits-all. The decision depends on state scope, complexity, and data source.

---

## Decision Tree

```
Is this server data (fetched from API)?
├─ Yes → React Query or SWR (patterns/data-fetching/)
│         Server state has different concerns (caching, refetching, synchronization)
│         Don't manage in Redux/Context - use specialized tools
│
└─ No (UI state) → Continue

Is state used by single component only?
├─ Yes → useState or useReducer (state-management/local/)
│         Keep state local when possible (component encapsulation)
│         useState: Simple state (string, number, boolean, single object)
│         useReducer: Complex state logic, multiple related actions
│
└─ No (shared state) → Continue

Is state shared by 2-3 closely related components?
├─ Yes → Lift state to common ancestor (state-management/local/lifting-state.md)
│         Simple prop passing if components are close in tree
│         Avoid context overhead for small, local sharing
│
└─ No (widely shared) → Continue

Is state theme, auth, or i18n?
├─ Yes → Context API (state-management/context/)
│         Perfect for global config that changes infrequently
│         Split contexts by concern (don't put everything in one)
│         Memoize context value to prevent re-renders
│
└─ No (complex global state) → Continue

Do you need time-travel debugging or complex state interactions?
├─ Yes → Redux Toolkit (state-management/external/redux.md)
│         Large applications with complex state logic
│         Predictable state container
│         DevTools for debugging
│
└─ No → Continue

Do you need simple global state with minimal boilerplate?
├─ Yes → Zustand (state-management/external/zustand.md)
│         Simple API, no provider needed
│         Perfect for medium-sized apps
│
└─ No → Jotai (state-management/external/jotai.md)
          Atomic state management
          Bottom-up composition
          Derived state easy
```

---

## State Categories

### 1. Server State

**Characteristics**:
- Fetched from remote source (API, database)
- Cached locally (stale data acceptable temporarily)
- Needs refetching, synchronization
- Owned by server (source of truth elsewhere)

**Tools**:
- **React Query** (recommended): Full-featured, caching, refetching, mutations
- **SWR**: Simpler, stale-while-revalidate pattern
- **Apollo Client**: For GraphQL specifically

**Examples**:
- User profile data
- Product listings
- Blog posts
- Search results

**Don't use**: Redux, Context, local state for server data

**File**: patterns/data-fetching/react-query.md

---

### 2. Local State

**Characteristics**:
- Used by single component
- Not shared with others
- Simple scope and lifecycle

**Tools**:
- **useState**: Simple values (string, number, boolean, single object)
- **useReducer**: Complex state logic, multiple actions, state machine

**Examples**:
- Form input values (controlled components)
- Modal open/closed state
- Toggle switches
- Dropdown expanded state

**File**: state-management/local/useState.md

**When to use useState**:
```jsx
// ✅ Good: Simple state
function Toggle() {
  const [isOn, setIsOn] = useState(false)
  return <button onClick={() => setIsOn(!isOn)}>{isOn ? 'On' : 'Off'}</button>
}
```

**When to use useReducer**:
```jsx
// ✅ Good: Complex state with multiple actions
function ShoppingCart() {
  const [state, dispatch] = useReducer(cartReducer, initialState)

  return (
    <>
      <button onClick={() => dispatch({ type: 'ADD_ITEM', item })}>Add</button>
      <button onClick={() => dispatch({ type: 'REMOVE_ITEM', id })}>Remove</button>
      <button onClick={() => dispatch({ type: 'CLEAR_CART' })}>Clear</button>
    </>
  )
}
```

---

### 3. Lifted State

**Characteristics**:
- Shared by 2-3 closely related components
- Components are close in component tree
- Simple prop passing sufficient

**Pattern**: Move state to nearest common ancestor

**Examples**:
- Parent component with multiple child forms
- Wizard/stepper with multiple steps
- Filter controls and filtered list

**File**: state-management/local/lifting-state.md

**Example**:
```jsx
// ✅ Good: Lifted state
function SearchPage() {
  const [query, setQuery] = useState('')

  return (
    <>
      <SearchInput query={query} onQueryChange={setQuery} />
      <SearchResults query={query} />
    </>
  )
}
```

**When to stop lifting**:
- Prop drilling >3 levels deep → Use Context
- Many unrelated components need state → Use global state

---

### 4. Context State

**Characteristics**:
- Shared by many components across tree
- Changes infrequently (theme, auth, language)
- Avoids prop drilling

**Use for**:
- Theme (light/dark mode)
- Authentication (user, login/logout)
- Internationalization (language, translations)
- UI state (sidebar open/closed, modal stack)

**Don't use for**:
- Frequently changing state (causes re-renders)
- Server data (use React Query/SWR)
- Complex state logic (use Redux/Zustand)

**File**: state-management/context/context-api.md

**Example**:
```jsx
// ✅ Good: Theme context (changes infrequently)
const ThemeContext = createContext()

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light')

  // Memoize to prevent re-renders
  const value = useMemo(
    () => ({ theme, setTheme }),
    [theme]
  )

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

// Usage
function Button() {
  const { theme } = useContext(ThemeContext)
  return <button className={theme}>Click me</button>
}
```

**Optimization**: Split contexts by concern
```jsx
// ✅ Good: Separate contexts
<AuthProvider>
  <ThemeProvider>
    <I18nProvider>
      <App />
    </I18nProvider>
  </ThemeProvider>
</AuthProvider>

// ❌ Bad: One giant context
<AppProvider value={{ auth, theme, i18n, ... }}>
  <App />
</AppProvider>
```

**File**: state-management/context/optimization.md

---

### 5. Global State (Redux)

**Characteristics**:
- Large application, complex state
- State interactions between distant components
- Time-travel debugging needed
- Predictable state updates required

**Use Redux Toolkit when**:
- Application is large (>50 components)
- Complex state logic (many actions, state slices)
- Need DevTools (time-travel, state inspection)
- Team familiar with Redux patterns

**Don't use Redux when**:
- Application is small (useState/Context sufficient)
- State is simple (overkill for basic needs)
- Only server data (use React Query/SWR)

**File**: state-management/external/redux.md

**Example**:
```jsx
// Redux Toolkit slice
import { createSlice } from '@reduxjs/toolkit'

const cartSlice = createSlice({
  name: 'cart',
  initialState: { items: [], total: 0 },
  reducers: {
    addItem: (state, action) => {
      state.items.push(action.payload)
      state.total += action.payload.price
    },
    removeItem: (state, action) => {
      const index = state.items.findIndex(item => item.id === action.payload)
      state.total -= state.items[index].price
      state.items.splice(index, 1)
    }
  }
})

// Usage
function Cart() {
  const dispatch = useDispatch()
  const items = useSelector(state => state.cart.items)

  return (
    <>
      {items.map(item => (
        <div key={item.id}>
          {item.name}
          <button onClick={() => dispatch(cartSlice.actions.removeItem(item.id))}>
            Remove
          </button>
        </div>
      ))}
    </>
  )
}
```

---

### 6. Global State (Zustand)

**Characteristics**:
- Simple global state without Redux boilerplate
- No provider needed (hooks-based)
- Perfect for medium-sized apps

**Use Zustand when**:
- Need global state but Redux is overkill
- Want minimal boilerplate
- Application is medium-sized (20-50 components)
- Don't need time-travel debugging

**File**: state-management/external/zustand.md

**Example**:
```jsx
// Create store
import create from 'zustand'

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 }))
}))

// Usage (no provider needed!)
function Counter() {
  const count = useStore((state) => state.count)
  const increment = useStore((state) => state.increment)

  return (
    <div>
      <p>{count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  )
}
```

---

### 7. Atomic State (Jotai)

**Characteristics**:
- Bottom-up composition (atoms combine to form state)
- Minimal re-renders (only subscribes to atoms used)
- Derived state easy

**Use Jotai when**:
- Want atomic state management (like Recoil)
- Need fine-grained reactivity (minimal re-renders)
- Complex derived state (computed from other atoms)

**File**: state-management/external/jotai.md

**Example**:
```jsx
// Define atoms
import { atom, useAtom } from 'jotai'

const countAtom = atom(0)
const doubleCountAtom = atom((get) => get(countAtom) * 2)

// Usage
function Counter() {
  const [count, setCount] = useAtom(countAtom)
  const [doubleCount] = useAtom(doubleCountAtom)

  return (
    <div>
      <p>Count: {count}</p>
      <p>Double: {doubleCount}</p>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
    </div>
  )
}
```

---

## Common Decision Patterns

### Pattern 1: Authentication

**State type**: Global, changes infrequently

**Solution**: Context API
```jsx
const AuthContext = createContext()

function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  const login = async (credentials) => {
    const user = await api.login(credentials)
    setUser(user)
  }

  const logout = () => setUser(null)

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
```

**File**: state-management/context/auth-pattern.md

---

### Pattern 2: Form State

**State type**: Local, component-specific

**Solution**: useState or useReducer (or React Hook Form)
```jsx
// Simple form: useState
function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  return (
    <form>
      <input value={email} onChange={e => setEmail(e.target.value)} />
      <input value={password} onChange={e => setPassword(e.target.value)} />
    </form>
  )
}

// Complex form: React Hook Form
import { useForm } from 'react-hook-form'

function RegistrationForm() {
  const { register, handleSubmit } = useForm()

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      <input {...register('password')} />
      <button type="submit">Submit</button>
    </form>
  )
}
```

**File**: patterns/forms/controlled-forms.md

---

### Pattern 3: Data Table (Server State)

**State type**: Server data, needs caching/refetching

**Solution**: React Query
```jsx
import { useQuery } from '@tanstack/react-query'

function UserTable() {
  const { data, isLoading, error } = useQuery(
    ['users'],
    () => fetch('/api/users').then(res => res.json())
  )

  if (isLoading) return <Spinner />
  if (error) return <Error message={error.message} />

  return (
    <table>
      {data.map(user => (
        <tr key={user.id}>
          <td>{user.name}</td>
          <td>{user.email}</td>
        </tr>
      ))}
    </table>
  )
}
```

**File**: patterns/data-fetching/react-query.md

---

### Pattern 4: E-Commerce Cart

**State type**: Complex global state, many interactions

**Solution**: Redux Toolkit or Zustand

**Redux Toolkit** (large app, time-travel debugging):
```jsx
const cartSlice = createSlice({
  name: 'cart',
  initialState: { items: [], total: 0 },
  reducers: {
    addItem: (state, action) => { /* ... */ },
    removeItem: (state, action) => { /* ... */ },
    updateQuantity: (state, action) => { /* ... */ },
    clearCart: (state) => { /* ... */ }
  }
})
```

**Zustand** (medium app, minimal boilerplate):
```jsx
const useCartStore = create((set) => ({
  items: [],
  total: 0,
  addItem: (item) => set((state) => ({
    items: [...state.items, item],
    total: state.total + item.price
  })),
  removeItem: (id) => set((state) => {
    const item = state.items.find(i => i.id === id)
    return {
      items: state.items.filter(i => i.id !== id),
      total: state.total - item.price
    }
  })
}))
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Everything in Redux

```jsx
// Bad: Redux for server data
const usersSlice = createSlice({
  name: 'users',
  initialState: { data: [], loading: false },
  reducers: {
    fetchUsersStart: (state) => { state.loading = true },
    fetchUsersSuccess: (state, action) => {
      state.data = action.payload
      state.loading = false
    }
  }
})

// Good: React Query for server data
const { data, isLoading } = useQuery(['users'], fetchUsers)
```

**Why**: React Query handles caching, refetching, error handling automatically.

---

### ❌ Anti-Pattern 2: Context for Frequently Changing State

```jsx
// Bad: Counter in context (changes frequently)
const CounterContext = createContext()

function App() {
  const [count, setCount] = useState(0)

  // Every increment re-renders entire tree!
  return (
    <CounterContext.Provider value={{ count, setCount }}>
      <DeepComponentTree />
    </CounterContext.Provider>
  )
}

// Good: Local state or Zustand
function Counter() {
  const [count, setCount] = useState(0)  // Local to component
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

**Why**: Context causes all consumers to re-render on every change.

---

### ❌ Anti-Pattern 3: Prop Drilling Instead of Context

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

// Good: Context for theme
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

**Why**: Context eliminates prop drilling for global config.

---

## Summary

**Decision tree guides state management**:
1. Server data? → React Query/SWR
2. Local to component? → useState/useReducer
3. Shared by 2-3 components? → Lift state
4. Theme/auth/i18n? → Context API
5. Complex global state? → Redux Toolkit
6. Simple global state? → Zustand
7. Atomic state? → Jotai

**Files to load**:
- Local: state-management/local/
- Context: state-management/context/
- External: state-management/external/
- Server: patterns/data-fetching/

**Navigate from question to solution via decision tree.**
