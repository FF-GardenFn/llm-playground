# Accessibility Audit Checklist

**GATE: Component cannot be marked complete without passing ALL checks.**

Accessibility is not optional. Phase 6 requires this checklist completion.

---

## Semantic HTML

- [ ] **Correct elements used**
  - Buttons use `<button>`, not `<div onClick>`
  - Links use `<a href>`, not `<span onClick>`
  - Inputs use appropriate types (email, tel, search)
  - Forms use `<form>` with proper submission

- [ ] **Heading hierarchy correct**
  - Single `<h1>` per page
  - No skipped levels (h1 → h2 → h3, not h1 → h3)
  - Headings describe content structure

- [ ] **Landmark regions present**
  - `<nav>` for navigation
  - `<main>` for main content (one per page)
  - `<aside>` for sidebars
  - `<footer>` for footer
  - `<header>` for header

**Why**: Screen readers use semantic HTML for navigation and understanding page structure.

---

## ARIA Labels & Roles

- [ ] **Interactive elements labeled**
  - Buttons have accessible names (text content or aria-label)
  - Icons have aria-label (e.g., aria-label="Close")
  - Form inputs have labels (label for="" or aria-label)

- [ ] **State communicated**
  - Toggles use aria-expanded (true/false)
  - Modals use aria-modal="true"
  - Hidden elements use aria-hidden="true"
  - Loading states use aria-live="polite" or aria-busy="true"

- [ ] **Relationships clear**
  - aria-labelledby connects labels to elements
  - aria-describedby provides additional context
  - aria-controls indicates controlled elements

**Examples**:
```jsx
// ✅ Good: Button with aria-label
<button aria-label="Close dialog">
  <XIcon />
</button>

// ✅ Good: Expanded state
<button aria-expanded={isOpen}>
  Menu
</button>

// ✅ Good: Live region for announcements
<div aria-live="polite" aria-atomic="true">
  {message}
</div>
```

**Why**: ARIA fills gaps where HTML semantics are insufficient.

---

## Keyboard Navigation

- [ ] **All interactive elements keyboard accessible**
  - Can reach all buttons with Tab
  - Can activate with Enter or Space
  - Can close modals with Escape
  - Custom components have tabindex (0 for focusable, -1 for programmatic focus)

- [ ] **Tab order logical**
  - Follows visual order (top-to-bottom, left-to-right)
  - No tab traps (can Tab out of all components)
  - Skip links provided for navigation (optional but recommended)

- [ ] **Focus management correct**
  - Modal opens → focus moves to first focusable element in modal
  - Modal closes → focus returns to trigger element
  - Route change → focus moves to main content or h1
  - Dropdown opens → focus moves to first option (optional)

**Examples**:
```jsx
// ✅ Good: Custom button with keyboard support
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }}
>
  Custom Button
</div>

// ✅ Good: Focus management in modal
useEffect(() => {
  if (isOpen) {
    const firstFocusable = modalRef.current.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')
    firstFocusable?.focus()
  } else {
    triggerRef.current?.focus()  // Return focus when closed
  }
}, [isOpen])
```

**Why**: Many users navigate via keyboard only (no mouse).

---

## Focus Visibility

- [ ] **Focus indicators visible**
  - Outline or focus ring visible on focus
  - Sufficient contrast (3:1 against background)
  - Not removed with outline: none (use :focus-visible instead)

**Examples**:
```css
/* ✅ Good: Visible focus indicator */
button:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}

/* ❌ Bad: Removing focus indicator */
button:focus {
  outline: none;  /* NEVER DO THIS without replacement */
}
```

**Why**: Keyboard users need to see where focus is.

---

## Color Contrast

- [ ] **Text contrast sufficient**
  - Normal text (< 18px): 4.5:1 contrast ratio
  - Large text (≥ 18px): 3:1 contrast ratio
  - UI components: 3:1 contrast ratio

- [ ] **Color not sole indicator**
  - Errors shown with icons + text, not just red color
  - Links distinguishable without color (underline, icon, etc.)
  - Charts have patterns or labels, not just colors

**Tool**: WebAIM Contrast Checker, browser DevTools

**Examples**:
```jsx
// ✅ Good: Error with icon + text + color
<div className="error">
  <AlertIcon />
  <span>Email is required</span>
</div>

// ❌ Bad: Error with only color
<span style={{ color: 'red' }}>Email is required</span>
```

**Why**: Users with low vision or color blindness need sufficient contrast.

---

## Form Labels

- [ ] **All inputs have labels**
  - `<label for="input-id">` with matching id
  - Or aria-label / aria-labelledby
  - Placeholder text is NOT a label

- [ ] **Error messages associated**
  - aria-describedby links input to error message
  - aria-invalid="true" when input invalid
  - Error message visible and announced

