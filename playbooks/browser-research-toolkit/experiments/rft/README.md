Rate-From-Time (RFT) Pilot — Phase Timing Heuristic

Objective
- Explore whether simple timing-based heuristics can suggest when to transition from harvest to synthesize phases.

Design (pilot)
- Collect t_triage and t_harvest durations via StateTracker/benchmarks.
- Heuristic: if harvest yields no new sources for N consecutive minutes or sources_processed growth < τ, suggest switching to synthesize.
- Guarded by a feature flag; never enforce automatically.

Procedure
1. Run standard tasks with benchmarks enabled.
2. After each harvest interval, evaluate heuristic and log a suggestion event.
3. Compare t_synth and citation_rate with and without following suggestions.

Notes
- Do not ship as default. This is strictly experimental and must be reversible.
