# Validate Debate Against Charter

Goal: Check a stored debate for constitutional compliance.

Status:
- CLI subcommand is scaffolded. The current implementation prints a TODO message.

Command:
```bash
cd constitutional-debate
debate validate <debate_id>
```

Planned behavior:
- Load the debate tree
- Run Charter.validate_debate_tree
- Report score, violations, and warnings

Workaround until implemented:
- Review debates/<debate_id>.md and check for:
  - Missing evidence in claims/challenges
  - Missing @node_id references in challenges
  - Weak consensus (< 75%) or no supporting evidence
