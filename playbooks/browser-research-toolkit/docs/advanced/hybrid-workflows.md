# Hybrid Workflows

## Overview

Hybrid workflows combine web research (via browser automation) with local codebase analysis (via local tools). This approach is particularly effective for tasks requiring cross-referencing between external documentation and internal implementation.

## Prerequisites

1. MCP-capable AI client (Claude Code, Cursor, Copilot, or Gemini)
2. chrome-devtools-mcp server installed
3. mcp-addons-server installed and configured
4. Local codebase in WORKSPACE_ROOT

## Architecture

```
┌───────────────────────────────────────────────┐
│ AI Client                                     │
│  ├─ Reads Charter with hybrid objectives     │
│  └─ Coordinates between MCP servers          │
└───────────┬───────────────────────────────────┘
            │
            ├──────────────────┬────────────────┐
            ↓                  ↓                ↓
┌──────────────────┐  ┌────────────────┐  ┌──────────────┐
│ chrome-devtools  │  │  mcp-addons    │  │ Shared Doc   │
│  (web research)  │  │  (local tools) │  │  (synthesis) │
│                  │  │                │  │              │
│ • API docs       │  │ • rg search    │  │ • Evidence   │
│ • GitHub issues  │  │ • git grep     │  │ • Analysis   │
│ • Blog posts     │  │ • jq filter    │  │ • Next steps │
└──────────────────┘  └────────────────┘  └──────────────┘
```

## Use Cases

### Use Case 1: API Migration Audit

**Objective**: Verify internal API usage aligns with external documentation changes.

**Workflow**:
1. **/triage**: Gather migration guides from vendor documentation
2. **/harvest (web)**: Extract new authentication requirements, endpoint changes, deprecation timelines
3. **/harvest (local)**: Use `ripgrep_search` to find all API calls in codebase
4. **/synthesize**: Cross-reference implementation against migration requirements, identify breaking changes

**Charter example**:
```yaml
task: "Audit internal Stripe API usage against v2 migration"
allowed_domains:
  - stripe.com/docs
  - github.com/stripe/*
acceptance:
  triage: "≥ 4 migration guides captured"
  harvest: "All v1 endpoint calls identified in codebase; v2 requirements documented"
  synthesize: "Gap analysis complete; migration checklist with file locations"
notes: |
  Focus on authentication changes and deprecated endpoints.
  Use ripgrep_search to find: 'stripe.charges.create', 'stripe.customers.retrieve'
```

**Key commands during harvest**:
```
# Agent uses chrome-devtools-mcp to read docs, then:
ripgrep_search(pattern="stripe\\.charges\\.", path="src/")
ripgrep_search(pattern="stripe\\.customers\\.", path="src/")
git_grep(pattern="v1/charges")
```

### Use Case 2: Security Vulnerability Assessment

**Objective**: Correlate CVE disclosures with internal library usage.

**Workflow**:
1. **/triage**: Collect CVE bulletins and security advisories
2. **/harvest (web)**: Extract affected versions, patch availability, exploit details
3. **/harvest (local)**: Use `git_grep` to find affected library imports and version specifications
4. **/synthesize**: Map vulnerabilities to codebase locations, prioritize patching by severity

**Charter example**:
```yaml
task: "Assess exposure to OpenSSL CVE-2024-XXXX"
allowed_domains:
  - nvd.nist.gov/*
  - openssl.org/*
  - github.com/advisories/*
acceptance:
  triage: "CVE details and patch notes captured"
  harvest: "All OpenSSL usages identified with version numbers"
  synthesize: "Exposure assessment with affected files and recommended patches"
notes: |
  Search for OpenSSL imports, version pins in requirements.txt, and vulnerable function calls.
```

### Use Case 3: Performance Regression Root Cause Analysis

**Objective**: Correlate observed performance degradation with recent code changes.

**Workflow**:
1. **/triage**: Profile target application, capture performance traces
2. **/harvest (web)**: Extract Core Web Vitals, long tasks, blocking resources from trace
3. **/harvest (local)**: Use `git_status` and `git_grep` to identify recent changes to implicated components
4. **/synthesize**: Link performance bottlenecks to specific commits, propose rollback or fixes

**Charter example**:
```yaml
task: "Root cause analysis: LCP regression on /products page"
allowed_domains:
  - [your-app].com/products
acceptance:
  triage: "Performance trace captured with LCP > 4s"
  harvest: "Blocking resources identified; recent commits to affected components found"
  synthesize: "Root cause identified with commit hash and proposed fix"
notes: |
  Focus on JavaScript execution time and render-blocking resources.
  Search git history for changes to ProductList, ImageGallery components.
```

**Key commands during harvest**:
```
performance_start_trace()
navigate_page(url="https://[your-app].com/products")
performance_stop_trace()
performance_analyze_insight()

# Then search local codebase:
git_status()
git_grep(pattern="ProductList")
ripgrep_search(pattern="ImageGallery", path="src/components/")
```

## Command Phase Patterns

### Pattern 1: Web-First, Local-Validate

Use when external documentation is authoritative:

1. **/triage**: Capture external references
2. **/harvest**: Extract specifications from web, then validate implementation in local code
3. **/synthesize**: Flag discrepancies between spec and implementation

### Pattern 2: Local-First, Web-Enhance

Use when codebase is source of truth:

