# Example: Creating a New API Endpoint

**Scenario:** Create a REST API endpoint to retrieve user profile by ID

**User Request:** "Create an endpoint to get user profile by ID"

---

## Agent Response

### PHASE 1: RECONNAISSANCE

**Understanding the Request**

Need to create a GET endpoint that returns user profile data by user ID.

**Initial Questions for Clarification:**
- What profile fields should be returned? (name, email, bio, avatar, etc.)
- What should happen for non-existent users? (404 or custom error?)
- Any authentication requirements? (public or requires auth token?)

**User Clarifies:**
- Return: id, name, email, created_at, profile_picture_url
- Return 404 with error message for non-existent users
- Requires authentication (JWT token)

**Acceptance Criteria:**
- GET /api/users/{id} endpoint
- Returns JSON with user profile fields
- Returns 404 if user not found
- Requires valid JWT token
- Handles errors gracefully
- Has comprehensive tests

**Codebase Reconnaissance**

Tool: `python atools/search_codebase.py --pattern "route\|endpoint\|api"`

Found:
- `api/routes.py:15` - Existing route definitions using Flask
- `api/serializers.py:8` - `UserSerializer` class for formatting responses
- `api/middleware.py:10` - `@require_auth` decorator for JWT validation
- `models/user.py:5` - `User` model with SQLAlchemy
- `tests/test_api.py:20` - Existing API tests using Flask test client

**Key Findings:**

**Existing Route Pattern** (api/routes.py):
```python
@app.route('/api/users', methods=['GET'])
@require_auth
def list_users():
    users = User.query.all()
    return jsonify(UserSerializer.serialize_many(users)), 200
```

**Existing Serializer Pattern** (api/serializers.py):
```python
class UserSerializer:
    @staticmethod
    def serialize(user):
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        }
```

**Existing Auth Pattern** (api/middleware.py):
```python
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No authorization token'}), 401
        # ... JWT validation logic ...
        return f(*args, **kwargs)
    return decorated
```

**Testing Pattern** (tests/test_api.py):
```python
class TestUserAPI:
    def test_list_users_authenticated(self, client, auth_headers):
        response = client.get('/api/users', headers=auth_headers)
        assert response.status_code == 200
```

**Integration Strategy:**
- Add new route to `api/routes.py` (follows existing Flask pattern)
- Extend `UserSerializer` to include `profile_picture_url` field
- Use existing `@require_auth` decorator
- Add tests to `tests/test_api.py` (follows pytest pattern with fixtures)

**Checkpoint:** ✓ I understand the requirement, found similar code, identified integration points

---

### PHASE 2: DESIGN

**Approach:** Add GET endpoint following existing Flask route pattern

**Components:**
1. **Route function** in `api/routes.py`
   - Use Flask `@app.route('/api/users/<int:user_id>', methods=['GET'])`
   - Apply `@require_auth` decorator
   - Query user by ID
   - Handle not found case
   - Return serialized response

2. **Serializer extension** in `api/serializers.py`
   - Add `profile_picture_url` to existing `serialize()` method
   - Keep existing fields (already has id, name, email, created_at)

3. **Tests** in `tests/test_api.py`
   - Valid user ID with auth (200 + correct data)
   - Non-existent user ID (404 + error message)
   - Missing authentication (401)
   - Invalid user ID format (400)

**Data Flow:**
1. Request arrives: `GET /api/users/123` with `Authorization: Bearer <token>`
2. `@require_auth` validates JWT token
3. Route handler queries: `User.query.get(user_id)`
4. If found: Serialize and return 200
5. If not found: Return 404 with error

**Justification:**
- Follows existing Flask route pattern (see: `list_users()` in api/routes.py:15)
- Reuses existing auth middleware (consistent security)
- Extends existing serializer (DRY principle)
- Integrates with existing User model (no schema changes needed)
- Testing follows established pytest fixture pattern

**Risks & Mitigations:**
- **Risk:** User ID could be malformed (non-integer)
  - **Mitigation:** Flask's `<int:user_id>` type converter handles this (returns 404 automatically)

- **Risk:** Serializer might access None values
  - **Mitigation:** Only serialize when user exists, handle null profile_picture_url

- **Risk:** Performance with large profile pictures
  - **Mitigation:** Return URL, not raw data (client fetches separately)

**Alternative Considered:**
- Could create separate `/api/profiles/{id}` endpoint
- Decision: Use `/api/users/{id}` to match RESTful convention and existing pattern

**Checkpoint:** ✓ Design is clear, follows existing patterns, testable, risks identified

---

### PHASE 3: IMPLEMENTATION

