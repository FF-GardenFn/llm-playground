MCP Clients Orchestrator (stub)

Purpose
- Demonstrate how an MCP-capable client can integrate with the Memory Store while using Chrome DevTools via MCP tools to extract DOM text.

Flow
1) Use MCP tools to navigate and extract readable text for allowed domains.
2) Call packages/memory-store/memory.py::Memory.add(url, text, selector, last_updated) during /harvest.
3) During /synthesize, call Memory.search(signature_query, k=5) and paste evidence blocks with URL + last-updated.

Notes
- Keep indices task-local (per Charter); snapshot and reset on /clean.
- Never store executable scripts or credentials; text only.


Clients
- JetBrains AI + Junie: see clients/jetbrains-ai-junie/preflight.md for a paste-in preflight prompt to attach to chrome-devtools-mcp and follow the Charter/commands.
- Other clients (Claude Code, Copilot, Gemini) can use analogous preflights under clients/.

Notes
- Cursor is not provided here; the upstream chrome-devtools-mcp docs describe client setup broadly and we recommend JetBrains Junie for IDE workflows.
