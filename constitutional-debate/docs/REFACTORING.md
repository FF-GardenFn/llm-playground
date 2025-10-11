Refactor: Split monolithic debater.py into modular package

Summary
- Date: 2025-10-11
- Scope: constitutional_debate.debater → constitutional_debate.debaters/*
- Goal: Improve maintainability, clarity, and testability by separating responsibilities across small, focused modules.

What changed
- New package: constitutional_debate/debaters/
  - base.py: Debater abstract class and shared helpers
  - utils.py: Response parsing helpers (parse_evidence, extract_claim_content)
  - claude.py: Anthropic Claude client
  - openai_gpt.py: OpenAI GPT4/GPT5 and O4 clients
  - gemini.py: Google Gemini client (stub)
  - llama.py: Local Llama client (stub)
  - factory.py: create_debater(ModelType, Config, Charter)
- Shim: constitutional_debate/debater.py now re-exports from debaters/ to preserve existing imports.

Why
- The previous debater.py had ~700+ lines mixing:
  - abstract interface, helpers, 5+ client implementations, and a factory
- Effects:
  - Harder to navigate and reason about changes
  - Harder to unit test utilities vs. client logic independently
  - Higher merge conflicts as the file grew

Design principles (rft.md / rft2.md alignment)
- Separation of concerns: each provider in its own module; base contract isolated
- Deterministic prompts and explicit error handling (no silent failures)
- Small, composable units to enable rigorous testing and iteration
- Backwards compatibility maintained via a thin shim to avoid breaking imports

Follow-ups
- Implement Gemini and Llama clients (replace stubs)
- Add unit tests for debaters.utils parsing functions
- Add retries/timeouts and structured logging per client
- Consider extracting prompts into constants for easier auditing

Impact
- No changes required for callers importing from constitutional_debate.debater
- Orchestrator and CLI continue to function; internal structure is cleaner
