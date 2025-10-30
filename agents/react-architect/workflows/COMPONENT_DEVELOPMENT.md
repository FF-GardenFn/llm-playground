# Component Development Workflow

**Purpose**: Systematic 6-phase workflow for building React components from requirements to production-ready code.

**When to Use**: Any component development task - from simple buttons to complex data tables.

**Core Principle**: Each phase has explicit gates. You cannot proceed to the next phase until current phase gates pass.

---

## Workflow Overview

```
Phase 1: Requirements Analysis
    ↓ GATE: Requirements documented
Phase 2: Pattern Selection
    ↓ GATE: Patterns chosen with rationale
Phase 3: State Management
    ↓ GATE: State strategy defined
Phase 4: Performance Optimization
    ↓ GATE: Performance checklist complete
Phase 5: Testing Strategy
    ↓ GATE: Test plan documented
Phase 6: Accessibility Audit
    ↓ GATE: A11y checklist passed
```

---

## Phase 1: Requirements Analysis

**Goal**: Document what the component must do, not how it will do it.

### Gate: Requirements Documented

**Cannot proceed to Phase 2 until**:
- [ ] Component purpose stated in 1-2 sentences
- [ ] User interactions listed (clicks, keyboard, focus, etc.)
- [ ] Data dependencies identified (props, context, API)
- [ ] Edge cases documented (loading, error, empty states)
- [ ] Success criteria defined (measurable)

### Process

#### Step 1.1: State Component Purpose

**Format**:
```
Component: [Name]
Purpose: [1-2 sentence description]
Primary Use Case: [When would a user interact with this?]
```

**Example: Data Table**:
```
Component: DataTable
Purpose: Display tabular data with sorting, filtering, and pagination.
Primary Use Case: Users need to explore large datasets (>100 rows) with search and sort.
```

**Example: Form Input**:
```
Component: TextInput
Purpose: Single-line text input with validation and error display.
Primary Use Case: Users enter email, password, or other short text values.
```

#### Step 1.2: List User Interactions

**Format**: For each interaction, specify trigger and expected outcome.

**Example: Data Table**:
```
Interactions:
1. Click column header → Sort by that column (toggle asc/desc)
2. Type in search box → Filter rows by search term
3. Click pagination button → Navigate to next/previous page
4. Click row → Select row (optional, based on use case)
5. Press arrow keys → Navigate cells (keyboard accessibility)
```

**Example: Form Input**:
```
Interactions:
1. Focus input → Show focus indicator
2. Type text → Update value, validate on blur
3. Press Enter → Submit form (if in form context)
4. Blur input → Run validation, show error if invalid
5. Click clear button → Clear value
```

#### Step 1.3: Identify Data Dependencies

**Format**: List all data sources the component needs.

**Categories**:
- **Props**: Data passed from parent
- **Context**: Shared state (theme, auth, etc.)
- **API**: External data fetching
- **Local State**: Component-internal state

**Example: Data Table**:
```
Data Dependencies:
- Props:
  - data: Array<Record<string, any>> (rows)
  - columns: Array<ColumnDef> (column config)
  - onRowClick?: (row: any) => void (optional)
- Context:
  - theme (light/dark mode)
- API:
  - None (data passed via props)
- Local State:
  - sortColumn: string | null
  - sortDirection: 'asc' | 'desc'
  - filterText: string
  - currentPage: number
```

**Example: Form Input**:
```
Data Dependencies:
- Props:
  - value: string
  - onChange: (value: string) => void
  - label: string
  - error?: string
  - required?: boolean
- Context:
  - formContext (for form-level validation)
- API:
  - None
- Local State:
  - isFocused: boolean
  - isDirty: boolean
```

#### Step 1.4: Document Edge Cases

**Format**: List states beyond "happy path".

**Common Edge Cases**:
- **Loading**: Data is fetching
- **Error**: Request failed or validation error
- **Empty**: No data to display
- **Partial**: Some data missing (null/undefined fields)
- **Overflow**: Too much data (truncation, pagination)

**Example: Data Table**:
```
Edge Cases:
1. Loading: Show skeleton rows while data fetches
2. Error: Show error message with retry button
3. Empty: Show "No data" message with optional action
4. Partial: Handle null/undefined cell values gracefully
5. Overflow: Implement pagination if rows > 50
6. No columns: Show error (cannot render without column config)
```

**Example: Form Input**:
```
Edge Cases:
1. Loading: Disable input, show spinner
2. Error: Show error message below input, red border
3. Empty: Show placeholder text
4. Max length: Truncate input at maxLength prop
5. Disabled: Grayed out, not focusable
6. Read-only: Focusable but not editable
```

#### Step 1.5: Define Success Criteria

**Format**: Measurable outcomes that define "done".

**Example: Data Table**:
```
Success Criteria:
1. Renders 1000 rows without visible lag (<100ms)
2. Sort toggles in <50ms (no flash of unsorted content)
3. Filter applies in <100ms with debounce
4. Keyboard navigation works (arrow keys, Tab)
5. Screen reader announces sort/filter changes
6. Passes all WCAG AA accessibility checks
7. Works on mobile (touch-friendly)
```

**Example: Form Input**:
```
Success Criteria:
1. Validation runs on blur, not on every keystroke
2. Error message appears within 100ms of blur
3. Screen reader announces error when it appears
4. Keyboard-only users can clear input (Esc key)
5. Works on mobile (touch-friendly, no zoom on focus)
6. Passes all WCAG AA accessibility checks
```

### Phase 1 Checklist

