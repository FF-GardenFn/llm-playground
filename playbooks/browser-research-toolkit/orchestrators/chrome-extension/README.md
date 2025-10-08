# Chrome Extension Orchestrator

## Abstract

This orchestrator provides a structured workflow framework for coordinating multi-phase research and analysis tasks using the Claude for Chrome extension. It implements a deterministic execution model wherein a Python-based task generator produces both a formal Task Charter and a set of domain-specific commands that guide the extension through phased data collection, synthesis, and reporting operations within constrained browser environments.

## Purpose

The chrome-extension orchestrator addresses the fundamental challenge of coordinating stateful, multi-step research workflows within the single-agent-per-tab-group constraint of the Claude for Chrome extension. By generating structured task specifications and phase-based command protocols, this system enables:

1. **Deterministic workflow execution**: Tasks proceed through well-defined phases (triage, harvest, synthesize) with explicit success criteria and stopping conditions.

2. **Domain-scoped operation**: All web interactions are restricted to pre-approved domains specified in the Task Charter, enforcing a security boundary.

3. **Provenance tracking**: All collected data must include source URLs and temporal metadata, ensuring verifiable lineage of information.

4. **Single source of truth**: A shared document serves as the authoritative record for all findings, with browser tabs functioning solely as ephemeral data collection interfaces.

## Requirements

### System Dependencies

- Python 3.7 or higher
- Claude for Chrome extension (installed and configured)
- Google Chrome browser
- Access to Google Docs (for output document creation)

### Python Environment

The orchestrator script (`orchestrator.py`) requires only Python standard library modules:
- `dataclasses`
- `datetime`
- `pathlib`
- `json`
- `textwrap`
- `re`

No external package dependencies are required.

## Installation

### Step 1: Verify Python Installation

```bash
python3 --version
```

Ensure the version is 3.7 or higher.

### Step 2: Locate Orchestrator Script

The orchestrator is located at:
```
/Users/hyperexploiter/PycharmProjects/MI/claude_in_browser/browser-research-toolkit/orchestrators/chrome-extension/orchestrator.py
```

### Step 3: Verify Claude for Chrome Extension

Ensure the Claude for Chrome extension is installed and that you have access to the Shortcuts feature under Settings.

## Usage

### Workflow Overview

The orchestrator implements a five-step workflow:

1. **Generate Charter and Commands** (local Python execution)
2. **Create Browser Environment** (Chrome tab group + Google Doc)
3. **Import Commands** (into Claude Shortcuts)
4. **Execute Phases** (invoke commands sequentially)
5. **Review and Clean** (finalize outputs)

### Step 1: Generate Charter and Commands

Execute the orchestrator script with a task title and one or more allowed domains:

```bash
python3 orchestrator.py "Task Title" domain1.com domain2.org [domain3.edu ...]
```

**Example:**

```bash
python3 orchestrator.py "Audit Stripe API migration" stripe.com/docs github.com/stripe/*
```

**Output:**

The script generates three files in `~/.tab_orchestrator/tasks/<slug>_<date>/`:

- `CHARTER.md`: The Task Charter to be pasted into the shared document
- `COMMANDS.json`: Command definitions for Claude Shortcuts
- `task.json`: Structured task metadata

