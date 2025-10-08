# Architecture

## Abstract

The Browser Research Toolkit implements a dual-runtime architecture supporting both browser extension and MCP-based workflows. This design accommodates heterogeneous AI client environments while maintaining a unified Charter contract model.

## Design Principles

### Separation of Concerns

The toolkit separates three orthogonal concerns:

1. **Workflow specification**: Charter contracts and command phase definitions (core/)
2. **Runtime orchestration**: Tools that generate and enforce these specifications (orchestrators/)
3. **Execution primitives**: Browser automation and local tool access (mcp-servers/)

This separation enables independent evolution of each layer and supports multiple execution environments without duplicating workflow logic.

### Contract-Driven Execution

Research tasks are governed by declarative Charter contracts rather than imperative scripts. A Charter specifies:

- Allowed domains (explicit allowlist)
- Forbidden actions (explicit denylist)
- Risk mode (approval requirements)
- Stop conditions (automatic halt triggers)
- Acceptance criteria (phase completion gates)

The agent reads the Charter and is constrained to operate within its boundaries. This inverts the traditional model where security constraints are enforced by the execution environment rather than declared upfront.

### Single Source of Truth

All research artifacts are written to a shared document (typically Google Docs or Notion) specified in the Charter. This document serves as:

- The persistent state of the research session
- The audit trail with provenance for all claims
- The handoff mechanism for human review or continuation

Browser tabs and local files are treated as ephemeral staging; only the shared document is canonical.

## Runtime Architectures

### Chrome Extension Runtime

```
┌─────────────────────────────────────────┐
│ Local Orchestrator (Python)             │
│  orchestrator.py                         │
│   ├─ Generates Charter (YAML/Markdown)  │
│   └─ Generates Commands (JSON)          │
└─────────────────┬───────────────────────┘
                  │
                  ↓ (User pastes Charter)
┌─────────────────────────────────────────┐
│ Chrome Tab Group                         │
│  ├─ Tab 1: Shared Document with Charter │
│  └─ Tabs 2-N: Research sources          │
└─────────────────┬───────────────────────┘
                  │
                  ↓ (User imports commands)
┌─────────────────────────────────────────┐
│ Claude for Chrome Extension              │
│  ├─ Reads Charter from shared doc       │
│  ├─ Executes /init-group → /triage →    │
│  │   /harvest → /synthesize             │
│  └─ Writes findings to shared doc       │
└─────────────────────────────────────────┘
```

**Key characteristics**:
- Manual Charter creation and command import
- Single Claude agent per tab group (no parallelism within group)
- All browser interaction via extension's native capabilities
- No MCP infrastructure required

### MCP Client Runtime

```
┌────────────────────────────────────────────┐
│ Orchestrator Templates                     │
│  ├─ Charter templates (YAML)              │
│  ├─ Commands (JSON)                        │
│  └─ Client-specific preflights            │
└────────────────┬───────────────────────────┘
                 │
                 ↓ (User configures)
┌────────────────────────────────────────────┐
│ MCP Client (Claude Code/Cursor/etc)        │
│  ├─ Reads Charter from shared doc          │
│  ├─ Connects to MCP servers via stdio      │
│  └─ Executes /init-cell → /triage →        │
│     /harvest → /synthesize                 │
└────────────────┬───────────────────────────┘
                 │
                 ├──────────────┬──────────────┐
                 ↓              ↓              ↓
┌─────────────────────┐  ┌──────────────┐  ┌─────────────┐
│ chrome-devtools-mcp │  │ mcp-addons   │  │ Shared Doc  │
│  (Google official)  │  │  (optional)  │  │  (SSoT)     │
│  • navigate_page    │  │  • rg search │  │             │
│  • click            │  │  • git grep  │  │             │
│  • screenshot       │  │  • jq filter │  │             │
│  • perf traces      │  │              │  │             │
└─────────────────────┘  └──────────────┘  └─────────────┘
```

**Key characteristics**:
- Template-based Charter creation
- MCP servers provide tool primitives
- Supports multiple AI clients (Claude Code, Cursor, Copilot, Gemini)
- Optional local codebase access via mcp-addons-server

## Component Interactions

### Charter Flow

1. User specifies research objective and allowed domains
2. Orchestrator generates Charter (chrome-extension: Python script; mcp-clients: template)
3. Charter is placed in shared document in first tab/page
4. Agent reads Charter and restates parameters for confirmation
5. Agent executes phases within Charter constraints
6. All findings written to shared document with URLs and timestamps

### Command Phase Execution