Before proceeding to Phase 2:
- [ ] Component purpose documented
- [ ] All user interactions listed
- [ ] Data dependencies identified (props, context, API, state)
- [ ] Edge cases documented (loading, error, empty, overflow)
- [ ] Success criteria defined (measurable)
- [ ] Requirements reviewed (no ambiguity)

### Phase 1 Output Example

**Component: SearchableDropdown**

```markdown
## Requirements

**Purpose**: Dropdown with search/filter for selecting from large lists (>20 options).

**Primary Use Case**: Users select a country, state, or category from a long list.

**Interactions**:
1. Click dropdown → Open menu
2. Type in search box → Filter options by text
3. Click option → Select option, close menu
4. Press arrow keys → Navigate options
5. Press Esc → Close menu
6. Click outside → Close menu

**Data Dependencies**:
- Props:
  - options: Array<{value: string, label: string}>
  - value: string | null
  - onChange: (value: string) => void
  - placeholder?: string
- Context: theme
- API: None
- Local State:
  - isOpen: boolean
  - filterText: string
  - highlightedIndex: number

**Edge Cases**:
1. Empty options: Show "No options" message
2. No match: Show "No results for '{query}'"
3. Loading: Show spinner in menu
4. Disabled: Grayed out, not clickable
5. Long labels: Truncate with ellipsis

**Success Criteria**:
1. Filter applies in <50ms with debounce
2. Keyboard navigation works (arrow keys, Enter, Esc)
3. Screen reader announces selection
4. Works on mobile (touch-friendly)
5. Passes WCAG AA checks
```

---

## Phase 2: Pattern Selection

**Goal**: Choose React patterns that match requirements. No coding yet - just decisions with rationale.

### Gate: Patterns Chosen

**Cannot proceed to Phase 3 until**:
- [ ] Component type chosen (simple, composition, data-fetching, form)
- [ ] Patterns documented with rationale
- [ ] Files to load identified (from patterns/ directory)
- [ ] Code structure sketched (file/folder layout)

### Process

#### Step 2.1: Choose Component Type

**Decision Tree**:

```
Does component fetch data?
├─ YES → Data-Fetching Component
│         Load: patterns/data-fetching/
│
└─ NO → Does component manage complex state?
         ├─ YES → Composition Component
         │         Load: patterns/composition/
         │
         └─ NO → Does component handle forms?
                  ├─ YES → Form Component
                  │         Load: patterns/forms/
                  │
                  └─ NO → Simple Component
                            Load: patterns/composition/simple-components.md
```

**Example: Data Table**:
```
Component Type: Composition Component
Rationale: Complex state (sort, filter, pagination) but no data fetching
Files to Load:
- patterns/composition/simple-components.md (for cell rendering)
- patterns/composition/render-props.md (for custom cell renderers)
```

**Example: SearchableDropdown**:
```
Component Type: Simple Component with Local State
Rationale: Local state (isOpen, filterText) but not complex enough for useReducer
Files to Load:
- patterns/composition/simple-components.md
- patterns/forms/controlled-forms.md (for input handling)
```

#### Step 2.2: Document Pattern Decisions

**Format**: For each pattern, state decision and rationale.

**Pattern Categories**:
1. **Composition**: How to structure component hierarchy
2. **State Management**: How to manage state
3. **Data Fetching**: How to load external data
4. **Performance**: How to optimize rendering
5. **Accessibility**: How to support assistive tech

**Example: Data Table**:
```markdown
### Pattern Decisions

**1. Composition**:
- Pattern: Simple Components (TableHeader, TableRow, TableCell)
- Rationale: Clear separation of concerns, easier to test

**2. State Management**:
- Pattern: useState for simple state (sortColumn, filterText)
- Rationale: State is independent (no complex interactions)

**3. Data Fetching**:
- Pattern: None (data via props)
- Rationale: Parent handles fetching, table just displays

**4. Performance**:
- Pattern: React.memo for TableRow
- Rationale: Prevent re-renders when parent state changes

**5. Accessibility**:
- Pattern: ARIA table role, keyboard navigation
- Rationale: Must work with screen readers
```

**Example: SearchableDropdown**:
```markdown
### Pattern Decisions

**1. Composition**:
- Pattern: Simple Component with sub-components (DropdownMenu, DropdownItem)
- Rationale: Menu rendering logic is reusable

**2. State Management**:
- Pattern: useState for isOpen, filterText, highlightedIndex
- Rationale: Simple state, no complex updates

**3. Data Fetching**:
- Pattern: None (options via props)
- Rationale: Parent handles option loading

**4. Performance**:
- Pattern: useMemo for filtered options
- Rationale: Avoid re-filtering on every render

**5. Accessibility**:
- Pattern: ARIA combobox role, keyboard navigation
- Rationale: Must support keyboard-only users
```

#### Step 2.3: Identify Files to Load

**Load patterns/ files based on decisions**.

**Example: Data Table**:
```
Files to Load:
1. patterns/composition/simple-components.md (for component structure)
2. state/hooks/useState.md (for sortColumn, filterText state)
3. performance/react-memo.md (for TableRow optimization)
4. accessibility/keyboard-navigation.md (for arrow key support)
```

**Example: SearchableDropdown**:
```
Files to Load:
1. patterns/composition/simple-components.md (for structure)
2. patterns/forms/controlled-forms.md (for search input)
3. state/hooks/useState.md (for isOpen, filterText)
4. performance/useMemo.md (for filtered options)
5. accessibility/keyboard-navigation.md (for arrow keys)
```

