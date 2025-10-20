TASK CHARTER Schema

Fields
- task: string — human-readable title for the research cell.
- created: ISO8601 timestamp — creation time.
- risk_mode: enum {"ask-before-acting", "always-allow-listed"} — permission posture.
- allowed_domains: list<string> — strict allowlist for navigation.
- forbidden_actions: list<string> — guardrails (e.g., login, financial_tx).
- stop_conditions: list<string> — hard stops (e.g., domain outside allowlist).
- outputs: list — one or more outputs, typically { doc: <name> } and optional { sheet: <name> }.
- review_protocol: multiline string — evidence standards and audit notes.
- notes: multiline string — focus areas, scoping guidance.

Acceptance Criteria
- Every claim in the doc has a source URL and last-updated date.
- No actions outside allowed_domains.
- User confirms before any irreversible action (default).
