# Compound Components Pattern

**Pattern Type**: Composition
**Complexity**: Medium
**When**: Related components work together as unit

---

## When to Use

**Good fit when**:
- Components naturally belong together (Accordion + Item, Tabs + Panel)
- Shared state between parent and children
- Flexible API (users compose as needed)
- Controlled disclosure (parent controls child state)

**Poor fit when**:
- Simple component (single element)
- No shared state needed
- Deep nesting required (>3 levels)

---

## Pattern Structure

### Parent Component
- Manages shared state
- Provides state via Context
- Exposes subcomponents as properties

### Child Components
- Access parent state via Context
- Render based on parent state
- No direct props needed (implicit through context)

---

## Implementation

### Example: Accordion Component

```jsx
import React, { createContext, useContext, useState } from 'react'

// 1. Create context for shared state
const AccordionContext = createContext()

// 2. Parent component manages state
function Accordion({ children, defaultIndex = 0 }) {
  const [activeIndex, setActiveIndex] = useState(defaultIndex)

  const value = {
    activeIndex,
    setActiveIndex
  }

  return (
    <AccordionContext.Provider value={value}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  )
}

// 3. Custom hook for accessing context
function useAccordionContext() {
  const context = useContext(AccordionContext)
  if (!context) {
    throw new Error('Accordion compound components must be used within Accordion')
  }
  return context
}

// 4. Child components access state via context
function AccordionItem({ children, index }) {
  const { activeIndex } = useAccordionContext()
  const isActive = activeIndex === index

  return (
    <div className={`accordion-item ${isActive ? 'active' : ''}`}>
      {children}
    </div>
  )
}

function AccordionHeader({ children, index }) {
  const { activeIndex, setActiveIndex } = useAccordionContext()
  const isActive = activeIndex === index

  return (
    <button
      className="accordion-header"
      onClick={() => setActiveIndex(isActive ? null : index)}
      aria-expanded={isActive}
    >
      {children}
    </button>
  )
}

function AccordionContent({ children, index }) {
  const { activeIndex } = useAccordionContext()
  const isActive = activeIndex === index

  if (!isActive) return null

  return <div className="accordion-content">{children}</div>
}

// 5. Attach subcomponents to parent
Accordion.Item = AccordionItem
Accordion.Header = AccordionHeader
Accordion.Content = AccordionContent

export default Accordion
```

### Usage

```jsx
// Flexible composition
<Accordion defaultIndex={0}>
  <Accordion.Item index={0}>
    <Accordion.Header index={0}>Section 1</Accordion.Header>
    <Accordion.Content index={0}>
      <p>Content for section 1</p>
    </Accordion.Content>
  </Accordion.Item>

  <Accordion.Item index={1}>
    <Accordion.Header index={1}>Section 2</Accordion.Header>
    <Accordion.Content index={1}>
      <p>Content for section 2</p>
    </Accordion.Content>
  </Accordion.Item>

  <Accordion.Item index={2}>
    <Accordion.Header index={2}>Section 3</Accordion.Header>
    <Accordion.Content index={2}>
      <p>Content for section 3</p>
    </Accordion.Content>
  </Accordion.Item>
</Accordion>
```

---

## Benefits

**Flexible API**:
- Users compose as needed
- Can skip optional parts
- Can add custom wrappers

**Implicit State**:
- No prop drilling
- Children automatically connected
- Clean, declarative API

**Separation of Concerns**:
- Parent handles state logic
- Children handle rendering
- Each component focused

---

## Common Patterns

### Tabs Component

```jsx
function Tabs({ children, defaultTab }) {
  const [activeTab, setActiveTab] = useState(defaultTab)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  )
}

Tabs.List = function TabsList({ children }) {
  return <div role="tablist">{children}</div>
}

Tabs.Tab = function Tab({ id, children }) {
  const { activeTab, setActiveTab } = useTabsContext()
  const isActive = activeTab === id

  return (
    <button
      role="tab"
      aria-selected={isActive}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  )
}

Tabs.Panel = function TabPanel({ id, children }) {
  const { activeTab } = useTabsContext()
  if (activeTab !== id) return null

  return <div role="tabpanel">{children}</div>
}

// Usage
<Tabs defaultTab="profile">
  <Tabs.List>
    <Tabs.Tab id="profile">Profile</Tabs.Tab>
    <Tabs.Tab id="settings">Settings</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="profile">
    <ProfileContent />
  </Tabs.Panel>
  <Tabs.Panel id="settings">
    <SettingsContent />
  </Tabs.Panel>
</Tabs>
```

### Select Component

```jsx
function Select({ children, value, onChange }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <SelectContext.Provider value={{ value, onChange, isOpen, setIsOpen }}>
      <div className="select">{children}</div>
    </SelectContext.Provider>
  )
}

Select.Trigger = function SelectTrigger({ children }) {
  const { isOpen, setIsOpen } = useSelectContext()

  return (
    <button
      onClick={() => setIsOpen(!isOpen)}
      aria-expanded={isOpen}
      aria-haspopup="listbox"
    >
      {children}
    </button>
  )
}

Select.Options = function SelectOptions({ children }) {
  const { isOpen } = useSelectContext()
  if (!isOpen) return null

  return <div role="listbox">{children}</div>
}

Select.Option = function SelectOption({ value, children }) {
  const { value: selectedValue, onChange, setIsOpen } = useSelectContext()
  const isSelected = selectedValue === value

  return (
    <button
      role="option"
      aria-selected={isSelected}
      onClick={() => {
        onChange(value)
        setIsOpen(false)
      }}
    >
      {children}
    </button>
  )
}

// Usage
<Select value={selectedValue} onChange={setSelectedValue}>
  <Select.Trigger>
    {selectedValue || 'Select an option'}
  </Select.Trigger>
  <Select.Options>
    <Select.Option value="apple">Apple</Select.Option>
    <Select.Option value="banana">Banana</Select.Option>
    <Select.Option value="cherry">Cherry</Select.Option>
  </Select.Options>
</Select>
```

