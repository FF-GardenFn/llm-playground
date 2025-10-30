---
description: Clarify ambiguous requirements before task decomposition (Orchestration Phase 1)
allowed-tools: Read, Write, TodoWrite, AskUserQuestion
argument-hint: [user-request]
---

# Reconnaissance Command

Execute Phase 1 orchestration: clarify ambiguous requirements, gather context, assess feasibility.

## What this does

1. **Detects ambiguity** in user request (under-specified, conflicting constraints)
2. **Gathers context** (codebase structure, existing patterns, conventions)
3. **Assesses feasibility** (complexity estimation, resource availability, risks)
4. **Asks clarifying questions** to resolve ambiguity
5. **Produces clear, well-scoped request** with measurable success criteria

## Usage

```bash
# Start orchestration with user request
/reconnaissance "Add user authentication with JWT tokens to API"

# Resume reconnaissance after user answers questions
/reconnaissance --continue
```

## Your Task

1. **Load reconnaissance workflow**: Read `reconnaissance/request-analysis.md`
2. **Detect ambiguity**: Check for under-specification, conflicting constraints
3. **Generate clarifying questions**: Use `reconnaissance/clarification/clarifying-questions.md`
4. **Ask user**: Use AskUserQuestion tool if ambiguity detected
5. **Gather context**: Read codebase structure, existing patterns
6. **Assess feasibility**: Complexity estimation, risk identification
7. **Complete gate**: `reconnaissance/GATE-REQUIREMENTS-CLEAR.md`
8. **Report**: Clear request with scope, success criteria, constraints

## Expected Output

```
OK Reconnaissance complete

Clear Request:
- Feature: JWT-based authentication (login, token generation, refresh, rate limiting)
- Constraints: Use bcrypt (12 rounds), stateless tokens, 5 attempts/min rate limit
- Success Criteria: Tests pass, tokens validate correctly, rate limiting functional
- Scope: Backend API only (4 endpoints: login, refresh, validate, logout)
- Out of Scope: Frontend UI, social auth, password reset

Context Gathered:
- Codebase: Flask API, PostgreSQL database
- Existing patterns: RESTful endpoints, JSON responses, Blueprint structure
- Dependencies: No conflicting auth system

Feasibility: HIGH (standard implementation, 8-12 hours)
Risks: LOW (well-established patterns)

-> Recommend: /decompose to break into parallelizable tasks
```

## Gate

**Cannot proceed to /decompose without**:
- [ ] All ambiguities resolved
- [ ] Success criteria specific and measurable
- [ ] Constraints identified
- [ ] Scope boundaries clear
