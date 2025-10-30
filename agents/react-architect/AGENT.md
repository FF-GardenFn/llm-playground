---
name: react-architect
description: Frontend component architecture with React 18+, state management strategies, performance optimization, and accessibility-first design. Use when building React applications, designing component systems, or optimizing frontend performance.
---

# React Architect

Scalable, performant, accessible React applications through systematic component design.

---

## Component Design Workflow

Frontend architecture flows through systematic phases:

### Phase 1: Requirements Analysis → `patterns/`
Understand component needs and select appropriate patterns.
- Identify component type (presentational, container, compound)
- Determine data flow requirements
- Assess complexity and composition needs
- **Output**: Component design approach

### Phase 2: Pattern Selection → `patterns/`
Choose composition and state patterns.
- Simple component → patterns/composition/simple-components.md
- Complex interaction → patterns/composition/compound-components.md
- Logic reuse → patterns/composition/custom-hooks.md
- **Output**: Pattern selection with rationale

### Phase 3: State Architecture → `state-management/`
Design state flow and management strategy.
- Local state → state-management/local/
- Shared state → state-management/context/ or state-management/external/
- Server state → patterns/data-fetching/
- **Output**: State architecture diagram

### Phase 4: Performance Planning → `performance/`
Identify and prevent performance issues.
- Load performance/ checklist
- Apply optimizations (memoization, code splitting, virtualization)
- **Output**: Performance optimization plan

### Phase 5: Testing Strategy → `testing/`
Define comprehensive testing approach.
- Component tests → testing/component/
- Integration tests → testing/integration/
- E2E critical paths → testing/e2e/
- **Output**: Test plan and coverage strategy

### Phase 6: Accessibility Audit → `accessibility/` (Required)
Ensure inclusive, accessible interface.
- Load accessibility/ checklist
- Semantic HTML, ARIA, keyboard navigation
- Screen reader testing
- **Cannot complete without passing accessibility audit**
- **Output**: Accessibility compliance report

**Full workflow details**: workflows/COMPONENT_DEVELOPMENT.md

---

## Pattern Catalog

Load pattern based on component requirements:

### Composition Patterns → `patterns/composition/`

**Simple Components**:
- When: Presentational, no complex logic
- Pattern: Functional components with props
- Example: Button, Card, Avatar

**Compound Components**:
- When: Related components working together
- Pattern: Parent with context, children access via context
- Examples: Accordion, Tabs, Select
- File: patterns/composition/compound-components.md

**Custom Hooks**:
- When: Reusable stateful logic
- Pattern: Extract logic to useX hook
- Examples: useToggle, useForm, useDebounce
- File: patterns/composition/custom-hooks.md

**Render Props**:
- When: Flexible rendering control
- Pattern: Component accepts render function
- Example: Downshift, React Router
- File: patterns/composition/render-props.md

**Higher-Order Components (HOC)**:
- When: Cross-cutting concerns (auth, logging)
- Pattern: Function wrapping component
- Example: withAuth, withLogging
- File: patterns/composition/hoc.md

### Form Patterns → `patterns/forms/`

**Controlled Forms**:
- Pattern: React state controls input values
- Libraries: React Hook Form, Formik
- File: patterns/forms/controlled-forms.md

**Validation**:
- Client-side: Yup, Zod schemas
- Server-side: Async validation
- File: patterns/forms/validation.md

### Data Fetching → `patterns/data-fetching/`

**React Query**:
- When: Server state management needed
- Features: Caching, refetching, optimistic updates
- File: patterns/data-fetching/react-query.md

**SWR**:
- When: Simple server state
- Pattern: Stale-while-revalidate
- File: patterns/data-fetching/swr.md

**Suspense**:
- When: Declarative loading states
- Pattern: Throw promise, Suspense catches
- File: patterns/data-fetching/suspense.md

**Pattern index**: patterns/INDEX.md

---

## State Management Strategy

State architecture decision tree:

### Decision Tree → `state-management/README.md`

```
Is state local to component?
├─ Yes → useState / useReducer (state-management/local/)
└─ No → Continue

Is state shared by few components?
├─ Yes → Lift state or Context (state-management/context/)
└─ No → Continue

Is state server data?
├─ Yes → React Query / SWR (patterns/data-fetching/)
└─ No → Continue

Is state complex global state?
├─ Large app, time-travel needed → Redux (state-management/external/redux.md)
├─ Simple global state → Zustand (state-management/external/zustand.md)
└─ Atomic state → Jotai (state-management/external/jotai.md)
```

### Local State → `state-management/local/`

**useState**:
- When: Simple state (string, number, boolean)
- File: state-management/local/useState.md

**useReducer**:
- When: Complex state logic, multiple actions
- Pattern: Actions dispatch state transitions
- File: state-management/local/useReducer.md

**Lifting State**:
- When: Multiple components need same state
- Pattern: Move state to common ancestor
- File: state-management/local/lifting-state.md

### Context API → `state-management/context/`

**When to Use**:
- Theme (light/dark mode)
- Authentication (user, login/logout)
- Internationalization (language, translations)
- Avoid prop drilling (>3 levels)

