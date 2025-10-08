Evaluations and Benchmarks

Purpose
- Track effectiveness and reliability of the Browser Research Toolkit across tasks.

Metrics
- t_synth — time to complete synthesis
- citation_rate — % of claims with URL + last-updated
- contradiction_find_rate — on seeded conflicts
- coverage — unique sources used
- error_rate — wrong-tab actions / total actions

Tools
- benchmarks/collector.py — local JSONL/CSV logger
- scripts/evals/runner.py — minimal harness to start/mark phases and compute citation compliance
- scripts/evals/claim_has_citation.py — parses synthesis_snapshot.md and reports a compliance percent

A/B guidance
- Compare runs with and without Concept Index (memory.use_concept_index flag)
- Apply stop rule: keep Concept Index only if it improves by the target margins within 7 tasks

Usage
1) Run your task via the orchestrator and agent; snapshot the synthesis doc to synthesis_snapshot.md under the task dir.
2) Invoke the runner (optionally):

   python scripts/evals/runner.py --title "CLS mitigation" --domains developers.chrome.com/* web.dev/* --snapshot ~/.tab_orchestrator/tasks/<slug>/synthesis_snapshot.md

3) Inspect ~/.tab_orchestrator/benchmarks/<slug>.jsonl and all_runs.csv.
