# Browser Research Toolkit

A systematic framework for conducting structured, auditable web research using AI agents. This toolkit provides Charter-driven workflows that enforce explicit scoping, safety constraints, and quality criteria across different execution runtimes.

## Architecture

The toolkit is organized into three layers:

1. **Orchestrators**: Tools that generate Charter contracts and command definitions for specific runtimes
2. **MCP Servers**: Optional Model Context Protocol servers providing browser automation and local tool access
3. **Core**: Shared specifications for Charter format, command phases, and domain-specific workflows

## Integration Paths

The toolkit supports three integration paths. Select based on your execution environment. See `docs/getting-started.md` for detailed comparison.

### Claude for Chrome Extension Users

If you have access to the Claude for Chrome browser extension, use the **chrome-extension orchestrator**.

**Location**: `orchestrators/chrome-extension/`

**What it provides**:
- Python-based Charter and command generator
- Structured workflow enforcement (triage → harvest → synthesize)
- Persona engineering for methodical execution
- Shared document as single source of truth

**Requirements**:
- Claude for Chrome extension (early access)
- Python 3.10 or later
- Google Docs or Notion account

**Quick start**:
```bash
cd orchestrators/chrome-extension
python orchestrator.py "Audit Stripe API migration" stripe.com/docs github.com/stripe/*
# Output written to ~/.tab_orchestrator/tasks/
# Paste CHARTER.md into first tab's shared document
# Import commands.json into Claude Shortcuts
# Execute: /init-group → /triage → /harvest → /synthesize
```

See `orchestrators/chrome-extension/README.md` for detailed instructions.

---

### MCP-Capable Client Users

If you have Claude Code, Cursor, GitHub Copilot Chat, or Gemini Code Assist, use the **mcp-clients orchestrator**.

**Location**: `orchestrators/mcp-clients/`

**What it provides**:
- Charter templates compatible with MCP-driven workflows
- Multi-client preflight instructions (Claude Code, Cursor, Copilot, Gemini)
- Integration with chrome-devtools-mcp for browser automation
- Optional integration with local code search tools

**Requirements**:
- MCP-capable AI client (Claude Code, Cursor, Copilot Chat, or Gemini Code Assist)
- chrome-devtools-mcp server installed
- (Optional) mcp-addons-server for local repository access

**Quick start**:
```bash
# Install required MCP servers
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest --isolated=true

# Optional: Install local tools server
cd mcp-servers/addons
npm install && npm run build
claude mcp add addons node dist/server.js

# Use Charter template and client-specific preflight
cd orchestrators/mcp-clients
cat clients/claude_code/preflight.md
# Paste Charter template into shared document
# Paste preflight into your AI client
# Execute: /init-cell → /triage → /harvest → /synthesize
```

See `orchestrators/mcp-clients/README.md` for detailed instructions.

---

### Python Agents and Custom Automation

If you are building custom automation, integrating with OpenAI Agents SDK, or need programmatic Charter management, use the **Python agents adapter**.

**Location**: `integrations/agentkit-adapter/`

**What it provides**:
- Direct Python API for Charter operations
- SDK-agnostic tool wrappers for Agents frameworks
- HTTP Charter server for stateful API access
- Automatic state tracking with STATUS.json
- Optional memory-store for evidence retrieval

**Requirements**:
- Python 3.11 or later
- pip

**Quick start**:
```python
import sys
sys.path.insert(0, '/path/to/integrations/agentkit-adapter')
import orchestrator_client as oc

# Create Charter
result = oc.start_task(
    title="Research Objective",
    allowlist=["example.com/*"]
)

# Execute phases
oc.run_phase(result.charter_id, "triage")
oc.run_phase(result.charter_id, "harvest")
oc.run_phase(result.charter_id, "synthesize")

# Check status
status = oc.get_status(result.charter_id)
```

**HTTP Charter Server**:
```bash
cd mcp-servers/brt-charter
export BRT_CHARTER_API_KEY="your_key"
python3 -m uvicorn server:app --host 127.0.0.1 --port 8399
```

Six HTTP tools available: brt_start_task, brt_advance_phase, brt_add_evidence, brt_search_evidence, brt_get_status, brt_validate_domain.

See `docs/getting-started-agents.md` for detailed instructions.

---

## Core Concepts

### Charter

A Charter is a declarative contract that specifies:
- Research objective
- Allowed web domains (explicit allowlist)
- Risk mode (ask-before-acting vs always-allow-listed)
- Forbidden actions (e.g., login, financial transactions)
- Stop conditions (e.g., domain violations, permission timeouts)
- Acceptance criteria for each workflow phase

See `core/charter-spec/specification.md` for complete details.

### Workflow Phases

Research tasks are decomposed into six sequential phases:

1. **/init**: Read Charter, confirm understanding, propose execution plan
2. **/triage**: Identify and catalog high-signal sources within allowed domains
3. **/harvest**: Extract structured information from open tabs
4. **/synthesize**: Produce analysis with explicit Known/Unknown/Risks and next actions
5. **/report**: Answer specific questions using only captured evidence
6. **/clean**: Close research cell with final accountability checklist

See `core/commands-spec/phases.md` for detailed specifications.

### Vertical Packs

Domain-specific templates that specify structured fields and synthesis requirements for common research patterns:

- **API Audit**: `core/vertical-packs/api-audit.md`
- **Performance Profiling**: `core/vertical-packs/performance-profiling.md`

## Documentation

- **Getting Started (Overview)**: `docs/getting-started.md` - Integration path selection and comparison
- **Getting Started (Chrome Extension)**: `docs/getting-started-chrome-extension.md`
- **Getting Started (MCP Clients)**: `docs/getting-started-mcp-clients.md`
- **Getting Started (Python Agents)**: `docs/getting-started-agents.md`
- **Architecture**: `docs/architecture.md` - Design rationale and security model
- **Advanced Workflows**: `docs/advanced/`

## Safety Model

This toolkit enforces multiple safety layers:

1. **Explicit allowlisting**: Only domains enumerated in the Charter are accessible
2. **Forbidden actions**: Login, financial transactions, and sensitive operations are prohibited by default
3. **Risk modes**: Ask-before-acting mode requires human approval for each action
4. **Stop conditions**: Automatic halt on domain violations or permission timeouts
5. **Workspace sandboxing**: MCP addons server restricts local file access to a designated workspace root

## License

MIT License. See LICENSE file in each component directory.


## ChatKit Integration

There are two supported paths to add an embeddable chat UI on top of the Browser Research Toolkit:

1) Recommended (OpenAI‑hosted ChatKit)
- Use integrations/chatkit-embed to run a tiny FastAPI backend that creates ChatKit sessions and returns a client_secret for your frontend widget.
- Endpoint: POST /api/chatkit/session → { client_secret }
- See integrations/chatkit-embed/README.md for setup and frontend example code (ChatKit JS/React bindings).

2) Advanced (self‑hosted ChatKit server + UI)
- See openai-chatkit-advanced-samples in this repo for a full ChatKit server and React UI template.
- You can adapt its Store to surface ~/.tab_orchestrator/tasks/<slug>/STATUS.json and bridge Charter tools if desired.

Security
- Keep the embed backend on trusted infra; require a bearer token if exposing to browsers.
- Do not log or persist ChatKit client secrets; they are handed to the client immediately.
