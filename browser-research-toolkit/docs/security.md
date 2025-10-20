Security model

Scope
- Local-first, LAN-only by default. Do not expose servers to the public internet.

Siri daemon guardrails
- Token auth (required): Authorization: Bearer <token>
- Fixed orchestrator paths; no arbitrary shell
- Timeouts and output truncation
- Optional (config.yaml → security):
  - enable_pii_redaction: redact emails/long numbers/API-key-like tokens from stdout/stderr
  - strict_domain_validation: reject malformed domain patterns in utterances
  - max_utterance_len: cap utterance size
  - rate_limit_per_minute: per-IP requests/minute limit

MCP Charter server
- API key via BRT_CHARTER_API_KEY; request size limits; evidence text only
- Allowed domains enforced server-side based on CHARTER.md

Memory store
- Task-local indices; snapshot on /clean; drop by default
- Text-only ingestion; never store scripts or credentials

Recommendations
- Use firewall rules to restrict to local network
- Rotate tokens regularly; store in env or local secret manager
- Monitor ~/.tab_orchestrator/ for unexpected changes
