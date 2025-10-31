---
title: Language-Specific Patterns
description: Language-specific best practices, idioms, and common pitfalls
category: Language Support
---

# Language-Specific Patterns

Framework integration and language-specific best practices for code review.

---

## Supported Languages

Code-reviewer provides specialized analysis for:

1. **Python** - Web frameworks (Django, Flask), async patterns, type hints
2. **JavaScript/TypeScript** - Node.js, React, async/await, type safety
3. **Java** - Spring, Streams API, Optional handling
4. **Go** - Goroutines, channels, error handling patterns
5. **Rust** - Ownership, borrowing, lifetimes, unsafe code

---

## Python

**Location**: `languages/python/`

### Style and Conventions

**PEP 8 Compliance**:
- Naming conventions: `snake_case` for functions/variables, `PascalCase` for classes
- Import organization: standard library, third-party, local
- Line length: 79 characters (or 99 for code, 72 for docstrings)
- Spacing: 2 blank lines between top-level functions/classes

**Example**:
```python
# GOOD: PEP 8 compliant
import os
import sys

from django.db import models
from flask import Flask

from myapp.utils import helper_function


class UserManager:
    """Manages user operations."""

    def create_user(self, username: str, email: str) -> User:
        """Create a new user with validation."""
        pass
```

### Type Hints

**Type Safety**:
```python
# GOOD: Clear type hints
from typing import Optional, List, Dict

def process_users(
    users: List[User],
    config: Dict[str, str],
    limit: Optional[int] = None
) -> List[ProcessedUser]:
    """Process users with configuration."""
    pass

# Use mypy for type checking
# mypy src/ --strict
```

### Context Managers

**Resource Management**:
```python
# GOOD: Context manager for resources
with open('file.txt', 'r') as f:
    content = f.read()

# GOOD: Database connections
with connection.cursor() as cursor:
    cursor.execute(query)

# GOOD: Custom context managers
from contextlib import contextmanager

@contextmanager
def temporary_file(filename):
    try:
        f = open(filename, 'w')
        yield f
    finally:
        f.close()
        os.remove(filename)
```

### Generators and Iterators

**Memory Efficiency**:
```python
# BAD: Loads all into memory
def get_all_users():
    return [user for user in User.objects.all()]

# GOOD: Generator for large datasets
def get_all_users():
    for user in User.objects.iterator():
        yield user

# GOOD: Generator expression
user_emails = (user.email for user in User.objects.all())
```

### Async Patterns

**Async/Await Usage**:
```python
# GOOD: Async function
async def fetch_data(url: str) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# GOOD: Gather concurrent tasks
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3)
)

# BAD: Blocking call in async function
async def bad_async():
    time.sleep(5)  # Blocks entire event loop!

# GOOD: Non-blocking
async def good_async():
    await asyncio.sleep(5)  # Non-blocking
```

### Common Python Pitfalls

- **Mutable default arguments**: `def func(items=[]):` - Use `items=None` instead
- **Late binding closures**: Lambdas in loops
- **Exception handling**: Avoid bare `except:`, use specific exceptions
- **Global interpreter lock (GIL)**: Use multiprocessing for CPU-bound tasks

**Files**:
- `languages/python/pep8.md`
- `languages/python/async-patterns.md`
- `languages/python/type-hints.md`

---

## JavaScript/TypeScript

**Location**: `languages/javascript/`

### ESLint Best Practices

**Recommended Rules**:
```javascript
// .eslintrc.js
module.exports = {
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  rules: {
    'no-console': 'warn',
    'no-unused-vars': 'error',
    'prefer-const': 'error',
    'no-var': 'error',
  }
};
```

### Async/Await vs Promises

**Modern Async Patterns**:
```javascript
// BAD: Promise hell
function getData() {
  return fetch(url)
    .then(response => response.json())
    .then(data => processData(data))
    .then(result => saveResult(result))
    .catch(error => handleError(error));
}

// GOOD: Async/await
async function getData() {
  try {
    const response = await fetch(url);
    const data = await response.json();
    const result = await processData(data);
    await saveResult(result);
  } catch (error) {
    handleError(error);
  }
}

// GOOD: Parallel execution
const [users, posts, comments] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
  fetchComments()
]);
```

### TypeScript Type Safety

**Strict Mode**:
```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}

// GOOD: Explicit types
interface User {
  id: number;
  name: string;
  email: string;
}

function getUser(id: number): Promise<User | null> {
  // Implementation
}

// GOOD: Type guards
function isUser(obj: any): obj is User {
  return obj && typeof obj.id === 'number' && typeof obj.name === 'string';
}
```

### Memory Leak Patterns

**Common Issues**:
```javascript
// BAD: Event listener not removed
class Component {
  constructor() {
    window.addEventListener('resize', this.handleResize);
  }
  // Memory leak: listener never removed!
}

// GOOD: Cleanup
class Component {
  constructor() {
    this.handleResize = this.handleResize.bind(this);
    window.addEventListener('resize', this.handleResize);
  }

  destroy() {
    window.removeEventListener('resize', this.handleResize);
  }
}

// BAD: Closure capturing large object
function createHandler(largeData) {
  return () => {
    console.log(largeData[0]); // Entire largeData kept in memory
  };
}

// GOOD: Extract only needed data
function createHandler(largeData) {
  const firstItem = largeData[0];
  return () => {
    console.log(firstItem); // Only firstItem kept
  };
}
```

