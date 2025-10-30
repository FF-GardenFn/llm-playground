# Composition: Simple Components

**Pattern**: Build components from small, focused sub-components with single responsibilities.

**When to Use**:
- Component has distinct visual sections (header, body, footer)
- Logic can be separated by concern (data, UI, interaction)
- Component will be used in multiple contexts
- Testing needs to be granular

**When NOT to Use**:
- Component is truly simple (<50 lines, single responsibility)
- Splitting would create artificial boundaries
- Props drilling becomes excessive (use composition patterns instead)

---

## Core Principle

**Single Responsibility**: Each component does one thing well.

**Example: Complex Button**
```tsx
// ❌ BAD: One component, many responsibilities
function Button({ icon, label, badge, loading, onClick }) {
  return (
    <button onClick={onClick}>
      {loading && <Spinner />}
      {icon && <Icon name={icon} />}
      <span>{label}</span>
      {badge && <Badge count={badge} />}
    </button>
  )
}
```

```tsx
// ✅ GOOD: Separated responsibilities
function Button({ children, onClick, disabled }) {
  return (
    <button onClick={onClick} disabled={disabled} className="button">
      {children}
    </button>
  )
}

function ButtonIcon({ name }) {
  return <Icon name={name} className="button-icon" />
}

function ButtonLabel({ children }) {
  return <span className="button-label">{children}</span>
}

function ButtonBadge({ count }) {
  return <span className="button-badge">{count}</span>
}

// Usage: Compose as needed
<Button onClick={handleSave}>
  <ButtonIcon name="save" />
  <ButtonLabel>Save</ButtonLabel>
  <ButtonBadge count={3} />
</Button>
```

**Why Better**:
- Each component testable in isolation
- Easy to add/remove parts (just remove `<ButtonBadge />`)
- Clear visual hierarchy in JSX
- No conditional logic bloat

---

## Pattern Structure

### Step 1: Identify Responsibilities

**Process**: List what the component does, then group by concern.

**Example: Card Component**

```
Responsibilities:
1. Display image
2. Display title
3. Display description
4. Display actions (buttons)
5. Handle click on card
6. Handle click on actions

Grouping:
- Visual: Image, Title, Description (CardContent)
- Interactive: Actions (CardActions)
- Container: Card (handles layout + click)
```

**Result**:
```tsx
// Container
function Card({ children, onClick }) {
  return <div className="card" onClick={onClick}>{children}</div>
}

// Visual
function CardImage({ src, alt }) {
  return <img className="card-image" src={src} alt={alt} />
}

function CardTitle({ children }) {
  return <h3 className="card-title">{children}</h3>
}

function CardDescription({ children }) {
  return <p className="card-description">{children}</p>
}

// Interactive
function CardActions({ children }) {
  return <div className="card-actions">{children}</div>
}
```

### Step 2: Define Component API

**Props Pattern**: Minimal, focused props for each component.

**Example: Card**
```typescript
// Container: Layout + interaction
interface CardProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'default' | 'elevated' | 'outlined'
}

// Visual: Display data
interface CardImageProps {
  src: string
  alt: string
  aspectRatio?: '16:9' | '4:3' | '1:1'
}

interface CardTitleProps {
  children: string
  level?: 1 | 2 | 3 // Semantic heading level
}

interface CardDescriptionProps {
  children: string
  lines?: number // Max lines before truncation
}

// Interactive: Actions
interface CardActionsProps {
  children: React.ReactNode
  alignment?: 'left' | 'center' | 'right'
}
```

### Step 3: Compose Components

**Usage Pattern**: Explicit composition in parent components.

**Example: Product Card**
```tsx
function ProductCard({ product, onBuy, onFavorite }) {
  return (
    <Card onClick={() => console.log('Card clicked')}>
      <CardImage src={product.image} alt={product.name} aspectRatio="4:3" />
      <CardTitle level={2}>{product.name}</CardTitle>
      <CardDescription lines={3}>{product.description}</CardDescription>
      <CardActions alignment="right">
        <Button variant="secondary" onClick={onFavorite}>
          <ButtonIcon name="heart" />
        </Button>
        <Button variant="primary" onClick={onBuy}>
          <ButtonLabel>Buy Now</ButtonLabel>
        </Button>
      </CardActions>
    </Card>
  )
}
```