#### Step 2.4: Sketch Code Structure

**Format**: File/folder layout, not implementation.

**Example: Data Table**:
```
components/
├── DataTable/
│   ├── index.tsx (main component)
│   ├── TableHeader.tsx (column headers)
│   ├── TableRow.tsx (row rendering)
│   ├── TableCell.tsx (cell rendering)
│   ├── TablePagination.tsx (pagination controls)
│   ├── useTableState.ts (custom hook for state)
│   └── DataTable.test.tsx (tests)
```

**Example: SearchableDropdown**:
```
components/
├── SearchableDropdown/
│   ├── index.tsx (main component)
│   ├── DropdownMenu.tsx (menu rendering)
│   ├── DropdownItem.tsx (single option)
│   ├── useDropdownKeyboard.ts (keyboard logic)
│   └── SearchableDropdown.test.tsx (tests)
```

### Phase 2 Checklist

Before proceeding to Phase 3:
- [ ] Component type chosen (simple, composition, data-fetching, form)
- [ ] Patterns documented for composition, state, data, performance, a11y
- [ ] Rationale provided for each pattern choice
- [ ] Files to load identified (from patterns/ directory)
- [ ] Code structure sketched (file/folder layout)
- [ ] Patterns reviewed (no over-engineering)

### Phase 2 Output Example

**Component: SearchableDropdown**

```markdown
## Pattern Selection

**Component Type**: Simple Component with Local State

**Pattern Decisions**:

1. **Composition**: Simple Components
   - DropdownMenu, DropdownItem sub-components
   - Rationale: Reusable menu rendering logic

2. **State Management**: useState
   - isOpen, filterText, highlightedIndex
   - Rationale: Simple independent state

3. **Data Fetching**: None
   - Options passed via props
   - Rationale: Parent handles loading

4. **Performance**: useMemo
   - Filter options once per render
   - Rationale: Avoid re-filtering on every keystroke

5. **Accessibility**: ARIA combobox + keyboard nav
   - Rationale: Must support keyboard-only users

**Files to Load**:
- patterns/composition/simple-components.md
- patterns/forms/controlled-forms.md
- state/hooks/useState.md
- performance/useMemo.md
- accessibility/keyboard-navigation.md

**Code Structure**:
```
components/SearchableDropdown/
├── index.tsx (main component)
├── DropdownMenu.tsx (menu UI)
├── DropdownItem.tsx (option UI)
├── useDropdownKeyboard.ts (keyboard logic)
└── SearchableDropdown.test.tsx (tests)
```
```

---

## Phase 3: State Management

**Goal**: Define state shape, update logic, and data flow before writing component code.

### Gate: State Strategy Defined

**Cannot proceed to Phase 4 until**:
- [ ] State shape documented (types)
- [ ] State updates documented (setters, actions)
- [ ] Data flow documented (props → state → render)
- [ ] State strategy chosen (useState, useReducer, zustand, etc.)
- [ ] Edge case handling documented (error, loading, empty)

### Process

#### Step 3.1: Define State Shape

**Format**: TypeScript interfaces for all state.

**Example: Data Table**:
```typescript
// Local State
interface TableState {
  sortColumn: string | null
  sortDirection: 'asc' | 'desc'
  filterText: string
  currentPage: number
}

// Props (parent-managed state)
interface DataTableProps {
  data: Array<Record<string, any>>
  columns: Array<ColumnDef>
  onRowClick?: (row: any) => void
}

// Derived State (computed from local + props)
interface DerivedState {
  filteredData: Array<Record<string, any>>
  sortedData: Array<Record<string, any>>
  paginatedData: Array<Record<string, any>>
  totalPages: number
}
```

**Example: SearchableDropdown**:
```typescript
// Local State
interface DropdownState {
  isOpen: boolean
  filterText: string
  highlightedIndex: number
}

// Props
interface DropdownProps {
  options: Array<{value: string, label: string}>
  value: string | null
  onChange: (value: string) => void
  placeholder?: string
}

// Derived State
interface DerivedState {
  filteredOptions: Array<{value: string, label: string}>
  selectedOption: {value: string, label: string} | null
}
```

#### Step 3.2: Document State Updates

**Format**: For each state field, list triggers and update logic.

**Example: Data Table**:
```typescript
// State Updates
interface TableActions {
  // Sort
  setSortColumn: (column: string) => void
  // Trigger: User clicks column header
  // Logic: Toggle direction if same column, else set to 'asc'

  // Filter
  setFilterText: (text: string) => void
  // Trigger: User types in search box
  // Logic: Update filterText, reset to page 1

  // Pagination
  setCurrentPage: (page: number) => void
  // Trigger: User clicks prev/next button
  // Logic: Update currentPage (clamped to 0...totalPages-1)
}
```

**Example: SearchableDropdown**:
```typescript
// State Updates
interface DropdownActions {
  // Open/Close
  setIsOpen: (open: boolean) => void
  // Trigger: Click dropdown, Esc key, click outside
  // Logic: Toggle isOpen

  // Filter
  setFilterText: (text: string) => void
  // Trigger: User types in search box
  // Logic: Update filterText, reset highlightedIndex to 0

  // Highlight
  setHighlightedIndex: (index: number) => void
  // Trigger: Arrow keys
  // Logic: Increment/decrement (wrap at boundaries)

  // Select
  selectOption: (value: string) => void
  // Trigger: Click option, Enter key
  // Logic: Call onChange(value), close menu, clear filter
}
```

#### Step 3.3: Document Data Flow

