# Example: User Profile Feature

## Scenario

**User Request**: "Add a user profile page where users can view and edit their name, email, and profile picture."

**Complexity**: Simple-Moderate
**Estimated Sequential Time**: 6 hours
**Actual Parallel Time**: 2.5 hours
**Efficiency Gain**: 58%

---

## Phase 1: Reconnaissance (20 minutes)

### Request Analysis

```markdown
## Initial Understanding

**Core Request:** User profile page with view/edit capabilities

**Immediate Questions:**
- What fields beyond name, email, photo?
- Edit inline or separate form?
- Photo upload limits?
- Email change requires verification?
```

### Clarifying Questions

```markdown
## Asked User:

1. Should email changes require re-verification?
   → Answer: Yes, send verification email

2. Profile picture size/format limits?
   → Answer: Max 5MB, JPG/PNG only

3. Can users delete their profile picture?
   → Answer: Yes, revert to default avatar

4. Any other profile fields needed?
   → Answer: No, just name, email, picture for now
```

### Success Criteria Defined

```markdown
## Success Criteria

1. **Display Profile:**
   - Shows current name, email, profile picture
   - Profile picture defaults to avatar if none uploaded
   - Loads in <300ms

2. **Edit Name:**
   - Inline editing or edit form
   - Name: 1-100 characters
   - Saves and displays updated name

3. **Edit Email:**
   - Validates email format
   - Sends verification email to new address
   - Updates only after verification
   - Old email works until verified

4. **Upload Profile Picture:**
   - Accept JPG/PNG <5MB
   - Preview before save
   - Crop/resize UI (nice-to-have)
   - Can delete and revert to default

5. **Error Handling:**
   - Network errors show retry
   - Validation errors highlight fields
   - Upload errors explain issue

6. **Security:**
   - Users can only edit own profile
   - Email verification prevents takeover
   - File upload validated server-side
```

### Feasibility Assessment

```markdown
## Feasibility: HIGH ✓

**Complexity:** Simple-Moderate
- Standard CRUD operations
- Established patterns available
- No novel technical challenges

**Resources:**
- Frontend: React components (2 hours)
- Backend: API endpoints (1.5 hours)
- Database: Schema update (30 min)

**Risks:** LOW
- Well-understood domain
- Clear requirements
- No external dependencies

**Verdict:** Proceed with confidence
```

### Gate Check: ✅ REQUIREMENTS CLEAR

```markdown
- [✓] Success criteria defined
- [✓] Constraints identified
- [✓] Ambiguities resolved
- [✓] Assumptions documented
- [✓] Scope boundaries set
```

---

## Phase 2: Decomposition (15 minutes)

### Task Breakdown

```markdown
## Task Structure

**Foundation (Sequential):**
Task 1: Database schema for profile pictures (30 min)
  - Add profile_picture_url column
  - Add email_verification_token column
  - Add email_verification_expires column

**Parallel Layer 1 (After Task 1):**
Task 2: Profile API endpoints (1 hour)
  - GET /api/profile
  - PUT /api/profile/name
  - PUT /api/profile/email
  - POST /api/profile/picture
  - DELETE /api/profile/picture

Task 3: Email verification service (45 min)
  - Generate verification tokens
  - Send verification emails
  - Verify token endpoint

**Parallel Layer 2 (After Tasks 2, 3):**
Task 4: Profile page UI component (1 hour)
  - Display current profile
  - Inline name editing
  - Email change form
  - Profile picture upload UI

Task 5: Integration tests (45 min)
  - Profile CRUD operations
  - Email verification flow
  - Picture upload/delete
  - Error scenarios
```

### Dependency Graph

```
       Task 1 (DB Schema)
       30 min
           │
     ┌─────┴─────┐
     ↓           ↓
  Task 2       Task 3
  (API)        (Email)
  1 hour       45 min
     │            │
     └─────┬──────┘
           ↓
  ┌────────┴────────┐
  ↓                 ↓
Task 4            Task 5
(Frontend)        (Tests)
1 hour            45 min

Sequential Time: 4.25 hours
Parallel Time: 2.5 hours
Efficiency: 41% parallel
```

### Integration Strategy

```markdown
## Integration Plan

**Phase 1: Backend Integration**
1. Apply database migration (Task 1)
2. Integrate API endpoints (Task 2) + Email service (Task 3)
3. Test API independently

**Phase 2: Full Integration**
1. Connect frontend (Task 4) to backend
2. Run integration tests (Task 5)
3. Fix any interface issues

**Merge Order:**
1. Task 1 (foundation)
2. Tasks 2 & 3 (parallel backend)
3. Task 4 (frontend)
4. Task 5 (validation)
```

