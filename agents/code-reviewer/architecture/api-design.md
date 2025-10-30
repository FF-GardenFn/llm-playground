# API Design Principles

**Purpose**: Assess REST API design quality, conventions, and best practices during code review.

**Phase**: Phase 2 (Manual Review)

**Priority**: Important (affects API usability and maintainability)

**Refactorable**: ❌ NO (requires API redesign, not code structure changes)

---

## Overview

Well-designed APIs are:
- **Consistent**: Follow conventions throughout
- **Intuitive**: Easy to understand and use
- **Predictable**: Behave as users expect
- **Versioned**: Support backward compatibility
- **Well-documented**: Clear usage examples

---

## REST API Principles

### 1. Resource-Oriented Design

**Principle**: APIs should model resources (nouns), not actions (verbs).

**Good - Resource Names**:
```
GET    /users              ← Collection
GET    /users/123          ← Single resource
POST   /users              ← Create
PUT    /users/123          ← Update (full)
PATCH  /users/123          ← Update (partial)
DELETE /users/123          ← Delete

GET    /users/123/orders   ← Nested resource
GET    /orders?user_id=123 ← Query parameter
```

**Bad - Action Names**:
```
❌ POST /createUser
❌ POST /getUser
❌ POST /updateUser
❌ POST /deleteUser

✅ Use HTTP methods (POST, GET, PUT, DELETE) instead
```

**Detection Heuristics**:
- URLs contain verbs (`/createUser`, `/getOrders`)
- All operations use POST
- Resource names not nouns

**Severity**: **Important**

---

### 2. HTTP Methods (Verbs)

**Standard Usage**:

| Method | Purpose | Idempotent? | Safe? |
|--------|---------|-------------|-------|
| GET | Retrieve resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Replace resource | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Delete resource | Yes | No |

**Good - Correct Methods**:
```python
# ✅ GOOD: Correct HTTP methods
@app.route('/users', methods=['GET'])
def list_users():
    return jsonify(User.objects.all())

@app.route('/users', methods=['POST'])
def create_user():
    user = User.objects.create(**request.json)
    return jsonify(user), 201  # Created

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.objects.get(id=id)
    user.update(**request.json)
    return jsonify(user), 200

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    User.objects.get(id=id).delete()
    return '', 204  # No Content
```

**Bad - Wrong Methods**:
```python
# ❌ BAD: Using POST for everything
@app.route('/getUsers', methods=['POST'])  # Should be GET!
def get_users():
    return jsonify(User.objects.all())

@app.route('/deleteUser', methods=['POST'])  # Should be DELETE!
def delete_user():
    user_id = request.json['id']
    User.objects.get(id=user_id).delete()
    return 'Deleted'
```

**Detection Heuristics**:
- GET requests that modify data
- POST used for retrievals
- Non-idempotent operations use GET

**Severity**: **Important**

---

### 3. Status Codes

**Standard Status Codes**:

**Success (2xx)**:
- `200 OK`: Successful request (GET, PUT, PATCH)
- `201 Created`: Resource created (POST)
- `204 No Content`: Successful deletion (DELETE)

**Client Errors (4xx)**:
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Not authorized
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: State conflict (e.g., duplicate)
- `422 Unprocessable Entity`: Validation failed

**Server Errors (5xx)**:
- `500 Internal Server Error`: Unexpected error
- `503 Service Unavailable`: Service down

**Good - Correct Status Codes**:
```python
# ✅ GOOD: Appropriate status codes
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user = User.objects.create(**request.json)
        return jsonify(user), 201  # Created
    except ValidationError as e:
        return jsonify({'error': str(e)}), 422  # Validation failed
    except IntegrityError:
        return jsonify({'error': 'User already exists'}), 409  # Conflict

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.objects.get(id=id)
        return jsonify(user), 200  # OK
    except User.DoesNotExist:
        return jsonify({'error': 'User not found'}), 404  # Not Found
```

**Bad - Wrong Status Codes**:
```python
# ❌ BAD: Always returns 200
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user = User.objects.create(**request.json)
        return jsonify(user), 200  # Should be 201!
    except ValidationError as e:
        return jsonify({'error': str(e)}), 200  # Should be 422!
    except User.DoesNotExist:
        return jsonify({'error': 'Not found'}), 200  # Should be 404!
```

