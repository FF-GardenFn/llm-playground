# Getting Started: Python Agents Runtime

## Prerequisites

1. **Python**: Version 3.11 or later
2. **pip**: Package installer for Python
3. **Shared Document Tool**: Google Docs or Notion account (optional for SDK-only usage)

## Installation

### Step 1: Install Dependencies

Navigate to the agentkit-adapter directory:

```bash
cd integrations/agentkit-adapter
pip install -r requirements.txt
```

This installs no dependencies (orchestrator_client.py uses stdlib only). The orchestrator itself requires no external packages.

### Step 2: Verify Orchestrator

Test the CLI directly:

```bash
python ../../orchestrators/chrome-extension/orchestrator.py "Test Task" example.com test.com
```

This creates a task directory in `~/.tab_orchestrator/tasks/` containing:
- `CHARTER.md`: Charter contract
- `COMMANDS.json`: Command definitions
- `task.json`: Task configuration
- `STATUS.json`: Phase tracking state

### Step 3: Test Orchestrator Client

Create a test script:

```python
import sys
sys.path.insert(0, '/path/to/integrations/agentkit-adapter')
import orchestrator_client as oc

# Create Charter
result = oc.start_task(
    title="Test Python Client",
    allowlist=["example.com", "test.com/*"]
)
print(f"Charter created: {result.charter_id}")
print(f"Task directory: {result.task_dir}")

# Run triage phase
out = oc.run_phase(result.charter_id, "triage")
print(f"Triage output: {out}")

# Check status
status = oc.get_status(result.charter_id)
print(f"Current phase: {status['current_phase']}")
print(f"Phase history: {status['phase_history']}")
```

Run:
```bash
python test_client.py
```

Expected output:
```
Charter created: Test_Python_Client_20251007
Task directory: /Users/you/.tab_orchestrator/tasks/Test_Python_Client_20251007
Triage output: {'ok': True, 'charter_id': 'Test_Python_Client_20251007', 'phase': 'triage'}
Current phase: triage
Phase history: [{'phase': 'triage', 'status': 'completed', ...}]
```

## Integration Options

### Option A: Direct API Usage (SDK-Agnostic)

Import orchestrator_client and call functions directly:

```python
import orchestrator_client as oc

# Start task
res = oc.start_task("Research X", ["example.com"])
charter_id = res.charter_id

# Execute phases
oc.run_phase(charter_id, "triage")
oc.run_phase(charter_id, "harvest")
oc.run_phase(charter_id, "synthesize")

# Check status
status = oc.get_status(charter_id)
```

This pattern works with any framework or no framework.

### Option B: OpenAI Agents SDK Tools

Wrap functions as tools for Agents SDK:

```python
from agent import start_task_tool, run_phase_tool, get_status_tool

# Register tools with your agent
agent.add_tool(start_task_tool)
agent.add_tool(run_phase_tool)
agent.add_tool(get_status_tool)

# Agent can now invoke:
# - start_task_tool(title="...", allowlist=[...])
# - run_phase_tool(phase="triage", title="...")
# - get_status_tool(title_or_charter_id="...")
```

### Option C: HTTP Charter Server (Stateful API)

Start the HTTP server for concurrent session access:

```bash
cd mcp-servers/brt-charter
export BRT_CHARTER_API_KEY="your_key_here"
export PYTHONPATH="/path/to/browser-research-toolkit:$PYTHONPATH"
python3 -m uvicorn server:app --host 127.0.0.1 --port 8399
```

Server provides six tools via HTTP POST:

**brt_start_task**:
```bash
curl -X POST http://127.0.0.1:8399/tools/brt_start_task \
  -H "Authorization: Bearer your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"title":"HTTP Task","allowlist":["example.com"]}'
```

Response:
```json
{"charter_id":"HTTP_Task_20251007","task_dir":"/Users/you/.tab_orchestrator/tasks/HTTP_Task_20251007"}
```

