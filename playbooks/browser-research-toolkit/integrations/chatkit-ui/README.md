ChatKit UI (demo-only)

Purpose
- Demonstrate a minimal UI server that surfaces Browser Research Toolkit task status for embedding in chatkit-python widgets.

Endpoints
- GET /tasks — list task slugs under ~/.tab_orchestrator/tasks
- GET /status/{slug} — return STATUS.json for a task

Quick start

    cd integrations/chatkit-ui
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn server:app --host 127.0.0.1 --port 8411

Notes
- Demo-only; no authentication. Do not expose to WAN.
- For full orchestration, use the brt-charter server or agentkit adapter.
