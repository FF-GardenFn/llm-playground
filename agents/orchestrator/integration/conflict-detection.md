# Conflict Detection: Identifying Integration Issues

**Purpose**: Systematic detection of conflicts before and during integration

---

## Conflict Categories

### 1. File Conflicts

**Definition**: Multiple specialists modify same file

**Detection**:
```python
def detect_file_conflicts(task_outputs):
    """Detect if multiple tasks modified same files."""
    file_map = {}  # file -> list of tasks that modified it

    for task_id, outputs in task_outputs.items():
        for file_path in outputs['modified_files']:
            if file_path not in file_map:
                file_map[file_path] = []
            file_map[file_path].append(task_id)

    conflicts = {f: tasks for f, tasks in file_map.items() if len(tasks) > 1}
    return conflicts
```

**Example**:
```
Task C: Modified app/routes/auth.py (added login endpoint)
Task D: Modified app/routes/auth.py (added refresh endpoint)
→ Conflict: Both modified same file
```

**Resolution**: See integration/merge-strategies.md

---

### 2. Semantic Conflicts

**Definition**: Incompatible logical changes (even if different files)

**Detection Patterns**:

**Pattern 1: API Contract Mismatch**:
```
Backend returns: { "token": "...", "expiry": "..." }
Frontend expects: { "access_token": "...", "expires_at": "..." }
→ Semantic conflict: Field name mismatch
```

**Pattern 2: Behavior Inconsistency**:
```
Component A: Expects authentication required
Component B: Implements optional authentication
→ Semantic conflict: Incompatible assumptions
```

**Pattern 3: Data Format Incompatibility**:
```
Module A: Writes dates as "YYYY-MM-DD"
Module B: Reads dates as "MM/DD/YYYY"
→ Semantic conflict: Format mismatch
```

**Detection**:
```python
def detect_semantic_conflicts(task_outputs):
    """Detect logical incompatibilities."""
    conflicts = []

    # Check API contracts
    for t1, t2 in combinations(task_outputs, 2):
        if produces_api(t1) and consumes_api(t2):
            if not contracts_compatible(t1.contract, t2.contract):
                conflicts.append(('api_mismatch', t1, t2))

    # Check data formats
    for t1, t2 in combinations(task_outputs, 2):
        if writes_data(t1) and reads_data(t2):
            if not formats_compatible(t1.format, t2.format):
                conflicts.append(('format_mismatch', t1, t2))

    return conflicts
```

---

### 3. Dependency Conflicts

**Definition**: Version or library incompatibilities

**Examples**:
```
Task A adds: Flask==2.3.0
Task B adds: Flask==3.0.0
→ Conflict: Different versions

Task A adds: requests==2.28.0
Task B adds: urllib3==2.0.0 (incompatible with requests 2.28.0)
→ Conflict: Transitive dependency incompatibility
```

**Detection**:
```python
def detect_dependency_conflicts(task_outputs):
    """Detect dependency version conflicts."""
    dependencies = {}  # package -> {task: version}

    for task_id, outputs in task_outputs.items():
        for package, version in outputs.get('dependencies', {}).items():
            if package not in dependencies:
                dependencies[package] = {}
            dependencies[package][task_id] = version

    # Find packages with multiple versions
    conflicts = {}
    for package, versions in dependencies.items():
        unique_versions = set(versions.values())
        if len(unique_versions) > 1:
            conflicts[package] = versions

    return conflicts
```

---

### 4. Database Schema Conflicts

**Definition**: Incompatible database changes

**Examples**:
```
Task A: ALTER TABLE users ADD COLUMN last_login TIMESTAMP
Task B: ALTER TABLE users ADD COLUMN email_verified BOOLEAN
→ Both modify same table (resolvable)

Task A: ALTER TABLE users DROP COLUMN email
Task B: Uses users.email in query
→ Conflict: B depends on column A removes
```

**Detection**:
```python
def detect_schema_conflicts(migrations):
    """Detect database schema conflicts."""
    conflicts = []

    # Check for conflicting table modifications
    table_changes = {}  # table -> list of migrations
    for migration in migrations:
        for table in migration.affected_tables:
            if table not in table_changes:
                table_changes[table] = []
            table_changes[table].append(migration)

    # Check for DROP followed by USE
    for m1, m2 in combinations(migrations, 2):
        if m1.drops_column(col) and m2.uses_column(col):
            conflicts.append(('drop_then_use', m1, m2))

    return conflicts
```

