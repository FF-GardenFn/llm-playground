# Forms: Controlled Components

**Pattern**: Form inputs whose values are controlled by React state, creating a single source of truth.

**When to Use**:
- Need to validate input on change/blur
- Format input as user types (masks, uppercase, etc.)
- Conditional fields based on other inputs
- Dynamic form generation
- Multi-step forms with state persistence

**When NOT to Use**:
- Simple read-only forms (uncontrolled is simpler)
- File uploads (use uncontrolled with refs)
- Performance-critical with many inputs (consider uncontrolled or debouncing)

---

## Core Principle

**Single Source of Truth**: React state controls input value, not the DOM.

```tsx
// ❌ UNCONTROLLED: DOM is source of truth
<input type="text" defaultValue="Hello" />

// ✅ CONTROLLED: React state is source of truth
const [value, setValue] = useState('Hello')
<input type="text" value={value} onChange={e => setValue(e.target.value)} />
```

**Why Controlled**:
- Validate on every keystroke
- Format input dynamically
- Disable submit until valid
- Reset form programmatically
- Sync with external state (URL, local storage)

---

## Basic Controlled Input

```tsx
function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log({ email, password })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  )
}
```

---

## Form State Patterns

### Pattern 1: Object State (Multiple Fields)

**Use**: Form with many fields.

```tsx
interface FormState {
  email: string
  password: string
  rememberMe: boolean
}

function LoginForm() {
  const [values, setValues] = useState<FormState>({
    email: '',
    password: '',
    rememberMe: false,
  })

  const handleChange = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setValues(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log(values)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={values.email}
        onChange={handleChange('email')}
      />
      <input
        type="password"
        value={values.password}
        onChange={handleChange('password')}
      />
      <label>
        <input
          type="checkbox"
          checked={values.rememberMe}
          onChange={handleChange('rememberMe')}
        />
        Remember me
      </label>
      <button type="submit">Login</button>
    </form>
  )
}
```

### Pattern 2: useReducer (Complex Forms)

**Use**: Form with complex state updates, validation, async operations.

```tsx
type FormAction =
  | { type: 'SET_FIELD'; field: string; value: any }
  | { type: 'SET_ERROR'; field: string; error: string }
  | { type: 'SET_SUBMITTING'; submitting: boolean }
  | { type: 'RESET' }

interface FormState {
  values: Record<string, any>
  errors: Record<string, string>
  touched: Record<string, boolean>
  isSubmitting: boolean
}

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case 'SET_FIELD':
      return {
        ...state,
        values: { ...state.values, [action.field]: action.value },
        touched: { ...state.touched, [action.field]: true },
      }
    case 'SET_ERROR':
      return {
        ...state,
        errors: { ...state.errors, [action.field]: action.error },
      }
    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.submitting }
    case 'RESET':
      return {
        values: {},
        errors: {},
        touched: {},
        isSubmitting: false,
      }
    default:
      return state
  }
}

function RegistrationForm() {
  const [state, dispatch] = useReducer(formReducer, {
    values: { email: '', password: '', confirmPassword: '' },
    errors: {},
    touched: {},
    isSubmitting: false,
  })

  const handleChange = (field: string, value: any) => {
    dispatch({ type: 'SET_FIELD', field, value })
  }

  const validate = () => {
    const errors: Record<string, string> = {}
    if (!state.values.email.includes('@')) {
      errors.email = 'Invalid email'
    }
    if (state.values.password.length < 8) {
      errors.password = 'Password must be 8+ characters'
    }
    if (state.values.password !== state.values.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match'
    }
    return errors
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const errors = validate()

    if (Object.keys(errors).length > 0) {
      Object.entries(errors).forEach(([field, error]) => {
        dispatch({ type: 'SET_ERROR', field, error })
      })
      return
    }

    dispatch({ type: 'SET_SUBMITTING', submitting: true })
    try {
      await fetch('/api/register', {
        method: 'POST',
        body: JSON.stringify(state.values),
      })
    } finally {
      dispatch({ type: 'SET_SUBMITTING', submitting: false })
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={state.values.email}
        onChange={e => handleChange('email', e.target.value)}
      />
      {state.touched.email && state.errors.email && (
        <span className="error">{state.errors.email}</span>
      )}

      <input
        type="password"
        value={state.values.password}
        onChange={e => handleChange('password', e.target.value)}
      />
      {state.touched.password && state.errors.password && (
        <span className="error">{state.errors.password}</span>
      )}

      <input
        type="password"
        value={state.values.confirmPassword}
        onChange={e => handleChange('confirmPassword', e.target.value)}
      />
      {state.touched.confirmPassword && state.errors.confirmPassword && (
        <span className="error">{state.errors.confirmPassword}</span>
      )}

      <button type="submit" disabled={state.isSubmitting}>
        {state.isSubmitting ? 'Registering...' : 'Register'}
      </button>
    </form>
  )
}
```

