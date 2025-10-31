# Changelog

All notable changes to the Orchestrator plugin will be documented in this file.

 Pre-1.0 versions may introduce changes in minor releases.

## [0.1.1] - 2025-10-30
### Added
- PRIMER.md as the default, token-lean entrypoint for the Skill.
- Five phase-specific Skills under `.claude-plugin/skills/` for progressive disclosure:
  - reconnaissance, decomposition, delegation, coordination, integration
- Per-plugin README with install, usage, safety, and examples.

### Changed
- Main Skill now loads `PRIMER.md` instead of `AGENT.md` by default.
- Normalized command docs; ensured consistent Expected Output and Gate sections.

### Fixed
- Minor path/includes consistency for skills and docs.

## [0.1.0] - 2025-10-29
### Added
- Initial pilot release with commands: reconnaissance, decompose, delegate, coordinate, integrate.
- `.claude-plugin/plugin.json` with strict mode and explicit commands array.
- Initial Skill loading full `AGENT.md`.