**Detection Heuristics**:
- Always returning 200 (even for errors)
- Returning 200 for created resources (should be 201)
- Using 500 for client errors

**Severity**: **Important**

---

### 4. Request/Response Format

**Principle**: Consistent JSON structure.

**Good - Consistent Format**:
```json
// ✅ GOOD: Consistent response structure

// Success
{
  "data": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com"
  }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email address",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  }
}

// Collection
{
  "data": [
    {"id": 1, "name": "User 1"},
    {"id": 2, "name": "User 2"}
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
```

**Bad - Inconsistent Format**:
```json
// ❌ BAD: Inconsistent structure

// Success (raw object)
{"id": 123, "name": "John Doe"}

// Error (different structure)
{"message": "Error occurred"}

// Error (another structure)
{"error": "Something went wrong", "status": "fail"}
```

**Detection Heuristics**:
- Response structure varies by endpoint
- No consistent error format
- Missing metadata (pagination, totals)

**Severity**: **Suggestion**

---

### 5. Pagination

**Principle**: Large collections should be paginated.

**Good - Pagination**:
```python
# ✅ GOOD: Paginated response
@app.route('/users')
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    users = User.objects.paginate(page=page, per_page=per_page)

    return jsonify({
        'data': [user.to_dict() for user in users.items],
        'meta': {
            'total': users.total,
            'page': page,
            'per_page': per_page,
            'pages': users.pages
        },
        'links': {
            'first': url_for('list_users', page=1),
            'last': url_for('list_users', page=users.pages),
            'next': url_for('list_users', page=page+1) if users.has_next else None,
            'prev': url_for('list_users', page=page-1) if users.has_prev else None
        }
    })
```

**Bad - No Pagination**:
```python
# ❌ BAD: Returns all records
@app.route('/users')
def list_users():
    users = User.objects.all()  # Could be 1 million users!
    return jsonify([user.to_dict() for user in users])
```

**Detection Heuristics**:
- `.all()` on large collections
- No `page` or `limit` parameters
- No metadata about total count

**Severity**: **Important** (for large datasets)

---

### 6. Filtering, Sorting, Searching

**Good - Query Parameters**:
```python
# ✅ GOOD: Support filtering, sorting, searching
@app.route('/users')
def list_users():
    # Filtering
    role = request.args.get('role')
    is_active = request.args.get('is_active', type=bool)

    # Searching
    search = request.args.get('search')

    # Sorting
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')

    query = User.objects

    if role:
        query = query.filter(role=role)
    if is_active is not None:
        query = query.filter(is_active=is_active)
    if search:
        query = query.filter(name__icontains=search)

    query = query.order_by(f"-{sort_by}" if order == 'desc' else sort_by)

    return jsonify(query.all())

# Usage:
# GET /users?role=admin
# GET /users?is_active=true
# GET /users?search=john
# GET /users?sort_by=name&order=asc
```

**Detection Heuristics**:
- No filtering on collection endpoints
- No sorting options
- No search capability

**Severity**: **Suggestion**

---

### 7. API Versioning

**Principle**: Support backward compatibility.

**Good - Versioned API**:
```python
# ✅ GOOD: URL versioning
@app.route('/api/v1/users')
def list_users_v1():
    return jsonify(User.objects.all())

@app.route('/api/v2/users')
def list_users_v2():
    # Breaking changes in v2
    return jsonify([user.to_v2_dict() for user in User.objects.all()])

# OR header versioning
@app.route('/api/users')
def list_users():
    version = request.headers.get('API-Version', 'v1')
    if version == 'v2':
        return jsonify([user.to_v2_dict() for user in User.objects.all()])
    return jsonify(User.objects.all())
```

**Bad - No Versioning**:
```python
# ❌ BAD: Breaking changes without versioning
@app.route('/users')
def list_users():
    # Changed response format - breaks existing clients!
    return jsonify({'users': User.objects.all()})
```

**Detection Heuristics**:
- No version in URL or headers
- Breaking changes without version bump
- No deprecation strategy

**Severity**: **Important** (for public APIs)

---

### 8. Error Messages

**Principle**: Clear, actionable error messages.

