# Composition Patterns

**Purpose**: Techniques for combining components to build complex UIs from simple, reusable pieces.

**Core Principle**: Components should be composable - small pieces that fit together in flexible ways.

---

## Quick Reference

| Pattern | Use When | Complexity | Modern Alternative |
|---------|----------|------------|-------------------|
| **Simple Components** | Component has distinct sections or responsibilities | Low | None (this is the default) |
| **Render Props** | Logic is reusable but UI varies | Medium | Hooks (in most cases) |
| **HOC** | Cross-cutting concern applied to many components | Medium-High | Hooks (in most cases) |

---

## Pattern Overview

### 1. Simple Components

**Pattern**: Decompose complex component into small, focused sub-components.

**Example**:
```tsx
<Card>
  <CardImage src="/product.jpg" alt="Product" />
  <CardTitle>Product Name</CardTitle>
  <CardDescription>Product description here</CardDescription>
  <CardActions>
    <Button>Buy</Button>
  </CardActions>
</Card>
```

**When to Use**:
- Component has multiple visual sections (header, body, footer)
- Testing needs to be granular
- Sub-components will be reused in different contexts

**File**: `simple-components.md`

---

### 2. Render Props

**Pattern**: Pass function as prop to control what component renders.

**Example**:
```tsx
<MouseTracker>
  {({ x, y }) => (
    <div>Mouse position: {x}, {y}</div>
  )}
</MouseTracker>
```

**When to Use**:
- Logic is reusable but UI varies
- Need to share stateful logic between components
- Custom rendering per use case

**Modern Alternative**: Hooks (for logic without UI wrapper)

**File**: `render-props.md`

---

### 3. Higher-Order Components (HOC)

**Pattern**: Function that takes component, returns enhanced component.

**Example**:
```tsx
const ProtectedDashboard = withAuth(Dashboard)
const TrackedProfile = withAnalytics(Profile)
```

**When to Use**:
- Cross-cutting concern applied to many components (auth, logging, theming)
- Legacy codebase with class components
- Need to enhance without modifying original code

**Modern Alternative**: Hooks (for logic reuse), Render Props (for flexible UI)

**File**: `hoc.md`

---

## Decision Tree

```
What are you trying to do?

├─ Build component from sub-components
│  → Use Simple Components
│  → Load: simple-components.md
│
├─ Reuse logic with different UIs
│  ├─ Need UI wrapper/container?
│  │  ├─ YES → Use Render Props
│  │  │        Load: render-props.md
│  │  └─ NO  → Use Hook (not in this directory)
│  │
│  └─ Apply to many components?
│     → Use HOC or Hook
│     → Load: hoc.md
│
└─ Add behavior to existing component
   → Use HOC
   → Load: hoc.md
```

---

## Examples by Use Case

### Use Case: Data Table

**Approach**: Simple Components

**Why**: Table has distinct sections (header, body, footer), each with specific rendering logic.

**Structure**:
```tsx
<DataTable>
  <TableHeader>
    <TableHeaderRow>
      <TableHeaderCell sortable>Name</TableHeaderCell>
      <TableHeaderCell sortable>Email</TableHeaderCell>
    </TableHeaderRow>
  </TableHeader>
  <TableBody>
    {users.map(user => (
      <TableRow key={user.id}>
        <TableCell>{user.name}</TableCell>
        <TableCell>{user.email}</TableCell>
      </TableRow>
    ))}
  </TableBody>
  <TableFooter>
    <TablePagination />
  </TableFooter>
</DataTable>
```

**File**: `simple-components.md` (Example 1)

---

### Use Case: Mouse Position Tracking

**Approach**: Render Props

**Why**: Logic (track mouse) is reusable, but UI varies (text, crosshair, tooltip).

**Structure**:
```tsx
// Usage 1: Text display
<MouseTracker>
  {({ x, y }) => <div>X: {x}, Y: {y}</div>}
</MouseTracker>

// Usage 2: Crosshair
<MouseTracker>
  {({ x, y }) => <Crosshair x={x} y={y} />}
</MouseTracker>
```

**Modern Alternative**: `useMousePosition()` hook

**File**: `render-props.md` (Core Example)

---

### Use Case: Protected Routes

**Approach**: HOC

**Why**: Auth check applies to many components, no need to modify each one.

**Structure**:
```tsx
function Dashboard() {
  return <div>Dashboard</div>
}

const ProtectedDashboard = withAuth(Dashboard)

<Route path="/dashboard" element={<ProtectedDashboard />} />
```

**File**: `hoc.md` (Example 1)

---

### Use Case: Form State Management

**Approach 1**: Render Props

```tsx
<Form
  initialValues={{ email: '', password: '' }}
  validate={validate}
  onSubmit={handleLogin}
>
  {({ values, errors, handleChange, handleSubmit }) => (
    <form onSubmit={handleSubmit}>
      <input value={values.email} onChange={e => handleChange('email', e.target.value)} />
      {errors.email && <span>{errors.email}</span>}
      <button type="submit">Login</button>
    </form>
  )}
</Form>
```

**Approach 2**: Simple Components (Formik-style)

```tsx
<Formik initialValues={{...}} onSubmit={...}>
  <Field name="email" />
  <ErrorMessage name="email" />
  <button type="submit">Login</button>
</Formik>
```

**Approach 3**: Hook

```tsx
const { values, errors, handleChange, handleSubmit } = useForm({
  initialValues: { email: '', password: '' },
  validate,
  onSubmit: handleLogin,
})
```

**Files**:
- Render Props: `render-props.md` (Example 2)
- Simple Components: `simple-components.md` (Example 2)

---

## Composition Anti-Patterns

### 1. Over-Decomposition

**Problem**: Too many tiny components.

