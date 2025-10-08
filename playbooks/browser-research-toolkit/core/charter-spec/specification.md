# Charter Specification

## Overview

A Charter is a declarative contract that governs the execution of a browser-based research task. It establishes scope boundaries, safety constraints, and acceptance criteria before any automated action occurs.

## Purpose

The Charter serves three functions:

1. **Scope definition**: Explicitly enumerate allowed domains and forbidden actions
2. **Safety enforcement**: Establish risk mode and stop conditions
3. **Quality assurance**: Define acceptance criteria for each workflow phase

## Structure

### Required Fields

**task** (string)
: A concise statement of the research objective.

**risk_mode** (enum: "ask-before-acting" | "always-allow-listed")
: Determines whether the agent must request approval before each action or may proceed autonomously within the allowlist.

**allowed_domains** (array of strings)
: Exhaustive list of permitted web domains. Glob patterns supported (e.g., `github.com/stripe/*`).

**outputs** (array of objects)
: Specification of where synthesized results will be written. Typically includes a shared document and optional spreadsheet.

### Optional Fields

**forbidden_actions** (array of strings)
: Explicit prohibitions (e.g., `login`, `financial_tx`, `cookie_consent_beyond_reject`).

**stop_conditions** (array of strings)
: Conditions that should halt execution (e.g., `permission stalled > 60s`, `domain not in allowed_domains`).

**acceptance** (object)
: Phase-specific completion criteria (e.g., `triage: "≥ 6 sources captured with URL + last-updated"`).

**notes** (string)
: Additional context or constraints for the research task.

## Example

```yaml
task: "Audit Stripe API migration path"
created: "2025-10-06T14:30:00"
risk_mode: "ask-before-acting"
allowed_domains:
  - stripe.com/docs
  - github.com/stripe/*
forbidden_actions:
  - login
  - financial_tx
stop_conditions:
  - "permission stalled > 60s"
  - "domain not in allowed_domains"
outputs:
  - doc: "Stripe_API_Audit — Charter & Synthesis"
  - sheet: "Stripe_API_Audit_table"
acceptance:
  triage: "≥ 6 sources captured with URL + last-updated"
  harvest: "structured rows complete; contradictions flagged"
  synthesize: "Known/Unknown, ranked sources, 3 next actions with owners/dates"
notes: |
  Focus on authentication changes, rate limit modifications, and deprecation timelines.
```

## Validation

A valid Charter must satisfy:

1. All required fields present
2. `risk_mode` is one of the enumerated values
3. `allowed_domains` contains at least one entry
4. `outputs` specifies at least one sink
5. If `acceptance` is provided, it includes criteria for each intended workflow phase

## Usage Patterns

### Chrome Extension Runtime

The Charter is pasted into a shared document in the first tab of a Chrome tab group. The agent reads it via the Claude for Chrome extension and follows its constraints throughout execution.

### MCP Client Runtime

The Charter is embedded in a shared document accessible to the MCP client. The agent reads it via the chrome-devtools-mcp server and adheres to its boundaries while using browser automation tools.

## Design Rationale

The Charter model enforces explicit scoping rather than implicit trust. By requiring upfront declaration of allowed domains and forbidden actions, it reduces the risk of unintended behavior during autonomous execution. The separation of scope (allowlist) from execution mode (risk_mode) enables fine-grained control appropriate to the task's sensitivity.
