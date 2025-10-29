# Context Gathering: Codebase Reconnaissance

**Purpose**: Systematic discovery of codebase structure, patterns, and conventions before task decomposition

---

## Core Objective

Gather essential context to inform:
- Task decomposition strategies
- Specialist assignment decisions
- Integration and merge planning
- Risk identification

**Goal**: Understand "what already exists" to make informed orchestration decisions

---

## Context Categories

### Category 1: Codebase Structure

**What to Discover**:
- Directory organization (where is code located?)
- Module boundaries (how is code organized?)
- Entry points (main files, initialization)
- Configuration files (settings, environment)

**Discovery Methods**:
```bash
# High-level structure
ls -la /path/to/project
tree -L 2 /path/to/project

# Find specific file types
find . -name "*.py" | head -20
find . -name "*.js" | head -20
find . -name "*.json" | grep -E "(config|package)"

# Identify main entry points
grep -r "if __name__ == '__main__'" --include="*.py"
grep -r "app.listen" --include="*.js"
```

**Example Findings**:
```
Project: flask-api
Structure:
  /app
    /models      → Database models
    /routes      → API endpoints
    /services    → Business logic
    /utils       → Helper functions
  /tests         → Test suite
  /migrations    → Database migrations
  /config        → Configuration files

Entry point: app.py (Flask application)
Config: config.py (environment-based configuration)
```

---

### Category 2: Existing Patterns and Conventions

**What to Discover**:
- Code organization patterns (MVC? Layered? Modular?)
- Naming conventions (camelCase? snake_case? Prefixes?)
- Testing patterns (pytest? unittest? Jest?)
- Error handling patterns (exceptions? error codes?)
- Documentation style (docstrings? JSDoc? inline comments?)

**Discovery Methods**:
```bash
# Naming patterns
ls app/routes/  # Check file naming
grep -r "class " --include="*.py" | head -10  # Class naming

# Testing patterns
find . -name "test_*.py" | head -5
find . -name "*.test.js" | head -5
cat tests/test_auth.py  # Examine test structure

# Error handling patterns
grep -r "raise " --include="*.py" | head -10
grep -r "try:" --include="*.py" -A 5 | head -20

# Documentation style
grep -r '"""' --include="*.py" | head -5  # Python docstrings
grep -r "/**" --include="*.js" | head -5  # JSDoc comments
```

**Example Findings**:
```
Patterns Observed:
  - Naming: snake_case for Python, camelCase for JavaScript
  - Testing: pytest with fixtures, ~80% coverage
  - Error handling: Custom exceptions (AuthenticationError, ValidationError)
  - Documentation: Google-style docstrings, type hints
  - Code organization: Blueprint-based routing (Flask)
  - Database: SQLAlchemy ORM, Alembic migrations
```

---

### Category 3: Dependencies and Integrations

**What to Discover**:
- External libraries (packages, dependencies)
- API integrations (third-party services)
- Database connections (PostgreSQL? MySQL? MongoDB?)
- Message queues (Redis? RabbitMQ?)
- Authentication providers (OAuth? SAML?)

**Discovery Methods**:
```bash
# Python dependencies
cat requirements.txt
cat pyproject.toml
poetry show  # If using Poetry

# JavaScript dependencies
cat package.json
npm ls --depth=0

# Database connections
grep -r "DATABASE_URL" --include="*.py" --include="*.js"
grep -r "connect(" --include="*.py"

# External API usage
grep -r "requests.get\|requests.post" --include="*.py"
grep -r "axios\|fetch" --include="*.js"
```

**Example Findings**:
```
Dependencies:
  Core:
    - Flask 2.3.0 (web framework)
    - SQLAlchemy 2.0.0 (ORM)
    - psycopg2 2.9.0 (PostgreSQL driver)

  Authentication:
    - PyJWT 2.8.0 (JWT tokens)
    - bcrypt 4.0.0 (password hashing)

  External Integrations:
    - Stripe API (payments)
    - SendGrid (email)
    - Redis (caching, rate limiting)

Database: PostgreSQL 14 (connection pooling via PGBouncer)
```

---

### Category 4: Related Work and History

**What to Discover**:
- Similar features already implemented
- Recent changes (git history)
- Open issues or TODOs
- Migration history (database changes)
- Deprecation notices