---

### 5. Performance Conflicts

**Definition**: Optimizations that conflict

**Examples**:
```
Task A: Adds caching (optimizes for speed)
Task B: Adds real-time updates (requires fresh data)
→ Conflict: Caching defeats real-time updates

Task A: Normalizes database (optimizes for storage)
Task B: Denormalizes same data (optimizes for queries)
→ Conflict: Incompatible optimization strategies
```

**Detection**: Often requires manual review

---

## Detection Timing

### Early Detection (Before Execution)

**During Decomposition**:
```
Analyze planned tasks for potential conflicts:
- Multiple tasks modify same file? → Flag for resolution strategy
- Tasks have different API assumptions? → Define contract first
- Tasks use incompatible libraries? → Standardize dependencies
```

**Example**:
```
Planning phase detects:
  Task C and D both will modify app/routes/auth.py

Decision before execution:
  - Strategy: Serialize (C then D)
  - OR: Partition file into auth_login.py and auth_refresh.py

Execute with strategy in place (proactive)
```

---

### Late Detection (After Execution)

**During Integration**:
```
Collect outputs from all specialists
Run conflict detector:
  - File conflict check
  - Semantic conflict check
  - Dependency conflict check
  - Schema conflict check

Resolve detected conflicts before merging
```

**Example**:
```
Integration phase detects:
  Backend returns { "token": "..." }
  Frontend expects { "access_token": "..." }

Resolution:
  - Update backend to match frontend expectation
  - OR: Update frontend to match backend response
  - OR: Add adapter layer

Re-test after resolution
```

---

## Conflict Detection Checklist

**Before Execution** (Proactive):
- [ ] Identify file overlaps (multiple tasks → same file)
- [ ] Check API contract alignment (producer/consumer compatibility)
- [ ] Verify dependency compatibility (no version conflicts)
- [ ] Check schema change compatibility (no conflicting migrations)

**After Execution** (Reactive):
- [ ] Run file conflict detector
- [ ] Run semantic conflict detector
- [ ] Run dependency conflict detector
- [ ] Run schema conflict detector
- [ ] Run integration tests (catch runtime conflicts)

---

## Conflict Resolution Priority

**Critical** (Must resolve before merge):
- File conflicts (same lines modified)
- Breaking API changes (incompatible contracts)
- Dependency conflicts (version incompatibilities)
- Schema conflicts (destructive operations)

**Important** (Should resolve, can defer):
- Performance conflicts (optimization trade-offs)
- Code style conflicts (consistency issues)
- Documentation conflicts (minor inconsistencies)

**Nice-to-Have** (Can defer):
- Minor refactoring differences
- Comment style differences
- Whitespace differences

---

## Tools Integration

Use `atools/conflict_detector.py`:
```bash
# Detect file conflicts
python atools/conflict_detector.py --type file --outputs task_outputs.json

# Detect semantic conflicts
python atools/conflict_detector.py --type semantic --outputs task_outputs.json

# Detect dependency conflicts
python atools/conflict_detector.py --type dependency --outputs task_outputs.json

# Detect all conflicts
python atools/conflict_detector.py --all --outputs task_outputs.json
```

---

## Output Format

**Conflict Report**:
```
Conflicts Detected: 3

1. File Conflict
   File: app/routes/auth.py
   Tasks: C (login), D (refresh)
   Resolution: Serialize (C then D) or partition file

2. Semantic Conflict
   Type: API contract mismatch
   Task A: Returns { "token": "..." }
   Task B: Expects { "access_token": "..." }
   Resolution: Align contract (update A or B)

3. Dependency Conflict
   Package: Flask
   Task A: Flask==2.3.0
   Task B: Flask==3.0.0
   Resolution: Choose single version
```

---

## Summary

**Conflict Types**:
1. File conflicts (same file modified)
2. Semantic conflicts (logical incompatibilities)
3. Dependency conflicts (version mismatches)
4. Schema conflicts (database changes)
5. Performance conflicts (optimization trade-offs)

**Detection Timing**:
- Early (proactive, during planning)
- Late (reactive, during integration)

**Resolution**: See integration/merge-strategies.md

**Tools**: Use atools/conflict_detector.py for automated detection
