Architecture Overview

One tab group = one worker.

Rationale
- Claude for Chrome currently runs a single agent per tab group; attempting parallelism within a single group causes race and state issues.
- We embrace this constraint and design a deterministic workflow: Charter → /commands → execution within allowed domains.

Flow
1) Local Python orchestrator emits:
   - CHARTER.md and COMMANDS.json
2) User creates a Chrome tab group and opens a shared doc in the first tab.
3) Paste Charter into that doc.
4) Import commands into Claude Shortcuts (/init-group, /triage, /harvest, /synthesize, /report, /clean).
5) Execute phase by phase; all outputs go into the shared doc (and optional Sheet).

Data Flow and Source of Truth
- The shared document is the single source of truth; tabs are only staging for gathering evidence.
- Each captured item must include URL and last-updated date.

Permissions
- Default risk mode is ask-before-acting.
- Allowed domain list in the Charter acts as a contract.

Notifications & Long-Running Tasks
- Enable notifications after a step runs >30s to avoid babysitting.
