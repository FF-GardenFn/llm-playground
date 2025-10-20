# Getting Started: MCP Client Runtime

## Prerequisites

1. **MCP-Capable AI Client**: One of the following:
   - Claude Code
   - Cursor
   - GitHub Copilot Chat (VS Code or CLI)
   - Gemini Code Assist
2. **Node.js**: Version 20.19 or later (for chrome-devtools-mcp)
3. **Chrome**: Stable version or newer
4. **Shared Document Tool**: Google Docs or Notion account

## Installation

### Step 1: Install chrome-devtools-mcp Server

The chrome-devtools-mcp server provides browser automation tools. Install it based on your AI client:

**Claude Code**:
```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest --isolated=true
```

**Cursor**:
Add to Cursor MCP settings:
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest", "--isolated=true"]
    }
  }
}
```

**Copilot (VS Code)**:
```bash
code --add-mcp '{"name":"chrome-devtools","command":"npx","args":["chrome-devtools-mcp@latest","--isolated=true"]}'
```

**Gemini Code Assist**:
```bash
gemini mcp add chrome-devtools npx chrome-devtools-mcp@latest --isolated=true
```

Verify installation by confirming the MCP server appears in your client's tools list.

### Step 2: Install mcp-addons-server (Optional)

The mcp-addons-server provides local repository access (ripgrep, git, jq). This is optional but recommended for hybrid workflows combining web research with local codebase analysis.

Navigate to the addons server directory:
```bash
cd mcp-servers/addons
npm install
npm run build
```

Add to your MCP client configuration:

**Claude Code**:
```bash
claude mcp add addons node /full/path/to/mcp-servers/addons/dist/server.js
```

**Other clients**: Add to MCP settings JSON:
```json
{
  "mcpServers": {
    "addons": {
      "command": "node",
      "args": ["/full/path/to/mcp-servers/addons/dist/server.js"],
      "env": {
        "WORKSPACE_ROOT": "/path/to/your/project"
      }
    }
  }
}
```

Set `WORKSPACE_ROOT` to the directory containing your local codebase. All file operations will be restricted to this directory and its subdirectories.

## Workflow Overview

The MCP client runtime follows a four-stage workflow:

1. **Prepare Charter**: Copy and customize Charter template for your research objective
2. **Configure Client**: Paste client-specific preflight instructions
3. **Execute Phases**: Run /init-cell → /triage → /harvest → /synthesize
4. **Review Output**: Verify synthesis meets acceptance criteria

## Step-by-Step Guide

### Step 1: Prepare Charter

Navigate to the mcp-clients orchestrator:
```bash
cd orchestrators/mcp-clients
```

Copy the Charter template:
```bash
cp templates/charter.md.tmpl my-research-charter.md
```

Edit `my-research-charter.md` to specify:

- `task`: Your research objective
- `allowed_domains`: Exhaustive list of permitted domains
- `outputs.doc`: Name of your shared document
- `notes`: Domain-specific constraints or focus areas

Example:
```yaml
task: "Performance profile: developers.chrome.com"
allowed_domains:
  - developers.chrome.com/*
  - web.dev/*
outputs:
  - doc: "Chrome_Docs_Performance — Charter & Synthesis"
  - sheet: "Chrome_Docs_Perf_Metrics"
notes: |
  Focus on Core Web Vitals, long tasks, network waterfalls, and CLS.
```

For domain-specific templates, see `core/vertical-packs/`.

### Step 2: Create Shared Document

1. Open your shared document tool (Google Docs or Notion)
2. Create a new document with the title specified in `outputs.doc`
3. Paste the entire Charter contents into this document
4. Optionally, append the doc scaffold from `templates/doc-scaffold.md`

### Step 3: Configure AI Client

Locate the preflight instructions for your AI client:

- Claude Code: `clients/claude_code/preflight.md`
- JetBrains Junie: `clients/jetbrains-ai-junie/preflight.md`
- Copilot: `clients/copilot/preflight.md`
- Gemini: `clients/gemini/preflight.md`

Open your AI client and paste the preflight contents. The preflight will:

1. Confirm MCP servers are connected
2. List available tools
3. Instruct the agent to read the Charter
4. Set expectations for phased execution

### Step 4: Execute Research Phases

**Phase 1: Initialize**

In your AI client, run:
```
/init-cell
```

The agent will:
- Confirm MCP server connectivity
- Read the Charter from the shared document URL
- Restate objectives, allowed domains, and risk mode
- Propose execution plan
- Request approval

Provide the shared document URL when prompted.

**Phase 2: Triage**

Run:
```
/triage
```

The agent will:
- Use `navigate_page` to open up to 6 sources within allowed domains
- Extract structured information from each page
- Write findings to the shared document or designated spreadsheet
- Take screenshots for visual evidence if relevant

**Phase 3: Harvest**

Run:
```
/harvest
```

The agent will:
- Use `evaluate_script` or similar tools to extract structured data from open pages
- Optionally use `ripgrep_search` (if mcp-addons-server installed) to search local codebase
- Append rows to evidence table
- Flag contradictions and outdated information

**Phase 4: Synthesize**

Run:
```
/synthesize
```

The agent will:
- Write synthesis section with Known/Unknown/Risks
- Rank sources with justifications
- Propose 3 next actions with owners and dates
- Include Data Appendix with source URLs and timestamps

**Phase 5 (Optional): Report**

For specific questions:
```
/report
<your question>
```

The agent answers using only captured evidence or identifies gaps.

**Phase 6: Clean**

When finished:
```
/clean
```

The agent will:
- Close browser tabs (via `close_page`)
- Write final checklist in shared document
- Summarize decisions, open questions, and next steps

### Step 5: Review and Archive

Verify the shared document contains:

- Complete evidence table with URLs and timestamps
- Synthesis with Known/Unknown/Risks
- Next actions with owner assignments
- Final checklist

## Available MCP Tools

### chrome-devtools-mcp Tools

**Navigation**:
- `navigate_page`: Navigate to URL
- `new_page`: Open new tab
- `close_page`: Close tab
- `select_page`: Switch active tab

**Interaction**:
- `click`: Click element
- `fill`: Fill form field
- `hover`: Hover over element

**Inspection**:
- `take_screenshot`: Capture page screenshot
- `list_console_messages`: View console logs
- `evaluate_script`: Execute JavaScript

**Performance**:
- `performance_start_trace`: Begin trace recording
- `performance_stop_trace`: End trace recording
- `performance_analyze_insight`: Extract trace insights

**Network**:
- `list_network_requests`: View network activity
- `get_network_request`: Inspect specific request

### mcp-addons-server Tools (Optional)

**Code Search**:
- `ripgrep_search`: Fast code search within WORKSPACE_ROOT
  - Parameters: `pattern` (string), `path` (string, optional), `max_results` (number, optional)

**Version Control**:
- `git_status`: Porcelain status of repository
- `git_grep`: Search tracked files for pattern

**Data Processing**:
- `jq_filter`: Filter JSON with jq expressions
  - Parameters: `json` (string), `filter` (string)

## Troubleshooting

**Issue**: MCP server not found

**Resolution**: Verify installation with `claude mcp list` (or equivalent for your client). Reinstall if necessary. Confirm Node.js version meets requirements (≥20.19).

---

**Issue**: Browser automation failing

**Resolution**: Ensure Chrome is installed and accessible. Check chrome-devtools-mcp logs. Try `--headless=false` flag to see browser UI for debugging.

---

**Issue**: mcp-addons-server path errors

**Resolution**: Verify `WORKSPACE_ROOT` is set correctly in MCP configuration. Ensure paths provided to tools are relative to WORKSPACE_ROOT or use absolute paths within that directory.

---

**Issue**: Agent not following Charter constraints

**Resolution**: Verify Charter is correctly formatted YAML. Check that agent read the Charter in /init-cell phase. Re-paste preflight if necessary.

## Best Practices

1. **Use isolated browser profiles**: Run chrome-devtools-mcp with `--isolated=true` for session isolation
2. **Set WORKSPACE_ROOT carefully**: Ensure it points to project root, not sensitive system directories
3. **Test vertical packs**: Use pre-built templates from `core/vertical-packs/` before creating custom ones
4. **Monitor tool usage**: Review MCP client logs to understand which tools are being invoked
5. **Version control Charters**: Store Charter templates in your project repository for reproducibility

## Next Steps

- Review `core/vertical-packs/` for domain-specific workflow examples
- Read `docs/architecture.md` for MCP integration details
- Explore `docs/advanced/hybrid-workflows.md` for combining web and local research
