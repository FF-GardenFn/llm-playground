# Initialize Research Cell

Goal: Create a Charter and preflight instructions for a new research cell.

Choose one integration path below.

Option A — Claude for Chrome (extension):
```bash
cd playbooks/browser-research-toolkit/orchestrators/chrome-extension
python orchestrator.py "<Task Title>" example.com docs.example.com/*
# Open the output folder printed by the script
# 1) Paste CHARTER.md into your shared doc (first tab)
# 2) Import commands.json into Claude Shortcuts
```

Option B — MCP-capable clients (Claude Code, Cursor, Copilot, Gemini):
```bash
# Install chrome-devtools-mcp (required for browser automation)
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest --isolated=true

# (Optional) Local addons server for file access
cd playbooks/browser-research-toolkit/mcp-servers/addons
npm install && npm run build
claude mcp add addons node dist/server.js

# Read preflight for your client
cd playbooks/browser-research-toolkit/orchestrators/mcp-clients
cat clients/claude_code/preflight.md
# Paste preflight into the client and start /init
```

Notes:
- The Charter enforces allowlists, forbidden actions, and risk modes.
- Keep all evidence in the shared document for auditability.
