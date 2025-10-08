Benchmarking Guide

Metrics to track per run
- t_synth: time from /init-group to /synthesize completion (seconds)
- perm_prompts: number of permission prompts encountered
- wrong_tab_actions: count of actions taken in an incorrect tab/group
- error_rate: errors / total actions
- coverage: number of rows captured in the evidence table; percent with last-updated date

Log formats
- JSONL: one object per event/phase with timestamp, task_slug, metric, value, notes
- CSV: same fields in comma-separated form

Example JSONL entry
{"timestamp":"2025-10-06T15:22:00","task_slug":"audit_stripe_api_20251006","phase":"triage","metric":"perm_prompts","value":3,"notes":"cookie banners on github"}

Example CSV row
timestamp,task_slug,phase,metric,value,notes
2025-10-06T15:22:00,audit_stripe_api_20251006,triage,perm_prompts,3,"cookie banners on github"
