# Forms: Validation

**Pattern**: Verify user input meets requirements before submission, providing clear feedback.

**When to Use**:
- User input must meet constraints (email format, password length, etc.)
- Prevent invalid data from reaching API
- Guide user to correct errors
- Multi-step forms with validation gates

**When NOT to Use**:
- Read-only forms
- Simple search inputs (no constraints)
- Forms where any input is valid

---

## Core Principle

**Validate Early, Validate Often**: Check on blur, before submit, never block typing.

**Validation Timing**:
1. **On Blur**: Validate field when user leaves it (most common)
2. **On Submit**: Final validation before API call (always do this)
3. **On Change**: Real-time validation (use sparingly - can be distracting)

```tsx
// ❌ BAD: Validate on every keystroke (annoying)
<input
  value={email}
  onChange={e => {
    setEmail(e.target.value)
    if (!e.target.value.includes('@')) {
      setError('Invalid email')  // Shows error while still typing!
    }
  }}
/>

// ✅ GOOD: Validate on blur
<input
  value={email}
  onChange={e => setEmail(e.target.value)}
  onBlur={() => {
    if (!email.includes('@')) {
      setError('Invalid email')
    }
  }}
/>
```

---

## Basic Validation Pattern

```tsx
interface FormState {
  email: string
  password: string
}

interface FormErrors {
  email?: string
  password?: string
}

function LoginForm() {
  const [values, setValues] = useState<FormState>({ email: '', password: '' })
  const [errors, setErrors] = useState<FormErrors>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const validate = (field: keyof FormState, value: string): string | undefined => {
    switch (field) {
      case 'email':
        if (!value) return 'Email is required'
        if (!value.includes('@')) return 'Invalid email format'
        return undefined

      case 'password':
        if (!value) return 'Password is required'
        if (value.length < 8) return 'Password must be at least 8 characters'
        return undefined

      default:
        return undefined
    }
  }

  const handleChange = (field: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setValues(prev => ({ ...prev, [field]: e.target.value }))
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  const handleBlur = (field: keyof FormState) => () => {
    setTouched(prev => ({ ...prev, [field]: true }))
    const error = validate(field, values[field])
    setErrors(prev => ({ ...prev, [field]: error }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate all fields
    const newErrors: FormErrors = {}
    Object.keys(values).forEach(field => {
      const error = validate(field as keyof FormState, values[field as keyof FormState])
      if (error) newErrors[field as keyof FormErrors] = error
    })

    setErrors(newErrors)

    // Only submit if no errors
    if (Object.keys(newErrors).length === 0) {
      console.log('Submit:', values)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={values.email}
          onChange={handleChange('email')}
          onBlur={handleBlur('email')}
          aria-invalid={touched.email && !!errors.email}
          aria-describedby={touched.email && errors.email ? 'email-error' : undefined}
        />
        {touched.email && errors.email && (
          <span id="email-error" role="alert" className="error">
            {errors.email}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={values.password}
          onChange={handleChange('password')}
          onBlur={handleBlur('password')}
          aria-invalid={touched.password && !!errors.password}
          aria-describedby={touched.password && errors.password ? 'password-error' : undefined}
        />
        {touched.password && errors.password && (
          <span id="password-error" role="alert" className="error">
            {errors.password}
          </span>
        )}
      </div>

      <button type="submit">Login</button>
    </form>
  )
}
```

---

## Validation Rules

### Required Field

```tsx
if (!value) return 'This field is required'
if (!value.trim()) return 'This field cannot be empty'
```

### Email Format

```tsx
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
if (!emailRegex.test(value)) return 'Invalid email format'

// OR: Simple check
if (!value.includes('@')) return 'Invalid email format'
```

### Password Strength

```tsx
if (value.length < 8) return 'Password must be at least 8 characters'
if (!/[A-Z]/.test(value)) return 'Password must contain an uppercase letter'
if (!/[a-z]/.test(value)) return 'Password must contain a lowercase letter'
if (!/[0-9]/.test(value)) return 'Password must contain a number'
if (!/[!@#$%^&*]/.test(value)) return 'Password must contain a special character'
```

### Confirm Password

```tsx
if (confirmPassword !== password) return 'Passwords do not match'
```

### Min/Max Length

```tsx
if (value.length < min) return `Must be at least ${min} characters`
if (value.length > max) return `Must be at most ${max} characters`
```

### Numeric Range

```tsx
const num = Number(value)
if (isNaN(num)) return 'Must be a number'
if (num < min) return `Must be at least ${min}`
if (num > max) return `Must be at most ${max}`
```

### URL Format

```tsx
try {
  new URL(value)
} catch {
  return 'Invalid URL'
}
```

### Phone Number

