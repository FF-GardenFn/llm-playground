# Workspace Statistics

Goal: Inspect usage statistics to monitor warm-up and performance.

Command:
```bash
cd playbooks/adaptive-memory
amem stats <workspace>
```

Outputs (example):
- total_queries, interactions, avg_useful
- avg_dwell_ms, avg_click_rank

Use cases:
- Track learning progression week-over-week
- Compare workspaces to spot where feedback is lacking
