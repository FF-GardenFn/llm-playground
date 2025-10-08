Browser Research Toolkit — Integration TODO (Agents SDK, ChatKit, MCP)

Context
- Goal: Keep BRT sovereign (Charter → triage → harvest → synthesize → report → clean, MCP/Chrome workers, task-local memory). Add thin adapters for visibility, safety, distribution, and optimization.
- Inputs: openai-agents-python (Agents SDK: agents, handoffs, guardrails, sessions, MCP examples), chatkit-python (actions, agents, widgets, server/store), our current BRT modules (orchestrators, memory-store, StateTracker, benchmarks, Siri daemon).
- Constraint: Start with documentation and adapters; minimize core logic churn. Ship in phases with a kill switch.

Priorities (ship order)
1) Agents Adapter + Tracing (Immediate)
- Outcome: Fresh agent can “naturally” start and advance a Charter via tools rather than shelling to CLI.
- Deliverables:
  - integrations/agentkit-adapter/
    - orchestrator_client.py: Thin client over current orchestrator CLI and STATUS.json (start_task, run_phase, get_status).
    - agent.py: Defines tool wrappers (start_task_tool, run_phase_tool, get_status_tool) for Agents SDK; adds tracing tags (charter_id, phase).
  - docs/agents-adapter.md: How to run locally; how Siri daemon and Agents coexist.
- Notes: Do not replace orchestrator logic; adapters call the existing CLI under the hood.

1.5) Charter MCP Server (Immediate)
- Outcome: Charter becomes a first-class MCP toolset so any MCP client (Claude Code, Junie) can call it directly.
- Deliverables:
  - mcp-servers/brt-charter/
    - server.py: Tools: brt_start_task, brt_advance_phase, brt_add_evidence, brt_search_evidence, brt_get_status, brt_validate_domain.
    - README.md: Setup, auth model, allowed_domains enforcement, examples.
- Notes: Tools should be strict-allowlist and idempotent; tie to STATUS.json and memory-store.

2) Guardrails Hardening (Immediate)
- Outcome: Safer HTTP boundary for voice/agent entry points.
- Deliverables:
  - integrations/siri-daemon: Add optional checks (PII redaction hooks, stricter domain pattern validation, per-IP rate limits, max utterance size). Keep defaults off via config.
  - docs/security.md: Threat model, defaults, and how to run on LAN only.
- Notes: We already enforce bearer token, timeouts, and fixed orchestrator paths; extend without introducing external deps.

3) Evals + Benchmarks Wiring (Week 1)
- Outcome: Automated grading for claims and phase timing.
- Deliverables:
  - scripts/evals/claim_has_citation.py: Parses synthesis_snapshot.md; asserts URL + last-updated per claim.
  - scripts/evals/runner.py: Runs a task, logs metrics via benchmarks/collector.py, and prints a summary.
  - docs/evals.md: How to run A/B (with/without concept index); stop rule criteria.
- Notes: Integrate with existing benchmarks/collector.log_metric; no external services.

4) Distribution via Apps SDK (Week 2)
- Outcome: Optional ChatGPT app packaging pathway (MCP-aware) called “BRT Research Cell”.
- Deliverables:
  - apps/brt-research-cell/: Manifest and glue for MCP + Charter tools; README with install/use.
- Notes: Keep as optional distribution; do not change core BRT flows.

5) Optional Experiments (Reversible)
- RFT pilot (phase timing): Use collected metrics to learn when to move from harvest → synthesize.
  - Deliverable: experiments/rft/README.md and a small pilot script; guarded by a feature flag.
- Codex hooks (code-adjacent packs only): Emit PR-ready patches during /report phase from cited evidence.
  - Deliverable: orchestrators/helpers/emit_claim.py and emit_patch.py (document-only initially).
- ChatKit UI (demo only): Simple web UI wrapping Charter tools and STATUS.json, using chatkit-python widgets.
  - Deliverable: integrations/chatkit-ui/ (stub server + README), gated behind local config.

Interfaces (what stays stable)
- Orchestrator CLI (existing): python orchestrator.py "<Task Title>" domain1 [domain2 ...]; --phase <phase> marks STATUS.json.
- Memory-store (existing): add(url,text,selector,last_updated), search(query,k,filters), snapshot(), reset().
- STATUS.json (existing): Append-only phase history; do not break schema.

Tool Contracts (new)
- start_task_tool(title: str, allowlist: list[str], doc_url: str|None) → {charter_id, task_dir}
- run_phase_tool(phase: Literal["init-group","triage","harvest","synthesize","report","clean"], title: str) → {status}
- get_status_tool(title: str|charter_id: str) → STATUS.json
- add_evidence_tool(charter_id: str, url: str, text: str, selector: str|None, last_updated: str|None) → count
- search_evidence_tool(charter_id: str, query: str, k: int) → hits[]

MCP Charter Server (draft)
- Tools: brt_start_task, brt_advance_phase, brt_add_evidence, brt_search_evidence, brt_get_status, brt_validate_domain.
- Auth: Local only by default; optional API key via env; request size limits; fixed-arg allowlist.
- Safety: Allowed domains enforced server-side; evidence text only (no scripts); no credentials.

Acceptance criteria
- Agents adapter can create a Charter and mark phases without shell access.
- MCP Charter server can start/advance tasks and read STATUS.json from any MCP client.
- Siri daemon rejects unauthenticated or out-of-allowlist requests (configurable policy).
- Evals show ≥90% citation compliance; stop rule honored for concept index.

Risks & mitigations
- Dependency bloat: Keep adapters pure-Python; avoid heavy libraries.
- Privacy: Default to local models for embeddings; do not transmit evidence content externally.
- Drift: Feature flags for concept index and RFT pilot; easy rollback.

Tasks (checklist)
- [✓] Create integrations/agentkit-adapter/ (orchestrator_client.py, agent.py, README)
- [✓] Draft mcp-servers/brt-charter/ (server.py, README); reuse security posture from mcp/server_stub.py
- [✓] Extend integrations/siri-daemon guardrails (PII hooks, stricter validation) behind config flags
- [✓] Add scripts/evals/claim_has_citation.py and runner.py; wire benchmarks/collector
- [✓] Draft apps/brt-research-cell/ (manifest + README) as optional
- [✓] Document experiments/rft/ and orchestrators/helpers/emit_claim.py (stubs)
- [✓] Prototype integrations/chatkit-ui/ (stub + docs) as demo-only
- [✓] Update docs: getting-started for Agents/MCP/ChatKit paths and support matrix
- [ ] wire in the cerebral cortex (metaphorically)

Notes and references
- Agents SDK examples: openai-agents-python/examples/mcp/* and examples/research_bot/ (planner/searcher/writer map to triage/harvest/synthesize)
- Sessions/tracing: openai-agents-python/src/agents/memory/sqlite_session.py and docs on tracing; can mirror STATUS.json history when needed
- ChatKit modules per mkdocs (actions/agents/widgets/server/store): candidate for a minimal demo UI, not core orchestration
- BRT core references: orchestrators/chrome-extension/orchestrator.py, packages/memory-store/*, scripts/validate_task.py, integrations/siri-daemon/*
