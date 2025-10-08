# Getting Started

## Integration Paths

The Browser Research Toolkit supports three integration paths. Select based on your execution environment:

| Path | Target Users | Prerequisites | Installation |
|------|-------------|---------------|--------------|
| Chrome Extension | Claude for Chrome users | Chrome extension, Python 3.10+ | None (stdlib only) |
| MCP Clients | Claude Code, Cursor, Copilot, Gemini users | MCP client, Node.js 20.19+ | `claude mcp add chrome-devtools` |
| Python Agents | OpenAI Agents SDK, custom automation | Python 3.11+, pip | `pip install -r requirements.txt` |

## Path Selection Criteria

**Chrome Extension Runtime**: Use when you have access to Claude for Chrome browser extension and prefer manual command execution within tab groups. Suitable for exploratory research with human oversight at each phase.

**MCP Client Runtime**: Use when your AI client supports Model Context Protocol and you need browser automation with tool primitives. Suitable for repeatable workflows with automated navigation and extraction.

**Python Agents Runtime**: Use when building custom automation, integrating with Agents SDK frameworks, or requiring programmatic Charter management. Suitable for batch processing, A/B testing, and API-driven workflows.

## Common Workflow Pattern

All paths follow the same Charter-driven phase sequence:

1. **start_task**: Create Charter with title and allowed_domains
2. **triage**: Identify 3-6 high-signal sources within allowlist
3. **harvest**: Extract structured evidence from sources
4. **synthesize**: Generate report with Known/Unknown/Risks sections
5. **clean**: Archive results and close ephemeral resources

## Charter Contract

Each task is governed by a Charter specifying:

- `task`: Research objective
- `allowed_domains`: Exhaustive domain allowlist with glob support
- `forbidden_actions`: Operations to reject (e.g., login, financial_tx)
- `risk_mode`: `ask-before-acting` (default) or `always-allow-listed`
- `stop_conditions`: Automatic halt triggers (e.g., domain violation, permission timeout)
- `outputs`: Shared document and optional spreadsheet names

Example:
```yaml
task: "Audit Stripe API migration"
allowed_domains:
  - stripe.com/docs/*
  - github.com/stripe/stripe-python
forbidden_actions:
  - login
  - cookie_consent_beyond_reject
risk_mode: "ask-before-acting"
outputs:
  - doc: "Stripe_API_Audit — Charter & Synthesis"
```

## Path-Specific Setup

**Chrome Extension**:
See [getting-started-chrome-extension.md](getting-started-chrome-extension.md) for Charter generation, command import, and tab group workflow.

**MCP Clients**:
See [getting-started-mcp-clients.md](getting-started-mcp-clients.md) for MCP server installation, preflight configuration, and tool usage.

**Python Agents**:
See [getting-started-agents.md](getting-started-agents.md) for orchestrator client setup, HTTP Charter server, and SDK integration.

## Phase Acceptance Criteria

Each phase has exit criteria that must be met before proceeding:

**Triage**:
- 3-6 sources identified within allowed_domains
- Evidence table written to shared document
- Source URLs and last-updated dates recorded

**Harvest**:
- Structured fields extracted per vertical pack specification
- All evidence rows appended to table
- Contradictions and gaps flagged

**Synthesize**:
- Known section with verified facts and citations
- Unknown section with identified gaps
- Risks section with potential issues
- Source ranking with justification
- 3 next actions with owner and due date

## Security Model

**Domain Allowlisting**: Only domains explicitly listed in `allowed_domains` are accessible. Agent must halt if URL outside allowlist is encountered.

**Forbidden Actions**: Operations in `forbidden_actions` list trigger immediate rejection. Common forbidden actions: login forms, financial transactions, excessive cookie consent.

**Risk Modes**: `ask-before-acting` requires human approval for each action. `always-allow-listed` permits autonomous operation within allowlist (use only for trusted static documentation).

**Audit Trail**: All claims in synthesis must cite source URL and last-updated date in format: `https://example.com (last updated: YYYY-MM-DD)`.

## Vertical Packs

Domain-specific templates in `core/vertical-packs/` define:

- Structured fields to extract during harvest
- Synthesis structure for the domain
- Charter template with appropriate allowlist
- Example use cases

Current packs:
- `api-audit.md`: API documentation and migration analysis
- `performance-profiling.md`: Web performance measurement

Custom vertical packs can be created by following the same structure.

## Support Matrix

| Feature | Chrome Extension | MCP Clients | Python Agents |
|---------|-----------------|-------------|---------------|
| Browser automation | Extension native | chrome-devtools-mcp | chrome-devtools-mcp or HTTP |
| Local file access | No | mcp-addons (optional) | Direct via stdlib |
| Shared document SSoT | Yes | Yes | Yes |
| Command shortcuts | Yes | No (tool calls) | No (API calls) |
| Programmatic access | No | Partial | Full |
| State tracking | Manual | Manual | Automatic (STATUS.json) |
| Memory store | No | No | Yes (optional) |
| Concurrent sessions | Manual (multiple tab groups) | Manual (multiple clients) | Automatic (HTTP server) |

## Next Steps

1. Select integration path based on your environment
2. Follow path-specific setup guide
3. Review `docs/architecture.md` for design rationale
4. Explore `core/vertical-packs/` for domain templates
5. Customize Charter for your research domain