### Modern ES6+ Features

- **Destructuring**: `const { name, email } = user;`
- **Spread operator**: `const newObj = { ...oldObj, updated: true };`
- **Optional chaining**: `const city = user?.address?.city;`
- **Nullish coalescing**: `const name = user.name ?? 'Guest';`
- **Template literals**: `` const msg = `Hello, ${name}!`; ``

**Files**:
- `languages/javascript/async-patterns.md`
- `languages/javascript/typescript-strict.md`
- `languages/javascript/memory-leaks.md`

---

## Java

**Location**: `languages/java/`

### Streams API Usage

**Functional Patterns**:
```java
// GOOD: Streams for collection processing
List<String> activeUserEmails = users.stream()
    .filter(User::isActive)
    .map(User::getEmail)
    .collect(Collectors.toList());

// GOOD: Parallel streams for large datasets
long count = items.parallelStream()
    .filter(item -> item.getPrice() > 100)
    .count();

// BAD: Modifying external state in stream
List<String> results = new ArrayList<>();
users.stream().forEach(user -> results.add(user.getName())); // Anti-pattern

// GOOD: Collect results
List<String> results = users.stream()
    .map(User::getName)
    .collect(Collectors.toList());
```

### Optional Handling

**Avoid .get() Without Check**:
```java
// BAD: Unsafe get()
Optional<User> user = findUser(id);
return user.get(); // Throws NoSuchElementException if empty!

// GOOD: Safe handling
return findUser(id)
    .orElseThrow(() -> new UserNotFoundException(id));

// GOOD: Provide default
return findUser(id)
    .orElse(DEFAULT_USER);

// GOOD: Transform if present
return findUser(id)
    .map(User::getEmail)
    .orElse("no-email@example.com");
```

### Spring Patterns

**Dependency Injection**:
```java
// GOOD: Constructor injection (recommended)
@Service
public class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}

// BAD: Field injection (harder to test)
@Service
public class UserService {
    @Autowired
    private UserRepository repository;
}

// GOOD: Configuration
@Configuration
public class AppConfig {
    @Bean
    public DataSource dataSource() {
        return new HikariDataSource(config);
    }
}
```

### Exception Handling

```java
// GOOD: Specific exceptions
try {
    processPayment(order);
} catch (InsufficientFundsException e) {
    log.warn("Payment failed: {}", e.getMessage());
    return PaymentResult.failed(e.getReason());
} catch (PaymentGatewayException e) {
    log.error("Gateway error", e);
    return PaymentResult.error();
}

// BAD: Catching generic Exception
try {
    processPayment(order);
} catch (Exception e) { // Too broad
    log.error("Error", e);
}
```

### Garbage Collection Awareness

- Minimize object creation in hot paths
- Use object pools for frequently created objects
- Consider StringBuilder for string concatenation in loops
- Monitor GC metrics in production

**Files**:
- `languages/java/streams-api.md`
- `languages/java/optional-handling.md`
- `languages/java/spring-patterns.md`

---

## Go

**Location**: `languages/go/`

### Interface Composition

**Small Interfaces**:
```go
// GOOD: Small, focused interfaces
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}

// GOOD: Accept interfaces, return structs
func ProcessData(r io.Reader) (*Result, error) {
    // Implementation
}
```

### Goroutines and Channels

**Proper Synchronization**:
```go
// GOOD: Use WaitGroup for goroutines
func processItems(items []Item) {
    var wg sync.WaitGroup
    for _, item := range items {
        wg.Add(1)
        go func(i Item) {
            defer wg.Done()
            process(i)
        }(item)
    }
    wg.Wait()
}

// GOOD: Channel for results
func fetchData(urls []string) []Result {
    results := make(chan Result, len(urls))
    for _, url := range urls {
        go func(u string) {
            results <- fetch(u)
        }(url)
    }

    var collected []Result
    for i := 0; i < len(urls); i++ {
        collected = append(collected, <-results)
    }
    return collected
}

// BAD: Race condition
var counter int
for i := 0; i < 100; i++ {
    go func() {
        counter++ // Race!
    }()
}

// GOOD: Use atomic or mutex
var counter int64
for i := 0; i < 100; i++ {
    go func() {
        atomic.AddInt64(&counter, 1)
    }()
}
```

### Error Handling Patterns

**No Exceptions**:
```go
// GOOD: Explicit error handling
func ReadFile(path string) ([]byte, error) {
    file, err := os.Open(path)
    if err != nil {
        return nil, fmt.Errorf("failed to open file: %w", err)
    }
    defer file.Close()

    data, err := io.ReadAll(file)
    if err != nil {
        return nil, fmt.Errorf("failed to read file: %w", err)
    }

    return data, nil
}

// GOOD: Custom error types
type ValidationError struct {
    Field string
    Reason string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Reason)
}
```