**Implementation Plan:**

Steps with checkpoints:
1. [ ] Extend UserSerializer with profile_picture_url field
2. [ ] Add get_user_by_id route to api/routes.py
3. [ ] Write tests (RED phase)
4. [ ] Verify tests fail (no implementation yet)
5. [ ] Run tests and verify passing (GREEN phase)
6. [ ] Add error handling tests
7. [ ] Run full test suite
8. [ ] Lint and verify

**Step 1: Extend Serializer**

**File: api/serializers.py** (modification)
```python
class UserSerializer:
    @staticmethod
    def serialize(user):
        """Serialize user object to JSON-compatible dict.

        Args:
            user (User): User model instance

        Returns:
            dict: Serialized user data
        """
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'profile_picture_url': user.profile_picture_url or None  # NEW: Handle null case
        }

    @staticmethod
    def serialize_many(users):
        """Serialize multiple user objects."""
        return [UserSerializer.serialize(user) for user in users]
```

**Step 2: Add Route**

**File: api/routes.py** (addition)
```python
@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user_by_id(user_id):
    """Get user profile by ID.

    Args:
        user_id (int): User ID from URL path

    Returns:
        JSON response with user data (200) or error (404)

    Requires:
        Valid JWT token in Authorization header
    """
    user = User.query.get(user_id)

    if not user:
        return jsonify({
            'error': 'User not found',
            'message': f'No user exists with ID {user_id}'
        }), 404

    return jsonify(UserSerializer.serialize(user)), 200
```

**Step 3-4: Write Tests (RED Phase)**

**File: tests/test_api.py** (addition)
```python
import pytest
from models.user import User
from api import create_app
from database import db

class TestGetUserByID:
    """Test GET /api/users/{id} endpoint."""

    @pytest.fixture
    def sample_user(self, app):
        """Create a sample user for testing."""
        with app.app_context():
            user = User(
                name="Test User",
                email="test@example.com",
                profile_picture_url="https://example.com/avatar.jpg"
            )
            db.session.add(user)
            db.session.commit()
            yield user
            db.session.delete(user)
            db.session.commit()

    def test_get_user_with_valid_id_authenticated(self, client, auth_headers, sample_user):
        """Valid user ID with authentication should return user data."""
        # Arrange: sample_user exists in database
        user_id = sample_user.id

        # Act: Request user profile
        response = client.get(f'/api/users/{user_id}', headers=auth_headers)
        data = response.get_json()

        # Assert: Returns 200 with correct data
        assert response.status_code == 200
        assert data['id'] == sample_user.id
        assert data['name'] == "Test User"
        assert data['email'] == "test@example.com"
        assert data['profile_picture_url'] == "https://example.com/avatar.jpg"
        assert 'created_at' in data

    def test_get_user_with_nonexistent_id(self, client, auth_headers):
        """Non-existent user ID should return 404."""
        # Arrange: User ID 99999 doesn't exist

        # Act: Request non-existent user
        response = client.get('/api/users/99999', headers=auth_headers)
        data = response.get_json()

        # Assert: Returns 404 with error message
        assert response.status_code == 404
        assert 'error' in data
        assert data['error'] == 'User not found'
        assert 'No user exists with ID 99999' in data['message']

    def test_get_user_without_authentication(self, client, sample_user):
        """Request without auth token should return 401."""
        # Arrange: No auth headers provided
        user_id = sample_user.id

        # Act: Request without authentication
        response = client.get(f'/api/users/{user_id}')
        data = response.get_json()

        # Assert: Returns 401
        assert response.status_code == 401
        assert 'error' in data
        assert 'authorization' in data['error'].lower()

    def test_get_user_with_invalid_id_format(self, client, auth_headers):
        """Invalid ID format should return 404 (Flask handles type conversion)."""
        # Arrange: ID is not an integer

        # Act: Request with string ID
        response = client.get('/api/users/not-a-number', headers=auth_headers)

        # Assert: Flask returns 404 for route not found
        assert response.status_code == 404

    def test_get_user_with_null_profile_picture(self, client, auth_headers, app):
        """User without profile picture should return null for that field."""
        # Arrange: Create user without profile picture
        with app.app_context():
            user = User(
                name="No Avatar User",
                email="noavatar@example.com",
                profile_picture_url=None
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Act: Request user profile
        response = client.get(f'/api/users/{user_id}', headers=auth_headers)
        data = response.get_json()

        # Assert: Returns 200 with null profile_picture_url
        assert response.status_code == 200
        assert data['profile_picture_url'] is None

        # Cleanup
        with app.app_context():
            db.session.delete(user)
            db.session.commit()
```

