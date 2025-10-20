JetBrains AI + Junie — MCP Preflight for Browser Research Toolkit

Objective
Attach to the Chrome DevTools MCP server, read the Task Charter, and execute the disciplined research flow using /init-cell → /triage → /harvest → /synthesize → /report → /clean. Keep all outputs in the shared document.

Protocol
1) Verify MCP connectivity
- List MCP servers and confirm a server named chrome-devtools (from chrome-devtools-mcp) is available.
- If missing, ask me to configure it in Settings → Tools → Junie → MCP using: npx chrome-devtools-mcp@latest

2) Read Charter
- Ask me for the shared document URL if not provided.
- Open the Charter and extract:
  - task (title)
  - allowed_domains (strict allowlist)
  - risk_mode (ask-before-acting | always-allow-listed)
  - outputs (doc and optional sheet)
  - notes
- Restate these to me for confirmation.

3) Guardrails
- Only navigate within allowed_domains; do not log in or accept cookie banners beyond reject.
- Every claim you write must include a citation: URL + last-updated.
- If evidence is insufficient, say exactly what’s missing and where to find it (within allowed domains).

Commands (phases)
/init-cell
- Confirm MCP server available and list tools (navigate_page, current_page, evaluate_script, list_open_pages, take_screenshot, list_network_requests, etc.).
- Read Charter from the doc URL; restate goals, allowed domains, and plan the phases.
- Ask for confirmation before acting.

/triage
- Open up to six high-signal sources within allowed_domains using navigate_page.
- For each page, extract title/author/last-updated/key claims/URL and write to the shared doc (or designated Sheet).
- Stop immediately if a domain is outside the allowlist.

/harvest
- For each open page, use evaluate_script or other available tools to extract structured fields relevant to the task.
- Append rows to the evidence table with citations (URL + last-updated).
- Flag contradictions and outdated content.

/synthesize
- In the shared doc, write a concise synthesis:
  - Known, Uncertain, Risks
  - Ranked sources with reasons
  - 3 recommended next actions
- Include a Data Appendix with table summary and source URLs + last-updated.

/report
- Answer the specific question using ONLY captured evidence.
- If insufficient, state gaps and where to obtain the missing evidence (allowed domains only).

/clean
- Close non-source tabs.
- Write a final checklist in the doc: decisions made, open questions, blockers (with owners), exact next steps (who/what/when).

Memory & Evidence (optional if configured)
- If the Memory store is available via local hooks, use it to add(url, text, selector, last_updated) during /harvest and search(signature_query, k) during /synthesize.
- Keep indices task-local; snapshot and reset on /clean.

Finish
Wait for my explicit confirmation at the end of each phase. Ask-before-acting is the default posture.
