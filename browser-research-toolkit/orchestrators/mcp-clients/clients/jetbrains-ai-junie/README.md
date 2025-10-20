JetBrains AI + Junie client (MCP preflight)

Purpose
- Provide a paste-in preflight for JetBrains AI + Junie to attach to the Chrome DevTools MCP server and follow the Browser Research Toolkit Charter/commands.

Where this fits
- Orchestrator: browser-research-toolkit/orchestrators/mcp-clients
- MCP server: claude_in_browser/chrome-devtools-mcp (external package in this repo)
- Evidence store: browser-research-toolkit/packages/memory-store

Quick start
1) Install and configure Chrome DevTools MCP in your environment as per claude_in_browser/chrome-devtools-mcp/README.md.
2) In JetBrains IDE: Settings → Tools → Junie → MCP → add server chrome-devtools-mcp (npx chrome-devtools-mcp@latest) and test connection.
3) Open your shared research document (Google Doc/Notion) prepared from the Charter.
4) Open JetBrains AI tool window → start a new chat.
5) Paste the contents of preflight.md from this directory. Follow its prompts.

Phases (what the preflight enforces)
- /init-cell: Read the Charter from the shared doc; restate goals, allowed_domains, risk_mode.
- /triage: Use MCP browser tools to open ≤6 high-signal pages within allowed_domains; capture evidence to the doc.
- /harvest: Extract structured fields from open tabs; append rows with citations.
- /synthesize: Write Known/Unknown/Risks; rank sources; propose next actions; include Data Appendix with URLs + last-updated.
- /report (optional): Answer a specific question using captured evidence only; otherwise state gaps.
- /clean: Close tabs; write final checklist; summarize decisions and next steps.

Guardrails
- Allowed domains only; no logins. 
- Every claim must have URL + last-updated; no evidence ⇒ no claim. 
- Task-local memory; snapshot + reset on /clean.

See also
- ../..../README.md (MCP Clients Orchestrator overview)
- ../../../../packages/memory-store/README.md (Evidence store + Concept Index)
