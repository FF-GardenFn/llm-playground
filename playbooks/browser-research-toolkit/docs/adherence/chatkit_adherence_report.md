ChatKit Framework Adherence Report (BRT vs. Advanced Samples)

Scope
- Compare the OpenAI ChatKit Advanced Samples to our Browser Research Toolkit (BRT) with a focus on:
  - Server wiring (FastAPI + ChatKitServer)
  - Store contract (chatkit.store.Store)
  - Widgets come later (out of scope for now)

References
- ChatKit advanced samples (server wiring):
  - openai-chatkit-advanced-samples/backend/app/main.py
  - openai-chatkit-advanced-samples/backend/app/chat.py
- ChatKit advanced samples (Store):
  - openai-chatkit-advanced-samples/backend/app/memory_store.py
- BRT servers and state:
  - browser-research-toolkit/mcp-servers/brt-charter/server.py (FastAPI, non-ChatKit)
  - browser-research-toolkit/orchestrators/chrome-extension/state_tracker.py (STATUS.json)
  - browser-research-toolkit/integrations/chatkit-ui (demo-only; not a ChatKit server)

Summary
- Adherence: Partial. BRT does not currently expose a ChatKitServer endpoint nor implement the chatkit.store.Store contract. We do have analogous building blocks (FastAPI server, STATUS.json state, evidence store), so adding a thin compatibility layer is straightforward without changing core BRT logic.

1) Server wiring (ChatKit -> FastAPI)
- What ChatKit expects (per advanced samples):
  - A FastAPI route POST /chatkit that forwards the raw request body to a ChatKitServer instance: result = await server.process(payload, {"request": request}).
  - The result is either a StreamingResult (SSE) or a JSON-like value. main.py returns StreamingResponse for streams and Response(JSON) otherwise.
  - The ChatKitServer itself is assembled in chat.py via create_chatkit_server(), wiring:
    - Agents SDK (agents.Agent/Runner) with chatkit.agents.stream_agent_response
    - A Store implementation for threads/items
    - Optional client tools and widget rendering helpers

- What BRT has:
  - FastAPI servers: mcp-servers/brt-charter/server.py (auth, size limits, evidence ops) and integrations/siri-daemon/daemon.py (voice bridge). These are not ChatKit servers and do not speak the ChatKit protocol.
  - No /chatkit endpoint, no ChatKitServer.process call, and no SSE streaming for ChatKit.

- Adherence verdict: Missing. We do not yet expose a ChatKitServer facade.

- Minimal path to compliance (no core changes):
  - Add integrations/chatkit-server/ with:
    - server.py: FastAPI app exposing POST /chatkit and GET /health following advanced samples’ pattern.
    - chat.py: create_chatkit_server() that bridges our orchestrator tools through the Agents SDK and returns a ChatKitServer instance.
    - store_adapter.py: a simple Store adapter (see section 2) that treats each ChatKit thread as a conversation view over a BRT task.
  - Security posture: replicate brt-charter’s bearer token and size caps as optional settings; default to localhost.

2) Store contract (chatkit.store.Store)
- What ChatKit expects (per advanced samples backend/app/memory_store.py):
  - A subclass of Store[TContext] implementing:
    - Thread metadata: load_thread, save_thread, load_threads (paged), delete_thread
    - Thread items: load_thread_items (paged), add_thread_item, save_item, load_item, delete_thread_item
    - Attachments: save_attachment, load_attachment, delete_attachment (can be NotImplemented for in-memory demo)
  - Types from chatkit.types (ThreadMetadata, ThreadItem, Page, Attachment).

- What BRT has today:
  - STATUS.json task state (state_tracker.py): phase_history, errors, checkpoints written under ~/.tab_orchestrator/tasks/<slug>/STATUS.json
  - Evidence store (packages/memory-store): unrelated to conversation threads; it stores research chunks, not chat threads.
  - No implementation of chatkit.store.Store; no mapping from thread items to BRT events.

- Adherence verdict: Missing. We have no ChatKit Store.

- Minimal Store adapter design for BRT (drop-in, safe-by-default):
  - Thread <-> Charter mapping:
    - ThreadMetadata.id == charter_id (or a synthetic thread id that points to the latest charter)
    - Use STATUS.json timestamps for created_at/updated_at
  - Thread items mapping:
    - Convert each STATUS.json phase entry into a HiddenContextItem or UserMessageItem snapshot for read-only history
    - On add/save item, append a synthetic note into STATUS.json checkpoints (so ChatKit UI sees the update without changing core schema)
  - Pagination: mirror advanced samples’ in-memory approach with simple slicing and ‘after’ cursors
  - Attachments: NotImplemented to avoid uploading; keep evidence privacy intact

3) Implementation notes (from advanced samples)
- main.py illustrates the FastAPI+ChatKitServer glue with StreamingResult routing.
- chat.py shows canonical use of:
  - chatkit.agents.AgentContext, ThreadItemConverter, stream_agent_response
  - Agents SDK function tools to surface server and client tool calls
  - Rendering a widget for rich responses (defer for now)
- memory_store.py demonstrates the exact Store surface ChatKit expects.

4) Recommended next steps (small, additive)
- Add a new integration module (no core edits):
  1. Create integrations/chatkit-server/ with:
     - server.py: POST /chatkit -> ChatKitServer.process; GET /health.
     - chat.py: create_chatkit_server() assembling a ChatKitServer over our agent tools (start_task, run_phase, get_status) using our existing agentkit-adapter.
     - store_adapter.py: implements chatkit.store.Store to back threads/items by STATUS.json (read-only OK for first pass).
  2. Document how to run (docs/integrations/chatkit.md): ports, auth, localhost-only default, how this coexists with brt-charter.
- Leave widgets for a follow-up (can render a small STATUS panel later).

5) Adherence checklist (post-implementation target)
- Server wiring:
  - [ ] POST /chatkit returns StreamingResponse when ChatKitServer emits a stream
  - [ ] GET /health returns {"ok": true}
- Store contract:
  - [ ] load/save/load_threads/delete_thread
  - [ ] load_thread_items/add_thread_item/save_item/load_item/delete_thread_item
  - [ ] Attachments stubbed with clear NotImplemented
- Security:
  - [ ] Optional bearer token and size caps (aligned with brt-charter)
  - [ ] Localhost default; do not expose to WAN

Conclusion
- We are conceptually aligned (FastAPI servers, Agents tools, local state), but have not yet implemented the ChatKit-specific server and Store contracts. The minimal adapter layer described above achieves full adherence without changing BRT’s core orchestrators, memory store, or STATUS.json schema.
