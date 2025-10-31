# Changelog

All notable changes to code-reviewer will be documented in this file.

## [0.1.1] - 2025-10-31

### Fixed
- Moved commands into `.claude-plugin/commands/` directory (Anthropic spec compliance)
- Fixed plugin.json command paths from `../commands/` to `./commands/`
- Removed "You are" anti-patterns from all 4 commands (structural framing alignment)
- Fixed smell catalog integration paths from `../../refactoring-engineer/` to `../refactoring-engineer/`

### Changed
- Updated marketplace entry description to highlight 5-phase workflow and refactoring-engineer integration
- Reframed all commands using structural navigation instead of role-based instructions
- Commands now use `# Command Name` headers instead of "You are..." introductions
- Replaced emoji severity markers with text: Critical:, Important:, Suggestion:, OK:, BAD:
- Files Renamed:
  1. integration/REFACTORING_TRIGGER.md → integration/refactoring-trigger.md
  2. integration/VERIFICATION_MODE.md → integration/verification-mode.md
  3. integration/METRICS_SHARING.md → integration/metrics-sharing.md
  4. workflows/REVIEW_PROCESS.md → workflows/review-process.md
  5. workflows/INTEGRATION_MODES.md → workflows/integration-modes.md
  6. quality/SMELL_INTEGRATION.md → quality/smell-integration.md


### Removed
- COGNITIVE_MODEL_DESIGN.md (archived as internal doc)



## [0.1.0] - 2025-10-30

### Added
- Initial code-reviewer agent implementation
- 5-phase review workflow (Automated Analysis → Manual Review → Feedback Synthesis → Priority Assessment → Recommendations)
- Security-focused review (OWASP Top 10, secure coding practices)
- Testing-focused review (coverage, quality, pyramid compliance)
- Refactoring verification mode (integration with refactoring-engineer)
- Integration protocol with refactoring-engineer (smell catalog sharing, verification mode)
- Comprehensive supporting files (architecture, feedback, integration, performance, priorities, quality, security, testing, verification, workflows)
- Plugin manifest for Claude Code marketplace
- Skills for model-invoked discovery

### Production Usage Features
- Evidence-based feedback with file paths and line numbers
- Constructive criticism patterns
- Priority-based issue classification (Critical/Important/Suggestion/Praise)
- OWASP Top 10 (2021) security scanning
- Testing pyramid validation
- FIRST principles adherence checking
- Integration with refactoring-engineer for automated workflow improvements
