# Context Provision Patterns

## Purpose

Define what context specialists need to work effectively in isolation while maintaining alignment with the overall solution.

---

## Context Architecture

### Minimum Viable Context

**Essential Context (Always provide)**:
- Task objective
- Success criteria
- Input specifications
- Output requirements
- Key constraints
- Integration points

**Supporting Context (Provide as needed)**:
- Architectural decisions
- Design patterns to follow
- Coding standards
- Performance targets
- Security requirements
- Testing expectations

**Excessive Context (Avoid)**:
- Other specialists' tasks
- Overall project timeline
- Unnecessary system details
- Implementation choices
- Personal preferences

---

## The Context Layering Model

```
Layer 1: WHAT (Required)
    ↓
    What needs to be built/changed
    Clear success criteria
    Deliverable format

Layer 2: WHY (Important)
    ↓
    Purpose of this task
    How it fits in larger solution
    User/business value

Layer 3: HOW (Constraints)
    ↓
    Must use specific technologies
    Must integrate with X
    Must maintain compatibility
    Performance requirements

Layer 4: REFERENCES (Optional)
    ↓
    Related documentation
    Example implementations
    Relevant code sections
```

---

## Task Specification Template

### Standard Task Context

```markdown
## Task: [Clear, specific title]

### Objective
[1-2 sentences describing what needs to be accomplished]

### Success Criteria
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2
- [ ] Specific, testable criterion 3

### Input Specifications
**Data format**: [Exact format]
**Source**: [Where data comes from]
**Validation**: [What's guaranteed about input]

### Output Requirements
**Format**: [Exact format expected]
**Destination**: [Where output goes]
**Validation**: [What must be true about output]

### Constraints
- Technical: [Technology/framework requirements]
- Performance: [Speed/memory requirements]
- Compatibility: [What must not break]
- Security: [Security requirements]

### Integration Points
**Depends on**: [Tasks that must complete first]
**Used by**: [What will consume this output]
**Interface**: [Exact API/contract]

### Examples
[Concrete examples of expected behavior]

### Out of Scope
[Explicitly state what should NOT be included]
```

---

## Domain-Specific Context Patterns

### Frontend Task Context

```markdown
## Frontend Task: Create User Profile Component

### Visual Specification
- Wireframe: [Link or description]
- Style guide: [Design system section]
- Responsive breakpoints: Mobile (360px), Tablet (768px), Desktop (1024px+)

### Behavior Specification
- User interactions: [Click, hover, keyboard events]
- State management: [Which state library, patterns]
- Loading states: [Skeleton, spinner, progressive]
- Error states: [Validation, network errors]

### Integration Points
- API endpoints: GET /api/user/profile
- Data shape: UserProfile interface
- Events to emit: profileUpdated, profileError

### Accessibility Requirements
- WCAG 2.1 Level AA compliance
- Keyboard navigation
- Screen reader support
- Focus management
```

### Backend Task Context

```markdown
## Backend Task: Implement User Authentication API

### Endpoint Specifications
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "string",
  "password": "string"
}

Response 200:
{
  "token": "jwt-string",
  "user": { "id": "string", "email": "string" }
}
```

### Security Requirements
- Password hashing: bcrypt, 12 rounds
- JWT signing: RS256, 1 hour expiration
- Rate limiting: 5 requests per minute per IP
- Input validation: Email format, password length 8-128

### Database Schema
```sql
users table:
  id UUID PRIMARY KEY
  email VARCHAR(255) UNIQUE NOT NULL
  password_hash VARCHAR(255) NOT NULL
  created_at TIMESTAMP DEFAULT NOW()
```