**Format**: Trace data from props → state → render.

**Example: Data Table**:
```
Data Flow:

1. Parent passes data, columns props
   ↓
2. Component initializes local state (sortColumn, filterText, etc.)
   ↓
3. useMemo computes filteredData (data + filterText)
   ↓
4. useMemo computes sortedData (filteredData + sortColumn)
   ↓
5. useMemo computes paginatedData (sortedData + currentPage)
   ↓
6. Component renders paginatedData
   ↓
7. User interaction updates state (setSortColumn, setFilterText, etc.)
   ↓
8. React re-renders with new derived state
```

**Example: SearchableDropdown**:
```
Data Flow:

1. Parent passes options, value, onChange props
   ↓
2. Component initializes local state (isOpen, filterText, highlightedIndex)
   ↓
3. useMemo computes filteredOptions (options + filterText)
   ↓
4. useMemo finds selectedOption (options + value)
   ↓
5. Component renders filteredOptions in menu
   ↓
6. User interaction updates state (setIsOpen, setFilterText, selectOption)
   ↓
7. React re-renders with new state
   ↓
8. selectOption calls onChange(value) to notify parent
```

#### Step 3.4: Choose State Strategy

**Decision Tree**:

```
Is state complex (>5 fields with interdependencies)?
├─ YES → useReducer
│         Load: state/hooks/useReducer.md
│
└─ NO → Does state need to be shared across components?
         ├─ YES → Context or Zustand
         │         Load: state/context/context-state.md
         │                state/patterns/zustand.md
         │
         └─ NO → useState
                   Load: state/hooks/useState.md
```

**Example: Data Table**:
```
Strategy: useState

Rationale:
- State is simple (4 fields)
- No interdependencies (sortColumn doesn't affect filterText)
- No need for global state (table is self-contained)

Implementation:
const [sortColumn, setSortColumn] = useState<string | null>(null)
const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
const [filterText, setFilterText] = useState('')
const [currentPage, setCurrentPage] = useState(0)
```

**Example: SearchableDropdown**:
```
Strategy: useState

Rationale:
- State is simple (3 fields)
- No interdependencies
- No need for global state

Implementation:
const [isOpen, setIsOpen] = useState(false)
const [filterText, setFilterText] = useState('')
const [highlightedIndex, setHighlightedIndex] = useState(0)
```

#### Step 3.5: Document Edge Case Handling

**Format**: For each edge case, specify state changes.

**Example: Data Table**:
```
Edge Case Handling:

1. Loading:
   - Add isLoading prop
   - Render skeleton rows when isLoading=true
   - Disable sort/filter controls

2. Error:
   - Add error prop
   - Render error message when error !== null
   - Show retry button

3. Empty:
   - Check data.length === 0
   - Render "No data" message
   - Hide pagination controls

4. No Match (filterText + no results):
   - Check filteredData.length === 0
   - Render "No results for '{filterText}'"
   - Show clear filter button

5. Page Out of Bounds (data changes):
   - useEffect: If currentPage >= totalPages, reset to 0
```

**Example: SearchableDropdown**:
```
Edge Case Handling:

1. Empty Options:
   - Check options.length === 0
   - Render "No options" message
   - Disable dropdown

2. No Match (filterText + no results):
   - Check filteredOptions.length === 0
   - Render "No results for '{filterText}'"
   - Don't show menu

3. Disabled:
   - Add disabled prop
   - Gray out component
   - Ignore click/keyboard events

4. Loading:
   - Add isLoading prop
   - Show spinner in menu
   - Disable selection

5. Highlighted Out of Bounds (filter changes):
   - useEffect: If highlightedIndex >= filteredOptions.length, reset to 0
```

### Phase 3 Checklist

Before proceeding to Phase 4:
- [ ] State shape documented (TypeScript interfaces)
- [ ] State updates documented (triggers + logic)
- [ ] Data flow documented (props → state → render)
- [ ] State strategy chosen (useState, useReducer, context, zustand)
- [ ] Edge case handling documented (error, loading, empty)
- [ ] State plan reviewed (no over-engineering)

### Phase 3 Output Example

**Component: SearchableDropdown**

```markdown
## State Management

**State Shape**:
```typescript
interface DropdownState {
  isOpen: boolean
  filterText: string
  highlightedIndex: number
}

interface DropdownProps {
  options: Array<{value: string, label: string}>
  value: string | null
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
  isLoading?: boolean
}

interface DerivedState {
  filteredOptions: Array<{value: string, label: string}>
  selectedOption: {value: string, label: string} | null
}
```

**State Updates**:
- setIsOpen: Toggle on click, Esc, click outside
- setFilterText: Update on keystroke, reset highlightedIndex
- setHighlightedIndex: Increment/decrement on arrow keys (wrap)
- selectOption: Call onChange, close menu, clear filter

**Data Flow**:
Props → Local State → Derived State (useMemo) → Render → User Event → Update State

**Strategy**: useState
- Rationale: Simple state (3 fields), no interdependencies

**Edge Cases**:
1. Empty options → "No options" message
2. No match → "No results for '{filterText}'"
3. Disabled → Gray out, ignore events
4. Loading → Show spinner, disable selection
5. Highlighted out of bounds → Reset to 0
```

---

## Phase 4: Performance Optimization

**Goal**: Ensure component renders efficiently. Load performance/ files and apply checklist.

### Gate: Performance Checklist Complete

