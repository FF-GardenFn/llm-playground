# Vertical Pack: Performance Profiling

## Scope

This vertical pack specifies the structured fields and synthesis requirements for profiling web application performance using browser developer tools and trace analysis.

## Harvest Fields

During the `/harvest` phase, extract the following performance metrics:

### Core Web Vitals

- **LCP** (Largest Contentful Paint): Time to render largest element (target: < 2.5s)
- **INP** (Interaction to Next Paint): Input responsiveness (target: < 200ms)
- **CLS** (Cumulative Layout Shift): Visual stability score (target: < 0.1)

### Resource Loading

- **total_requests**: Number of network requests
- **total_size**: Total transferred bytes
- **blocking_resources**: Scripts or stylesheets blocking render
- **long_tasks**: Tasks exceeding 50ms
- **cache_hit_rate**: Percentage of resources served from cache

### Runtime Performance

- **js_execution_time**: Total JavaScript execution time
- **main_thread_blocking**: Time main thread is blocked
- **layout_shifts**: Count and magnitude of unexpected shifts
- **memory_usage**: Heap size and allocation patterns

### Critical Path

- **critical_chain**: Sequence of resources on critical rendering path
- **render_blocking**: CSS files blocking first paint
- **parser_blocking**: Scripts blocking HTML parsing

## Synthesis Structure

### Known

- Measured Core Web Vitals with comparison to thresholds
- Identified blocking resources with specific file paths
- Documented long tasks with call stacks
- Quantified layout shift sources

### Unknown

- Performance characteristics under varying network conditions
- Behavior on different device types or browser versions
- Impact of third-party scripts not under control
- Performance regression history

### Risks

- Core Web Vitals exceeding recommended thresholds
- Render-blocking resources on critical path
- Unoptimized images or fonts
- Memory leaks in long-running sessions

### Next Actions

1. Optimize [specific resource] to reduce blocking time (Owner: [name], Due: [date])
2. Implement lazy loading for below-fold images (Owner: [name], Due: [date])
3. Add performance budget monitoring to CI/CD (Owner: [name], Due: [date])

## Charter Template

```yaml
task: "Performance profile: [domain]"
risk_mode: "ask-before-acting"
allowed_domains:
  - [domain]
  - [domain]/*
forbidden_actions:
  - login
  - financial_tx
  - cookie_consent_beyond_reject
outputs:
  - doc: "[Domain]_Perf_Profile — Charter & Synthesis"
  - sheet: "[Domain]_Perf_Metrics"
acceptance:
  triage: "≥ 3 key pages captured with performance traces"
  harvest: "Core Web Vitals, blocking resources, and long tasks documented"
  synthesize: "Bottlenecks identified; optimization priorities ranked"
notes: |
  Focus on Core Web Vitals, long tasks, network waterfalls, and CLS sources.
```

## MCP Tools Integration

When using the chrome-devtools-mcp server, leverage these tools:

- `performance_start_trace`: Begin recording performance trace
- `performance_stop_trace`: End recording and retrieve trace data
- `performance_analyze_insight`: Extract structured insights from trace
- `take_screenshot`: Capture visual regression evidence
- `list_network_requests`: Analyze resource loading waterfall

## Example Domains

- Developer documentation: `developers.chrome.com/*`, `web.dev/*`
- E-commerce: `shopify.com/*`, `woocommerce.com/*`
- News/media: `nytimes.com/*`, `bbc.com/*`