**Step 5: Run Tests (GREEN Phase)**

Tool: `bash atools/run_tests.sh tests/test_api.py::TestGetUserByID`

Result:
```
✓ test_get_user_with_valid_id_authenticated PASSED
✓ test_get_user_with_nonexistent_id PASSED
✓ test_get_user_without_authentication PASSED
✓ test_get_user_with_invalid_id_format PASSED
✓ test_get_user_with_null_profile_picture PASSED

5/5 tests passed
```

**Step 7: Run Full Test Suite**

Tool: `bash atools/run_tests.sh`

Result:
```
✓ All existing tests still pass (42/42)
✓ New endpoint tests pass (5/5)

Total: 47/47 tests passed
No regressions detected
```

**Checkpoint:** ✓ Tests pass, functionality works, no regressions

---

### PHASE 4: VALIDATION

**Verification Checklist**

Tool: `bash atools/lint_code.sh api/routes.py api/serializers.py tests/test_api.py`

Result:
```
✓ No linting issues
✓ Code style consistent
✓ Docstrings present
✓ Type hints where applicable
```

Tool: `python atools/analyze_complexity.py api/routes.py`

Result:
```
get_user_by_id():
  Cyclomatic Complexity: 2 (Simple)
  Lines of Code: 14
  ✓ Complexity acceptable
```

**Edge Cases Verified:**
- [x] Valid user ID: Returns 200 with correct data
- [x] Non-existent user ID: Returns 404 with clear message
- [x] Missing authentication: Returns 401
- [x] Invalid ID format: Returns 404 (Flask type converter handles)
- [x] Null profile picture: Returns null gracefully
- [x] All existing endpoints: Still work (regression check)

**Security Verification:**
- [x] Authentication required (enforced by @require_auth)
- [x] JWT token validated before processing
- [x] No SQL injection risk (using ORM with parameterized queries)
- [x] Error messages don't leak sensitive information

**Performance Considerations:**
- [x] Single database query (no N+1 problem)
- [x] Returns URL, not binary data (efficient)
- [x] Serialization is O(1) complexity

**Completion Checklist:**
- [x] All tests pass (47/47, no regressions)
- [x] Linting clean
- [x] Complexity reasonable (2)
- [x] Follows existing Flask route pattern
- [x] Documentation added (docstrings)
- [x] Edge cases handled
- [x] Error messages are clear
- [x] Security requirements met
- [x] No performance issues

**Checkpoint:** ✓ Production-ready, all validation criteria met

---

## Summary

**What Was Implemented:**
- GET /api/users/{id} endpoint in `api/routes.py`
- Extended UserSerializer with profile_picture_url field
- Comprehensive test suite (5 tests: happy path, 404, 401, edge cases)

**How It Was Tested:**
- Unit tests cover all response codes (200, 404, 401)
- Edge cases tested (null profile picture, invalid ID format)
- Integration tests verify auth middleware works
- Full regression suite passed (47/47 tests)

**Key Decisions:**
- Used existing Flask route pattern (consistency with codebase)
- Reused @require_auth decorator (DRY principle)
- Extended existing UserSerializer (minimal changes)
- Flask's <int:user_id> type converter handles invalid formats automatically
- Return profile_picture_url as URL, not binary data (performance)

**Integration Points:**
- Follows existing route structure in api/routes.py
- Uses existing User model from models/user.py
- Applies existing auth middleware from api/middleware.py
- Extends existing UserSerializer pattern

**Notes:**
- Endpoint follows RESTful conventions (GET /api/users/{id})
- Error responses include helpful messages for debugging
- Authentication enforced consistently with other endpoints
- Can be extended later for PATCH/DELETE operations

---

## Learnings

**What Worked Well:**
- Finding existing route pattern made implementation straightforward
- Reusing auth decorator ensured consistent security
- Flask's type converters eliminated need for manual validation
- Test fixtures reduced duplication in test setup

**What to Remember:**
- Always search for existing patterns first (found route, serializer, auth patterns)
- Security middleware should be applied consistently across endpoints
- RESTful conventions make API predictable and easy to use
- Error messages should be helpful but not expose sensitive details
- Testing authentication separately from business logic keeps tests focused

**Pattern Recognition:**
This follows a common REST API pattern:
1. **Route decorator** defines HTTP method and path
2. **Auth decorator** enforces security requirements
3. **Query model** retrieves data from database
4. **Serialize** transforms model to JSON-compatible format
5. **Return** with appropriate status code

This pattern can be reused for other entity endpoints (orders, products, etc.)
