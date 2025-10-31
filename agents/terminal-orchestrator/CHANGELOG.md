# Changelog

All notable changes to the Terminal-Orchestrator plugin will be documented in this file.

## [0.1.1] - 2025-10-30
### Added
- PRIMER.md as the default, token-lean entrypoint for the Skill.
- Handoff protocol document at `.claude-plugin/coordination/main-orchestrator-handoff.md`.
- README with install, usage, safety, and example.

### Changed
- Main Skill now loads `PRIMER.md` instead of `AGENT.md` by default.

### Fixed
- Ensured include path for handoff protocol resolves from command `orchestrate-parallel.md`.

## [0.1.0] - 2025-10-29
### Added
- Initial pilot release with `/orchestrate-parallel` command.
- `.claude-plugin/plugin.json` with strict mode and explicit commands array.
- Initial Skill loading full `AGENT.md`.