Each phase follows a standard pattern:

```
Phase Entry:
  ├─ Read acceptance criteria from Charter
  ├─ Verify prerequisites from prior phase
  └─ Execute phase operations

Phase Operations:
  ├─ For each action:
  │   ├─ Check domain allowlist
  │   ├─ Check forbidden actions
  │   ├─ Request approval if risk_mode = "ask-before-acting"
  │   └─ Execute if approved
  └─ Write results to shared document

Phase Exit:
  ├─ Verify acceptance criteria met
  ├─ Write phase summary to shared document
  └─ Return control for next phase
```

### Stop Condition Handling

Stop conditions are checked before each action:

1. **Domain violation**: Requested URL not in allowed_domains
2. **Permission timeout**: User approval not received within threshold
3. **Forbidden action**: Requested operation in forbidden_actions list
4. **Explicit halt**: User issues stop command

When triggered:
1. Halt all operations immediately
2. Write stop condition to shared document
3. Request user intervention before proceeding

## Security Model

### Defense in Depth

The toolkit implements multiple security layers:

**Layer 1: Domain Allowlisting**
- Only domains explicitly enumerated in Charter are accessible
- Glob patterns supported (e.g., `github.com/stripe/*`)
- Enforcement: Agent checks URL before each navigation

**Layer 2: Forbidden Actions**
- Login attempts, financial transactions, sensitive operations prohibited by default
- Enforcement: Agent checks action type before execution

**Layer 3: Risk Modes**
- `ask-before-acting`: Human approval required for each action
- `always-allow-listed`: Autonomous operation within allowlist (for trusted domains only)

**Layer 4: Workspace Sandboxing** (MCP runtime only)
- mcp-addons-server restricts file access to WORKSPACE_ROOT
- Path traversal protection via `resolveInRoot()` function
- No arbitrary shell command execution

**Layer 5: Audit Trail**
- Every claim in shared document must cite source URL and last-updated date
- Enables post-hoc verification and accountability

### Threat Model

**In scope**:
- Accidental navigation to unintended domains
- Prompt injection from malicious web content
- Credential leakage via login forms
- Unintentional financial transactions

**Out of scope**:
- Malicious AI client or MCP server
- Compromised browser or operating system
- User deliberately overriding Charter constraints

## Extensibility

### Vertical Packs

Domain-specific workflows are implemented as vertical packs in `core/vertical-packs/`. Each pack specifies:

- Structured fields to extract during /harvest
- Synthesis structure for Known/Unknown/Risks
- Charter template with domain-appropriate allowlist
- Example domains and use cases

Current packs:
- `api-audit.md`: API documentation and migration analysis
- `performance-profiling.md`: Web performance measurement and optimization

### Custom MCP Tools

The mcp-addons-server can be extended with additional tools by modifying `src/server.ts`:

```typescript
server.tool("tool_name", "Description", {
  param1: { type: "string" },
  param2: { type: "number", optional: true }
}, async (args) => {
  // Tool implementation
  return { content: [{ type: "text", text: result }] };
});
```

New tools inherit the workspace sandboxing and path validation automatically.

## Performance Considerations

### Parallelism

**Chrome extension runtime**: No parallelism within a single tab group. Concurrency achieved by creating multiple tab groups, each with its own Charter.

**MCP client runtime**: Dependent on client capabilities. Most MCP clients serialize tool calls, so true parallelism requires multiple client instances or async tool implementations.

### State Management

All state is maintained in the shared document. This avoids synchronization issues but introduces latency for document writes. For optimal performance:

- Use spreadsheet outputs for tabular data (faster than document tables)
- Batch writes when possible (e.g., write entire evidence table at once)
- Keep Charter document focused (archive old sections to separate documents)

## Limitations

1. **Browser-only data**: Cannot directly access local files in chrome-extension runtime
2. **Single agent per cell**: No parallel agents within one research cell
3. **Manual command import**: Chrome extension runtime requires copying commands to shortcuts
4. **Network latency**: Shared document writes introduce round-trip delays
5. **No caching**: Each session starts fresh; no persistent cache of prior research

## Future Directions

Potential enhancements while maintaining core architecture:

- **State tracking**: JSON file tracking current phase and completion status
- **Checkpoint/resume**: Recover from interruptions without restarting
- **Validation layer**: Automated post-run verification of Charter compliance
- **Metric collection**: Structured logging of performance metrics (t_synth, perm_prompts, error_rate)
- **Multi-cell coordination**: Python daemon managing multiple research cells in parallel
