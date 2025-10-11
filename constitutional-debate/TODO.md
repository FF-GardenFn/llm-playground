# Constitutional Debate TODO

High priority
- [ ] Implement Gemini client using google-generativeai SDK
- [ ] Implement Llama local client (Ollama or similar)
- [ ] Add retries, timeouts, and structured logging to all client calls
- [ ] Unit tests for debaters/utils.py (parse_evidence, extract_claim_content)

Medium priority
- [ ] Extract prompt templates into constants for easier auditing
- [ ] Add per-model defaults in ModelConfig (temperature, max_tokens)
- [ ] Parallelize calls with asyncio.gather and per-task timeouts

Low priority
- [ ] CLI validate command to run Charter validation over saved trees
- [ ] Export debates as JSONL alongside markdown
- [ ] Embedding-based consensus grouping in orchestrator

Notes
- This refactor splits debater implementations across small modules under constitutional_debate/debaters/.
- debater.py remains as a thin shim re-exporting public classes and factory to preserve imports.
