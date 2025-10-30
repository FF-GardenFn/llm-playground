# Extract Method Refactoring

**Category**: Composing Methods
**Difficulty**: Easy
**Risk**: Low (if well-tested)

The most fundamental and most frequently used refactoring. Extract Method is the Swiss Army knife of refactoring.

---

## Intent

**Pull code fragment into its own method** with a name explaining the purpose of the method.

Turn code fragment into method whose name explains what it does, not how it does it.

---

## Motivation

**When to use**:
- Method too long (>20 lines)
- Code needs comment to explain what it does
- Logic appears in multiple places (DRY violation)
- Method does multiple things (SRP violation)
- Code has distinct sections

**Benefits**:
- Shorter methods (easier to understand)
- Reusable code (call from multiple places)
- Better names (explains intent)
- Easier testing (test extracted method separately)
- Overridable (can override in subclass)

---

## Mechanics

**Steps**:
1. **Create new method** with descriptive name
2. **Copy extracted code** to new method
3. **Scan for local variables** used in extracted code
   - Variables used only in fragment → local variables of new method
   - Variables used before and after → parameters to new method
   - Variables modified → return value from new method
4. **Replace extracted code** with call to new method
5. **Compile and test** (tests must stay green)

**Always**: Run tests after extraction. If tests fail, revert and try again.

---

## Simple Example

### Before

```python
def print_owing(self):
    outstanding = 0.0

    print("*" * 25)
    print("Customer Owes")
    print("*" * 25)

    # Calculate outstanding
    for order in self.orders:
        outstanding += order.amount

    # Print details
    print(f"Name: {self.name}")
    print(f"Amount: ${outstanding:.2f}")
```

**Problems**:
- Method does three things: print banner, calculate outstanding, print details
- Can't reuse calculation or printing logic
- Hard to test calculation separately

### After

```python
def print_owing(self):
    self.print_banner()
    outstanding = self.calculate_outstanding()
    self.print_details(outstanding)

def print_banner(self):
    print("*" * 25)
    print("Customer Owes")
    print("*" * 25)

def calculate_outstanding(self):
    return sum(order.amount for order in self.orders)

def print_details(self, outstanding):
    print(f"Name: {self.name}")
    print(f"Amount: ${outstanding:.2f}")
```

**Benefits**:
- Each method has one clear responsibility
- Can test `calculate_outstanding` independently
- Can reuse banner/calculation/details printing
- Main method reads like documentation

---

## No Local Variables

**Easiest case**: Extracted code uses no local variables.

```python
# Before
def print_invoice(self):
    print("*" * 25)
    print("Invoice")
    print("*" * 25)

    # ... rest of code

# After
def print_invoice(self):
    self.print_banner()
    # ... rest of code

def print_banner(self):
    print("*" * 25)
    print("Invoice")
    print("*" * 25)
```

---

## Using Local Variables

### Reading Local Variables

**Variables read but not modified** → Pass as parameters

```python
# Before
def print_owing(self):
    outstanding = 0.0

    # Print details
    print(f"Name: {self.name}")
    print(f"Amount: ${outstanding:.2f}")

# After
def print_owing(self):
    outstanding = 0.0
    self.print_details(outstanding)

def print_details(self, outstanding):
    print(f"Name: {self.name}")
    print(f"Amount: ${outstanding:.2f}")
```

### Reassigning Local Variables

**Variable assigned in fragment** → Return value from method

```python
# Before
def calculate_total(self):
    base_price = self.quantity * self.item_price
    discount_factor = 0
    if base_price > 1000:
        discount_factor = 0.05
    return base_price * (1 - discount_factor)

# After
def calculate_total(self):
    base_price = self.quantity * self.item_price
    discount_factor = self.get_discount_factor(base_price)
    return base_price * (1 - discount_factor)

def get_discount_factor(self, base_price):
    if base_price > 1000:
        return 0.05
    else:
        return 0
```

---

## Multiple Return Values

**When extracted code modifies multiple variables**: Return tuple or object.