**Cannot proceed to Phase 5 until**:
- [ ] Performance checklist from performance/checklist.md reviewed
- [ ] Applicable optimizations documented (memo, useMemo, useCallback)
- [ ] Render count analyzed (React DevTools Profiler)
- [ ] Large data handling strategy defined (virtualization, pagination)
- [ ] Bundle size checked (no unnecessary imports)

### Process

**Load File**: `performance/checklist.md`

**Key Questions**:
1. Does component re-render unnecessarily?
2. Does component handle large datasets (>100 items)?
3. Does component import heavy libraries?
4. Does component compute expensive values on every render?

**Common Optimizations**:

#### 4.1: React.memo for Child Components

**When**: Child re-renders even when props don't change.

**Example: Data Table**:
```typescript
// TableRow re-renders when sortColumn changes (but row data doesn't)
const TableRow = React.memo<TableRowProps>(({ row, columns }) => {
  return (
    <tr>
      {columns.map(col => <TableCell key={col.key} value={row[col.key]} />)}
    </tr>
  )
})
```

#### 4.2: useMemo for Expensive Computations

**When**: Derived state is expensive to compute.

**Example: Data Table**:
```typescript
// Filtering + sorting is expensive for large datasets
const filteredData = useMemo(() => {
  return data.filter(row =>
    Object.values(row).some(val =>
      String(val).toLowerCase().includes(filterText.toLowerCase())
    )
  )
}, [data, filterText])

const sortedData = useMemo(() => {
  if (!sortColumn) return filteredData
  return [...filteredData].sort((a, b) => {
    const aVal = a[sortColumn]
    const bVal = b[sortColumn]
    if (sortDirection === 'asc') return aVal > bVal ? 1 : -1
    return aVal < bVal ? 1 : -1
  })
}, [filteredData, sortColumn, sortDirection])
```

#### 4.3: useCallback for Stable Function References

**When**: Passing callbacks to memoized children.

**Example: Data Table**:
```typescript
const handleSort = useCallback((column: string) => {
  if (sortColumn === column) {
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
  } else {
    setSortColumn(column)
    setSortDirection('asc')
  }
}, [sortColumn])

// Now TableHeader can be memoized
<TableHeader columns={columns} onSort={handleSort} />
```

#### 4.4: Virtualization for Large Lists

**When**: Rendering >100 items.

**Example: Data Table**:
```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

const rowVirtualizer = useVirtualizer({
  count: sortedData.length,
  getScrollElement: () => tableContainerRef.current,
  estimateSize: () => 50, // Row height
  overscan: 5, // Render 5 extra rows
})

// Only render visible rows
{rowVirtualizer.getVirtualItems().map(virtualRow => (
  <TableRow
    key={virtualRow.index}
    row={sortedData[virtualRow.index]}
    style={{ height: `${virtualRow.size}px` }}
  />
))}
```

#### 4.5: Debounce for High-Frequency Updates

**When**: User input triggers expensive operations.

**Example: SearchableDropdown**:
```typescript
import { useDebouncedValue } from '@/hooks/useDebouncedValue'

const [filterText, setFilterText] = useState('')
const debouncedFilterText = useDebouncedValue(filterText, 150)

// Filter using debounced value (avoids re-filtering on every keystroke)
const filteredOptions = useMemo(() => {
  return options.filter(opt =>
    opt.label.toLowerCase().includes(debouncedFilterText.toLowerCase())
  )
}, [options, debouncedFilterText])
```

### Phase 4 Checklist

Before proceeding to Phase 5:
- [ ] Performance checklist reviewed
- [ ] React.memo applied to child components (if needed)
- [ ] useMemo applied to expensive computations
- [ ] useCallback applied to callbacks passed to memoized children
- [ ] Virtualization considered for large lists (>100 items)
- [ ] Debounce applied to high-frequency updates
- [ ] Bundle size checked (no unused imports)
- [ ] React DevTools Profiler checked (no excessive re-renders)

### Phase 4 Output Example

**Component: SearchableDropdown**

```markdown
## Performance Optimizations

**Applied Optimizations**:

1. **useMemo for filtered options**:
   - Rationale: Avoid re-filtering on every render
   - Implementation: `useMemo(() => filter(options, debouncedFilterText), [options, debouncedFilterText])`

2. **Debounce for filter text**:
   - Rationale: Avoid re-filtering on every keystroke
   - Implementation: `useDebouncedValue(filterText, 150)`

3. **React.memo for DropdownItem**:
   - Rationale: Prevent re-render when highlightedIndex changes
   - Implementation: `React.memo<DropdownItemProps>(DropdownItem)`

4. **useCallback for selectOption**:
   - Rationale: Stable reference for memoized DropdownItem
   - Implementation: `useCallback((value) => { onChange(value); setIsOpen(false) }, [onChange])`

**Not Applied**:
- Virtualization: Dropdown typically <100 options
- Code splitting: Component is small (<5KB)

**Profiler Results**:
- Initial render: 8ms
- Re-render (filter text change): 2ms
- Re-render (highlighted index change): <1ms (DropdownItem memoized)
```

---

## Phase 5: Testing Strategy

**Goal**: Define test plan before writing component code. Ensures testability from the start.

### Gate: Test Plan Documented

**Cannot proceed to Phase 6 until**:
- [ ] Test cases documented (unit, integration, accessibility)
- [ ] Testing strategy chosen (Jest, React Testing Library, Vitest)
- [ ] Edge cases covered (error, loading, empty)
- [ ] Accessibility tests included (keyboard, screen reader)
- [ ] Performance benchmarks defined (render time, re-render count)

### Process