```tsx
const phoneRegex = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/
if (!phoneRegex.test(value)) return 'Invalid phone number'
```

### Credit Card (Luhn Algorithm)

```tsx
function isValidCreditCard(cardNumber: string): boolean {
  const digits = cardNumber.replace(/\D/g, '')
  let sum = 0
  let isEven = false

  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10)

    if (isEven) {
      digit *= 2
      if (digit > 9) digit -= 9
    }

    sum += digit
    isEven = !isEven
  }

  return sum % 10 === 0
}

if (!isValidCreditCard(value)) return 'Invalid credit card number'
```

---

## Schema Validation Libraries

### Zod

```tsx
import { z } from 'zod'

const loginSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type LoginForm = z.infer<typeof loginSchema>

function LoginForm() {
  const [values, setValues] = useState<LoginForm>({ email: '', password: '' })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const result = loginSchema.safeParse(values)

    if (!result.success) {
      const newErrors: Record<string, string> = {}
      result.error.issues.forEach(issue => {
        if (issue.path[0]) {
          newErrors[issue.path[0] as string] = issue.message
        }
      })
      setErrors(newErrors)
    } else {
      console.log('Valid:', result.data)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  )
}
```

### Yup

```tsx
import * as yup from 'yup'

const loginSchema = yup.object({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(8, 'Password must be 8+ characters').required('Password is required'),
})

function LoginForm() {
  const [values, setValues] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await loginSchema.validate(values, { abortEarly: false })
      console.log('Valid:', values)
    } catch (err) {
      if (err instanceof yup.ValidationError) {
        const newErrors: Record<string, string> = {}
        err.inner.forEach(error => {
          if (error.path) {
            newErrors[error.path] = error.message
          }
        })
        setErrors(newErrors)
      }
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  )
}
```

---

## Async Validation

**Use Case**: Check if username/email is already taken.

```tsx
function RegistrationForm() {
  const [email, setEmail] = useState('')
  const [emailError, setEmailError] = useState<string | null>(null)
  const [isCheckingEmail, setIsCheckingEmail] = useState(false)

  const checkEmailAvailability = useMemo(
    () =>
      debounce(async (email: string) => {
        setIsCheckingEmail(true)
        try {
          const res = await fetch(`/api/check-email?email=${email}`)
          const data = await res.json()

          if (!data.available) {
            setEmailError('Email is already registered')
          } else {
            setEmailError(null)
          }
        } catch (err) {
          setEmailError('Could not verify email availability')
        } finally {
          setIsCheckingEmail(false)
        }
      }, 500),
    []
  )

  useEffect(() => {
    if (email && email.includes('@')) {
      checkEmailAvailability(email)
    }
  }, [email, checkEmailAvailability])

  return (
    <div>
      <input
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        aria-invalid={!!emailError}
      />
      {isCheckingEmail && <span>Checking...</span>}
      {emailError && <span className="error">{emailError}</span>}
    </div>
  )
}
```

---

## Form-Level Validation

**Use Case**: Validation depends on multiple fields.

```tsx
interface FormState {
  password: string
  confirmPassword: string
  agreeToTerms: boolean
}

function RegistrationForm() {
  const [values, setValues] = useState<FormState>({
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  })
  const [formError, setFormError] = useState<string | null>(null)

  const validateForm = (): string | null => {
    if (values.password !== values.confirmPassword) {
      return 'Passwords do not match'
    }
    if (!values.agreeToTerms) {
      return 'You must agree to the terms and conditions'
    }
    return null
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const error = validateForm()
    setFormError(error)

    if (!error) {
      console.log('Submit:', values)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}

      {formError && (
        <div role="alert" className="form-error">
          {formError}
        </div>
      )}

      <button type="submit">Register</button>
    </form>
  )
}
```

---

## Server-Side Validation

**Pattern**: Display server errors returned from API.

```tsx
interface ServerErrors {
  email?: string
  password?: string
  _form?: string  // General form error
}

function LoginForm() {
  const [values, setValues] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState<ServerErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrors({})

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      })

      if (!res.ok) {
        const data = await res.json()
        setErrors(data.errors || { _form: 'Login failed' })
      } else {
        console.log('Login successful')
      }
    } catch (err) {
      setErrors({ _form: 'Network error. Please try again.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {errors._form && (
        <div role="alert" className="form-error">
          {errors._form}
        </div>
      )}

      <div>
        <input
          type="email"
          value={values.email}
          onChange={e => setValues(prev => ({ ...prev, email: e.target.value }))}
          aria-invalid={!!errors.email}
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </div>

      <div>
        <input
          type="password"
          value={values.password}
          onChange={e => setValues(prev => ({ ...prev, password: e.target.value }))}
          aria-invalid={!!errors.password}
        />
        {errors.password && <span className="error">{errors.password}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  )
}
```

