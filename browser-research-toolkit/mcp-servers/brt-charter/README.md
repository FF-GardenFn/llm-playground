BRT Charter Tools Server (HTTP)

Purpose
- Provide a minimal, local HTTP API exposing Charter operations as callable tools for MCP clients or Agents adapters.
- Keep BRT sovereign: this server delegates to the existing orchestrator and task-local memory-store.

Endpoints
- POST /tools/brt_start_task         { title, allowlist[], doc_url? } → { charter_id, task_dir }
- POST /tools/brt_advance_phase      { title_or_charter_id, phase } → { ok, charter_id, phase }
- GET  /tools/brt_get_status         ?id=<title_or_charter_id> → STATUS.json
- POST /tools/brt_add_evidence       { charter_id, url, text, selector?, last_updated? } → { added_chunks }
- POST /tools/brt_search_evidence    { charter_id, query, k? } → { hits: [{score, snippet, url, last_updated, selector}] }
- POST /tools/brt_validate_domain    { charter_id, url } → { allowed, allowed_domains }
- GET  /health → { ok: true }

Security
- Authorization: Bearer <token> required (env BRT_CHARTER_API_KEY).
- Basic request size caps; allowed_domains enforced for evidence ops.
- Intended for localhost/LAN. Do not expose to WAN.

Quick start
1) Create venv and install deps
   cd claude_in_browser/browser-research-toolkit/mcp-servers/brt-charter
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt

2) Set API key and run
   export BRT_CHARTER_API_KEY="REPLACE_ME"
   uvicorn server:app --host 0.0.0.0 --port 8390

3) Call tools (example)
   TOKEN="$BRT_CHARTER_API_KEY"
   curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -X POST http://localhost:8390/tools/brt_start_task \
     -d '{"title":"Audit Stripe API","allowlist":["https://stripe.com/docs","https://github.com/stripe/*"]}'

Notes
- Evidence store is in-process and ephemeral; snapshot/reset remain the responsibility of orchestrators.
- This is an HTTP facade, not a full MCP stdio server. It is sufficient for most IDE/agent integrations.