```python
# Before
def process_payment(self):
    total = self.calculate_base_price()
    tax = 0
    discount = 0

    if self.is_premium_customer():
        discount = total * 0.1

    tax = total * 0.08

    return total - discount + tax

# After
def process_payment(self):
    total = self.calculate_base_price()
    discount, tax = self.calculate_adjustments(total)
    return total - discount + tax

def calculate_adjustments(self, total):
    discount = self.calculate_discount(total)
    tax = self.calculate_tax(total)
    return discount, tax

def calculate_discount(self, total):
    if self.is_premium_customer():
        return total * 0.1
    return 0

def calculate_tax(self, total):
    return total * 0.08
```

**Better**: Extract smaller methods, each returning one value.

---

## Naming

**Good method names**:
- Explain **what** method does, not **how**
- Use verbs for actions
- Be specific and descriptive

```python
# ❌ Bad names (how, not what)
def loop_items_and_sum():  # Implementation detail
def do_it():  # Meaningless
def step_two():  # Position, not intent

# ✅ Good names (what, clear intent)
def calculate_total():
def send_confirmation_email():
def validate_credit_card():
def is_premium_customer():
```

**If hard to name**: Code fragment may be doing too much (extract smaller fragment).

---

## Complete Example

### Before Refactoring

```python
class Order:
    def __init__(self, customer, items):
        self.customer = customer
        self.items = items

    def process(self):
        # Validate items
        for item in self.items:
            if item.quantity <= 0:
                raise ValueError(f"Invalid quantity for {item.name}")
            if item.price < 0:
                raise ValueError(f"Invalid price for {item.name}")

        # Calculate totals
        subtotal = 0
        for item in self.items:
            subtotal += item.quantity * item.price

        discount = 0
        if self.customer.is_premium and subtotal > 1000:
            discount = subtotal * 0.1

        tax = subtotal * 0.08

        total = subtotal - discount + tax

        # Check payment
        if self.customer.balance < total:
            raise ValueError("Insufficient balance")

        # Process payment
        self.customer.balance -= total

        # Send confirmation
        send_email(
            to=self.customer.email,
            subject="Order Confirmation",
            body=f"Your order total is ${total:.2f}"
        )

        return total
```

**Problems**:
- 40+ lines doing 5 things
- Can't test validation, calculation, payment separately
- Can't reuse calculation logic

### After Refactoring

```python
class Order:
    def __init__(self, customer, items):
        self.customer = customer
        self.items = items

    def process(self):
        self.validate_items()
        total = self.calculate_total()
        self.process_payment(total)
        self.send_confirmation(total)
        return total

    def validate_items(self):
        for item in self.items:
            if item.quantity <= 0:
                raise ValueError(f"Invalid quantity for {item.name}")
            if item.price < 0:
                raise ValueError(f"Invalid price for {item.name}")

    def calculate_total(self):
        subtotal = self.calculate_subtotal()
        discount = self.calculate_discount(subtotal)
        tax = self.calculate_tax(subtotal)
        return subtotal - discount + tax

    def calculate_subtotal(self):
        return sum(item.quantity * item.price for item in self.items)

    def calculate_discount(self, subtotal):
        if self.customer.is_premium and subtotal > 1000:
            return subtotal * 0.1
        return 0

    def calculate_tax(self, subtotal):
        return subtotal * 0.08

    def process_payment(self, total):
        if self.customer.balance < total:
            raise ValueError("Insufficient balance")
        self.customer.balance -= total

    def send_confirmation(self, total):
        send_email(
            to=self.customer.email,
            subject="Order Confirmation",
            body=f"Your order total is ${total:.2f}"
        )
```

**Benefits**:
- Each method has one responsibility
- Can test each piece independently
- Can reuse calculation methods
- Main `process` method reads like documentation
- Easy to modify (change discount logic without touching payment)

---

## Testing Strategy

### Before Extraction