### Gate Check: ✅ TASKS DECOMPOSED

```markdown
- [✓] Optimal granularity (30-60 min each)
- [✓] Natural boundaries
- [✓] Dependencies explicit
- [✓] Parallelization identified
- [✓] Integration strategy clear
```

---

## Phase 3: Delegation (10 minutes)

### Specialist Assignment

```markdown
## Task Assignments

**Task 1: Database Schema**
Specialist: Database Specialist
Duration: 30 minutes

Context Provided:
---
## Task: Add Profile Picture Support to Database

### Objective
Extend users table to support profile pictures and email verification.

### Schema Changes
```sql
ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(500);
ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(100);
ALTER TABLE users ADD COLUMN email_verification_expires TIMESTAMP;
```

### Success Criteria
- [✓] Migration created and tested
- [✓] Rollback migration provided
- [✓] No data loss for existing users
- [✓] Indexes added if needed

### Constraints
- Must not break existing user queries
- Must be backwards compatible
---

**Task 2: Profile API Endpoints**
Specialist: Code Generator
Duration: 1 hour

Context Provided:
---
## Task: Implement Profile API Endpoints

### Objective
Create REST API for profile management.

### Endpoints Required
```
GET /api/profile
  Response: { name, email, profilePictureUrl }

PUT /api/profile/name
  Body: { name: string }
  Response: { success: true, name: string }

PUT /api/profile/email
  Body: { email: string }
  Response: { success: true, message: "Verification email sent" }

POST /api/profile/picture
  Body: multipart/form-data (image file)
  Response: { success: true, pictureUrl: string }

DELETE /api/profile/picture
  Response: { success: true }
```

### Success Criteria
- [✓] All endpoints implemented
- [✓] Authentication required
- [✓] Validation on all inputs
- [✓] Unit tests for each endpoint

### Integration
- Depends on: Task 1 (schema)
- Used by: Task 4 (frontend)
---

[Similar detailed contexts for Tasks 3, 4, 5...]
```

### Gate Check: ✅ SPECIALISTS ASSIGNED

```markdown
- [✓] Optimal specialist-task matching
- [✓] Complete context provided
- [✓] Clear success criteria
- [✓] Integration points specified
```

---

## Phase 4: Coordination (During Execution)

### Timeline

```
Time 0:00 - Task 1 starts (Database Specialist)
    ↓
Time 0:30 - Task 1 complete ✓
            Tasks 2 & 3 start in parallel
            - Task 2: Code Generator (API)
            - Task 3: Code Generator (Email)
    ↓
Time 1:15 - Task 3 complete ✓ (Email service)
Time 1:30 - Task 2 complete ✓ (API endpoints)
            Backend integration check
    ↓
Time 1:40 - Backend integration verified
            Tasks 4 & 5 start in parallel
            - Task 4: React Architect (Frontend)
            - Task 5: Code Generator (Tests)
    ↓
Time 2:25 - Task 5 complete ✓ (Tests ready)
Time 2:40 - Task 4 complete ✓ (Frontend)
    ↓
Time 2:50 - Full integration and testing
```

### Progress Tracking

```
t=0:30  Task 1 ████████████████████ 100% ✓
        Task 2 ░░░░░░░░░░░░░░░░░░░░   0%
        Task 3 ░░░░░░░░░░░░░░░░░░░░   0%

t=1:00  Task 2 ███████████░░░░░░░░░  60%
        Task 3 ██████████████░░░░░░  80%

t=1:30  Task 2 ████████████████████ 100% ✓
        Task 3 ████████████████████ 100% ✓
        Backend Integration ██░░░░   20%

t=1:40  Backend Integration ████ 100% ✓
        Task 4 ░░░░░░░░░░░░░░░░░░░░   0%
        Task 5 ░░░░░░░░░░░░░░░░░░░░   0%

t=2:20  Task 4 ██████████████████░░  90%
        Task 5 ████████████████████ 100% ✓

t=2:40  Task 4 ████████████████████ 100% ✓

Total Time: 2:40 (vs 4:15 sequential)
```

### Issues Encountered

```markdown
## Issue at t=1:20

**Issue:** Task 2 specialist discovered email change needs to temporarily store pending email

**Resolution:**
- Quick consultation with Task 1 specialist
- Added pending_email column to migration
- Updated Task 2 context
- No timeline impact (within buffer)

**Lesson:** Consider pending states in initial schema design
```

