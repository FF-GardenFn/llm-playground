# Custom Hooks Pattern

**Pattern Type**: Composition
**Complexity**: Low-Medium
**When**: Reusable stateful logic across components

---

## When to Use

**Good fit when**:
- Logic used in multiple components (don't repeat yourself)
- Stateful logic separable from UI (business logic vs presentation)
- Component becomes too complex (extract logic to simplify)
- Side effects need organization (separate concerns)

**Poor fit when**:
- Logic used once (keep in component)
- Logic is purely computational (use utility function)
- UI and logic are tightly coupled

---

## Pattern Structure

**Custom Hook**:
- Function name starts with `use` (React convention)
- Can use other hooks (useState, useEffect, etc.)
- Returns values/functions for component to use
- Encapsulates stateful logic

**Component using hook**:
- Calls custom hook
- Receives state and functions
- Focuses on rendering, not logic

---

## Basic Example: useToggle

### Implementation

```jsx
import { useState, useCallback } from 'react'

function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue)

  const toggle = useCallback(() => {
    setValue(v => !v)
  }, [])

  const setTrue = useCallback(() => {
    setValue(true)
  }, [])

  const setFalse = useCallback(() => {
    setValue(false)
  }, [])

  return [value, toggle, setTrue, setFalse]
}

export default useToggle
```

### Usage

```jsx
function Modal() {
  const [isOpen, toggle, open, close] = useToggle(false)

  return (
    <>
      <button onClick={open}>Open Modal</button>
      {isOpen && (
        <div className="modal">
          <h2>Modal Content</h2>
          <button onClick={close}>Close</button>
        </div>
      )}
    </>
  )
}

function Sidebar() {
  const [isExpanded, toggle] = useToggle(true)

  return (
    <aside className={isExpanded ? 'expanded' : 'collapsed'}>
      <button onClick={toggle}>Toggle</button>
      {/* Sidebar content */}
    </aside>
  )
}
```

**Why**: Toggle logic reused across Modal, Sidebar, Dropdown, etc.

---

## Common Custom Hooks

### useDebounce

**Problem**: Search input triggers API call on every keystroke (expensive)

**Solution**: Debounce value updates

```jsx
import { useState, useEffect } from 'react'

function useDebounce(value, delay = 500) {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

// Usage
function SearchInput() {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, 300)

  const { data } = useQuery(
    ['search', debouncedQuery],
    () => fetch(`/api/search?q=${debouncedQuery}`)
  )

  return (
    <>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search..."
      />
      <SearchResults results={data} />
    </>
  )
}
```

**Why**: API called only after user stops typing (300ms delay).

---

### useLocalStorage

**Problem**: Persist state to localStorage (boilerplate in every component)

**Solution**: Custom hook handles persistence

```jsx
import { useState, useEffect } from 'react'

function useLocalStorage(key, initialValue) {
  // State to store value
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(error)
      return initialValue
    }
  })

  // Return wrapped version of useState's setter that persists to localStorage
  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(error)
    }
  }

  return [storedValue, setValue]
}

// Usage
function Settings() {
  const [theme, setTheme] = useLocalStorage('theme', 'light')
  const [fontSize, setFontSize] = useLocalStorage('fontSize', 16)

  return (
    <div>
      <select value={theme} onChange={e => setTheme(e.target.value)}>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>

      <input
        type="number"
        value={fontSize}
        onChange={e => setFontSize(Number(e.target.value))}
      />
    </div>
  )
}
```

**Why**: Settings persist across page reloads automatically.

---

### useFetch

**Problem**: Data fetching logic repeated across components

**Solution**: Extract to custom hook

```jsx
import { useState, useEffect } from 'react'

function useFetch(url) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const response = await fetch(url)
        if (!response.ok) throw new Error('Network response was not ok')
        const json = await response.json()
        setData(json)
        setError(null)
      } catch (err) {
        setError(err.message)
        setData(null)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [url])

  return { data, loading, error }
}

// Usage
function UserProfile({ userId }) {
  const { data, loading, error } = useFetch(`/api/users/${userId}`)

  if (loading) return <Spinner />
  if (error) return <Error message={error} />
  if (!data) return null

  return (
    <div>
      <h2>{data.name}</h2>
      <p>{data.email}</p>
    </div>
  )
}
```

**Note**: For production, use React Query or SWR instead (better caching, refetching).

---

### useForm

**Problem**: Form state management boilerplate

**Solution**: Custom hook handles inputs, validation, submission

```jsx
import { useState } from 'react'

function useForm(initialValues, onSubmit) {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setValues(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      await onSubmit(values)
    } catch (err) {
      setErrors(err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const reset = () => {
    setValues(initialValues)
    setErrors({})
  }

  return {
    values,
    errors,
    isSubmitting,
    handleChange,
    handleSubmit,
    reset
  }
}

// Usage
function LoginForm() {
  const { values, errors, isSubmitting, handleChange, handleSubmit } = useForm(
    { email: '', password: '' },
    async (values) => {
      const response = await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify(values)
      })
      if (!response.ok) throw await response.json()
    }
  )

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="email"
        value={values.email}
        onChange={handleChange}
      />
      {errors.email && <span>{errors.email}</span>}

      <input
        name="password"
        type="password"
        value={values.password}
        onChange={handleChange}
      />
      {errors.password && <span>{errors.password}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  )
}
```

**Note**: For production, use React Hook Form or Formik (better validation, performance).

---

### useClickOutside

**Problem**: Close dropdown/modal when clicking outside (common pattern)

**Solution**: Custom hook handles click detection

```jsx
import { useEffect, useRef } from 'react'

function useClickOutside(callback) {
  const ref = useRef(null)

  useEffect(() => {
    const handleClick = (event) => {
      if (ref.current && !ref.current.contains(event.target)) {
        callback()
      }
    }

    document.addEventListener('mousedown', handleClick)
    return () => {
      document.removeEventListener('mousedown', handleClick)
    }
  }, [callback])

  return ref
}

// Usage
function Dropdown() {
  const [isOpen, , , close] = useToggle(false)
  const dropdownRef = useClickOutside(close)

  return (
    <div ref={dropdownRef}>
      <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
      {isOpen && (
        <ul className="dropdown-menu">
          <li>Option 1</li>
          <li>Option 2</li>
          <li>Option 3</li>
        </ul>
      )}
    </div>
  )
}
```

---

### useMediaQuery

**Problem**: Responsive behavior based on screen size

**Solution**: Custom hook tracks media query

```jsx
import { useState, useEffect } from 'react'

function useMediaQuery(query) {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)

    if (media.matches !== matches) {
      setMatches(media.matches)
    }

    const listener = () => setMatches(media.matches)
    media.addEventListener('change', listener)

    return () => media.removeEventListener('change', listener)
  }, [matches, query])

  return matches
}

// Usage
function ResponsiveLayout() {
  const isMobile = useMediaQuery('(max-width: 768px)')
  const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)')
  const isDesktop = useMediaQuery('(min-width: 1025px)')

  return (
    <div>
      {isMobile && <MobileNav />}
      {isTablet && <TabletNav />}
      {isDesktop && <DesktopNav />}
    </div>
  )
}
```

---

## Best Practices

### 1. Name with `use` Prefix

```jsx
// ✅ Good: Follows convention
function useToggle() { /* ... */ }
function useDebounce() { /* ... */ }
function useAuth() { /* ... */ }

// ❌ Bad: No `use` prefix
function toggle() { /* ... */ }  // Looks like utility function
function debounce() { /* ... */ }
```

**Why**: React relies on `use` prefix to enforce hook rules.

---

### 2. Return Array or Object

**Return array** when order matters, few values:
```jsx
// ✅ Good: Array for simple hooks
const [value, toggle] = useToggle()
const [user, setUser] = useState()
```

**Return object** when many values, named access better:
```jsx
// ✅ Good: Object for complex hooks
const { data, loading, error, refetch } = useFetch('/api/users')
const { values, errors, handleChange, handleSubmit } = useForm()
```

---

### 3. Keep Hooks Focused

```jsx
// ✅ Good: Single responsibility
function useDebounce(value, delay) { /* ... */ }
function useLocalStorage(key, initialValue) { /* ... */ }

// ❌ Bad: Doing too much
function useEverything() {
  const [value, setValue] = useState()
  const [debounced] = useDebounce(value)
  const [stored, setStored] = useLocalStorage('key', value)
  const { data } = useFetch('/api')
  // Too many concerns in one hook
}
```

**Why**: Small, focused hooks are reusable and testable.

---

### 4. Document Dependencies

```jsx
// ✅ Good: Clear dependencies
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(handler)
  }, [value, delay])  // Dependencies clear

  return debouncedValue
}
```

---

### 5. Memoize Callbacks

```jsx
// ✅ Good: Memoized callbacks
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue)

  const toggle = useCallback(() => {
    setValue(v => !v)
  }, [])

  return [value, toggle]
}

// ❌ Bad: New function on every render
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue)

  const toggle = () => {  // New function every render
    setValue(v => !v)
  }

  return [value, toggle]
}
```

**Why**: Prevents unnecessary re-renders in components using hook.

---

## Testing Custom Hooks

### Use @testing-library/react-hooks

```jsx
import { renderHook, act } from '@testing-library/react-hooks'
import useToggle from './useToggle'

test('useToggle toggles value', () => {
  const { result } = renderHook(() => useToggle(false))

  expect(result.current[0]).toBe(false)

  act(() => {
    result.current[1]()  // Call toggle
  })

  expect(result.current[0]).toBe(true)
})

test('useToggle setTrue sets value to true', () => {
  const { result } = renderHook(() => useToggle(false))

  act(() => {
    result.current[2]()  // Call setTrue
  })

  expect(result.current[0]).toBe(true)
})
```

---

## Common Mistakes

### ❌ Mistake 1: Calling Hooks Conditionally

```jsx
// Bad: Conditional hook call
function MyComponent({ shouldFetch }) {
  if (shouldFetch) {
    const { data } = useFetch('/api/data')  // ❌ Breaks hook rules
  }
}

// Good: Hook called unconditionally
function MyComponent({ shouldFetch }) {
  const { data } = useFetch(shouldFetch ? '/api/data' : null)  // ✅
}
```

**Why**: Hooks must be called in same order every render.

---

### ❌ Mistake 2: Not Memoizing Return Values

```jsx
// Bad: Creating new objects every render
function useUser() {
  const [user, setUser] = useState(null)

  return {  // ❌ New object every render
    user,
    setUser
  }
}

// Good: Memoized return value
function useUser() {
  const [user, setUser] = useState(null)

  return useMemo(() => ({  // ✅ Only new object when user changes
    user,
    setUser
  }), [user])
}
```

---

### ❌ Mistake 3: Hook Calling Hook Without `use` Prefix

```jsx
// Bad: Helper function uses hooks (violates rules)
function validateForm(values) {
  const [errors, setErrors] = useState({})  // ❌ Not a hook (no `use` prefix)
  // ...
}

// Good: Custom hook with `use` prefix
function useFormValidation(values) {
  const [errors, setErrors] = useState({})  // ✅ Custom hook
  // ...
  return errors
}
```

---

## When Not to Use Custom Hooks

**Don't create custom hook when**:
1. **Logic used once**: Keep in component
2. **Pure function**: Use utility function instead
3. **No hooks needed**: Regular function sufficient

**Example**:
```jsx
// ❌ Don't need custom hook (pure function)
function useFormatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

// ✅ Use utility function
function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}
```

---

## Related Patterns

**Also consider**:
- **Compound Components**: When sharing state between related components
- **Render Props**: When need rendering control
- **HOC**: When wrapping components with behavior

**See also**:
- patterns/composition/compound-components.md
- patterns/composition/render-props.md
- patterns/composition/hoc.md

---

## Summary

**Custom hooks pattern**:
- ✅ Reusable stateful logic
- ✅ Separates logic from UI
- ✅ Simplifies components
- ✅ Testable in isolation

**Use when**: Stateful logic used in multiple components

**Avoid when**: Logic used once, pure function, no hooks needed

**Name with `use` prefix, keep focused, memoize callbacks.**