**Load File**: `testing/react-testing-library.md`

#### Step 5.1: Document Unit Tests

**Format**: List all unit tests with expected behavior.

**Example: Data Table**:
```typescript
// Unit Tests
describe('DataTable', () => {
  test('renders all rows', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    expect(screen.getAllByRole('row')).toHaveLength(mockData.length + 1) // +1 for header
  })

  test('sorts column on header click', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    fireEvent.click(screen.getByText('Name'))
    const rows = screen.getAllByRole('row').slice(1) // Exclude header
    expect(rows[0]).toHaveTextContent('Alice') // First alphabetically
  })

  test('filters rows by search text', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    fireEvent.change(screen.getByPlaceholderText('Search...'), { target: { value: 'Bob' } })
    expect(screen.getAllByRole('row')).toHaveLength(2) // Header + 1 match
  })

  test('paginates data', () => {
    render(<DataTable data={largeDataset} columns={mockColumns} />)
    expect(screen.getAllByRole('row')).toHaveLength(51) // 50 rows + header
    fireEvent.click(screen.getByLabelText('Next page'))
    expect(screen.getAllByRole('row')).toHaveLength(51) // Next 50 rows
  })
})
```

**Example: SearchableDropdown**:
```typescript
// Unit Tests
describe('SearchableDropdown', () => {
  test('opens menu on click', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} />)
    fireEvent.click(screen.getByRole('combobox'))
    expect(screen.getByRole('listbox')).toBeInTheDocument()
  })

  test('filters options by search text', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} />)
    fireEvent.click(screen.getByRole('combobox'))
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'Canada' } })
    expect(screen.getAllByRole('option')).toHaveLength(1)
    expect(screen.getByText('Canada')).toBeInTheDocument()
  })

  test('selects option on click', () => {
    const onChange = jest.fn()
    render(<SearchableDropdown options={mockOptions} value={null} onChange={onChange} />)
    fireEvent.click(screen.getByRole('combobox'))
    fireEvent.click(screen.getByText('Canada'))
    expect(onChange).toHaveBeenCalledWith('ca')
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument() // Menu closed
  })
})
```

#### Step 5.2: Document Integration Tests

**Format**: Tests for interaction between components.

**Example: Data Table**:
```typescript
// Integration Tests
describe('DataTable Integration', () => {
  test('sort + filter interaction', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)

    // Sort by Name
    fireEvent.click(screen.getByText('Name'))

    // Filter
    fireEvent.change(screen.getByPlaceholderText('Search...'), { target: { value: 'Alice' } })

    // Verify: Only Alice shows, sorted correctly
    const rows = screen.getAllByRole('row').slice(1)
    expect(rows).toHaveLength(1)
    expect(rows[0]).toHaveTextContent('Alice')
  })

  test('pagination resets on filter', () => {
    render(<DataTable data={largeDataset} columns={mockColumns} />)

    // Go to page 2
    fireEvent.click(screen.getByLabelText('Next page'))
    expect(screen.getByText('Page 2 of 5')).toBeInTheDocument()

    // Apply filter
    fireEvent.change(screen.getByPlaceholderText('Search...'), { target: { value: 'Alice' } })

    // Verify: Back to page 1
    expect(screen.getByText('Page 1 of 1')).toBeInTheDocument()
  })
})
```

**Example: SearchableDropdown**:
```typescript
// Integration Tests
describe('SearchableDropdown Integration', () => {
  test('keyboard navigation + selection', () => {
    const onChange = jest.fn()
    render(<SearchableDropdown options={mockOptions} value={null} onChange={onChange} />)

    const combobox = screen.getByRole('combobox')

    // Open menu
    fireEvent.click(combobox)

    // Navigate with arrow keys
    fireEvent.keyDown(combobox, { key: 'ArrowDown' })
    fireEvent.keyDown(combobox, { key: 'ArrowDown' })

    // Select with Enter
    fireEvent.keyDown(combobox, { key: 'Enter' })

    expect(onChange).toHaveBeenCalledWith(mockOptions[1].value)
  })

  test('filter + keyboard navigation', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} />)

    // Open and filter
    fireEvent.click(screen.getByRole('combobox'))
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'United' } })

    // Verify: Only 2 options (United States, United Kingdom)
    expect(screen.getAllByRole('option')).toHaveLength(2)

    // Navigate
    fireEvent.keyDown(screen.getByRole('searchbox'), { key: 'ArrowDown' })

    // Verify: First option highlighted
    expect(screen.getAllByRole('option')[0]).toHaveClass('highlighted')
  })
})
```

#### Step 5.3: Document Edge Case Tests

**Format**: Tests for error, loading, empty states.

**Example: Data Table**:
```typescript
// Edge Case Tests
describe('DataTable Edge Cases', () => {
  test('empty data shows message', () => {
    render(<DataTable data={[]} columns={mockColumns} />)
    expect(screen.getByText('No data')).toBeInTheDocument()
  })

  test('no match shows message', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    fireEvent.change(screen.getByPlaceholderText('Search...'), { target: { value: 'xyz' } })
    expect(screen.getByText(/No results for 'xyz'/)).toBeInTheDocument()
  })

  test('loading shows skeleton', () => {
    render(<DataTable data={mockData} columns={mockColumns} isLoading />)
    expect(screen.getAllByTestId('skeleton-row')).toHaveLength(5) // 5 skeleton rows
  })

  test('error shows message with retry', () => {
    const onRetry = jest.fn()
    render(<DataTable data={[]} columns={mockColumns} error="Failed to load" onRetry={onRetry} />)
    expect(screen.getByText('Failed to load')).toBeInTheDocument()
    fireEvent.click(screen.getByText('Retry'))
    expect(onRetry).toHaveBeenCalled()
  })
})
```