**Discovery Methods**:
```bash
# Recent changes
git log --oneline --since="1 month ago" | head -20
git log --grep="auth" --oneline | head -10

# TODO markers
grep -r "TODO\|FIXME\|HACK" --include="*.py" --include="*.js"

# Similar implementations
find . -name "*auth*" -type f
find . -name "*payment*" -type f

# Database migrations
ls -lt migrations/ | head -10
cat migrations/versions/latest_*.py
```

**Example Findings**:
```
Related Work:
  - Basic user model exists (app/models/user.py)
  - Password hashing implemented (uses bcrypt)
  - No authentication endpoints yet
  - User registration exists but not secured

Recent Changes:
  - [2 weeks ago] Added user roles (admin, user)
  - [1 week ago] Database migration: added user.last_login
  - [3 days ago] Fixed password validation bug

Open TODOs:
  - TODO: Add rate limiting to registration endpoint
  - FIXME: User model lacks email verification status
  - TODO: Implement password reset flow
```

---

### Category 5: Architecture and Design Decisions

**What to Discover**:
- Architectural patterns (monolith? microservices? layered?)
- Design documentation (ADRs? README?)
- Separation of concerns (how is logic organized?)
- Scalability considerations (caching? load balancing?)

**Discovery Methods**:
```bash
# Documentation
find . -name "README.md" -o -name "ARCHITECTURE.md"
find . -name "ADR*.md"  # Architecture Decision Records
cat docs/architecture.md

# Examine key files
cat app/__init__.py  # Application initialization
cat app/config.py    # Configuration structure
```

**Example Findings**:
```
Architecture:
  - Monolithic Flask application
  - Layered architecture:
    - Routes (presentation layer)
    - Services (business logic)
    - Models (data layer)

  - Blueprint-based routing (modular routes)
  - Factory pattern for app initialization
  - SQLAlchemy for database abstraction

Design Decisions:
  - Stateless API (JWT tokens, no sessions)
  - RESTful conventions (POST for mutations, GET for queries)
  - JSON response format (standardized error structure)
  - Environment-based configuration (dev, staging, prod)

Scalability:
  - Redis caching (frequently accessed data)
  - Database connection pooling (PGBouncer)
  - Async task queue (Celery + Redis)
```

---

## Context Gathering Workflow