1. **/triage**: Profile local codebase (e.g., via `ripgrep_search`)
2. **/harvest**: Enrich findings with external context (documentation, best practices)
3. **/synthesize**: Recommend improvements based on external research

### Pattern 3: Parallel Harvest

Use when web and local research are independent:

1. **/triage**: Identify both web sources and local search patterns
2. **/harvest**: Alternate between browser tools and local tools
3. **/synthesize**: Merge findings from both sources into unified analysis

## Tool Coordination

### Temporal Sequencing

Execute web research before local search when external data informs search patterns:

```
# First, extract API endpoint from docs
navigate_page("https://api-docs.example.com/v2/users")
evaluate_script("document.querySelector('.endpoint-url').textContent")

# Then search codebase for that endpoint
ripgrep_search(pattern="/v2/users", path="src/")
```

### Spatial Partitioning

Use web research for one aspect, local tools for another:

```
# Web: performance metrics
performance_start_trace()
navigate_page("https://myapp.com")
performance_stop_trace()

# Local: implementation of slow component
ripgrep_search(pattern="SlowComponent", path="src/")
git_grep(pattern="useEffect.*SlowComponent")
```

## Charter Design for Hybrid Workflows

### Hybrid Objectives

Specify both web and local research goals in Charter `notes`:

```yaml
notes: |
  Web research:
    - Stripe API v2 migration timeline
    - Breaking changes in authentication

  Local research:
    - All stripe.charges.* calls in src/
    - Payment processing flows in services/payment/
```

### Acceptance Criteria

Define separate criteria for web and local components:

```yaml
acceptance:
  harvest: "API changes documented from web; all usage sites identified in codebase"
  synthesize: "Migration plan includes: (1) external requirements, (2) affected files with line numbers, (3) estimated effort"
```

### WORKSPACE_ROOT Constraints

Ensure local search scope is appropriate:

```json
{
  "env": {
    "WORKSPACE_ROOT": "/path/to/project"
  }
}
```

All `ripgrep_search`, `git_grep`, and `git_status` operations are scoped to this directory.

## Security Considerations

### Isolation

Keep web and local research isolated:
- Use `--isolated=true` for chrome-devtools-mcp to prevent cookie/session leakage
- Restrict WORKSPACE_ROOT to project directory, not home directory

### Data Flow

Be cautious when including local code snippets in shared document:
- Avoid pasting entire functions; summarize or cite file:line instead
- Do not include secrets, API keys, or credentials in synthesis
- Review Data Appendix before sharing externally

### Audit Trail

Ensure both web and local sources are cited:

**Web sources**:
```
Source: https://stripe.com/docs/api/charges/create
Last Updated: 2024-10-06
```

**Local sources**:
```
Source: src/services/payment/stripe_client.py:142
Git Commit: a3b2c1d (2024-09-15)
```

## Limitations

1. **No bidirectional updates**: Changes in codebase after harvest phase are not reflected in synthesis
2. **Manual git operations**: mcp-addons-server provides read-only git access; commits/pushes must be done manually
3. **Performance overhead**: Interleaving web and local tools introduces latency
4. **Context window constraints**: Large codebases may exceed practical limits for synthesis

## Best Practices

1. **Prioritize web triage**: Gather external context before searching locally
2. **Use specific search patterns**: Avoid overly broad `ripgrep_search` patterns that return thousands of matches
3. **Batch local searches**: Group related `ripgrep_search` calls to minimize tool invocations
4. **Version control state**: Run `git_status` early to understand uncommitted changes
5. **Document WORKSPACE_ROOT**: Include the workspace path in Charter for reproducibility

## Example End-to-End Session

**Objective**: Audit internal usage of deprecated React API

**Setup**:
```bash
# Install MCP servers
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest --isolated=true
cd mcp-servers/addons && npm install && npm run build
claude mcp add addons node dist/server.js
```

**Charter**:
```yaml
task: "Audit usage of deprecated React.findDOMNode API"
allowed_domains:
  - react.dev/*
  - github.com/facebook/react/*
acceptance:
  triage: "React migration guide and deprecation timeline captured"
  harvest: "All findDOMNode calls identified with file locations"
  synthesize: "Migration plan with alternative APIs and estimated effort per file"
notes: |
  Find React docs on componentWillMount deprecation and recommended alternatives.
  Search codebase for: findDOMNode, componentWillMount patterns.
```

**Execution**:
```
/init-cell
→ Agent confirms MCP servers, reads Charter

/triage
→ Agent navigates to react.dev/learn/lifecycle-methods
→ Captures deprecation warnings and migration guides

/harvest
→ Agent extracts recommended alternatives (useRef, forwardRef)
→ Runs: ripgrep_search(pattern="findDOMNode", path="src/components/")
→ Runs: git_grep(pattern="componentWillMount")
→ Writes table: File | Line | Current API | Suggested Alternative

/synthesize
→ Known: 12 findDOMNode calls across 8 components
→ Unknown: Whether tests cover alternative implementations
→ Risks: Breaking changes in component lifecycle
→ Next Actions:
    1. Refactor UserProfile.jsx to use useRef (Owner: @dev1, Due: 2024-10-15)
    2. Add tests for Modal.jsx after migration (Owner: @dev2, Due: 2024-10-20)
    3. Schedule code review for all refactored components (Owner: @lead, Due: 2024-10-25)

/clean
→ Final checklist written to doc
```

**Output**: Shared document with complete audit, file-level migration plan, and next actions.