**Why This Works**:
- Clear visual hierarchy (image → title → description → actions)
- Each sub-component independently testable
- Easy to customize (swap CardImage for CardVideo)
- No prop drilling (each component gets exactly what it needs)

---

## Examples: Common Patterns

### Example 1: Data Table

**Problem**: Table with sortable columns, filterable rows, pagination.

**Decomposition**:
```tsx
// Container
function DataTable({ children }) {
  return <table className="data-table">{children}</table>
}

// Header
function TableHeader({ children }) {
  return <thead>{children}</thead>
}

function TableHeaderRow({ children }) {
  return <tr>{children}</tr>
}

function TableHeaderCell({ children, sortable, sortDirection, onSort }) {
  return (
    <th>
      <button onClick={onSort} disabled={!sortable}>
        {children}
        {sortable && <SortIcon direction={sortDirection} />}
      </button>
    </th>
  )
}

// Body
function TableBody({ children }) {
  return <tbody>{children}</tbody>
}

function TableRow({ children, onClick, selected }) {
  return (
    <tr
      onClick={onClick}
      className={selected ? 'selected' : ''}
      role="row"
      aria-selected={selected}
    >
      {children}
    </tr>
  )
}

function TableCell({ children }) {
  return <td>{children}</td>
}

// Footer
function TableFooter({ children }) {
  return <tfoot>{children}</tfoot>
}
```

**Usage**:
```tsx
function UserTable({ users }) {
  const [sortColumn, setSortColumn] = useState('name')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')

  const sortedUsers = useMemo(() => {
    return [...users].sort((a, b) => {
      const aVal = a[sortColumn]
      const bVal = b[sortColumn]
      return sortDirection === 'asc'
        ? aVal > bVal ? 1 : -1
        : aVal < bVal ? 1 : -1
    })
  }, [users, sortColumn, sortDirection])

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  return (
    <DataTable>
      <TableHeader>
        <TableHeaderRow>
          <TableHeaderCell
            sortable
            sortDirection={sortColumn === 'name' ? sortDirection : null}
            onSort={() => handleSort('name')}
          >
            Name
          </TableHeaderCell>
          <TableHeaderCell
            sortable
            sortDirection={sortColumn === 'email' ? sortDirection : null}
            onSort={() => handleSort('email')}
          >
            Email
          </TableHeaderCell>
          <TableHeaderCell>Actions</TableHeaderCell>
        </TableHeaderRow>
      </TableHeader>
      <TableBody>
        {sortedUsers.map(user => (
          <TableRow key={user.id}>
            <TableCell>{user.name}</TableCell>
            <TableCell>{user.email}</TableCell>
            <TableCell>
              <Button size="small">Edit</Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </DataTable>
  )
}
```

**Benefits**:
- Each cell independently styled/tested
- Easy to add new cell types (TableCellImage, TableCellLink)
- Header logic separated from body
- Clear semantic HTML structure

---

### Example 2: Form

**Problem**: Multi-field form with validation, error display, submit button.

**Decomposition**:
```tsx
// Container
function Form({ children, onSubmit }) {
  return <form onSubmit={onSubmit} className="form">{children}</form>
}

// Field
function FormField({ children, error }) {
  return (
    <div className="form-field" aria-invalid={!!error}>
      {children}
      {error && <FormFieldError>{error}</FormFieldError>}
    </div>
  )
}

function FormLabel({ children, htmlFor, required }) {
  return (
    <label htmlFor={htmlFor} className="form-label">
      {children}
      {required && <span className="required">*</span>}
    </label>
  )
}

function FormInput({ id, type, value, onChange, placeholder }) {
  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      className="form-input"
    />
  )
}

function FormFieldError({ children }) {
  return (
    <span className="form-field-error" role="alert">
      {children}
    </span>
  )
}

// Actions
function FormActions({ children, alignment = 'right' }) {
  return (
    <div className="form-actions" style={{ justifyContent: alignment }}>
      {children}
    </div>
  )
}
```