---

## Input Types

### Text Input

```tsx
const [text, setText] = useState('')

<input
  type="text"
  value={text}
  onChange={e => setText(e.target.value)}
  placeholder="Enter text"
/>
```

### Textarea

```tsx
const [message, setMessage] = useState('')

<textarea
  value={message}
  onChange={e => setMessage(e.target.value)}
  rows={5}
  placeholder="Enter message"
/>
```

### Checkbox

```tsx
const [agreed, setAgreed] = useState(false)

<label>
  <input
    type="checkbox"
    checked={agreed}
    onChange={e => setAgreed(e.target.checked)}
  />
  I agree to terms
</label>
```

### Radio Buttons

```tsx
const [size, setSize] = useState('medium')

<div>
  <label>
    <input
      type="radio"
      value="small"
      checked={size === 'small'}
      onChange={e => setSize(e.target.value)}
    />
    Small
  </label>
  <label>
    <input
      type="radio"
      value="medium"
      checked={size === 'medium'}
      onChange={e => setSize(e.target.value)}
    />
    Medium
  </label>
  <label>
    <input
      type="radio"
      value="large"
      checked={size === 'large'}
      onChange={e => setSize(e.target.value)}
    />
    Large
  </label>
</div>
```

### Select Dropdown

```tsx
const [country, setCountry] = useState('us')

<select value={country} onChange={e => setCountry(e.target.value)}>
  <option value="us">United States</option>
  <option value="ca">Canada</option>
  <option value="uk">United Kingdom</option>
</select>
```

### Multi-Select

```tsx
const [selectedOptions, setSelectedOptions] = useState<string[]>([])

<select
  multiple
  value={selectedOptions}
  onChange={e => {
    const selected = Array.from(e.target.selectedOptions, option => option.value)
    setSelectedOptions(selected)
  }}
>
  <option value="option1">Option 1</option>
  <option value="option2">Option 2</option>
  <option value="option3">Option 3</option>
</select>
```

---

## Input Formatting

### Pattern: Format on Change

**Use**: Format as user types (phone, credit card, currency).

```tsx
function formatPhoneNumber(value: string): string {
  const digits = value.replace(/\D/g, '')
  if (digits.length <= 3) return digits
  if (digits.length <= 6) return `(${digits.slice(0, 3)}) ${digits.slice(3)}`
  return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6, 10)}`
}

function PhoneInput() {
  const [phone, setPhone] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhoneNumber(e.target.value)
    setPhone(formatted)
  }

  return (
    <input
      type="tel"
      value={phone}
      onChange={handleChange}
      placeholder="(555) 123-4567"
    />
  )
}
```

### Pattern: Controlled Uppercase

```tsx
const [code, setCode] = useState('')

<input
  type="text"
  value={code}
  onChange={e => setCode(e.target.value.toUpperCase())}
  placeholder="PROMO"
/>
```

### Pattern: Max Length Enforcement

```tsx
const [code, setCode] = useState('')

<input
  type="text"
  value={code}
  onChange={e => {
    const value = e.target.value
    if (value.length <= 6) {
      setCode(value)
    }
  }}
  placeholder="Enter 6-digit code"
/>
```

---

## Performance Optimization

### Pattern 1: Debounce onChange

**Problem**: Expensive operations on every keystroke (API calls, validation).

```tsx
import { useDebouncedValue } from '@/hooks/useDebouncedValue'

