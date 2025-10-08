BRT Research Cell (App manifest)

Purpose
- Optional distribution path to package the Browser Research Toolkit Charter tools as an MCP-aware app.
- Points to the local brt-charter server and lists Charter-related tools.

Files
- manifest.json — Declares the MCP server URL, auth, and tools.

Usage
1) Start the brt-charter server locally (example, using uvicorn):

   export BRT_CHARTER_API_KEY=REPLACE_WITH_SECRET
   uvicorn browser-research-toolkit.mcp-servers.brt-charter.server:app --host 0.0.0.0 --port 8399

2) Configure your MCP-aware client to import apps/brt-research-cell/manifest.json.

3) From your client, call tools like brt_start_task or brt_advance_phase.

Notes
- This is optional and meant for convenience. You can instead connect directly to the brt-charter server.
- Charter tools operate on ~/.tab_orchestrator/tasks/<slug>/ and respect allowed_domains in CHARTER.md.