**Examples**:
```jsx
// ✅ Good: Proper label
<label htmlFor="email">Email Address</label>
<input
  id="email"
  type="email"
  aria-describedby={error ? "email-error" : undefined}
  aria-invalid={!!error}
/>
{error && <span id="email-error">{error}</span>}

// ❌ Bad: Placeholder as label
<input type="email" placeholder="Email Address" />
```

**Why**: Screen readers need explicit label associations.

---

## Screen Reader Testing

- [ ] **Tested with screen reader**
  - Windows: NVDA (free) or JAWS
  - Mac: VoiceOver (built-in)
  - Test: Navigate with screen reader, verify all content announced

- [ ] **Announcements correct**
  - Loading states announced (aria-live)
  - Form errors announced
  - Dynamic content changes announced
  - Modal open/close announced

**How to test**:
```
Mac (VoiceOver):
  Cmd+F5: Enable VoiceOver
  Ctrl+Option+Arrow: Navigate
  Ctrl+Option+Space: Click

Windows (NVDA):
  Install NVDA (free)
  Ctrl: Stop speech
  Arrow keys: Navigate
  Enter/Space: Click
```

**Why**: Only way to truly verify screen reader experience.

---

## Image Alt Text

- [ ] **All images have alt text**
  - Informative images: Descriptive alt text
  - Decorative images: Empty alt="" (not missing)
  - Icons with meaning: aria-label or alt text

**Examples**:
```jsx
// ✅ Good: Descriptive alt text
<img src="chart.png" alt="Sales increased 50% in Q2" />

// ✅ Good: Decorative image (empty alt)
<img src="background-pattern.png" alt="" />

// ✅ Good: Icon with label
<button>
  <TrashIcon aria-label="Delete item" />
</button>
```

**Why**: Screen readers need text alternative for images.

---

## Responsive & Zoom

- [ ] **Works with zoom**
  - Page usable at 200% zoom
  - No horizontal scrolling at 200%
  - Text doesn't overflow or get cut off

- [ ] **Touch targets sufficient**
  - Minimum 44x44 pixels (WCAG 2.1 AA)
  - Adequate spacing between touch targets

**Why**: Users with low vision zoom in significantly.

---

## Gate Status

**Phase 6 Complete**: Only when ALL checkboxes above are checked.

**If any unchecked**:
- Accessibility audit incomplete
- Component not ready for production
- Must address issues before proceeding

---

## Automated Testing

**Tools to use**:
```bash
# Jest + jest-axe
npm install --save-dev jest-axe
import { axe, toHaveNoViolations } from 'jest-axe'
expect.extend(toHaveNoViolations)

test('has no accessibility violations', async () => {
  const { container } = render(<MyComponent />)
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})

# Lighthouse CI
npm install -g @lhci/cli
lhci autorun
```

**Browser Extensions**:
- axe DevTools (Chrome, Firefox)
- WAVE (Chrome, Firefox)
- Lighthouse (Chrome DevTools)

**Why**: Catch common issues automatically, but doesn't replace manual testing.

---

## Common Mistakes

### ❌ Mistake 1: Div instead of Button

```jsx
// Bad
<div onClick={handleClick}>Click me</div>

// Good
<button onClick={handleClick}>Click me</button>
```

**Problem**: Div not keyboard accessible, no semantic meaning

### ❌ Mistake 2: Placeholder as Label

```jsx
// Bad
<input type="email" placeholder="Email Address" />

// Good
<label htmlFor="email">Email Address</label>
<input id="email" type="email" />
```

**Problem**: Placeholder disappears when typing, not announced as label

### ❌ Mistake 3: Removing Focus Outline

```css
/* Bad */
* { outline: none; }

/* Good */
button:focus-visible {
  outline: 2px solid #0066cc;
}
```

**Problem**: Keyboard users can't see focus

### ❌ Mistake 4: Color Only for Meaning

```jsx
// Bad: Error shown with color only
<span style={{ color: 'red' }}>Error</span>

// Good: Error with icon + text + color
<div className="error">
  <AlertIcon aria-label="Error" />
  <span>Error: Email is required</span>
</div>
```

**Problem**: Color blind users miss the meaning

---

## Resources

**WCAG 2.1 Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
**MDN Accessibility**: https://developer.mozilla.org/en-US/docs/Web/Accessibility
**WebAIM**: https://webaim.org/
**A11y Project**: https://www.a11yproject.com/

---

## Summary

**Accessibility checklist enforces**:
- Semantic HTML
- ARIA labels and roles
- Keyboard navigation
- Focus management
- Color contrast
- Form labels
- Screen reader compatibility

**Cannot complete Phase 6 without passing checklist.**

**This is not optional. This is a gate.**