### Gate Check: ✅ ALL COMPLETE

```markdown
- [✓] All tasks finished
- [✓] All outputs delivered
- [✓] No blockers remain
- [✓] Ready for integration
```

---

## Phase 5: Integration (10 minutes)

### Integration Steps

```markdown
## Step 1: Database Migration
- Applied migration from Task 1
- Verified schema changes
- No issues ✓

## Step 2: Backend Integration
- Integrated API endpoints (Task 2)
- Integrated email service (Task 3)
- Tested API independently
- All endpoints functional ✓

## Step 3: Frontend Connection
- Connected UI (Task 4) to API
- Verified all API calls work
- UI rendering correctly ✓

## Step 4: End-to-End Testing
- Ran integration tests (Task 5)
- All tests passing ✓
- Manual smoke testing ✓
```

### Conflicts Encountered

```markdown
## Conflict: None

Well-defined interfaces prevented conflicts.
All integrations smooth.
```

### Gate Check: ✅ VERIFIED

```markdown
- [✓] All outputs merged
- [✓] No conflicts
- [✓] Coherent solution
- [✓] Context preserved
```

---

## Phase 6: Verification (10 minutes)

### Success Criteria Validation

```markdown
## Validation Results

**1. Display Profile:** ✓ PASS
- Shows name, email, picture correctly
- Defaults to avatar when no picture
- Loads in 180ms (target: 300ms)

**2. Edit Name:** ✓ PASS
- Inline editing works
- Validation: 1-100 characters enforced
- Updates display immediately

**3. Edit Email:** ✓ PASS
- Format validation working
- Verification email sends
- Old email works until verified
- New email activates after verification

**4. Upload Profile Picture:** ✓ PASS
- Accepts JPG/PNG <5MB
- Preview shows before save
- Upload succeeds
- Delete reverts to default

**5. Error Handling:** ✓ PASS
- Network errors show retry
- Validation highlights fields
- Upload errors clear

**6. Security:** ✓ PASS
- Authorization verified (users can't edit others)
- Email verification prevents account takeover
- File upload validated server-side
- SQL injection prevented

**Final Verdict: ALL CRITERIA MET ✓**
```

### Quality Metrics

```markdown
## Quality Assessment

**Code Quality:**
- Test coverage: 87% ✓
- Linter: 0 issues ✓
- Code review: Approved ✓

**Performance:**
- Profile load: 180ms ✓
- Name update: 120ms ✓
- Picture upload: 2.3s (5MB image) ✓

**Security:**
- Auth checks: Present ✓
- Input validation: Comprehensive ✓
- File upload: Sanitized ✓
```

---

## Orchestration Analysis

### Efficiency Metrics

```markdown
## Time Analysis

Sequential Estimate: 4.25 hours
Actual Parallel Time: 2.67 hours
Efficiency Gain: 37%

Specialist Utilization:
- Database Specialist: 30 min (100% utilized)
- Code Generator #1: 1.75 hours (92% utilized)
- Code Generator #2: 1.75 hours (88% utilized)

Total Person-Hours: 4.0 hours
Wall-Clock Time: 2.67 hours
Parallelization: 40% of work done in parallel
```

### Quality Outcome

```markdown
## Orchestration Quality Score: 88/100 (EXCELLENT)

**Efficiency: 17/20**
- Parallelization: 40% (target: 50%) → 8/10
- Specialist utilization: 93% → 9/10

**Clarity: 19/20**
- Zero clarification requests → 10/10
- No rework needed → 9/10

**Completeness: 20/20**
- 100% requirements satisfied → 10/10
- All success criteria met → 10/10

**Quality: 18/20**
- Test coverage 87% → 9/10
- Code quality excellent → 9/10

**Coherence: 14/20**
- Smooth integration → 8/10
- Consistent patterns → 6/10 (minor style variations)
```

### Lessons Learned

```markdown
## What Went Well
- Clear interface definitions prevented conflicts
- Parallel execution saved significant time
- Detailed success criteria ensured completeness

## What Could Improve
- Initial schema could have included pending_email
- Could have achieved 50%+ parallelization with better decomposition
- Style guide should be more explicit

## Patterns to Reuse
- Database schema first, then parallel development
- Email verification pattern
- Profile picture upload handling
```

---

*This example demonstrates orchestration of a simple feature. The key was clear requirements, optimal decomposition, and parallel execution. Result: Feature delivered in 63% of sequential time with high quality.*