**Usage**:
```tsx
function LoginForm({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const newErrors: Record<string, string> = {}
    if (!email.includes('@')) newErrors.email = 'Invalid email'
    if (password.length < 8) newErrors.password = 'Password must be 8+ characters'
    return newErrors
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newErrors = validate()
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
    } else {
      onLogin({ email, password })
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormField error={errors.email}>
        <FormLabel htmlFor="email" required>Email</FormLabel>
        <FormInput
          id="email"
          type="email"
          value={email}
          onChange={setEmail}
          placeholder="you@example.com"
        />
      </FormField>

      <FormField error={errors.password}>
        <FormLabel htmlFor="password" required>Password</FormLabel>
        <FormInput
          id="password"
          type="password"
          value={password}
          onChange={setPassword}
          placeholder="••••••••"
        />
      </FormField>

      <FormActions>
        <Button type="button" variant="secondary">Cancel</Button>
        <Button type="submit" variant="primary">Login</Button>
      </FormActions>
    </Form>
  )
}
```

**Benefits**:
- Error display consistent across fields
- Easy to add new field types (FormSelect, FormCheckbox)
- Validation logic separated from UI
- Accessible by default (labels, error announcements)

---

### Example 3: Modal

**Problem**: Overlay with header, scrollable content, footer actions.

**Decomposition**:
```tsx
// Container
function Modal({ children, isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} role="dialog" aria-modal="true">
        {children}
      </div>
    </div>
  )
}

// Header
function ModalHeader({ children, onClose }) {
  return (
    <div className="modal-header">
      <h2 className="modal-title">{children}</h2>
      <button onClick={onClose} aria-label="Close modal" className="modal-close">
        ✕
      </button>
    </div>
  )
}

// Body
function ModalBody({ children }) {
  return <div className="modal-body">{children}</div>
}

// Footer
function ModalFooter({ children, alignment = 'right' }) {
  return (
    <div className="modal-footer" style={{ justifyContent: alignment }}>
      {children}
    </div>
  )
}
```

**Usage**:
```tsx
function ConfirmDeleteModal({ isOpen, onClose, onConfirm, itemName }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalHeader onClose={onClose}>Confirm Deletion</ModalHeader>
      <ModalBody>
        <p>Are you sure you want to delete "{itemName}"?</p>
        <p>This action cannot be undone.</p>
      </ModalBody>
      <ModalFooter>
        <Button variant="secondary" onClick={onClose}>Cancel</Button>
        <Button variant="danger" onClick={onConfirm}>Delete</Button>
      </ModalFooter>
    </Modal>
  )
}
```

**Benefits**:
- Header always has close button
- Body is scrollable by default (CSS)
- Footer actions always aligned
- Easy to customize layout (remove footer, add multiple sections)

---

## Testing Simple Components

### Unit Tests

**Pattern**: Test each sub-component in isolation.

```tsx
describe('Card Components', () => {
  test('Card renders children', () => {
    render(<Card><div>Content</div></Card>)
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  test('Card onClick fires', () => {
    const onClick = jest.fn()
    render(<Card onClick={onClick}><div>Content</div></Card>)
    fireEvent.click(screen.getByText('Content'))
    expect(onClick).toHaveBeenCalled()
  })

  test('CardImage renders with alt text', () => {
    render(<CardImage src="/image.jpg" alt="Test image" />)
    expect(screen.getByAltText('Test image')).toHaveAttribute('src', '/image.jpg')
  })

  test('CardTitle renders as h3', () => {
    render(<CardTitle level={3}>Title</CardTitle>)
    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('Title')
  })

  test('CardDescription truncates after maxLines', () => {
    const longText = 'Line 1\nLine 2\nLine 3\nLine 4'
    render(<CardDescription lines={2}>{longText}</CardDescription>)
    const description = screen.getByText(/Line 1/)
    expect(description).toHaveClass('truncated') // Assuming CSS class
  })
})
```