**Step 1: High-Level Scan**
- Examine directory structure (where is code?)
- Identify entry points (how does it start?)
- Check configuration files (how is it configured?)
- Review README/documentation (what's documented?)

**Step 2: Pattern Discovery**
- Sample key files (how is code written?)
- Examine tests (how is code tested?)
- Check error handling (how are errors managed?)
- Review recent commits (what changed recently?)

**Step 3: Dependency Analysis**
- List external dependencies (what libraries?)
- Identify integrations (what external services?)
- Check database schema (what data structure?)
- Note authentication/authorization (how is security handled?)

**Step 4: Related Work Identification**
- Search for similar features (what already exists?)
- Check TODO comments (what's planned?)
- Review open issues (what's broken or missing?)
- Examine migration history (how has it evolved?)

**Step 5: Architecture Understanding**
- Identify architectural patterns (how is it organized?)
- Review design decisions (why this approach?)
- Note scalability considerations (how does it scale?)
- Check separation of concerns (is logic well-organized?)

---

## Context Templates

### Template 1: Web Application Context

```
Application Type: [Flask / Django / Express / React / etc.]

Structure:
  - Entry point: [file path]
  - Routes/Endpoints: [directory]
  - Business logic: [directory]
  - Data models: [directory]
  - Tests: [directory]

Conventions:
  - Naming: [snake_case / camelCase / etc.]
  - Testing: [pytest / jest / etc.]
  - Error handling: [exceptions / error codes / etc.]
  - Documentation: [docstrings / JSDoc / etc.]

Dependencies:
  - Framework: [version]
  - Database: [type + driver]
  - Authentication: [library]
  - Key libraries: [list]

Patterns:
  - Architecture: [MVC / layered / microservices / etc.]
  - Routing: [Blueprint / Router / etc.]
  - Database: [ORM / raw SQL / query builder]
  - API style: [REST / GraphQL / RPC]

Recent Work:
  - [Recent feature 1]
  - [Recent feature 2]
  - [Recent bug fix]

TODOs:
  - [TODO 1]
  - [TODO 2]
```

---

### Template 2: Data Pipeline Context

```
Pipeline Type: [ETL / Stream processing / Batch / etc.]

Structure:
  - Data sources: [databases / APIs / files]
  - Processing steps: [directory]
  - Output destinations: [database / S3 / etc.]
  - Orchestration: [Airflow / Luigi / cron / etc.]

Data Format:
  - Input: [CSV / JSON / Parquet / etc.]
  - Intermediate: [format]
  - Output: [format]

Dependencies:
  - Processing: [pandas / Spark / Dask / etc.]
  - Storage: [S3 / GCS / etc.]
  - Orchestration: [tool + version]

Conventions:
  - Naming: [pipeline / task naming patterns]
  - Testing: [unit tests / integration tests]
  - Monitoring: [logging / metrics / alerts]

Data Quality:
  - Validation: [schema validation / data quality checks]
  - Error handling: [retry logic / dead letter queue]
  - Monitoring: [data freshness / completeness]
```

---

### Template 3: ML Project Context

```
ML Task: [Classification / Regression / Clustering / etc.]

Structure:
  - Data: [directory for raw / processed data]
  - Models: [model definitions]
  - Training: [training scripts]
  - Evaluation: [evaluation notebooks]
  - Deployment: [serving / inference]

Data Pipeline:
  - Data source: [location]
  - Feature engineering: [approach]
  - Train/test split: [method + ratio]
  - Validation: [k-fold / holdout / etc.]

Models:
  - Framework: [TensorFlow / PyTorch / scikit-learn / etc.]
  - Model types: [architectures used]
  - Hyperparameters: [tracking method]
  - Versioning: [MLflow / DVC / etc.]

Conventions:
  - Experiment tracking: [tool]
  - Model registry: [tool]
  - Reproducibility: [seeds / requirements / docker]
  - Evaluation metrics: [accuracy / F1 / AUC / etc.]
```

---

## Risk Identification from Context

**Security Risks**:
- Missing authentication (unprotected endpoints)
- SQL injection vulnerabilities (raw SQL queries)
- XSS vulnerabilities (unescaped user input)
- Exposed secrets (hard-coded credentials)

**Integration Risks**:
- Breaking existing patterns (inconsistent with conventions)
- Database migration conflicts (concurrent schema changes)
- API compatibility issues (breaking changes)
- Dependency conflicts (version incompatibilities)

**Performance Risks**:
- N+1 query patterns (ORM misuse)
- Missing indexes (slow queries)
- Memory leaks (resource cleanup)
- Blocking operations (synchronous I/O)

**Maintainability Risks**:
- Inconsistent patterns (multiple approaches for same problem)
- Missing tests (low coverage areas)
- Poor separation of concerns (tangled code)
- Outdated documentation (code-doc mismatch)

---

## Context-Informed Decomposition

**Context influences decomposition strategy**:

**If codebase uses Blueprint pattern**:
→ Decompose by route/module (aligns with existing structure)

**If codebase has strong layer separation**:
→ Decompose by layer (models → services → routes)

**If codebase has established test patterns**:
→ Include test tasks matching existing patterns

**If codebase has migration system**:
→ Include database migration tasks

**If codebase uses specific frameworks/libraries**:
→ Assign specialists familiar with those tools

---

## Output Format

**Context Report**:
```
Codebase: [project name]

Structure:
  - [key directories and their purposes]

Entry Points:
  - [main application files]

Conventions:
  - Naming: [patterns]
  - Testing: [frameworks + patterns]
  - Error handling: [approach]
  - Documentation: [style]

Dependencies:
  - Framework: [name + version]
  - Database: [type + version]
  - Key libraries: [list with versions]

Patterns:
  - Architecture: [pattern]
  - Database: [ORM / query approach]
  - API: [REST / GraphQL / etc.]
  - Authentication: [approach]

Related Work:
  - [Similar features already implemented]
  - [Recent relevant changes]
  - [Open TODOs in related areas]

Risks Identified:
  - [Security risks]
  - [Integration risks]
  - [Performance risks]
  - [Maintainability risks]

Recommendations:
  - [Decomposition approach based on structure]
  - [Specialist assignments based on tech stack]
  - [Integration considerations based on patterns]
```

---

## Integration with Task Decomposition

Once context gathered:
- Use structure to inform decomposition strategy
- Use conventions to set specialist boundaries
- Use dependencies to identify integration points
- Use related work to avoid duplication
- Use risks to plan mitigation

Context gathering enables intelligent decomposition and assignment.