The console will display:
1. The Charter text (to be pasted into the first tab's document)
2. The Commands JSON (to be imported into Claude Shortcuts)

### Step 2: Create Browser Environment

1. Open Google Chrome
2. Create a new tab group (right-click tab → "Add to new group")
3. In the first tab of this group, create a new Google Doc
4. Paste the entire Charter text from Step 1 into this document

### Step 3: Import Commands into Claude Shortcuts

The orchestrator generates six commands: `/init-group`, `/triage`, `/harvest`, `/synthesize`, `/report`, and `/clean`.

For each command:

1. Open Claude for Chrome → Settings → Shortcuts
2. Create a new shortcut with:
   - **Name**: The command name (e.g., `/init-group`)
   - **Content**: The corresponding text from `COMMANDS.json`
3. Save the shortcut

Repeat for all six commands.

**Reference**: See `/scripts/import_shortcuts.md` for detailed instructions.

### Step 4: Execute Phases

Within the Chrome tab group containing the Charter document, invoke commands sequentially:

#### Phase 0: Initialization

```
/init-group
```

This command instructs the agent to:
- Read and restate the Task Charter goals, allowed domains, and risk mode
- Propose a three-phase execution plan
- Request explicit user confirmation before proceeding

#### Phase 1: Triage

```
/triage
```

This command directs the agent to:
- Open up to six high-signal sources within the allowed domains
- Extract metadata (title, author, date, primary claims, URL) from each page
- Record extracted data in a structured table within the Charter document or designated Google Sheet
- Halt execution if any domain falls outside the allowlist

#### Phase 2: Harvest

```
/harvest
```

This command instructs the agent to:
- Systematically extract structured fields from all open tabs
- For API documentation: extract endpoint names, authentication requirements, rate limits, versioning, licensing terms
- For research sources: extract claims, methodologies, datasets, stated limitations
- Append extracted data as rows in the document or Sheet
- Flag contradictions or temporally outdated content

#### Phase 3: Synthesize

```
/synthesize
```

This command directs the agent to:
- Produce a concise synthesis section in the Charter document containing:
  - Enumerated known facts versus remaining uncertainties
  - Ranked source assessments with justifications
  - Three recommended next actions
- Append a Data Appendix with tabular summary and complete source URL list

#### Phase 4: Report (Optional)

```
/report
```

This command restricts the agent to:
- Answer specific user questions using only material captured within the tab group
- Explicitly state insufficient evidence conditions
- Propose additional sources (constrained to allowed domains only)

#### Phase 5: Clean

```
/clean
```

This command instructs the agent to:
- Close non-essential tabs, retaining only Charter and synthesis documents
- Generate a final checklist in the document containing:
  - Decisions made during the workflow
  - Open questions requiring further investigation
  - Blocking issues with identified ownership
  - Exact next steps (actor, action, timeline)

### Step 5: Review and Export

Upon completion, review the shared document for:
- Completeness of citations (all claims must include source URL and date)
- Adherence to forbidden actions (no login attempts, no financial transactions)
- Compliance with allowed domain restrictions

## File Structure

```
chrome-extension/
├── orchestrator.py              # Main task generator script
├── README.md                    # This document
├── scripts/
│   ├── import_shortcuts.md      # Claude Shortcuts import instructions
│   ├── make_task.sh             # Convenience wrapper for orchestrator.py
│   └── seed_examples.sh         # Example task generation script
├── templates/
│   ├── charter.md.tmpl          # Charter template (embedded in orchestrator.py)
│   ├── commands.json.tmpl       # Commands template (embedded in orchestrator.py)
│   └── doc_scaffold.md          # Optional Google Doc scaffold
├── examples/
│   └── tasks/
│       └── audit_stripe_api/    # Example: Stripe API audit task
│           ├── CHARTER.md
│           ├── COMMANDS.json
│           └── task.json
└── docs/
    ├── ARCHITECTURE.md          # System architecture rationale
    ├── CHARTER_SCHEMA.md        # Charter field specifications
    ├── CLAUDE_SHORTCUTS.md      # Shortcuts configuration guide
    ├── SAFETY_AND_PRIVACY.md    # Security and privacy protocols
    └── BENCHMARKING.md          # Performance evaluation metrics
```

### Key Files

#### `orchestrator.py`

The core Python script implementing task generation logic. Key functions:

- `TaskSpec`: Dataclass defining task parameters (title, allowed_domains, output destinations, risk_mode, notes)
- `make_charter(ts: TaskSpec) -> str`: Renders the Charter template with task-specific parameters
- `emit_shortcuts_json() -> str`: Generates JSON-formatted command definitions for Claude Shortcuts import
- `save_task(ts: TaskSpec, charter: str) -> Path`: Persists task artifacts to `~/.tab_orchestrator/tasks/`

#### `CHARTER.md` (Generated)

The Task Charter is a structured specification document containing:

- **task**: Human-readable task title
- **created**: ISO 8601 timestamp of task creation
- **risk_mode**: Execution mode (`ask-before-acting` or `always-allow-listed`)
- **allowed_domains**: List of permitted web domains for data collection
- **forbidden_actions**: Enumerated prohibited operations (login, financial transactions, excessive cookie consent interactions)
- **stop_conditions**: Criteria triggering workflow termination
- **outputs**: Specification of output document and optional spreadsheet
- **review_protocol**: Citation and verification requirements
- **notes**: Task-specific guidance or constraints

#### `COMMANDS.json` (Generated)

A JSON object mapping command names to their prompt definitions. Each command includes both the task-specific prompt and a persona preface defining the metacognitive planner role.

## Examples

### Example 1: API Documentation Audit

**Objective**: Audit the Stripe API for migration-relevant changes.

**Command:**

```bash
python3 orchestrator.py "Audit Stripe API migration" stripe.com/docs github.com/stripe/*
```

**Expected Outputs:**

- Charter document with allowed domains: `stripe.com/docs`, `github.com/stripe/*`
- Commands configured to extract: API versions, rate limits, authentication changes, deprecation timelines
- Synthesis section ranking sources by recency and authority

### Example 2: Literature Review

**Objective**: Survey recent research on transformer architectures.

**Command:**

```bash
python3 orchestrator.py "Survey transformer architecture research 2024" arxiv.org paperswithcode.com huggingface.co/papers
```

**Expected Outputs:**

- Charter document with allowed domains: `arxiv.org`, `paperswithcode.com`, `huggingface.co/papers`
- Triage phase capturing: paper title, authors, publication date, primary claims, dataset identifiers
- Harvest phase extracting: model architectures, training procedures, evaluation metrics, stated limitations
- Synthesis with ranked papers and identified research gaps

### Example 3: Competitive Analysis

**Objective**: Analyze feature sets of project management tools.

**Command:**

```bash
python3 orchestrator.py "Compare PM tool features" monday.com/product asana.com/product linear.app/features
```

**Expected Outputs:**

- Charter document with allowed domains limited to official product pages
- Structured table comparing: feature availability, pricing tiers, integration capabilities
- Synthesis identifying feature gaps and market positioning

## Architecture Notes

### Design Rationale

The orchestrator embraces the single-agent-per-tab-group constraint of Claude for Chrome rather than attempting to circumvent it. This design choice yields:

- **Deterministic execution**: State is maintained in a single document, eliminating race conditions
- **Explicit control flow**: Phase progression requires deliberate command invocation
- **Verifiable provenance**: All data includes source attribution and temporal metadata

### Risk Modes

The Charter supports two risk modes:

1. **ask-before-acting** (default): The agent must request user permission before any potentially sensitive action (opening URLs, creating files, modifying spreadsheets).

2. **always-allow-listed**: The agent may operate autonomously within allowed domains without per-action confirmation, provided no forbidden actions are triggered.

### Forbidden Actions

The following actions are prohibited in all risk modes:

- Login or authentication attempts
- Financial transactions or payment form interactions
- Cookie consent actions beyond rejecting non-essential cookies

### Stop Conditions

Workflow execution terminates automatically if:

- Permission request remains unresolved for more than 60 seconds
- The agent attempts to access a domain outside the allowed list
- A forbidden action is detected

## Security and Privacy Considerations

1. **Domain Allowlisting**: The Charter's `allowed_domains` field functions as a security boundary, preventing inadvertent data exfiltration or access to unintended resources.

2. **No Credential Handling**: The orchestrator explicitly forbids login actions, ensuring no credentials are transmitted during task execution.

3. **Local Storage**: All task metadata is stored locally in `~/.tab_orchestrator/tasks/` with user-controlled access permissions.

4. **Citation Requirements**: The review protocol mandates source URLs for all captured claims, enabling post-hoc verification and audit.

## Troubleshooting

### Issue: Commands Not Appearing in Claude Shortcuts

**Resolution**: Verify that shortcuts were saved after import. Navigate to Claude for Chrome → Settings → Shortcuts and confirm each command name appears in the list.

### Issue: Agent Accessing Prohibited Domains

**Resolution**: Review the Charter's `allowed_domains` list. If the domain should be permitted, regenerate the Charter with the corrected domain list using `orchestrator.py`.

### Issue: Missing Citations in Output

**Resolution**: Re-invoke `/harvest` or `/synthesize` with explicit instruction to include source URLs and dates for all claims.

### Issue: Task Files Not Found

**Resolution**: Verify the task was created successfully by checking `~/.tab_orchestrator/tasks/`. The directory structure should contain a folder named `<task_slug>_<date>/` with `CHARTER.md`, `COMMANDS.json`, and `task.json`.

## References

- `docs/ARCHITECTURE.md`: Detailed architectural rationale and data flow specifications
- `docs/CHARTER_SCHEMA.md`: Complete Charter field reference
- `docs/CLAUDE_SHORTCUTS.md`: Claude Shortcuts configuration and troubleshooting
- `docs/SAFETY_AND_PRIVACY.md`: Security model and privacy guarantees
- `docs/BENCHMARKING.md`: Performance characteristics and evaluation methodology

## License

This orchestrator is part of the browser-research-toolkit. Consult the parent repository for licensing terms.

---

**Version**: 1.0
**Last Updated**: 2025-10-06
**Maintainer**: browser-research-toolkit contributors
