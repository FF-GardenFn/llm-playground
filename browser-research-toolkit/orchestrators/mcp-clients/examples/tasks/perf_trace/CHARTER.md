# === BROWSER CELL CHARTER ===
task: "Performance profile: developers.chrome.com"
created: "2025-10-06T20:46:55"
risk_mode: "ask-before-acting"
allowed_domains:
  - developers.chrome.com/*
  - web.dev/*
forbidden_actions:
  - login
  - financial_tx
  - cookie_consent_beyond_reject
stop_conditions:
  - "permission stalled > 60s"
  - "domain not in allowed_domains"
outputs:
  - doc: "Perf profile — Charter & Synthesis"
  - sheet: "Perf_profile_table"
acceptance:
  triage: "≥ 6 sources captured with URL + last-updated"
  harvest: "structured rows complete; contradictions flagged"
  synthesize: "Known/Unknown, ranked sources, 3 next actions with owners/dates"
notes: |
  Focus on Core Web Vitals, long tasks, network waterfalls, and CLS.