**Example: SearchableDropdown**:
```typescript
// Edge Case Tests
describe('SearchableDropdown Edge Cases', () => {
  test('empty options shows message', () => {
    render(<SearchableDropdown options={[]} value={null} onChange={jest.fn()} />)
    fireEvent.click(screen.getByRole('combobox'))
    expect(screen.getByText('No options')).toBeInTheDocument()
  })

  test('no match shows message', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} />)
    fireEvent.click(screen.getByRole('combobox'))
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'xyz' } })
    expect(screen.getByText(/No results for 'xyz'/)).toBeInTheDocument()
  })

  test('disabled prevents interaction', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} disabled />)
    fireEvent.click(screen.getByRole('combobox'))
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument() // Menu doesn't open
  })

  test('loading shows spinner', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} isLoading />)
    fireEvent.click(screen.getByRole('combobox'))
    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })
})
```

#### Step 5.4: Document Accessibility Tests

**Format**: Tests for keyboard, screen reader, ARIA.

**Example: Data Table**:
```typescript
// Accessibility Tests
describe('DataTable Accessibility', () => {
  test('table has correct ARIA roles', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getAllByRole('row')).toHaveLength(mockData.length + 1)
    expect(screen.getAllByRole('columnheader')).toHaveLength(mockColumns.length)
  })

  test('sort button has aria-label', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    const sortButton = screen.getByLabelText('Sort by Name')
    expect(sortButton).toBeInTheDocument()
  })

  test('keyboard navigation works', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    const table = screen.getByRole('table')

    // Tab to table
    table.focus()

    // Arrow key navigation
    fireEvent.keyDown(table, { key: 'ArrowDown' })
    expect(screen.getAllByRole('row')[1]).toHaveFocus()
  })

  test('screen reader announces sort', () => {
    render(<DataTable data={mockData} columns={mockColumns} />)
    fireEvent.click(screen.getByText('Name'))
    expect(screen.getByRole('status')).toHaveTextContent('Sorted by Name ascending')
  })
})
```

**Example: SearchableDropdown**:
```typescript
// Accessibility Tests
describe('SearchableDropdown Accessibility', () => {
  test('combobox has correct ARIA attributes', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} />)
    const combobox = screen.getByRole('combobox')
    expect(combobox).toHaveAttribute('aria-haspopup', 'listbox')
    expect(combobox).toHaveAttribute('aria-expanded', 'false')
  })

  test('menu opens with aria-expanded=true', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} />)
    fireEvent.click(screen.getByRole('combobox'))
    expect(screen.getByRole('combobox')).toHaveAttribute('aria-expanded', 'true')
  })

  test('keyboard navigation works', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} />)
    const combobox = screen.getByRole('combobox')

    // Open with Enter
    fireEvent.keyDown(combobox, { key: 'Enter' })
    expect(screen.getByRole('listbox')).toBeInTheDocument()

    // Navigate with arrow keys
    fireEvent.keyDown(combobox, { key: 'ArrowDown' })
    expect(screen.getAllByRole('option')[0]).toHaveAttribute('aria-selected', 'true')

    // Close with Esc
    fireEvent.keyDown(combobox, { key: 'Escape' })
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  test('screen reader announces selection', () => {
    render(<SearchableDropdown options={mockOptions} value={null} onChange={jest.fn()} />)
    fireEvent.click(screen.getByRole('combobox'))
    fireEvent.click(screen.getByText('Canada'))
    expect(screen.getByRole('status')).toHaveTextContent('Canada selected')
  })
})
```

### Phase 5 Checklist

Before proceeding to Phase 6:
- [ ] Unit tests documented (renders, interactions)
- [ ] Integration tests documented (component interactions)
- [ ] Edge case tests documented (empty, error, loading)
- [ ] Accessibility tests documented (keyboard, ARIA, screen reader)
- [ ] Performance benchmarks defined (render time)
- [ ] Test coverage target defined (>80%)

---

## Phase 6: Accessibility Audit

**Goal**: Ensure component meets WCAG AA standards before deployment.

### Gate: Accessibility Checklist Passed

**Cannot proceed to deployment until**:
- [ ] Accessibility checklist from accessibility/audit-checklist.md reviewed
- [ ] Keyboard navigation tested (Tab, Arrow keys, Enter, Esc)
- [ ] Screen reader tested (VoiceOver on Mac, NVDA on Windows)
- [ ] Color contrast verified (4.5:1 for text, 3:1 for UI)
- [ ] Focus indicators visible (outline or custom)
- [ ] ARIA attributes correct (roles, labels, states)
- [ ] Touch targets sized (44x44px minimum)
- [ ] Automated tests run (axe-core or similar)

### Process

**Load File**: `accessibility/audit-checklist.md`

**Key Categories**:
1. Keyboard Navigation
2. Screen Reader Support
3. Visual Design
4. ARIA Attributes
5. Touch/Mobile
6. Automated Testing

