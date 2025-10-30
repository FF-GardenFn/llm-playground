# Performance Optimization Checklist

**GATE: Cannot claim performance work complete without addressing ALL applicable checks.**

Performance is not optional for production React applications.

---

## Render Optimization

- [ ] **Expensive calculations memoized**
  - useMemo wraps calculations that run on every render
  - Dependencies array accurate (only recompute when needed)
  - Verified with React DevTools Profiler (reduced render time)

- [ ] **Callback functions stable**
  - useCallback prevents new function instances
  - Event handlers passed to memoized components stable
  - Dependencies array minimal and accurate

- [ ] **Components memoized appropriately**
  - React.memo wraps components that re-render unnecessarily
  - Props comparison function if needed (complex prop types)
  - Verified re-render reduction with Profiler

**Why**: Unnecessary re-renders are the #1 performance issue in React apps.

---

## List & Data Optimization

- [ ] **Large lists virtualized**
  - Lists >100 items use react-window or react-virtualized
  - Only visible items rendered (windowing technique)
  - Scroll performance smooth (60fps)

- [ ] **Data transformations optimized**
  - Filter/map/sort operations memoized
  - Derived data computed once, not on every render
  - Consider moving heavy operations to Web Workers

**Example**:
```jsx
// ✅ Good: Virtualized list
import { FixedSizeList } from 'react-window'

function LargeList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>{items[index].name}</div>
  )

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  )
}

// ❌ Bad: Rendering all items
function LargeList({ items }) {
  return (
    <div>
      {items.map(item => <div key={item.id}>{item.name}</div>)}
    </div>
  )
}
```

**Why**: Rendering thousands of DOM nodes tanks performance.

---

## Code Splitting

- [ ] **Routes split by dynamic import**
  - React.lazy() + Suspense for route components
  - Each route in separate bundle
  - Loading states shown during code load

- [ ] **Large dependencies lazy loaded**
  - Heavy libraries (charts, editors) loaded on demand
  - Dynamic import() for conditional features
  - Bundle analyzer used to identify large deps

- [ ] **Initial bundle size reasonable**
  - Main bundle <200KB (gzipped)
  - Analyzed with webpack-bundle-analyzer or similar
  - Tree shaking enabled (ES modules)

**Example**:
```jsx
// ✅ Good: Route-based splitting
const Dashboard = React.lazy(() => import('./Dashboard'))
const Settings = React.lazy(() => import('./Settings'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  )
}

// ✅ Good: Lazy load heavy component
const ChartEditor = React.lazy(() => import('./ChartEditor'))

function Dashboard({ showChart }) {
  return (
    <div>
      {showChart && (
        <Suspense fallback={<Skeleton />}>
          <ChartEditor />
        </Suspense>
      )}
    </div>
  )
}
```

**Why**: Users shouldn't download code they don't use.

---

## Image & Media Optimization

- [ ] **Images optimized**
  - Modern formats (WebP, AVIF) with fallbacks
  - Responsive images (srcset, sizes)
  - Lazy loading (loading="lazy" or Intersection Observer)
  - Next.js: Use next/image component

- [ ] **Icons optimized**
  - SVG icons instead of icon fonts (better performance)
  - Inline critical icons, lazy load others
  - Icon sprite sheets for repeated icons

- [ ] **Video/animations optimized**
  - Autoplay videos muted and short
  - CSS animations instead of JS (when possible)
  - Avoid layout shifts (reserve space for media)

**Example**:
```jsx
// ✅ Good: Optimized image (Next.js)
import Image from 'next/image'

function Hero() {
  return (
    <Image
      src="/hero.jpg"
      alt="Hero image"
      width={1200}
      height={600}
      priority  // LCP image loaded immediately
      placeholder="blur"
    />
  )
}

// ✅ Good: Lazy loaded images
<img
  src="/image.jpg"
  alt="Description"
  loading="lazy"
  width="800"
  height="600"
/>
```

**Why**: Images are often the largest assets, optimizing them improves LCP.

---

## State & Data Fetching

- [ ] **Server state managed correctly**
  - React Query or SWR for server data (caching, deduplication)
  - Separate server state from UI state
  - Optimistic updates for better UX

- [ ] **API calls optimized**
  - Debounced/throttled search/filter inputs
  - Pagination or infinite scroll for large datasets
  - GraphQL queries fetch only needed fields

- [ ] **Context optimized**
  - Context value memoized (prevent re-renders)
  - Split contexts by concern (theme, auth separate)
  - Use context selectors if available (prevent unnecessary subscriptions)

**Example**:
```jsx
// ✅ Good: Memoized context value
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

// ✅ Good: Debounced search
function SearchInput() {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, 300)

  const { data } = useQuery(['search', debouncedQuery], () =>
    fetch(`/api/search?q=${debouncedQuery}`)
  )

  return <input value={query} onChange={e => setQuery(e.target.value)} />
}
```

**Why**: Unnecessary API calls and re-renders waste resources.

---

## Performance Metrics

- [ ] **Lighthouse score >90**
  - Performance score >90 (desktop)
  - Performance score >80 (mobile)
  - Run audits regularly (CI/CD)

- [ ] **Core Web Vitals passing**
  - LCP (Largest Contentful Paint) <2.5s
  - FID (First Input Delay) <100ms
  - CLS (Cumulative Layout Shift) <0.1

- [ ] **Bundle size monitored**
  - Bundle size tracked in CI (fail if too large)
  - Regular audits with bundle analyzer
  - Third-party dependencies evaluated (size vs value)