**Good - Helpful Errors**:
```python
# ✅ GOOD: Detailed error response
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user = User.objects.create(**request.json)
        return jsonify(user), 201
    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'User validation failed',
                'details': e.messages,  # Field-level errors
                'documentation': 'https://api.example.com/docs/errors#validation'
            }
        }), 422

# Response:
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "User validation failed",
    "details": {
      "email": ["Invalid email format"],
      "age": ["Must be at least 18"]
    },
    "documentation": "https://api.example.com/docs/errors#validation"
  }
}
```

**Bad - Vague Errors**:
```python
# ❌ BAD: Vague error
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user = User.objects.create(**request.json)
        return jsonify(user), 201
    except Exception as e:
        return jsonify({'error': 'Something went wrong'}), 500

# No information about what went wrong!
```

**Detection Heuristics**:
- Generic error messages ("Error occurred", "Something went wrong")
- No error codes
- No field-level validation errors

**Severity**: **Suggestion**

---

### 9. Authentication & Authorization

**Principle**: Secure API endpoints appropriately.

**Good - Authentication**:
```python
# ✅ GOOD: Token-based authentication
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not is_valid_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/users', methods=['POST'])
@require_auth
def create_user():
    user = User.objects.create(**request.json)
    return jsonify(user), 201

# Usage:
# POST /users
# Headers: Authorization: Bearer <token>
```

**Detection Heuristics**:
- No authentication on sensitive endpoints
- Passwords in query parameters
- No authorization checks

**Severity**: **Critical** (security issue)

---

### 10. Rate Limiting

**Principle**: Prevent abuse with rate limits.

**Good - Rate Limiting**:
```python
# ✅ GOOD: Rate limiting
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/users', methods=['POST'])
@limiter.limit("10 per minute")
def create_user():
    user = User.objects.create(**request.json)
    return jsonify(user), 201

# Response headers:
# X-RateLimit-Limit: 10
# X-RateLimit-Remaining: 7
# X-RateLimit-Reset: 1640000000
```

**Detection Heuristics**:
- No rate limiting on public endpoints
- No rate limit headers
- No throttling for expensive operations

**Severity**: **Important** (DoS prevention)

---

## Review Checklist

### Phase 2: Manual Review

**Resource Design**:
- [ ] Are resources named with nouns (not verbs)?
- [ ] Are HTTP methods used correctly (GET, POST, PUT, DELETE)?
- [ ] Are URLs consistent and RESTful?

**HTTP Conventions**:
- [ ] Are appropriate status codes used (200, 201, 404, 422, 500)?
- [ ] Are methods idempotent where required (PUT, DELETE)?
- [ ] Is GET used only for safe operations (no side effects)?

**Response Format**:
- [ ] Is response format consistent across endpoints?
- [ ] Are errors returned in consistent structure?
- [ ] Is metadata included for collections (pagination, totals)?

**Usability**:
- [ ] Is pagination implemented for large collections?
- [ ] Are filtering, sorting, searching supported?
- [ ] Are error messages clear and actionable?

**Security**:
- [ ] Is authentication required for sensitive endpoints?
- [ ] Is authorization checked (not just authentication)?
- [ ] Is rate limiting implemented?

**Versioning**:
- [ ] Is API versioned (URL or header)?
- [ ] Is backward compatibility maintained?
- [ ] Is deprecation strategy defined?

**Documentation**:
- [ ] Are endpoints documented?
- [ ] Are request/response examples provided?
- [ ] Are error codes documented?

---

## Summary

**API Design Principles**:
1. Resource-oriented (nouns, not verbs)
2. Correct HTTP methods (GET, POST, PUT, DELETE)
3. Appropriate status codes (2xx, 4xx, 5xx)
4. Consistent JSON format
5. Pagination for large collections
6. Filtering, sorting, searching support
7. API versioning
8. Clear error messages
9. Authentication & authorization
10. Rate limiting

**Common Violations**:
- Action names in URLs (`/createUser`)
- Wrong HTTP methods (POST for everything)
- Always returning 200
- Inconsistent response format
- No pagination
- No versioning
- Vague error messages
- No authentication
- No rate limiting

**Detection**:
- Phase 2: Manual API design review
- Check conventions, consistency, security

**Refactorable**: ❌ NO (requires API redesign)

**Priority**: **Important** (affects API usability and maintainability)
