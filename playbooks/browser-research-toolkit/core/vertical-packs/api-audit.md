# Vertical Pack: API Audit

## Scope

This vertical pack specifies the structured fields and synthesis requirements for auditing API documentation and migration paths.

## Harvest Fields

During the `/harvest` phase, extract the following fields for each API endpoint or service:

### Required Fields

- **endpoint**: Full URL path or pattern (e.g., `/v1/charges`)
- **method**: HTTP method (GET, POST, PUT, DELETE, PATCH)
- **authentication**: Authentication mechanism (API key, OAuth, JWT)
- **rate_limit**: Requests per unit time (e.g., `100/min`, `1000/hour`)
- **version**: API version (e.g., `v1`, `v2`, `2024-01-15`)
- **status**: Current status (stable, deprecated, sunset)

### Optional Fields

- **pagination**: Pagination mechanism if applicable
- **request_schema**: Link to request body schema documentation
- **response_schema**: Link to response body schema documentation
- **error_codes**: List of common error codes and meanings
- **migration_notes**: Changes from previous version
- **sunset_date**: Deprecation timeline if applicable

## Synthesis Structure

### Known

- Verified endpoint specifications
- Confirmed authentication requirements
- Documented rate limits and quotas
- Migration timelines with dates

### Unknown

- Undocumented edge cases or error conditions
- Performance characteristics under load
- Breaking changes not explicitly flagged
- Compatibility with specific client libraries

### Risks

- Endpoints marked as deprecated without clear migration path
- Rate limits insufficient for expected usage patterns
- Authentication changes requiring code modifications
- Version incompatibilities

### Next Actions

1. Test critical endpoints in sandbox environment (Owner: [name], Due: [date])
2. Update client library to support new authentication flow (Owner: [name], Due: [date])
3. Schedule migration of deprecated endpoints (Owner: [name], Due: [date])

## Charter Template

```yaml
task: "Audit [Service] API migration path"
risk_mode: "ask-before-acting"
allowed_domains:
  - [service].com/docs
  - api.[service].com/reference
  - github.com/[service]/*
forbidden_actions:
  - login
  - financial_tx
outputs:
  - doc: "[Service]_API_Audit — Charter & Synthesis"
  - sheet: "[Service]_API_Audit_endpoints"
acceptance:
  triage: "≥ 6 API reference pages captured with URL + last-updated"
  harvest: "All endpoints documented with authentication, rate limits, and version"
  synthesize: "Migration timeline established; breaking changes identified"
notes: |
  Focus on authentication changes, rate limit modifications, deprecated endpoints, and sunset timelines.
```

## Example Domains

- Stripe: `stripe.com/docs`, `github.com/stripe/*`
- Twilio: `twilio.com/docs`, `github.com/twilio/*`
- AWS: `docs.aws.amazon.com`, `aws.amazon.com/blogs/aws/*`
- GitHub: `docs.github.com`, `github.blog/*`