---

## Best Practices

### 1. Enforce Parent-Child Relationship

```jsx
function useAccordionContext() {
  const context = useContext(AccordionContext)
  if (!context) {
    throw new Error(
      'Accordion compound components must be used within Accordion'
    )
  }
  return context
}
```

**Why**: Fail fast with clear error if used incorrectly

### 2. Use TypeScript for Safety

```tsx
type AccordionContextValue = {
  activeIndex: number | null
  setActiveIndex: (index: number | null) => void
}

const AccordionContext = createContext<AccordionContextValue | undefined>(undefined)

interface AccordionItemProps {
  children: React.ReactNode
  index: number
}

function AccordionItem({ children, index }: AccordionItemProps) {
  // ...
}
```

**Why**: Type safety prevents misuse

### 3. Memoize Context Value

```jsx
function Accordion({ children, defaultIndex = 0 }) {
  const [activeIndex, setActiveIndex] = useState(defaultIndex)

  // ✅ Memoize to prevent unnecessary re-renders
  const value = useMemo(
    () => ({ activeIndex, setActiveIndex }),
    [activeIndex]
  )

  return (
    <AccordionContext.Provider value={value}>
      {children}
    </AccordionContext.Provider>
  )
}
```

**Why**: Prevents re-renders of all children when parent re-renders

### 4. Provide Default Styles

```jsx
function Accordion({ children, className = '', ...props }) {
  return (
    <div className={`accordion ${className}`} {...props}>
      {children}
    </div>
  )
}
```

**Why**: Works out of box, customizable if needed

---

## Accessibility Considerations

### ARIA Roles

```jsx
// Accordion
<button
  role="button"
  aria-expanded={isActive}
  aria-controls={`panel-${index}`}
>
  {children}
</button>

// Tabs
<button
  role="tab"
  aria-selected={isActive}
  aria-controls={`panel-${id}`}
>
  {children}
</button>

// Select
<button
  role="combobox"
  aria-expanded={isOpen}
  aria-haspopup="listbox"
>
  {children}
</button>
```

### Keyboard Navigation

```jsx
function AccordionHeader({ children, index }) {
  const { setActiveIndex } = useAccordionContext()

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setActiveIndex(index)
    }
  }

  return (
    <button
      onClick={() => setActiveIndex(index)}
      onKeyDown={handleKeyDown}
    >
      {children}
    </button>
  )
}
```

---

## Common Mistakes

### ❌ Mistake 1: Prop Drilling Instead

```jsx
// Bad: Passing state through props
<Accordion activeIndex={0} onIndexChange={setIndex}>
  <AccordionItem index={0} activeIndex={0} onIndexChange={setIndex}>
    <AccordionHeader index={0} activeIndex={0} onIndexChange={setIndex}>
      Section 1
    </AccordionHeader>
  </AccordionItem>
</Accordion>
```

**Problem**: Verbose, error-prone, tight coupling

**Solution**: Use compound components with context

### ❌ Mistake 2: Not Enforcing Parent-Child

```jsx
// Bad: No error if used outside parent
function AccordionItem() {
  const context = useContext(AccordionContext)  // Could be undefined
  return <div>{context.activeIndex}</div>  // Runtime error
}
```

**Problem**: Silent failure or confusing errors

**Solution**: Throw error in custom hook if context undefined

### ❌ Mistake 3: Re-Creating Context Value

```jsx
// Bad: Creates new object every render
function Accordion({ children, defaultIndex }) {
  const [activeIndex, setActiveIndex] = useState(defaultIndex)

  // ❌ New object every render → all children re-render
  return (
    <AccordionContext.Provider value={{ activeIndex, setActiveIndex }}>
      {children}
    </AccordionContext.Provider>
  )
}
```

**Problem**: Unnecessary re-renders

**Solution**: Memoize context value

---

## When Not to Use

**Don't use compound components when**:

1. **Simple component** (Button, Input)
   - Use props instead
   - No shared state needed

2. **Deep nesting required** (>3 levels)
   - Context overhead too high
   - Consider splitting components

3. **Performance critical** (large lists)
   - Context causes re-renders
   - Use prop passing instead

4. **No related components**
   - Components independent
   - No benefit from coupling

---

## Related Patterns

**Also consider**:
- **Render Props**: When need more rendering control
- **Custom Hooks**: When sharing logic, not rendering
- **HOC**: When adding behavior cross-cutting

**See also**:
- patterns/composition/custom-hooks.md
- patterns/composition/render-props.md
- patterns/composition/hoc.md

---

## Summary

**Compound components pattern**:
- ✅ Flexible, composable API
- ✅ Implicit state sharing via Context
- ✅ Clean, declarative usage
- ✅ Great for related components (Accordion, Tabs, Select)

**Use when**: Related components, shared state, flexible composition needed

**Avoid when**: Simple components, deep nesting, performance critical

**Structure enforces good API design.**