function SearchForm() {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebouncedValue(query, 300)

  useEffect(() => {
    if (debouncedQuery) {
      // Expensive API call only fires after 300ms of no typing
      fetch(`/api/search?q=${debouncedQuery}`)
    }
  }, [debouncedQuery])

  return (
    <input
      type="search"
      value={query}
      onChange={e => setQuery(e.target.value)}
      placeholder="Search..."
    />
  )
}
```

### Pattern 2: Controlled with defaultValue (Hybrid)

**Problem**: Controlled inputs cause re-renders on every keystroke.

**Solution**: Start uncontrolled, sync to state on blur.

```tsx
function HybridInput() {
  const [value, setValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleBlur = () => {
    if (inputRef.current) {
      setValue(inputRef.current.value)
    }
  }

  return (
    <input
      ref={inputRef}
      type="text"
      defaultValue={value}
      onBlur={handleBlur}
    />
  )
}
```

**When to Use**: Large forms (>20 inputs) where re-renders are expensive.

---

## Accessibility

### Label Association

```tsx
// ✅ GOOD: Explicit label association
<label htmlFor="email">Email</label>
<input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} />

// OR: Implicit (label wraps input)
<label>
  Email
  <input type="email" value={email} onChange={e => setEmail(e.target.value)} />
</label>
```

### Error Announcements

```tsx
<input
  type="email"
  value={email}
  onChange={e => setEmail(e.target.value)}
  aria-invalid={!!error}
  aria-describedby={error ? 'email-error' : undefined}
/>
{error && (
  <span id="email-error" role="alert" className="error">
    {error}
  </span>
)}
```

### Required Fields

```tsx
<label htmlFor="email">
  Email <span aria-label="required">*</span>
</label>
<input
  id="email"
  type="email"
  value={email}
  onChange={e => setEmail(e.target.value)}
  required
  aria-required="true"
/>
```

---

## Testing

```tsx
describe('LoginForm', () => {
  test('updates email on change', () => {
    render(<LoginForm />)
    const emailInput = screen.getByPlaceholderText('Email')

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

    expect(emailInput).toHaveValue('test@example.com')
  })

  test('submits form with values', () => {
    const onSubmit = jest.fn()
    render(<LoginForm onSubmit={onSubmit} />)

    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'test@example.com' },
    })
    fireEvent.change(screen.getByPlaceholderText('Password'), {
      target: { value: 'password123' },
    })
    fireEvent.click(screen.getByText('Login'))

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    })
  })

  test('shows error for invalid email', () => {
    render(<LoginForm />)

    fireEvent.change(screen.getByPlaceholderText('Email'), {
      target: { value: 'invalid' },
    })
    fireEvent.blur(screen.getByPlaceholderText('Email'))

    expect(screen.getByText('Invalid email')).toBeInTheDocument()
  })
})
```

---

## Anti-Patterns

### 1. Mixing Controlled and Uncontrolled

```tsx
// ❌ BAD: Sometimes controlled, sometimes uncontrolled
const [value, setValue] = useState<string | undefined>(undefined)
<input value={value} onChange={e => setValue(e.target.value)} />
// Result: Warning "component is changing from uncontrolled to controlled"

// ✅ GOOD: Always controlled (initialize to empty string)
const [value, setValue] = useState('')
<input value={value} onChange={e => setValue(e.target.value)} />
```

### 2. Not Preventing Default on Submit

```tsx
// ❌ BAD: Form triggers page reload
<form onSubmit={() => console.log('submit')}>

// ✅ GOOD: Prevent default behavior
<form onSubmit={(e) => { e.preventDefault(); console.log('submit'); }}>
```

### 3. Inline Functions in onChange

```tsx
// ❌ BAD: New function on every render
<input value={email} onChange={e => setEmail(e.target.value)} />

// ✅ GOOD: Extract if used multiple times or causing performance issues
const handleEmailChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
  setEmail(e.target.value)
}, [])

<input value={email} onChange={handleEmailChange} />
```

---

## Summary

**Controlled Form Pattern**:
- React state controls input values (single source of truth)
- Use `value` + `onChange` for inputs
- Use `checked` + `onChange` for checkboxes/radios

**When to Use**:
- Need validation on change/blur
- Format input as user types
- Conditional fields
- Multi-step forms

**State Patterns**:
- Simple forms: Multiple `useState`
- Many fields: Single object state
- Complex forms: `useReducer`

**Performance**:
- Debounce expensive operations
- Consider uncontrolled for large forms

**Accessibility**:
- Associate labels with inputs
- Use `aria-invalid` and `aria-describedby` for errors
- Mark required fields

**Result**: Full control over form behavior with React as single source of truth.