### Integration Tests

**Pattern**: Test composition of sub-components.

```tsx
describe('ProductCard Integration', () => {
  test('renders all parts', () => {
    const product = {
      image: '/product.jpg',
      name: 'Widget',
      description: 'A great widget',
    }

    render(
      <ProductCard
        product={product}
        onBuy={jest.fn()}
        onFavorite={jest.fn()}
      />
    )

    expect(screen.getByAltText('Widget')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Widget' })).toBeInTheDocument()
    expect(screen.getByText('A great widget')).toBeInTheDocument()
    expect(screen.getByText('Buy Now')).toBeInTheDocument()
  })

  test('buy button triggers onBuy', () => {
    const onBuy = jest.fn()
    const product = { image: '/product.jpg', name: 'Widget', description: 'Great' }

    render(<ProductCard product={product} onBuy={onBuy} onFavorite={jest.fn()} />)

    fireEvent.click(screen.getByText('Buy Now'))
    expect(onBuy).toHaveBeenCalled()
  })
})
```

---

## Performance Considerations

### 1. Memo Sub-Components

**When**: Sub-components re-render unnecessarily.

```tsx
// ❌ BAD: TableRow re-renders when sortColumn changes (even if row data doesn't)
function TableRow({ children, onClick }) {
  return <tr onClick={onClick}>{children}</tr>
}

// ✅ GOOD: Memo prevents unnecessary re-renders
const TableRow = React.memo<TableRowProps>(({ children, onClick }) => {
  return <tr onClick={onClick}>{children}</tr>
})
```

### 2. Stable Callbacks

**When**: Passing callbacks to memoized sub-components.

```tsx
// ❌ BAD: handleSort is recreated on every render
function UserTable({ users }) {
  const [sortColumn, setSortColumn] = useState('name')

  const handleSort = (column: string) => {
    setSortColumn(column)
  }

  return (
    <TableHeader>
      <TableHeaderCell onSort={() => handleSort('name')}>Name</TableHeaderCell>
    </TableHeader>
  )
}

// ✅ GOOD: useCallback stabilizes handleSort
function UserTable({ users }) {
  const [sortColumn, setSortColumn] = useState('name')

  const handleSort = useCallback((column: string) => {
    setSortColumn(column)
  }, [])

  return (
    <TableHeader>
      <TableHeaderCell onSort={() => handleSort('name')}>Name</TableHeaderCell>
    </TableHeader>
  )
}
```

### 3. Avoid Deep Nesting

**When**: Too many wrapper components.

```tsx
// ❌ BAD: 5 levels of nesting
<Card>
  <CardContainer>
    <CardInner>
      <CardContent>
        <CardText>Hello</CardText>
      </CardContent>
    </CardInner>
  </CardContainer>
</Card>

// ✅ GOOD: Flat structure
<Card>
  <CardText>Hello</CardText>
</Card>
```

---

## Accessibility

### 1. Semantic HTML

**Pattern**: Use correct HTML elements.

```tsx
// ❌ BAD: Generic div
function CardTitle({ children }) {
  return <div className="card-title">{children}</div>
}

// ✅ GOOD: Semantic heading
function CardTitle({ children, level = 3 }) {
  const Tag = `h${level}` as 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
  return <Tag className="card-title">{children}</Tag>
}
```

### 2. ARIA Attributes

**Pattern**: Add ARIA when semantic HTML isn't enough.

```tsx
function TableRow({ children, onClick, selected }) {
  return (
    <tr
      onClick={onClick}
      role="row"
      aria-selected={selected}
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onClick?.()}
    >
      {children}
    </tr>
  )
}
```

### 3. Focus Management