### Error Handling
- 400: Invalid input format
- 401: Invalid credentials
- 429: Rate limit exceeded
- 500: Server error (log, don't expose details)
```

### Data Task Context

```markdown
## Data Task: Generate User Analytics Report

### Data Sources
- PostgreSQL: users, events tables
- Redis: cached aggregations (use if available)
- S3: historical event logs (if needed for date range > 30 days)

### Query Performance Requirements
- Response time: <5 seconds for 30-day range
- Use materialized views: user_daily_stats
- Batch size: 1000 records for aggregation

### Output Format
```json
{
  "period": { "start": "ISO8601", "end": "ISO8601" },
  "metrics": {
    "active_users": integer,
    "events_per_user": float,
    "top_events": [{"name": string, "count": integer}]
  }
}
```

### Edge Cases
- No data for period: Return zeros
- Partial data: Flag with "incomplete": true
- Timeout: Return cached if available
```

---

## Constraint Communication

### Hard Constraints (Must follow)

**Technical Constraints**:
```markdown
MUST use Python 3.11+
MUST use React 18+ hooks (no class components)
MUST maintain backward compatibility with API v2
MUST pass existing test suite
```

**Security Constraints**:
```markdown
MUST sanitize all user input
MUST use parameterized queries (no string concatenation)
MUST validate JWT signatures
MUST log security events
```

**Performance Constraints**:
```markdown
MUST respond within 200ms (p95)
MUST handle 1000 concurrent requests
MUST limit memory usage to 512MB
MUST cache frequently accessed data
```

### Soft Constraints (Should follow)

```markdown
SHOULD follow existing code patterns
SHOULD write comprehensive tests
SHOULD document complex logic
SHOULD optimize for readability
```

---

## Interface Specifications

### API Contract Definition

```typescript
/**
 * User service interface
 * All implementations must satisfy this contract
 */
interface UserService {
  /**
   * Retrieve user by ID
   * @param id - User UUID
   * @returns User object or null if not found
   * @throws ServiceError if database unavailable
   */
  getUser(id: string): Promise<User | null>

  /**
   * Create new user
   * @param data - User creation data
   * @returns Created user with generated ID
   * @throws ValidationError if data invalid
   * @throws ConflictError if email already exists
   */
  createUser(data: CreateUserDTO): Promise<User>
}
```

### Data Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "id": {"type": "string", "format": "uuid"},
        "email": {"type": "string", "format": "email"},
        "createdAt": {"type": "string", "format": "date-time"}
      },
      "required": ["id", "email", "createdAt"]
    }
  }
}
```

---

## Boundary Definition

### Clear Scope Boundaries

**In Scope**:
```markdown
✓ Implement login endpoint
✓ Validate credentials
✓ Generate JWT token
✓ Return user data
✓ Handle rate limiting
```

**Out of Scope**:
```markdown
✗ Password reset flow (separate task)
✗ OAuth integration (future work)
✗ Email verification (handled by registration task)
✗ Session management (handled by middleware)
✗ Admin authentication (different system)
```

### File Ownership Boundaries

```
Your ownership:
  /api/auth/login.py
  /api/auth/validators.py
  /tests/auth/test_login.py

Read-only references:
  /models/user.py (use, don't modify)
  /middleware/auth.py (use, don't modify)

Shared coordination:
  /api/auth/__init__.py (coordinate changes)
```

---

## Example-Driven Context

### Concrete Input/Output Examples

**Example 1: Success Case**
```
Input:
POST /api/auth/login
{"email": "user@example.com", "password": "SecurePass123"}

Expected Output:
200 OK
{
  "token": "eyJhbGc...",
  "user": {"id": "123", "email": "user@example.com"}
}
```

**Example 2: Validation Error**
```
Input:
POST /api/auth/login
{"email": "invalid-email", "password": "short"}

Expected Output:
400 Bad Request
{
  "error": "validation_error",
  "details": [
    {"field": "email", "message": "Invalid email format"},
    {"field": "password", "message": "Password must be at least 8 characters"}
  ]
}
```

**Example 3: Authentication Failure**
```
Input:
POST /api/auth/login
{"email": "user@example.com", "password": "WrongPassword"}

Expected Output:
401 Unauthorized
{"error": "invalid_credentials", "message": "Email or password incorrect"}
```

---

## Context Verification Checklist

Before delegating, verify you've provided:

**Core Context:**
- [ ] Clear task objective (what to build)
- [ ] Measurable success criteria
- [ ] Input specifications
- [ ] Output requirements
- [ ] Hard constraints

**Integration Context:**
- [ ] Dependencies identified
- [ ] Interfaces defined
- [ ] Integration points specified
- [ ] Scope boundaries clear

**Quality Context:**
- [ ] Testing expectations
- [ ] Performance targets
- [ ] Security requirements
- [ ] Error handling patterns

**Support Context:**
- [ ] Concrete examples provided
- [ ] Edge cases identified
- [ ] Patterns to follow
- [ ] Resources/references

---

## Context Anti-Patterns

### Avoid These Common Mistakes

**Too Vague**:
```markdown
❌ "Make it fast"
✓ "Response time <200ms at p95"

❌ "Handle errors properly"
✓ "Catch ValueError, log to sentry, return 400 with error details"

❌ "Follow best practices"
✓ "Use React hooks, functional components, memo for expensive computations"
```

**Too Prescriptive**:
```markdown
❌ "Use a for loop from 0 to len(items)"
✓ "Iterate through items and validate each"

❌ "Create a variable called userCache"
✓ "Cache user data to avoid repeated database queries"
```

**Missing Critical Information**:
```markdown
❌ Task: "Create user profile page"
    (Missing: Data source, required fields, validation rules, error states)

✓ Task: "Create user profile page"
   - Data: GET /api/users/:id
   - Fields: name, email, avatar (optional), bio (optional)
   - Validation: Name 1-100 chars, bio <500 chars
   - States: loading, success, error, not found
```

---

## Context Adaptation by Specialist Type

### Code Generator Context

Focus on:
- Exact specifications
- Code patterns to follow
- Library/framework constraints
- File structure
- Testing requirements

### Code Reviewer Context

Focus on:
- Code quality standards
- Security concerns
- Performance criteria
- Consistency requirements
- Review checklist

### Data Profiler Context

Focus on:
- Data sources
- Analysis questions
- Statistical requirements
- Output format
- Performance limits

### React Architect Context

Focus on:
- Component hierarchy
- State management approach
- Design system integration
- Accessibility requirements
- Performance optimization

---

## Progressive Context Disclosure

### Initial Context (Start Work)

```markdown
Provide enough to:
- Understand the task
- Begin implementation
- Ask clarifying questions
```

### On-Demand Context (When Needed)

```markdown
Available but not pushed:
- Detailed architectural docs
- Full system context
- Historical decisions
- Related features
```

### Just-in-Time Context (During Work)

```markdown
Provide when specialist encounters:
- Edge cases
- Integration challenges
- Ambiguous requirements
- Conflicting constraints
```

---

## Context Documentation Format

```markdown
# Task Context Document

## Quick Reference
[2-3 sentences for experienced specialists who know the system]

## Detailed Specification
[Complete requirements for those who need full context]

## Integration Guide
[How this fits with other components]

## Examples
[Concrete examples of expected behavior]

## FAQ
[Common questions and answers]

## References
[Links to related documentation]
```

---

*Context is the bridge between orchestration and execution. A Senior Engineering Manager provides just enough context for autonomous work, without overwhelming or under-specifying.*