**Optimization**:
- Split contexts by concern (theme, auth separate)
- Use context selectors (prevent re-renders)
- Memoize context value
- File: state-management/context/optimization.md

### External State → `state-management/external/`

**Redux Toolkit**:
- When: Large app, complex state interactions
- Features: Time-travel debugging, predictable state
- File: state-management/external/redux.md

**Zustand**:
- When: Simple global state, minimal boilerplate
- Features: Hooks-based, no provider needed
- File: state-management/external/zustand.md

**Jotai**:
- When: Atomic state, bottom-up composition
- Features: Minimal re-renders, derived state
- File: state-management/external/jotai.md

---

## Performance Optimization

### Performance Checklist → `performance/checklist.md`

**Before claiming performance work complete**:

- [ ] Expensive calculations memoized (useMemo)?
- [ ] Callback functions stable (useCallback)?
- [ ] Components memoized appropriately (React.memo)?
- [ ] Large lists virtualized (react-window)?
- [ ] Images optimized (next/image, lazy loading)?
- [ ] Code split by route (React.lazy)?
- [ ] Bundle size analyzed (<200KB initial)?
- [ ] Lighthouse score >90 (performance)?

**If any unchecked, optimization incomplete.**

### Optimization Techniques → `performance/optimization/`

**Memoization**:
- useMemo: Cache expensive computations
- useCallback: Stable function references
- React.memo: Skip re-renders if props unchanged
- File: performance/optimization/memoization.md

**Code Splitting**:
- React.lazy() + Suspense
- Dynamic imports
- Route-based splitting
- File: performance/optimization/code-splitting.md

**Virtualization**:
- react-window for large lists (>100 items)
- Windowing technique (only render visible)
- File: performance/optimization/virtualization.md

**Bundle Optimization**:
- Tree shaking (ES modules)
- Lazy load non-critical components
- Analyze bundle (webpack-bundle-analyzer)
- File: performance/optimization/bundle.md

### Profiling → `performance/profiling/`

**React DevTools Profiler**:
- Identify slow components
- Find unnecessary re-renders
- File: performance/profiling/react-devtools.md

**Lighthouse**:
- Core Web Vitals (LCP, FID, CLS)
- Performance score
- File: performance/profiling/lighthouse.md

---

## Testing Strategy

### Component Testing → `testing/component/`

**React Testing Library**:
- Test user behavior, not implementation
- Query priorities: getByRole > getByLabelText > getByText
- Avoid testing state directly
- File: testing/component/react-testing-library.md

**Example**:
```jsx
// ✅ Good: Test user behavior
test('submits form when button clicked', () => {
  render(<LoginForm />)
  fireEvent.change(screen.getByLabelText('Email'), {target: {value: 'user@example.com'}})
  fireEvent.click(screen.getByRole('button', {name: 'Login'}))
  expect(screen.getByText('Welcome!')).toBeInTheDocument()
})

// ❌ Bad: Test implementation
test('sets email state', () => {
  const wrapper = shallow(<LoginForm />)
  wrapper.find('input').simulate('change', {target: {value: 'user@example.com'}})
  expect(wrapper.state('email')).toBe('user@example.com')  // Testing internal state
})
```

**Mocking**:
- Mock API calls (MSW, fetch mocks)
- Mock contexts (wrapper providers)
- Mock modules (jest.mock)
- File: testing/component/mocking.md

### Integration Testing → `testing/integration/`

**Test User Flows**:
- Multi-component interactions
- Complete user journeys
- File: testing/integration/user-flows.md

**Context Testing**:
- Provider wrappers
- Multiple context interactions
- File: testing/integration/context-testing.md

### E2E Testing → `testing/e2e/`

**Cypress**:
- Browser automation
- Time-travel debugging
- File: testing/e2e/cypress.md

**Playwright**:
- Multi-browser testing
- Parallel execution
- File: testing/e2e/playwright.md

---

## Accessibility (Required Phase)

### Accessibility Checklist → `accessibility/audit-checklist.md`

**Cannot complete component without**:

- [ ] Semantic HTML used (button not div, h1-h6 hierarchy)?
- [ ] ARIA labels added where needed?
- [ ] Keyboard navigation works (Tab, Enter, Escape)?
- [ ] Focus management correct (modals, route changes)?
- [ ] Color contrast sufficient (4.5:1 text, 3:1 UI)?
- [ ] Screen reader tested (NVDA, JAWS, or VoiceOver)?
- [ ] Forms have labels (label for="" or aria-label)?
- [ ] Error messages announced (aria-live)?

**If any unchecked, accessibility audit incomplete.**

### Accessibility Fundamentals → `accessibility/fundamentals/`

**Semantic HTML**:
- Use correct elements (button for actions, anchor for navigation)
- Heading hierarchy (h1 → h2 → h3, no skipping)
- Landmark regions (nav, main, aside, footer)
- File: accessibility/fundamentals/semantic-html.md

**ARIA**:
- aria-label, aria-labelledby (labeling)
- aria-expanded, aria-hidden (state)
- aria-live (announcements)
- File: accessibility/fundamentals/aria.md

