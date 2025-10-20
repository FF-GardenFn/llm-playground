# Agents Adapter

## Overview

Thin adapter exposing the orchestrator CLI and STATUS.json as Python-callable tools. Enables integration with OpenAI Agents SDK, custom automation frameworks, and direct API usage.

Location: `integrations/agentkit-adapter/`

## Components

**orchestrator_client.py**: Core API wrapper over orchestrator CLI
- `start_task(title, allowlist, doc_url)` - Create Charter and STATUS.json
- `run_phase(title_or_charter_id, phase)` - Execute phase with state tracking
- `get_status(title_or_charter_id)` - Read STATUS.json

**agent.py**: SDK-agnostic tool wrappers
- `start_task_tool()` - Dict-returning wrapper for Agents SDK
- `run_phase_tool()` - Dict-returning wrapper for phase execution
- `get_status_tool()` - Dict-returning wrapper for status checks

All functions emit JSON payloads with charter_id and phase for trace tagging.

## Security

Inputs truncated to safe limits:
- Title: 200 chars max
- Domains: 50 max, 150 chars each
- Phase names validated against allowed set

Use `allowed_domains` strictly. Domain validation occurs before evidence addition when using HTTP Charter server.

## Usage

See [getting-started-agents.md](getting-started-agents.md) for:
- Installation and setup
- Direct API usage patterns
- OpenAI Agents SDK integration
- HTTP Charter server deployment
- State tracking with STATUS.json
- Memory store integration
- Testing workflows
