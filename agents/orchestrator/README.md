# Orchestrator Plugin

Senior engineering manager coordinating parallel specialist agents through a systematic 5-phase workflow with hard gates and verification.

## Install

1) Add marketplace (GitHub repo):
```
/plugin marketplace add FF-GardenFn/llm-playground
```
2) Install the plugin:
```
/plugin install orchestrator@llm-playground-plugins
```

## Commands
- `/reconnaissance` — clarify requirements; produce clear scope and success criteria
- `/decompose [--strategy domain|layer|component|phase]` — produce task graph + dependencies
- `/delegate [--task-id ID]` — match tasks to specialists and launch via Task tool
- `/coordinate [--check-status <id>]` — monitor completions and blockers
- `/integrate [--verify-tests | --dry-run]` — detect conflicts, merge, verify

Each command enforces a gate. Do not proceed if a gate fails.

## Skills
- Default: minimal `PRIMER.md` (token-lean). Deeper details in `AGENT.md`.
- Phase skills (discoverable, concise):
  - `reconnaissance/` — clarify + gate
  - `decomposition/` — strategies + merge planning
  - `delegation/` — specialist matching + context
  - `coordination/` — progress tracking + dependency mgmt
  - `integration/` — conflict resolution + merge strategies

## Safety
- Verification-first; never run in trust mode
- Ask clarifying questions when ambiguous (uses `AskUserQuestion`)
- Least privilege in `allowed-tools`; only use Bash for scoped `atools/*`
- Gates are hard blockers; report and return if unmet

## Examples
```
/reconnaissance "Add JWT-based authentication to the API"
/decompose --strategy phase
/delegate
/coordinate
/integrate --verify-tests
```

## Versioning
- Pre-1.0 SemVer: backward compatibility may change between minor versions.
- See CHANGELOG for details.

## Links
- Repository: https://github.com/FF-GardenFn/llm-playground
- Marketplace: .claude-plugin/marketplace.json