**Tools**:
```bash
# Lighthouse CLI
npm install -g lighthouse
lighthouse https://yourapp.com --view

# Bundle analyzer (webpack)
npm install --save-dev webpack-bundle-analyzer
# Add to webpack config, then run build

# Next.js bundle analyzer
npm install --save-dev @next/bundle-analyzer
# Add to next.config.js
```

**Why**: Metrics provide objective performance measurement.

---

## React 18+ Features

- [ ] **useTransition for non-urgent updates**
  - Search input, filtering use startTransition
  - UI stays responsive during heavy updates
  - Pending state shown to user

- [ ] **useDeferredValue for expensive renders**
  - Large lists defer updates while typing
  - Keep input responsive, defer re-render

- [ ] **Suspense for data fetching**
  - Declarative loading states
  - Streaming SSR (Next.js App Router)
  - Better UX with loading boundaries

**Example**:
```jsx
// ✅ Good: useTransition for search
function SearchResults() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [isPending, startTransition] = useTransition()

  const handleSearch = (value) => {
    setQuery(value)  // Immediate update (input stays responsive)
    startTransition(() => {
      setResults(heavySearchFunction(value))  // Deferred update
    })
  }

  return (
    <>
      <input value={query} onChange={e => handleSearch(e.target.value)} />
      {isPending ? <Spinner /> : <ResultsList results={results} />}
    </>
  )
}
```

**Why**: React 18 features improve perceived performance.

---

## Common Performance Mistakes

### ❌ Mistake 1: Inline Functions in Render

```jsx
// Bad: Creates new function on every render
function List({ items }) {
  return (
    <div>
      {items.map(item => (
        <Item key={item.id} onClick={() => handleClick(item.id)} />
      ))}
    </div>
  )
}

// Good: Stable function reference
function List({ items }) {
  const handleClick = useCallback((id) => {
    // handle click
  }, [])

  return (
    <div>
      {items.map(item => (
        <Item key={item.id} onClick={() => handleClick(item.id)} />
      ))}
    </div>
  )
}
```

### ❌ Mistake 2: Not Memoizing Expensive Calculations

```jsx
// Bad: Recalculates on every render
function Dashboard({ data }) {
  const sortedData = data.sort((a, b) => a.value - b.value)  // Runs every render!
  return <Chart data={sortedData} />
}

// Good: Only recalculates when data changes
function Dashboard({ data }) {
  const sortedData = useMemo(
    () => data.sort((a, b) => a.value - b.value),
    [data]
  )
  return <Chart data={sortedData} />
}
```

### ❌ Mistake 3: Rendering All List Items

```jsx
// Bad: Renders 10,000 DOM nodes
function DataTable({ rows }) {
  return (
    <div>
      {rows.map(row => <Row key={row.id} data={row} />)}
    </div>
  )
}

// Good: Virtualizes list (only renders visible)
import { FixedSizeList } from 'react-window'

function DataTable({ rows }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={rows.length}
      itemSize={50}
    >
      {({ index, style }) => (
        <div style={style}>
          <Row data={rows[index]} />
        </div>
      )}
    </FixedSizeList>
  )
}
```

### ❌ Mistake 4: Large Bundle (No Code Splitting)

```jsx
// Bad: All routes in main bundle
import Dashboard from './Dashboard'
import Settings from './Settings'
import Reports from './Reports'

function App() {
  return (
    <Routes>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/reports" element={<Reports />} />
    </Routes>
  )
}

// Good: Route-based code splitting
const Dashboard = React.lazy(() => import('./Dashboard'))
const Settings = React.lazy(() => import('./Settings'))
const Reports = React.lazy(() => import('./Reports'))

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </Suspense>
  )
}
```

---

## When to Optimize

**Optimize when**:
- Profiling shows actual performance issue
- User-facing metrics (LCP, FID) exceed thresholds
- User feedback mentions slow interactions
- Large datasets (>100 items in lists)

**Don't optimize when**:
- No measured performance issue (premature optimization)
- Adding complexity without benefit
- Micro-optimizing insignificant operations

**Rule**: Measure first, optimize second.

---

## Gate Status

**Performance work complete**: Only when applicable checks above are addressed.

**If any applicable item unchecked**:
- Performance optimization incomplete
- Application may have poor user experience
- Must address issues before production

---

## Profiling Tools

**React DevTools Profiler**:
1. Install React DevTools extension
2. Open Profiler tab
3. Click "Record" and interact with app
4. Identify slow components (flame graph)
5. Check "Why did this render?" for each component

**Chrome DevTools Performance**:
1. Open Performance tab
2. Record interaction
3. Look for long tasks (>50ms)
4. Identify bottlenecks in Main thread

**Lighthouse**:
```bash
# Run Lighthouse audit
lighthouse https://yourapp.com --view

# Run in CI
lighthouse https://yourapp.com --output=json --output-path=./report.json
```

**Bundle Analyzer**:
```bash
# Webpack Bundle Analyzer
npm run build -- --analyze

# Next.js Bundle Analyzer
ANALYZE=true npm run build
```

---

## Summary

**Performance checklist enforces**:
- Render optimization (memoization, stable callbacks)
- List virtualization (large datasets)
- Code splitting (reasonable bundle size)
- Image optimization (modern formats, lazy loading)
- State management (server state, context optimization)
- Performance metrics (Lighthouse >90, Core Web Vitals)

**Cannot claim performance work complete without addressing applicable checks.**

**This is not optional. This is a gate.**