**Pattern**: Focus indicators, keyboard navigation.

```tsx
function Modal({ children, isOpen, onClose }) {
  const modalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      // Focus first focusable element in modal
      const firstFocusable = modalRef.current?.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      firstFocusable?.focus()
    }
  }, [isOpen])

  return (
    <div className="modal" ref={modalRef} role="dialog" aria-modal="true">
      {children}
    </div>
  )
}
```

---

## Anti-Patterns

### 1. Over-Decomposition

**Problem**: Too many tiny components.

```tsx
// ❌ BAD: Each prop becomes a component
function ButtonTextContent({ text }) {
  return <span>{text}</span>
}

function ButtonIconWrapper({ icon }) {
  return <span><Icon name={icon} /></span>
}

// ✅ GOOD: Reasonable granularity
function Button({ children, icon }) {
  return (
    <button>
      {icon && <Icon name={icon} />}
      <span>{children}</span>
    </button>
  )
}
```

### 2. Prop Drilling Through Sub-Components

**Problem**: Passing props through multiple layers.

```tsx
// ❌ BAD: CardContent doesn't use onClick, just passes it down
function Card({ children, onClick }) {
  return <div className="card" onClick={onClick}>{children}</div>
}

function CardContent({ children, onClick }) {
  return <div className="card-content">{children}</div>
}

function CardTitle({ children, onClick }) {
  return <h3 onClick={onClick}>{children}</h3>
}

// Usage: onClick passed through CardContent even though it doesn't use it
<Card onClick={handleClick}>
  <CardContent onClick={handleClick}>
    <CardTitle onClick={handleClick}>Title</CardTitle>
  </CardContent>
</Card>

// ✅ GOOD: onClick only where needed
function Card({ children, onClick }) {
  return <div className="card" onClick={onClick}>{children}</div>
}

function CardContent({ children }) {
  return <div className="card-content">{children}</div>
}

function CardTitle({ children }) {
  return <h3>{children}</h3>
}

// Usage: onClick only on Card
<Card onClick={handleClick}>
  <CardContent>
    <CardTitle>Title</CardTitle>
  </CardContent>
</Card>
```

### 3. Inconsistent Composition API

**Problem**: Some components accept children, others use props.

```tsx
// ❌ BAD: Inconsistent
<Card>
  <CardImage src="/image.jpg" alt="Image" />
  <CardTitle text="Title" /> {/* Why not children? */}
  <CardDescription>Description text</CardDescription>
</Card>

// ✅ GOOD: Consistent
<Card>
  <CardImage src="/image.jpg" alt="Image" />
  <CardTitle>Title</CardTitle>
  <CardDescription>Description text</CardDescription>
</Card>
```

---

## Decision Flowchart

```
Does component have distinct visual sections?
├─ YES → Decompose by section (Header, Body, Footer)
│
└─ NO → Does component have multiple responsibilities?
         ├─ YES → Decompose by responsibility (Data, UI, Interaction)
         │
         └─ NO → Keep as single component
```

**Example Decisions**:

| Component | Decompose? | Rationale |
|-----------|------------|-----------|
| Button with icon + label | NO | Single responsibility (trigger action), icon/label are just props |
| Card with image + title + actions | YES | Multiple sections (visual, interactive) |
| Input with validation | MAYBE | Depends on complexity. Simple validation → single component. Complex async validation → separate ValidationMessage component |
| Data table | YES | Multiple sections (header, body, footer) + distinct cell rendering logic |

---

## Summary

**Simple Components Pattern**:
- Decompose by responsibility or visual section
- Each sub-component has single purpose
- Compose explicitly in parent components
- Test each sub-component in isolation
- Memo sub-components to prevent unnecessary re-renders
- Use semantic HTML and ARIA for accessibility
- Avoid over-decomposition and prop drilling

**When to Use**:
- Component has multiple sections or responsibilities
- Testing needs to be granular
- Reusability across contexts

**Result**: Clean, testable, composable component hierarchy.