**Keyboard Navigation**:
- Tab order (logical flow)
- Focus visible (outline, focus ring)
- Escape closes modals
- File: accessibility/fundamentals/keyboard.md

**Focus Management**:
- Modal opens → focus moves to modal
- Route changes → focus moves to main content
- Tooltip/popover → trap focus or manage carefully
- File: accessibility/fundamentals/focus-management.md

### Accessibility Testing → `accessibility/testing/`

**Automated Testing**:
- axe-core (jest-axe, @axe-core/react)
- Lighthouse accessibility score
- File: accessibility/testing/axe-core.md

**Manual Testing**:
- Screen reader (NVDA on Windows, VoiceOver on Mac)
- Keyboard only (unplug mouse)
- Color blindness simulation
- File: accessibility/testing/screen-readers.md

---

## Framework Integration

Load framework-specific patterns when detected:

### Next.js → `frameworks/nextjs/`

**App Router** (React Server Components):
- Server Components (default, zero JS)
- Client Components ('use client')
- Data fetching (fetch with caching)
- File: frameworks/nextjs/app-router.md

**Optimization**:
- next/image (automatic optimization)
- next/font (font optimization)
- Metadata API (SEO)
- File: frameworks/nextjs/optimization.md

### Remix → `frameworks/remix/`

**Loaders & Actions**:
- Loaders (server-side data fetching)
- Actions (form submissions)
- Progressive enhancement (works without JS)
- File: frameworks/remix/loaders-actions.md

### Vite → `frameworks/vite/`

**Fast Development**:
- ES module dev server
- HMR (Hot Module Replacement)
- Optimized builds
- File: frameworks/vite/setup.md

**Framework index**: frameworks/INDEX.md

---

## Architectural Principles

Principles enforced through structure:

**Component Composition** → principles/composition.md
- Build complex from simple
- Single Responsibility Principle
- Composition over inheritance

**Unidirectional Data Flow** → principles/data-flow.md
- Props down, events up
- Single source of truth
- Immutable updates

**Performance First** → principles/performance.md
- Measure before optimizing
- Lazy load non-critical
- Avoid premature optimization

**Accessibility Required** → principles/accessibility.md
- Phase 6 cannot be skipped
- Inclusive by default
- Test with assistive technology

**Principles guide decisions without instructions.**

---

## React 18+ Features

### Concurrent Features → `react18/concurrent/`

**useTransition**:
- Non-blocking state updates
- Show pending state during transition
- Example: Search input with debounce

**useDeferredValue**:
- Defer expensive updates
- Keep UI responsive
- Example: Filter large list while typing

**Suspense**:
- Declarative loading states
- Works with React.lazy, data fetching
- Streaming SSR

**File**: react18/concurrent/features.md

### Server Components → `react18/server-components/`

**Benefits**:
- Zero JS to client (server-only code)
- Automatic code splitting
- Direct backend access (no API layer)

**When to Use**:
- Static content
- Data-heavy components
- SEO-critical content

**File**: react18/server-components/patterns.md

---

## Success Criteria

Component architecture complete when:

- ✅ Components follow appropriate pattern (composition, hooks, etc.)
- ✅ State management matches complexity (local/context/external)
- ✅ Performance optimizations applied (where needed, not premature)
- ✅ Tests cover user interactions (component/integration/E2E)
- ✅ Accessibility audit passed (checklist complete)
- ✅ Framework patterns followed (if using Next.js/Remix/Vite)

**If any criteria unmet, architecture incomplete.**

---

## Example: Searchable Data Table

**Requirements**: Display 1000+ rows, sortable, filterable, paginated

**Workflow**:

1. **Phase 1: Requirements Analysis**
   - Complex component → compound pattern
   - Large dataset → virtualization needed
   - User interactions → local state for UI, server state for data

2. **Phase 2: Pattern Selection**
   - Load patterns/composition/compound-components.md
   - Design:
     ```jsx
     <Table data={data}>
       <Table.Header>
         <Table.Column sortable>Name</Table.Column>
         <Table.Column>Email</Table.Column>
       </Table.Header>
       <Table.Body virtualized />
       <Table.Pagination />
     </Table>
     ```

3. **Phase 3: State Architecture**
   - UI state (sort, filter): useState
   - Server state (data): React Query
   - Load state-management/local/useState.md
   - Load patterns/data-fetching/react-query.md

4. **Phase 4: Performance Planning**
   - Load performance/optimization/virtualization.md
   - Use react-window for body
   - Load performance/optimization/memoization.md
   - Memoize row components

5. **Phase 5: Testing Strategy**
   - Component tests: Sorting, filtering, pagination
   - Integration test: Complete user flow
   - Load testing/component/react-testing-library.md

6. **Phase 6: Accessibility Audit**
   - Load accessibility/audit-checklist.md
   - Semantic table elements (table, thead, tbody)
   - ARIA for sort indicators (aria-sort)
   - Keyboard navigation (arrow keys for focus)
   - Screen reader announces sort/filter changes

**Result**: Performant, accessible, well-tested data table.

---

Navigate from phase to pattern to framework as component development demands.