**brt_advance_phase**:
```bash
curl -X POST http://127.0.0.1:8399/tools/brt_advance_phase \
  -H "Authorization: Bearer your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"title_or_charter_id":"HTTP Task","phase":"triage"}'
```

**brt_add_evidence**:
```bash
curl -X POST http://127.0.0.1:8399/tools/brt_add_evidence \
  -H "Authorization: Bearer your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"charter_id":"HTTP_Task_20251007","url":"https://example.com","text":"Evidence text here"}'
```

**brt_search_evidence**:
```bash
curl -X POST http://127.0.0.1:8399/tools/brt_search_evidence \
  -H "Authorization: Bearer your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"charter_id":"HTTP_Task_20251007","query":"search terms","k":5}'
```

**brt_get_status**:
```bash
curl -X POST http://127.0.0.1:8399/tools/brt_get_status \
  -H "Authorization: Bearer your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"title_or_charter_id":"HTTP Task"}'
```

**brt_validate_domain**:
```bash
curl -X POST http://127.0.0.1:8399/tools/brt_validate_domain \
  -H "Authorization: Bearer your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"charter_id":"HTTP_Task_20251007","url":"https://example.com/page"}'
```

## API Reference

### orchestrator_client.py

**start_task(title: str, allowlist: List[str], doc_url: Optional[str] = None) -> StartResult**

Creates Charter and STATUS.json, returns charter_id and task_dir.

Parameters:
- `title`: Research objective (max 200 chars)
- `allowlist`: Allowed domains (max 50 domains, 150 chars each)
- `doc_url`: Optional shared document URL

Returns:
```python
StartResult(charter_id="Task_20251007", task_dir="/path/to/tasks/Task_20251007")
```

**run_phase(title_or_charter_id: str, phase: str) -> Dict[str, str]**

Executes phase and updates STATUS.json with timestamps and duration.

Parameters:
- `title_or_charter_id`: Original title or full charter_id
- `phase`: One of: triage, harvest, synthesize, report, clean

Returns:
```python
{"ok": True, "charter_id": "Task_20251007", "phase": "triage"}
```

**get_status(title_or_charter_id: str) -> Dict**

Reads STATUS.json for given task.

Returns:
```python
{
  "charter_id": "Task_20251007",
  "created_at": "2025-10-07T14:12:15Z",
  "updated_at": "2025-10-07T14:15:32Z",
  "current_phase": "synthesize",
  "phase_history": [
    {"phase": "triage", "status": "completed", "started_at": "...", "completed_at": "...", "duration_s": 12},
    {"phase": "harvest", "status": "completed", "started_at": "...", "completed_at": "...", "duration_s": 45}
  ],
  "errors": [],
  "checkpoints": []
}
```

### agent.py

**start_task_tool(title: str, allowlist: List[str], doc_url: Optional[str] = None) -> Dict[str, Any]**

Dict-returning wrapper over `start_task()`. Returns `{"charter_id": "...", "task_dir": "..."}`.

**run_phase_tool(phase: str, title: str) -> Dict[str, Any]**

Dict-returning wrapper over `run_phase()`. Returns `{"ok": True, "charter_id": "...", "phase": "..."}`.

**get_status_tool(title_or_charter_id: str) -> Dict[str, Any]**

Dict-returning wrapper over `get_status()`. Returns full STATUS.json contents.

## State Tracking

STATUS.json is automatically updated by `run_phase()`:

**Phase Entry**:
- Appends entry to `phase_history` with `status: "in_progress"`
- Sets `current_phase` to phase name
- Records `started_at` timestamp

**Phase Exit**:
- Updates entry to `status: "completed"`
- Records `completed_at` timestamp
- Calculates `duration_s`
- Logs benchmark metric to `.tab_orchestrator/benchmarks.jsonl` if enabled

**Error Handling**:
- Exceptions append to `errors` array with timestamp and traceback
- Phase remains `in_progress` on error
- Subsequent `run_phase()` call can retry or advance to next phase

