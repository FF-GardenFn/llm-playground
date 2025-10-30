# Terminal-Orchestrator Plugin

Parallel agent execution engine with tmux isolation, monitoring, validation, conflict detection, and merge verification. Infrastructure plugin used by the main Orchestrator.

## Install

1) Add marketplace (GitHub repo):
```
/plugin marketplace add FF-GardenFn/llm-playground
```
2) Install the plugin:
```
/plugin install terminal-orchestrator@llm-playground-plugins
```

## Command
- `/orchestrate-parallel agent1,agent2,...` — creates tmux sessions, runs agents in parallel, validates outputs, detects conflicts, merges, and returns an execution report

Example:
```
/orchestrate-parallel code-generator,code-reviewer,data-profiler
```

## Skills
- Default: `PRIMER.md` (token-lean). Detailed execution workflow in `AGENT.md`.
- On-demand docs loaded by the command: `coordination/main-orchestrator-handoff.md`.

## Safety
- Keep sessions until results are collected; always capture logs.
- If validation fails, do not merge; return report + artifacts.
- Prefer dry-run merges when uncertain.

## Versioning
- Pre-1.0 SemVer; see CHANGELOG for details.

## Links
- Repository: https://github.com/FF-GardenFn/llm-playground
- Marketplace: .claude-plugin/marketplace.json