### Defer, Panic, Recover

```go
// GOOD: Defer for cleanup
func processFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close() // Guaranteed cleanup

    // Process file
}

// GOOD: Recover from panic (rare)
func safeHandler(w http.ResponseWriter, r *http.Request) {
    defer func() {
        if r := recover(); r != nil {
            log.Printf("Panic recovered: %v", r)
            http.Error(w, "Internal error", 500)
        }
    }()

    handler(w, r)
}
```

**Files**:
- `languages/go/concurrency.md`
- `languages/go/error-handling.md`
- `languages/go/interfaces.md`

---

## Rust

**Location**: `languages/rust/`

### Ownership and Borrowing

**Memory Safety**:
```rust
// GOOD: Ownership transfer
fn consume_string(s: String) {
    println!("{}", s);
} // s is dropped here

// GOOD: Borrowing (immutable)
fn read_string(s: &String) {
    println!("{}", s);
} // s is not dropped, ownership remains with caller

// GOOD: Mutable borrowing
fn modify_string(s: &mut String) {
    s.push_str(" world");
}

// Example usage
let mut s = String::from("Hello");
read_string(&s); // Immutable borrow
modify_string(&mut s); // Mutable borrow
consume_string(s); // s is moved, no longer accessible
```

### Lifetimes Correctness

**Explicit Lifetimes**:
```rust
// GOOD: Lifetime annotation
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// GOOD: Struct with references
struct User<'a> {
    name: &'a str,
    email: &'a str,
}

impl<'a> User<'a> {
    fn get_name(&self) -> &str {
        self.name
    }
}
```

### Error Handling (Result, Option)

**Pattern Matching**:
```rust
// GOOD: Result handling
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}

// GOOD: Using ? operator
fn process_file(path: &str) -> Result<String, std::io::Error> {
    let mut file = File::open(path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}

// GOOD: Option handling
fn find_user(id: i32) -> Option<User> {
    users.get(&id).cloned()
}

match find_user(42) {
    Some(user) => println!("Found: {}", user.name),
    None => println!("Not found"),
}
```

### Unsafe Code Review

**Minimize and Justify**:
```rust
// BAD: Unnecessary unsafe
unsafe {
    let x = 5; // No need for unsafe
}

// GOOD: Justified unsafe with documentation
/// # Safety
/// Caller must ensure ptr is valid and aligned
unsafe fn read_raw(ptr: *const u8) -> u8 {
    *ptr
}

// GOOD: Encapsulate unsafe
pub fn safe_wrapper(data: &[u8], index: usize) -> Option<u8> {
    if index < data.len() {
        unsafe {
            Some(*data.as_ptr().add(index))
        }
    } else {
        None
    }
}
```

**Files**:
- `languages/rust/ownership.md`
- `languages/rust/lifetimes.md`
- `languages/rust/error-handling.md`
- `languages/rust/unsafe-review.md`

---

## Language Detection

Code-reviewer automatically detects language from file extensions:

| Language | Extensions | Framework Detection |
|----------|-----------|-------------------|
| Python | `.py` | Django (models.py, views.py), Flask (app.py) |
| JavaScript | `.js`, `.jsx` | React (JSX), Node.js (package.json) |
| TypeScript | `.ts`, `.tsx` | Angular, React |
| Java | `.java` | Spring (@Service, @Controller) |
| Go | `.go` | Standard library patterns |
| Rust | `.rs` | Cargo.toml |

---

## Framework-Specific Patterns

### Django (Python)
- ORM best practices: `select_related()`, `prefetch_related()`
- Security: CSRF middleware, SQL injection via ORM
- Migrations: Always review migration files

### Flask (Python)
- Route security: Authorization decorators
- Session management: Signed cookies
- Blueprint organization

### React (JavaScript/TypeScript)
- Hook patterns: `useEffect` dependencies
- Memoization: `useMemo`, `useCallback`
- State management: Redux, Context

### Spring (Java)
- Transaction management: `@Transactional`
- Security: Spring Security filters
- REST: `@RestController`, `@RequestMapping`

---

## Cross-Language Patterns

**Common Across All Languages**:
1. Input validation
2. Error handling
3. Resource management (file handles, connections)
4. Concurrency safety
5. Security best practices

**Language-Specific Trade-offs**:
- **Python**: Flexibility vs performance
- **JavaScript**: Dynamic typing vs TypeScript safety
- **Java**: Verbosity vs explicitness
- **Go**: Simplicity vs expressiveness
- **Rust**: Safety vs learning curve

---

## Adding New Languages

To extend code-reviewer for new languages:

1. Create `languages/{language}/` directory
2. Add language-specific patterns file
3. Document common pitfalls
4. Include framework integration guides
5. Update this INDEX.md

---

## References

- Python PEP 8: https://pep8.org/
- JavaScript MDN: https://developer.mozilla.org/
- TypeScript Handbook: https://www.typescriptlang.org/docs/
- Effective Java: Joshua Bloch
- Effective Go: https://golang.org/doc/effective_go
- The Rust Book: https://doc.rust-lang.org/book/