**Ensure tests exist**:
```python
def test_order_process():
    customer = Customer(email="test@example.com", balance=100, is_premium=False)
    items = [Item(name="Widget", quantity=2, price=10)]
    order = Order(customer, items)

    total = order.process()

    assert total == 21.6  # 20 + 8% tax
    assert customer.balance == 78.4
```

### During Extraction

**Run tests after each extraction**:
1. Extract `validate_items()`
2. Run tests → Must be green
3. Extract `calculate_total()`
4. Run tests → Must be green
5. Continue...

### After Extraction

**Add tests for extracted methods** (if public):
```python
def test_calculate_total():
    customer = Customer(is_premium=False)
    items = [Item(name="Widget", quantity=2, price=10)]
    order = Order(customer, items)

    total = order.calculate_total()

    assert total == 21.6  # 20 + 8% tax

def test_calculate_discount_for_premium_customer():
    customer = Customer(is_premium=True)
    order = Order(customer, [])

    discount = order.calculate_discount(1500)

    assert discount == 150  # 10% of 1500
```

---

## IDE Support

**Most IDEs automate Extract Method**:

- **VS Code**: Select code → Right-click → "Extract Method"
- **PyCharm**: Select code → Ctrl+Alt+M (Win) or Cmd+Alt+M (Mac)
- **IntelliJ**: Select code → Refactor → Extract Method

**IDE handles**:
- Creating new method
- Identifying variables (params vs locals)
- Updating callers

**Always run tests after IDE refactoring** (IDEs can make mistakes).

---

## Common Mistakes

### ❌ Mistake 1: Extracting Too Much

```python
# Bad: Extracted method too complex (still doing multiple things)
def process_order(self):
    self.do_everything()  # Doesn't help!

def do_everything(self):
    # 50 lines of code doing multiple things
```

**Fix**: Extract smaller pieces, each with one responsibility.

### ❌ Mistake 2: Poor Names

```python
# Bad: Meaningless names
def process_order(self):
    self.step_one()
    self.step_two()
    self.step_three()

# Good: Descriptive names
def process_order(self):
    self.validate_order()
    self.calculate_total()
    self.charge_customer()
```

### ❌ Mistake 3: Not Running Tests

```python
# Extract method
def calculate_total(self):
    return self.subtotal() - self.discount()  # Typo: should be + tax

# Forgot to run tests!
# Tests would catch the bug
```

**Always**: Run tests after extraction.

---

## Advanced: Extract to Class

**When extracted methods use shared data**: Consider extracting to new class.

```python
# Before: Many extracted methods sharing data
class Order:
    def calculate_total(self):
        subtotal = self.calculate_subtotal()
        discount = self.calculate_discount(subtotal)
        tax = self.calculate_tax(subtotal)
        return subtotal - discount + tax

    def calculate_subtotal(self):
        return sum(item.quantity * item.price for item in self.items)

    def calculate_discount(self, subtotal):
        if self.customer.is_premium and subtotal > 1000:
            return subtotal * 0.1
        return 0

    def calculate_tax(self, subtotal):
        return subtotal * 0.08

# After: Extract to OrderCalculator class
class Order:
    def calculate_total(self):
        calculator = OrderCalculator(self.items, self.customer)
        return calculator.total()

class OrderCalculator:
    def __init__(self, items, customer):
        self.items = items
        self.customer = customer

    def total(self):
        return self.subtotal() - self.discount() + self.tax()

    def subtotal(self):
        return sum(item.quantity * item.price for item in self.items)

    def discount(self):
        if self.customer.is_premium and self.subtotal() > 1000:
            return self.subtotal() * 0.1
        return 0

    def tax(self):
        return self.subtotal() * 0.08
```

**See**: refactorings/moving-features/extract-class.md

---

## Summary

**Extract Method refactoring**:
- Pull code fragment into new method
- Name method after what it does (not how)
- Pass local variables as parameters
- Return modified variables

**Use when**:
- Method too long
- Code needs comment
- Logic duplicated
- Method does multiple things

**Benefits**:
- Shorter, clearer methods
- Reusable code
- Easier testing
- Better names

**Always run tests after extraction.**