## Memory Store Integration

The HTTP Charter server integrates memory-store for evidence retrieval:

**add_evidence**: Chunks text, generates feature hash embeddings, stores in per-charter index
**search_evidence**: kNN search with MMR diversity, returns top-k chunks with scores

This enables semantic search over harvested evidence without external embedding APIs.

Example:
```python
# Add evidence during harvest
oc.run_phase(charter_id, "harvest")  # Agent extracts text from sources

# Later, search for specific claims
hits = search_evidence(charter_id, "OAuth 2.1 security requirements", k=5)
for hit in hits:
    print(f"{hit['url']}: {hit['text'][:100]}...")
```

Memory store uses privacy-first feature hashing (SHA256-based). No external API calls required.

## Testing Pattern

Fresh Claude test workflow:

1. Start HTTP Charter server with test API key
2. Provide import instructions to fresh Claude session
3. Claude calls `oc.start_task()` to create Charter
4. Claude executes `oc.run_phase()` for each phase
5. Monitor STATUS.json for real-time progress
6. Review synthesis document for quality

Example briefing for fresh Claude:

```
You will use the orchestrator_client to manage a research Charter.

Import setup:
import sys
sys.path.insert(0, '/path/to/integrations/agentkit-adapter')
import orchestrator_client as oc

Start task:
result = oc.start_task(title="Research Objective", allowlist=["domain.com/*"])
charter_id = result.charter_id

Execute phases in order:
oc.run_phase(charter_id, "triage")   # Identify sources via WebSearch
oc.run_phase(charter_id, "harvest")  # Extract evidence via WebFetch
oc.run_phase(charter_id, "synthesize")  # Generate report

All synthesis claims must cite sources as: https://example.com (last updated: YYYY-MM-DD)

Check status anytime:
status = oc.get_status(charter_id)
```

This pattern enables autonomous execution with state tracking.

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'orchestrator_client'`

**Resolution**: Ensure `sys.path.insert(0, '/path/to/integrations/agentkit-adapter')` before import. Use absolute path.

---

**Issue**: `RuntimeError: orchestrator phase failed: rc=4: No existing task directory found for title 'X'`

**Resolution**: Use original title string, not charter_id slug. Orchestrator resolves title to latest matching directory.

---

**Issue**: HTTP Charter server returns 401 Unauthorized

**Resolution**: Verify `Authorization: Bearer <key>` header matches `BRT_CHARTER_API_KEY` environment variable. Check header format.

---

**Issue**: STATUS.json not updating

**Resolution**: Verify `run_phase()` completed successfully. Check `~/.tab_orchestrator/tasks/<charter_id>/STATUS.json` exists. Ensure no permission issues.

## Best Practices

1. **Use charter_id for consistency**: Store returned charter_id and pass to subsequent calls rather than relying on title resolution
2. **Check status before phase transitions**: Verify previous phase completed before advancing
3. **Handle errors in phase_history**: Check for `status: "in_progress"` without completion timestamp indicating failure
4. **Isolate tests**: Use unique title prefixes for test runs to avoid directory collisions
5. **Set API key securely**: Use environment variables for BRT_CHARTER_API_KEY, never hardcode

## Integration with MCP

The HTTP Charter server can be exposed as MCP stdio server for Claude Code/Cursor integration:

1. Implement MCP stdio wrapper that translates JSON-RPC to HTTP POST
2. Define six tools matching HTTP endpoints
3. Add to `claude_desktop_config.json` or Cursor MCP settings

This enables Charter management via MCP tools alongside chrome-devtools-mcp browser automation.

Future enhancement: Native MCP stdio server in `mcp-servers/brt-charter-stdio/`.

## Next Steps

- Review `scripts/evals/claim_has_citation.py` for citation compliance validation
- Explore `packages/memory-store/` for evidence retrieval internals
- Read `docs/architecture.md` for design rationale
- Create custom automation workflows using orchestrator_client API
