# === TASK CHARTER (Paste in first tab doc) ===

task: "Audit Stripe API migration"
created: "2025-10-06T15:48:00"
risk_mode: "ask-before-acting"
allowed_domains:
  - stripe.com/docs
  - github.com/stripe/*
forbidden_actions:
  - login
  - financial_tx
  - cookie_consent_beyond_reject
stop_conditions:
  - "permission stalled > 60s"
  - "domain not in allowed_domains"
outputs:
  - doc: "audit_stripe_api_migration — Charter & Synthesis"
  - sheet: "audit_stripe_api_migration_table"
review_protocol: |
  - All findings must be written into the doc above.
  - Cite source URL + last-updated date for every claim.
  - Ask before creating any files or sheets.
notes: |
  - Focus on versioning, rate limits, auth changes, deprecations, migration timelines.
