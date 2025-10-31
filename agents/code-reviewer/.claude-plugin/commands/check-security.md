---
description: Security-focused code review against OWASP Top 10 and secure coding practices
allowed-tools: Read, Write, AskUserQuestion
argument-hint: [paths...]
---

# Security-Focused Code Review

Security-focused review scanning for vulnerabilities, compliance issues, and attack vectors. Validates against OWASP Top 10 (2021) and secure coding practices.

## Security Review Focus

Complete security workflow:
→ Load {{load: ../workflows/review-process.md#security}}

---

## OWASP Top 10 Checklist

When security scanning:
  → Load {{load: ../security/owasp-checklist.md}}

**Auto-load triggers by category**:
- Access control issues detected → {{load: ../security/owasp-checklist.md#A01}}
- Crypto failures detected → {{load: ../security/owasp-checklist.md#A02}}
- Injection vulnerabilities detected → {{load: ../security/owasp-checklist.md#A03}}
- Insecure design detected → {{load: ../security/owasp-checklist.md#A04}}
- Misconfiguration detected → {{load: ../security/owasp-checklist.md#A05}}
- Vulnerable components detected → {{load: ../security/owasp-checklist.md#A06}}
- Auth failures detected → {{load: ../security/owasp-checklist.md#A07}}
- Integrity failures detected → {{load: ../security/owasp-checklist.md#A08}}
- Logging failures detected → {{load: ../security/owasp-checklist.md#A09}}
- SSRF detected → {{load: ../security/owasp-checklist.md#A10}}

---

## Input Validation

When injection vulnerabilities suspected:
  → Load {{load: ../security/input-validation.md}}

**Covers**: SQL injection, XSS, command injection detection patterns

---

## Detection Patterns

When scanning code for vulnerabilities:
  → Load {{load: ../security/detection-heuristics.md}}

**Heuristics**: Red flags vs safe patterns for common vulnerabilities

---

## Vulnerability Database

When analyzing dependencies:
  → Load {{load: ../security/vulnerabilities.md}}

**Check**: CVEs, outdated packages, known vulnerabilities

---

## Output Format

Use format from {{load: ../feedback/format.md}} with security-specific sections:
- Executive summary (security status)
- Critical vulnerabilities (fix immediately)
- Important vulnerabilities (address soon)
- Security suggestions (best practices)
- OWASP Top 10 compliance assessment
- Recommended actions

---

## Security Focus Areas

**Priority checks**:
1. **Injection**: SQL injection (parameterized queries), XSS (escaping), command injection
2. **Authentication**: Password hashing (bcrypt), session management, MFA
3. **Authorization**: Access control, privilege escalation
4. **Data Protection**: Encryption at rest/transit, secrets management
5. **Logging**: Security events, sensitive data exclusion

---

## Start Security Review

Ask user: "What code would you like me to review for security vulnerabilities? Please provide file paths or paste code."
