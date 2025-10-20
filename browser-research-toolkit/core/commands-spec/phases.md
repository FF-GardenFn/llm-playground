Commands Phases — with Dump / Index / Retrieve

Overview
- This orchestrator runs a disciplined flow inside a browser tab group with a shared doc as the single source of truth.
- Add the following boxes to keep evidence handling explicit:

1) Dump (during /harvest)
- Extract readable text + metadata (URL, selector/XPath, last-updated) for each open tab.
- Chunk: sliding window size≈800 tokens, overlap≈160.
- Hash each chunk (sha256) to deduplicate across pages and versions.
- Embed locally and upsert into the task-local Memory store.

2) Index (optional during /harvest)
- Update Concept Index nodes with centroids and ≤50-word micro‑summaries.
- Keep nodes task‑local and status="tentative" until support_docs ≥ k.
- Promotions require hysteresis and are logged as events.

3) Retrieve (during /synthesize)
- Generate 2–4 signature queries per section (base, paraphrase, counterfactual).
- kNN top-20 → optional rerank → top-k; apply MMR for diversity.
- If Concept Index is enabled, filter to the relevant subtree path.
- Insert Evidence Blocks into the doc: include URL + last‑updated + snippet.

Guardrails
- No evidence, no claim: every assertion cites its source.
- Task‑local by default; reset on /clean unless Charter sets persist.
- Respect Charter allowed_domains; never log in.