**Example: Data Table**:
```markdown
## Accessibility Audit

### 1. Keyboard Navigation
- [x] Tab reaches table
- [x] Arrow keys navigate cells
- [x] Enter activates sort
- [x] Esc closes filter dropdown (if present)
- [x] Focus visible at all times

### 2. Screen Reader Support
- [x] Table role announced
- [x] Row/column count announced
- [x] Sort state announced ("Sorted by Name ascending")
- [x] Filter applied announced ("3 results for 'Alice'")
- [x] Page change announced ("Page 2 of 5")

### 3. Visual Design
- [x] Text contrast ≥ 4.5:1 (body text)
- [x] UI contrast ≥ 3:1 (buttons, borders)
- [x] Focus indicator visible (2px outline)
- [x] Color not sole indicator (sort uses icon + color)

### 4. ARIA Attributes
- [x] table role
- [x] columnheader role for headers
- [x] aria-sort on sorted column
- [x] aria-label for sort buttons
- [x] aria-live for announcements

### 5. Touch/Mobile
- [x] Touch targets ≥ 44x44px
- [x] No hover-only interactions
- [x] Works on touchscreen (no mouse-only events)

### 6. Automated Testing
- [x] axe-core: 0 violations
- [x] Lighthouse Accessibility: 100/100
```

**Example: SearchableDropdown**:
```markdown
## Accessibility Audit

### 1. Keyboard Navigation
- [x] Tab reaches combobox
- [x] Enter opens menu
- [x] Arrow keys navigate options
- [x] Enter selects option
- [x] Esc closes menu
- [x] Type to search (filter)
- [x] Focus visible at all times

### 2. Screen Reader Support
- [x] Combobox role announced
- [x] aria-expanded state announced
- [x] aria-haspopup="listbox" set
- [x] Selected option announced
- [x] Filter count announced ("3 options available")
- [x] No match announced ("No results for 'xyz'")

### 3. Visual Design
- [x] Text contrast ≥ 4.5:1
- [x] UI contrast ≥ 3:1
- [x] Focus indicator visible (2px outline)
- [x] Disabled state clear (grayed out)

### 4. ARIA Attributes
- [x] combobox role
- [x] aria-expanded (true/false)
- [x] aria-haspopup="listbox"
- [x] aria-controls (menu ID)
- [x] aria-activedescendant (highlighted option)
- [x] aria-label (if no visible label)
- [x] aria-live for announcements

### 5. Touch/Mobile
- [x] Touch targets ≥ 44x44px
- [x] Works on mobile (no hover-only)
- [x] Touch scrolling works in menu

### 6. Automated Testing
- [x] axe-core: 0 violations
- [x] Lighthouse Accessibility: 100/100
```

### Phase 6 Checklist

Before deployment:
- [ ] Keyboard navigation tested (all interactions)
- [ ] Screen reader tested (VoiceOver or NVDA)
- [ ] Color contrast verified (WCAG AA)
- [ ] Focus indicators visible
- [ ] ARIA attributes correct
- [ ] Touch targets sized (44x44px)
- [ ] Automated tests passed (axe-core)
- [ ] Lighthouse Accessibility ≥ 90/100

---

## Complete Workflow Example: SearchableDropdown

### Phase 1: Requirements ✓

```markdown
**Purpose**: Dropdown with search for large option lists (>20 items).
**Interactions**: Click to open, type to filter, arrow keys to navigate, Enter to select, Esc to close.
**Data**: options (array), value, onChange (props).
**Edge Cases**: Empty options, no match, disabled, loading.
**Success**: Filter in <50ms, keyboard works, screen reader support, WCAG AA.
```

### Phase 2: Patterns ✓

```markdown
**Type**: Simple Component
**Patterns**: useState (isOpen, filterText, highlightedIndex), useMemo (filtered options), ARIA combobox
**Files**: patterns/composition/simple-components.md, state/hooks/useState.md, performance/useMemo.md
**Structure**: components/SearchableDropdown/{index.tsx, DropdownMenu.tsx, DropdownItem.tsx}
```

### Phase 3: State ✓

```typescript
interface DropdownState {
  isOpen: boolean
  filterText: string
  highlightedIndex: number
}

// useState for all 3 fields
// useMemo for filteredOptions = filter(options, debouncedFilterText)
// selectOption calls onChange(value), closes menu
```

### Phase 4: Performance ✓

```markdown
**Optimizations**:
- useMemo for filteredOptions
- Debounce filterText (150ms)
- React.memo for DropdownItem
- useCallback for selectOption
```

### Phase 5: Testing ✓

```markdown
**Tests**:
- Opens menu on click
- Filters options by search text
- Selects option on click/Enter
- Closes menu on Esc/click outside
- Keyboard navigation works
- Screen reader announces selection
- Empty/no match states render
```

### Phase 6: Accessibility ✓

```markdown
**Checklist**:
- Keyboard navigation (Tab, Arrow, Enter, Esc)
- Screen reader (VoiceOver tested)
- ARIA attributes (combobox, aria-expanded, aria-activedescendant)
- Focus indicators visible
- Touch targets ≥ 44x44px
- axe-core: 0 violations
```

---

## Workflow Summary

**6-Phase Process**:
1. **Requirements** → Document purpose, interactions, data, edge cases, success criteria
2. **Patterns** → Choose component type, patterns, files to load, code structure
3. **State** → Define state shape, updates, data flow, strategy, edge case handling
4. **Performance** → Apply memo, useMemo, useCallback, virtualization, debounce
5. **Testing** → Document unit, integration, edge case, accessibility tests
6. **Accessibility** → Audit keyboard, screen reader, ARIA, contrast, touch targets

**Key Principle**: Each phase has explicit gates. Cannot proceed until current phase checklist passes.

**Result**: Production-ready component with clean architecture, performance optimization, comprehensive tests, and full accessibility support.

---

**End of Component Development Workflow**
