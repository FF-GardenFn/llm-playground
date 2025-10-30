# Long Method Smell

**Category**: Method-Level Smell
**Severity**: Medium-High
**Frequency**: Very Common

The most common code smell. Long methods are hard to understand, test, and reuse.

---

## Symptoms

**Indicators of Long Method**:
- Method >20 lines (guideline, not rule)
- Method does multiple things
- Hard to name method clearly
- Method has many local variables
- Method has multiple levels of abstraction
- Scrolling required to see entire method
- Comments explaining "sections" of code

**Example**:
```python
# ❌ Long Method (60+ lines)
def process_order(self, order_data):
    # Validate order
    if not order_data.get('customer_id'):
        raise ValueError("Customer ID required")
    if not order_data.get('items'):
        raise ValueError("Order must have items")
    for item in order_data['items']:
        if item['quantity'] <= 0:
            raise ValueError(f"Invalid quantity for {item['product_id']}")
        if item['price'] < 0:
            raise ValueError(f"Invalid price for {item['product_id']}")

    # Calculate totals
    subtotal = 0
    for item in order_data['items']:
        subtotal += item['quantity'] * item['price']

    tax_rate = 0.08
    if order_data.get('state') == 'CA':
        tax_rate = 0.0725
    elif order_data.get('state') == 'NY':
        tax_rate = 0.08875

    tax = subtotal * tax_rate

    shipping = 0
    if subtotal < 50:
        shipping = 5.99
    elif subtotal < 100:
        shipping = 3.99

    total = subtotal + tax + shipping

    # Check inventory
    for item in order_data['items']:
        product = Product.query.get(item['product_id'])
        if product.stock < item['quantity']:
            raise ValueError(f"Insufficient stock for {product.name}")

    # Reserve inventory
    for item in order_data['items']:
        product = Product.query.get(item['product_id'])
        product.stock -= item['quantity']
        db.session.add(product)

    # Create order
    order = Order(
        customer_id=order_data['customer_id'],
        subtotal=subtotal,
        tax=tax,
        shipping=shipping,
        total=total
    )
    db.session.add(order)

    # Create order items
    for item in order_data['items']:
        order_item = OrderItem(
            order=order,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)

    # Send confirmation email
    customer = Customer.query.get(order_data['customer_id'])
    send_email(
        to=customer.email,
        subject=f"Order #{order.id} Confirmation",
        body=f"Thank you for your order of ${total:.2f}"
    )

    db.session.commit()
    return order
```

**Problems**:
- 60+ lines doing 6 different things
- Hard to understand entire flow
- Can't reuse validation, calculation, or email logic
- Hard to test individual pieces
- One change might break multiple parts

---

## Why It's a Problem

**Cognitive Load**:
- Developers must understand entire method
- Multiple levels of abstraction (validation, calculation, database, email)
- Context switching between concerns

