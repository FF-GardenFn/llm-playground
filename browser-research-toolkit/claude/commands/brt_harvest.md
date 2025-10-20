# Harvest Phase

Goal: Extract structured facts from open tabs and captured sources.

Claude for Chrome path:
- Use Shortcut: /harvest
- Capture evidence as bullet points: Claim, Quote, URL, Capture-Time
- Use tab anchors and selectors when applicable

MCP clients path:
```bash
# Follow HARVEST instructions from the Charter template
# Record: Claim, Evidence Quote, URL, Context, Capture-Time
```

Acceptance criteria:
- Every fact has a source URL and exact quote
- No ungrounded statements
- Evidence is stored in the shared document
