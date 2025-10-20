Agents SDK Adapter for Browser Research Toolkit

Purpose
- Make the BRT Charter a first-class, tool-driven resource so agents can start tasks, advance phases, and query status without shelling out.
- Keep BRT sovereign: we call the existing orchestrator and read STATUS.json; no changes to core logic.

Layout
- orchestrator_client.py: subprocess wrapper for the Chrome Extension orchestrator; reads ~/.tab_orchestrator/tasks/*
- agent.py: plain functions that can be decorated (e.g., @function_tool) in an Agents SDK environment

Quick start (local)
1) Ensure your orchestrator runs from CLI:
   python browser-research-toolkit/orchestrators/chrome-extension/orchestrator.py "Test" example.com

2) Use the adapter from your agent code (outside this repo):
   from agentkit_adapter.agent import start_task_tool, run_phase_tool, get_status_tool
   # decorate these with your SDK’s tool decorator

Contracts
- start_task_tool(title: str, allowlist: list[str], doc_url: str|None) -> { charter_id, task_dir }
- run_phase_tool(phase: "init-group"|"triage"|"harvest"|"synthesize"|"report"|"clean", title: str) -> { ok, charter_id, phase }
- get_status_tool(title_or_charter_id: str) -> STATUS.json dict

Notes
- To change which Python interpreter runs the orchestrator, set env BRT_PYTHON.
- The adapter enforces basic length limits for safety; see constants in orchestrator_client.py.
- Evidence operations (add/search) remain inside the orchestrators and memory-store; expose them later if needed.