**Maintenance Burden**:
- Hard to modify (fear of breaking something)
- Hard to debug (where's the bug?)
- Hard to test (many code paths)

**Reusability**:
- Can't reuse parts (all or nothing)
- Duplicate logic likely elsewhere

---

## Detection

**Automated** (linters, static analysis):
```python
# Pylint, Flake8, etc. can detect long methods
# Configure max-method-length = 20
```

**Manual** (code review):
- Scroll test: Can't see entire method without scrolling
- Comment test: Comments explain sections (each section should be method)
- Responsibility test: Method does >1 thing (violates Single Responsibility)

---

## Refactoring Solutions

### Primary: Extract Method

**Most common solution**: Break long method into smaller methods.

**Pattern**: Extract Method (refactorings/composing-methods/extract-method.md)

**Steps**:
1. Identify logical sections (often indicated by comments)
2. Extract each section into well-named method
3. Replace section with method call
4. Run tests

**Example**:
```python
# ✅ Refactored: Each step is clear method
def process_order(self, order_data):
    self._validate_order(order_data)

    totals = self._calculate_totals(order_data)

    self._check_inventory(order_data['items'])
    self._reserve_inventory(order_data['items'])

    order = self._create_order(order_data, totals)
    self._create_order_items(order, order_data['items'])

    self._send_confirmation_email(order)

    db.session.commit()
    return order

def _validate_order(self, order_data):
    if not order_data.get('customer_id'):
        raise ValueError("Customer ID required")
    if not order_data.get('items'):
        raise ValueError("Order must have items")

    for item in order_data['items']:
        self._validate_order_item(item)

def _validate_order_item(self, item):
    if item['quantity'] <= 0:
        raise ValueError(f"Invalid quantity for {item['product_id']}")
    if item['price'] < 0:
        raise ValueError(f"Invalid price for {item['product_id']}")

def _calculate_totals(self, order_data):
    subtotal = self._calculate_subtotal(order_data['items'])
    tax = self._calculate_tax(subtotal, order_data.get('state'))
    shipping = self._calculate_shipping(subtotal)
    total = subtotal + tax + shipping

    return {
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total
    }

def _calculate_subtotal(self, items):
    return sum(item['quantity'] * item['price'] for item in items)

def _calculate_tax(self, subtotal, state):
    tax_rates = {
        'CA': 0.0725,
        'NY': 0.08875
    }
    tax_rate = tax_rates.get(state, 0.08)
    return subtotal * tax_rate

def _calculate_shipping(self, subtotal):
    if subtotal < 50:
        return 5.99
    elif subtotal < 100:
        return 3.99
    else:
        return 0

def _check_inventory(self, items):
    for item in items:
        product = Product.query.get(item['product_id'])
        if product.stock < item['quantity']:
            raise ValueError(f"Insufficient stock for {product.name}")

def _reserve_inventory(self, items):
    for item in items:
        product = Product.query.get(item['product_id'])
        product.stock -= item['quantity']
        db.session.add(product)

def _create_order(self, order_data, totals):
    order = Order(
        customer_id=order_data['customer_id'],
        **totals
    )
    db.session.add(order)
    return order

def _create_order_items(self, order, items):
    for item in items:
        order_item = OrderItem(
            order=order,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)

def _send_confirmation_email(self, order):
    customer = Customer.query.get(order.customer_id)
    send_email(
        to=customer.email,
        subject=f"Order #{order.id} Confirmation",
        body=f"Thank you for your order of ${order.total:.2f}"
    )
```

**Benefits**:
- Each method has one clear responsibility
- Can test each piece independently
- Can reuse methods (e.g., _calculate_tax elsewhere)
- Main method reads like documentation
- Easy to modify (change validation without touching calculation)

---

### Alternative: Replace Temp with Query

**When**: Long method with many temporary variables

**Pattern**: Replace Temp with Query (refactorings/composing-methods/replace-temp-with-query.md)

**Example**:
```python
# Before: Temp variables clutter method
def calculate_total(self, order):
    base_price = order.quantity * order.item_price
    discount_factor = 0.1 if order.quantity > 100 else 0
    discount = base_price * discount_factor
    shipping = min(base_price * 0.1, 100)
    return base_price - discount + shipping

# After: Temps replaced with query methods
def calculate_total(self, order):
    return self.base_price(order) - self.discount(order) + self.shipping(order)

def base_price(self, order):
    return order.quantity * order.item_price

def discount(self, order):
    return self.base_price(order) * self.discount_factor(order)

def discount_factor(self, order):
    return 0.1 if order.quantity > 100 else 0

def shipping(self, order):
    return min(self.base_price(order) * 0.1, 100)
```

**Benefits**:
- No temp variables (simpler)
- Each calculation reusable
- Can override in subclass

---

### Alternative: Decompose Conditional

**When**: Long method with complex conditionals

**Pattern**: Decompose Conditional (refactorings/simplifying-conditionals/decompose-conditional.md)

**Example**:
```python
# Before: Long conditional
def calculate_charge(self, date, quantity):
    if date.month == 12 or date.month == 1 or date.month == 2:
        charge = quantity * self.winter_rate + self.winter_service_charge
    else:
        charge = quantity * self.summer_rate

# After: Decompose conditional
def calculate_charge(self, date, quantity):
    if self.is_winter(date):
        charge = self.winter_charge(quantity)
    else:
        charge = self.summer_charge(quantity)

def is_winter(self, date):
    return date.month in [12, 1, 2]

def winter_charge(self, quantity):
    return quantity * self.winter_rate + self.winter_service_charge

def summer_charge(self, quantity):
    return quantity * self.summer_rate
```

---

## Incremental Refactoring

**For very long methods** (>100 lines):

1. **Don't refactor all at once** (too risky)
2. **Extract one section at a time**:
   - Extract first logical section
   - Run tests (must be green)
   - Commit
   - Extract next section
   - Repeat
3. **Keep tests green** throughout

**Example progression**:
```python
# Step 1: Extract validation
def process_order(self, order_data):
    self._validate_order(order_data)  # Extracted

    # ... rest of original code ...

# Step 2: Extract calculation
def process_order(self, order_data):
    self._validate_order(order_data)
    totals = self._calculate_totals(order_data)  # Extracted

    # ... rest of original code ...

# Step 3: Continue extracting...
```

**Key**: Small steps, tests always green.

---

## When NOT to Refactor

**Don't extract methods when**:
1. **Code is clear as-is**: Short, well-named, obvious
2. **Extraction makes code worse**: Creating tiny methods for no benefit
3. **No tests exist**: Write tests first

**Example of over-extraction**:
```python
# ❌ Over-extracted: Hurts readability
def calculate_total(self, items):
    return self.add(self.sum_items(items), self.tax(items))

def add(self, a, b):
    return a + b

def sum_items(self, items):
    return sum(item.price for item in items)

def tax(self, items):
    return self.sum_items(items) * 0.08

# ✅ Better: Balance extraction with clarity
def calculate_total(self, items):
    subtotal = sum(item.price for item in items)
    tax = subtotal * 0.08
    return subtotal + tax
```

---

## Testing Strategy

**Before refactoring**:
- Ensure characterization tests exist (capture current behavior)
- Tests must be green

**During refactoring**:
- Extract one method
- Run tests (must stay green)
- Commit
- Repeat

**After refactoring**:
- All tests green
- Add tests for new extracted methods (if public)

---

## Metrics

**Before refactoring**:
- Method length (lines)
- Cyclomatic complexity
- Number of local variables
- Number of parameters

**After refactoring**:
- Method length reduced (aim for <20 lines)
- Cyclomatic complexity reduced
- Fewer local variables (extracted to methods)
- Clearer single responsibility

---

## Related Smells

**Often appears with**:
- Long Parameter List (long methods need many params)
- Duplicate Code (long methods copied elsewhere)
- Large Class (many long methods → large class)

**Cascading improvements**: Fixing Long Method often reveals other smells to fix.

---

## Summary

**Long Method smell**:
- Method >20 lines, doing multiple things
- Hard to understand, test, reuse
- Most common code smell

**Primary refactoring**: Extract Method
- Break into smaller, focused methods
- Each method one responsibility
- Main method reads like documentation

**Incremental approach**:
- Extract one section at a time
- Keep tests green
- Commit frequently

**Long methods → Extract methods → Smaller, clearer, testable code.**
