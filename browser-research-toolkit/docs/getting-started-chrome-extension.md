# Getting Started: Chrome Extension Runtime

## Prerequisites

1. **Claude for Chrome Extension**: Early access to Anthropic's Claude for Chrome browser extension
2. **Python**: Version 3.10 or later
3. **Shared Document Tool**: Google Docs or Notion account
4. **Browser**: Chrome stable version or newer

## Installation

Navigate to the chrome-extension orchestrator directory:

```bash
cd orchestrators/chrome-extension
```

No external dependencies required. The orchestrator uses Python standard library only.

## Workflow Overview

The chrome-extension runtime follows a five-stage workflow:

1. **Generate Charter**: Use orchestrator.py to create Charter and commands
2. **Create Tab Group**: Open new Chrome tab group with shared document in first tab
3. **Import Commands**: Add generated commands to Claude Shortcuts
4. **Execute Phases**: Run /init-group → /triage → /harvest → /synthesize
5. **Review Output**: Verify synthesis in shared document meets acceptance criteria

## Step-by-Step Guide

### Step 1: Generate Charter and Commands

Run the orchestrator with your research objective and allowed domains:

```bash
python orchestrator.py "Audit Stripe API migration" stripe.com/docs github.com/stripe/*
```

This creates a task directory in `~/.tab_orchestrator/tasks/<slug>/` containing:

- `CHARTER.md`: Charter contract to paste in shared document
- `COMMANDS.json`: Command definitions for Claude Shortcuts
- `task.json`: Task configuration for reference

### Step 2: Create Tab Group and Shared Document

1. Open Chrome and create a new tab group (right-click tab → "Add tab to new group")
2. In the first tab, create a new Google Doc or Notion page
3. Paste the entire contents of `CHARTER.md` into this document
4. Do not navigate away from this tab; it serves as the session anchor

### Step 3: Import Commands to Claude Shortcuts

Open Claude for Chrome in the tab group:

1. Press `Cmd+E` (macOS) or `Ctrl+E` (Windows/Linux) to open Claude
2. Navigate to Settings → Shortcuts
3. For each command in `COMMANDS.json`:
   - Click "Add Shortcut"
   - Enter the command name (e.g., `/init-group`)
   - Paste the command text from the JSON
   - Save

Alternatively, paste command text directly in Claude when needed (not recommended for repeated use).

### Step 4: Execute Research Phases

**Phase 1: Initialize**

In Claude, run:
```
/init-group
```

Claude will:
- Read the Charter from the shared document
- Restate the objectives, allowed domains, and risk mode
- Propose a phase execution plan
- Request your approval to proceed

Confirm when ready.

**Phase 2: Triage**

Run:
```
/triage
```

Claude will:
- Open up to 6 high-signal sources within allowed domains
- Extract title, author, date, claims, and URL from each
- Write findings to a table in the shared document
- Halt if any source is outside the allowlist

**Phase 3: Harvest**

Run:
```
/harvest
```

Claude will:
- Examine all open tabs in the tab group
- Extract structured fields appropriate to the domain (see Charter notes)
- Append rows to the evidence table
- Flag contradictions or outdated content

**Phase 4: Synthesize**

Run:
```
/synthesize
```

Claude will:
- Write a synthesis section in the shared document containing:
  - Known: Verified facts
  - Unknown: Identified gaps
  - Risks: Potential issues
- Rank sources by credibility with justification
- Propose 3 next actions with owners and dates
- Append a Data Appendix with source URLs

**Phase 5 (Optional): Report**

If you have a specific question, run:
```
/report
```

Then ask your question. Claude will answer using only the captured evidence, or identify what additional information is needed.

**Phase 6: Clean**

When finished, run:
```
/clean
```

Claude will:
- Close non-source tabs
- Append a final checklist with decisions, open questions, blockers, and next steps
- Leave only the Charter document open

### Step 5: Review and Archive

Review the shared document to verify:

- All claims have source URLs and last-updated dates
- Synthesis section includes Known/Unknown/Risks
- Next actions have owners and due dates
- Final checklist is complete

Archive the document for future reference or handoff to team members.

## Risk Modes

The Charter specifies a `risk_mode`:

**ask-before-acting** (default):
- Claude requests approval before each navigation or action
- Recommended for sensitive research or unfamiliar domains

**always-allow-listed**:
- Claude proceeds autonomously within the allowed domains
- Recommended only for trusted, static documentation sites

To change risk mode, edit the `risk_mode` field in the Charter before starting /init-group.

## Troubleshooting

**Issue**: Claude navigates to a domain not in the allowlist

**Resolution**: Stop execution immediately. Add the domain to `allowed_domains` in the Charter, or explicitly forbid it if unintended.

---

**Issue**: Commands not appearing in Claude Shortcuts

**Resolution**: Ensure you are in the same Chrome profile where Claude for Chrome is active. Re-import commands if necessary.

---

**Issue**: Evidence table incomplete after /triage

**Resolution**: Check if Claude encountered permission prompts or cookie banners. Manually close these and re-run /triage. Consider adding `cookie_consent_beyond_reject` to `forbidden_actions`.

---

**Issue**: Synthesis section missing Known/Unknown/Risks structure

**Resolution**: Verify acceptance criteria are present in the Charter. Re-run /synthesize with explicit instruction to include all three sections.

## Best Practices

1. **Use separate Chrome profiles**: Create a dedicated profile for research to avoid mixing personal browsing with research sessions
2. **Limit allowed domains**: Only include domains strictly necessary for the research objective
3. **Review Charters before execution**: Ensure forbidden actions and stop conditions are appropriate
4. **Archive completed sessions**: Save shared documents to a central repository for team access
5. **Iterate on vertical packs**: Customize `notes` section in Charter for domain-specific structured fields

## Next Steps

- Explore vertical packs in `core/vertical-packs/` for domain-specific templates
- Read `docs/architecture.md` for design rationale and extensibility options
- Create custom vertical packs for your research domains