```tsx
// ❌ BAD: Each word is a component
<Button>
  <ButtonIconWrapper>
    <ButtonIcon name="save" />
  </ButtonIconWrapper>
  <ButtonTextContent>
    <ButtonText>Save</ButtonText>
  </ButtonTextContent>
</Button>

// ✅ GOOD: Reasonable granularity
<Button icon="save">Save</Button>
```

**Guideline**: Decompose when sub-components have distinct responsibilities or will be reused independently.

---

### 2. Prop Drilling Through Layers

**Problem**: Passing props through multiple components that don't use them.

```tsx
// ❌ BAD: onClick passed through CardContent even though it doesn't use it
<Card onClick={handleClick}>
  <CardContent onClick={handleClick}>
    <CardTitle onClick={handleClick}>Title</CardTitle>
  </CardContent>
</Card>

// ✅ GOOD: onClick only where needed
<Card onClick={handleClick}>
  <CardContent>
    <CardTitle>Title</CardTitle>
  </CardContent>
</Card>
```

**Solution**: Use Context, Render Props, or state management library.

---

### 3. Wrapper Hell

**Problem**: Too many nested HOCs or render props.

```tsx
// ❌ BAD: 5 layers of nesting
<Fetch url="/api/user">
  {({ data: user }) => (
    <Fetch url={`/api/user/${user.id}/posts`}>
      {({ data: posts }) => (
        <Pagination items={posts} pageSize={5}>
          {(paginatedPosts) => (
            <Filter items={paginatedPosts} filterKey="published">
              {(filteredPosts) => (
                <div>{filteredPosts.map(post => <Post key={post.id} post={post} />)}</div>
              )}
            </Filter>
          )}
        </Pagination>
      )}
    </Fetch>
  )}
</Fetch>

// ✅ GOOD: Extract to separate component or use hooks
function UserPosts({ userId }: { userId: string }) {
  const posts = useFetch(`/api/user/${userId}/posts`)
  const paginatedPosts = usePagination(posts, 5)
  const filteredPosts = useFilter(paginatedPosts, 'published')

  return (
    <div>
      {filteredPosts.map(post => <Post key={post.id} post={post} />)}
    </div>
  )
}
```

**Solution**: Extract logic into hooks or separate components.

---

## Migration Guide

### From HOC to Hook

**Before (HOC)**:
```tsx
const UserProfile = withUser(Profile)
```

**After (Hook)**:
```tsx
function Profile() {
  const user = useUser()
  return <div>{user.name}</div>
}
```

**When Hooks Can't Replace HOCs**:
- Error boundaries (no error boundary hook)
- Class components (no hooks in classes)
- Need to wrap without modifying code

---

### From Render Prop to Hook

**Before (Render Prop)**:
```tsx
<WindowSize>
  {({ width, height }) => <div>Window: {width} x {height}</div>}
</WindowSize>
```

**After (Hook)**:
```tsx
function App() {
  const { width, height } = useWindowSize()
  return <div>Window: {width} x {height}</div>
}
```

**When Render Props Better**:
- Logic is tied to UI container (e.g., Dropdown with wrapper div)
- Multiple render areas (e.g., `renderHeader`, `renderItem`, `renderFooter`)

---

### From Simple Components to Compound Component

**Before (Simple)**:
```tsx
<Tabs>
  <Tab label="Tab 1">Content 1</Tab>
  <Tab label="Tab 2">Content 2</Tab>
</Tabs>
```

**After (Compound)**:
```tsx
<Tabs>
  <TabList>
    <Tab>Tab 1</Tab>
    <Tab>Tab 2</Tab>
  </TabList>
  <TabPanels>
    <TabPanel>Content 1</TabPanel>
    <TabPanel>Content 2</TabPanel>
  </TabPanels>
</Tabs>
```

**Why**: More flexible (tabs and panels can be in different locations).

---

## Performance Comparison

| Pattern | Re-render Behavior | Optimization |
|---------|-------------------|--------------|
| **Simple Components** | Each sub-component re-renders when parent state changes | Use `React.memo` on sub-components |
| **Render Props** | Inline functions cause re-renders | Extract function or use `useCallback` |
| **HOC** | Creates new component, can cause unnecessary re-renders | Define HOC outside render, use `React.memo` |

---

## Accessibility Notes

### Simple Components
- Use semantic HTML (`<h3>` for CardTitle, not `<div>`)
- Preserve ARIA attributes in sub-components

### Render Props
- Don't break HTML semantics (e.g., `<ul><div><li>` is invalid)
- Pass ARIA props through render function

### HOC
- Forward refs to wrapped component
- Don't override wrapped component's ARIA attributes

---

## Testing Strategies

### Simple Components
- Test each sub-component in isolation
- Test composition in integration tests

### Render Props
- Test logic component with mock render function
- Test full usage with real render function

### HOC
- Test HOC in isolation (mock wrapped component)
- Test wrapped component without HOC
- Test enhanced component (with HOC applied)

---

## Summary

**Composition is about**:
- Building complex UIs from simple, reusable pieces
- Choosing the right pattern for the use case
- Avoiding over-engineering (prefer simplest pattern that works)

**Pattern Selection**:
1. **Default**: Simple Components (most cases)
2. **Logic reuse with variable UI**: Render Props or Hooks
3. **Cross-cutting concerns**: HOC or Hooks
4. **Modern React**: Prefer Hooks over Render Props/HOC when possible

**Files in this directory**:
- `simple-components.md` - Decompose into focused sub-components
- `render-props.md` - Pass function as prop to control rendering
- `hoc.md` - Wrap component to add functionality

**Next Steps**:
- Read `simple-components.md` for most common pattern
- Read `render-props.md` if UI varies per use case
- Read `hoc.md` for cross-cutting concerns (auth, logging, etc.)