---

## Custom Validation Hook

**Pattern**: Reusable validation logic.

```tsx
interface UseFormValidationOptions<T> {
  initialValues: T
  validate: (values: T) => Partial<Record<keyof T, string>>
  onSubmit: (values: T) => void | Promise<void>
}

function useFormValidation<T extends Record<string, any>>({
  initialValues,
  validate,
  onSubmit,
}: UseFormValidationOptions<T>) {
  const [values, setValues] = useState<T>(initialValues)
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({})
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (field: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [field]: value }))
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  const handleBlur = (field: keyof T) => {
    setTouched(prev => ({ ...prev, [field]: true }))
    const fieldErrors = validate(values)
    setErrors(prev => ({ ...prev, [field]: fieldErrors[field] }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Mark all fields as touched
    const allTouched = Object.keys(values).reduce(
      (acc, field) => ({ ...acc, [field]: true }),
      {} as Partial<Record<keyof T, boolean>>
    )
    setTouched(allTouched)

    // Validate all fields
    const fieldErrors = validate(values)
    setErrors(fieldErrors)

    // Submit if no errors
    if (Object.keys(fieldErrors).length === 0) {
      setIsSubmitting(true)
      try {
        await onSubmit(values)
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
  }
}

// Usage
function LoginForm() {
  const form = useFormValidation({
    initialValues: { email: '', password: '' },
    validate: values => {
      const errors: Record<string, string> = {}
      if (!values.email.includes('@')) errors.email = 'Invalid email'
      if (values.password.length < 8) errors.password = 'Password must be 8+ characters'
      return errors
    },
    onSubmit: async values => {
      await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify(values),
      })
    },
  })

  return (
    <form onSubmit={form.handleSubmit}>
      <input
        type="email"
        value={form.values.email}
        onChange={e => form.handleChange('email', e.target.value)}
        onBlur={() => form.handleBlur('email')}
      />
      {form.touched.email && form.errors.email && <span>{form.errors.email}</span>}

      <input
        type="password"
        value={form.values.password}
        onChange={e => form.handleChange('password', e.target.value)}
        onBlur={() => form.handleBlur('password')}
      />
      {form.touched.password && form.errors.password && <span>{form.errors.password}</span>}

      <button type="submit" disabled={form.isSubmitting}>
        {form.isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  )
}
```

---

## Accessibility

### Error Announcements

```tsx
<input
  aria-invalid={touched && !!error}
  aria-describedby={touched && error ? 'field-error' : undefined}
/>
{touched && error && (
  <span id="field-error" role="alert">
    {error}
  </span>
)}
```

### Focus Management

```tsx
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()

  const newErrors = validate(values)
  setErrors(newErrors)

  if (Object.keys(newErrors).length > 0) {
    // Focus first field with error
    const firstErrorField = Object.keys(newErrors)[0]
    document.getElementById(firstErrorField)?.focus()
  }
}
```

---

## Testing

```tsx
describe('Form Validation', () => {
  test('shows error on blur if invalid', async () => {
    render(<LoginForm />)

    const emailInput = screen.getByLabelText('Email')
    fireEvent.change(emailInput, { target: { value: 'invalid' } })
    fireEvent.blur(emailInput)

    await waitFor(() => {
      expect(screen.getByText('Invalid email format')).toBeInTheDocument()
    })
  })

  test('clears error when user starts typing', () => {
    render(<LoginForm />)

    const emailInput = screen.getByLabelText('Email')
    fireEvent.change(emailInput, { target: { value: 'invalid' } })
    fireEvent.blur(emailInput)

    expect(screen.getByText('Invalid email format')).toBeInTheDocument()

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

    expect(screen.queryByText('Invalid email format')).not.toBeInTheDocument()
  })

  test('prevents submission if invalid', () => {
    const onSubmit = jest.fn()
    render(<LoginForm onSubmit={onSubmit} />)

    fireEvent.click(screen.getByText('Login'))

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByText('Email is required')).toBeInTheDocument()
  })
})
```

---

## Summary

**Validation Pattern**:
- Validate on blur (most common)
- Always validate on submit
- Show error only after field is touched
- Clear error when user starts typing

**Validation Rules**:
- Required, email, password strength, min/max length, numeric range, etc.
- Use schema validation libraries (Zod, Yup) for complex forms

**Async Validation**:
- Check email/username availability
- Debounce API calls (500ms)

**Server Validation**:
- Display server errors from API response
- Handle form-level errors (_form field)

**Accessibility**:
- Use `aria-invalid` and `aria-describedby`
- Announce errors with `role="alert"`
- Focus first error field on submit

**Result**: Clear, accessible validation that guides users to correct inputs.
