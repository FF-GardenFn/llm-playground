# Memory Store (kNN Evidence Cache + Concept Index)
**Ephemeral, per-charter memory for browser research.**  
This module gives each research task a *local* evidence cache (kNN over page chunks) and an optional *symbolic* Concept Index (tree/DAG) to route queries. It plugs into both orchestrators:

- `orchestrators/chrome-extension/` (Claude for Chrome)
- `orchestrators/mcp-clients/` (any MCP-capable client + Chrome DevTools MCP)

> Philosophy: **No evidence, no claim.** All synthesis must cite URL + last-updated from the memory store.

---

## Why this exists
- **Context window is finite.** We harvest 10–50 pages; only 1–2 are visible during synthesis.  
- **Reliability beats recall.** Task-local kNN retrieves relevant snippets with provenance; the Concept Index narrows searches to the right subtree.  
- **Safety by scope.** Indices are tied to the **Task Charter** (allowed domains, acceptance criteria) and destroyed on `/clean`.

---

## Architecture

```
          ┌──────────────────────────────────────────────────┐
          │                  Task Charter                     │
          │ (allowed_domains, acceptance, outputs, notes...)  │
          └──────────────────────────────────────────────────┘
                             │
                  during /harvest (Dump)
                             ▼
┌───────────────────────────────────────────────────────────────────┐
│             Evidence Store (kNN, per-charter, ephemeral)          │
│ chunks: {text, url, selector, last_updated, hash, embedding}      │
│ backend: FAISS (default) | Chroma | LanceDB                       │
└───────────────────────────────────────────────────────────────────┘
                             │
                   optional during /harvest
                             ▼
┌───────────────────────────────────────────────────────────────────┐
│                     Concept Index (DAG)                           │
│ nodes: {label, centroid, summary≤50w, support, children[]}        │
│ edges: typed (is-a | part-of | influences)                        │
└───────────────────────────────────────────────────────────────────┘
                             │
                 during /synthesize (Signature & Retrieve)
                             ▼
             Path-Aware Retrieval → Evidence Blocks → Synthesis
```

---

## Core flows

### 1) Dump (during `/harvest`)
1. Extract readable text + metadata from each page (URL, selector/XPath, last-updated).  
2. **Chunk** text (size≈800 tokens, overlap≈160); compute hash per chunk.  
3. **Embed** chunks (local: `bge-m3`, `gte-large`, or `nomic-embed-text`).  
4. **Upsert** into the Evidence Store with full provenance.  
5. (Optional) Update Concept Index nodes (centroid + micro-summary).

### 2) Signature & Retrieve (during `/synthesize`)
1. For each section (e.g., “CLS mitigation”), generate 2–4 **signature queries** (base, paraphrase, counterfactual).  
2. kNN on Evidence Store (**filtered** to relevant Concept subtree if in use).  
3. (Optional) **Rerank** top-20 via cross-encoder (e.g., `bge-reranker-base`), keep top-5.  
4. **MMR** (diversity) to avoid near-duplicates.  
5. Insert **Evidence Blocks** into the shared doc:
   ```
   [CLS Evidence #1] “…” — developers.chrome.com/... (last updated: 2025‑09‑14)
   ```

### 3) Clean (during `/clean`)
- Snapshot index to JSONL (audit).  
- Destroy ephemeral store (default) unless Charter sets `persist: true`.

---

## Data models

### Chunk
```json
{
  "id": "sha256:…",
  "charter_id": "audit_stripe_api_20251006",
  "url": "https://developers.chrome.com/…",
  "selector": "main#content",
  "text": "…",
  "tokens": 742,
  "split_algo": "sliding_800_160",
  "last_updated": "2025-09-14",
  "created_at": "2025-10-06T14:09:20Z",
  "embedding": [0.012, -0.031, …]
}
```

### Concept Node
```json
{
  "id": "node_cwv_cls",
  "label": "Cumulative Layout Shift (CLS)",
  "parent_id": "node_core_web_vitals",
  "children": ["node_cwv_inp"],
  "centroid": [0.01, -0.02, …],
  "support_docs": 6,
  "summary_50w": "CLS measures unexpected layout shifts…",
  "status": "stable"   // "tentative" until support ≥ k
}
```

---

## Python API (thin, explicit)

```python
# packages/memory_store/memory.py
from memory_store import Memory

mem = Memory(charter_id="audit_stripe_api_20251006", backend="faiss", basepath="~/.brt/memory")

# During /harvest
mem.add(url, text, selector="body", last_updated="2025-09-14")  # chunks + embed + upsert

# During /synthesize
evidence = mem.search("Best practices to minimize CLS", k=5, subtree="Performance > CWV > CLS")
for hit in evidence:
    print(hit.score, hit.metadata["url"], hit.snippet)

mem.snapshot("/tmp/audit_cls_evidence.jsonl")  # audit trail
mem.reset()  # wipe on /clean
```

```python
# packages/memory_store/concept_index.py
from memory_store import ConceptIndex

ci = ConceptIndex(charter_id)
ci.insert("Core Web Vitals", start_id="root")
ci.insert("Cumulative Layout Shift (CLS)")
path = ci.resolve_path("CLS mitigation")    # e.g., "Performance > CWV > CLS"
```

---

## Algorithms

### Chunking
- Sliding window 800 tokens, 160 overlap (≈20%).  
- Drop boilerplate (nav, footer) via CSS selectors where possible.  
- **Hash** each chunk to deduplicate across pages.

### Embeddings
- Local models first (privacy-by-default).  
- Cache embeddings per hash; batch during `/harvest`.

### Retrieval
- kNN top-20 → (optional) cross-encoder rerank → top-5 → **MMR** (λ≈0.7).  
- **Path filter** if using Concept Index: restrict to node subtree.

### Concept insertion (O(depth))
```python
async def insert(concept: str, start_id="root"):
    node = tree[start_id]
    d = await compare_generality(concept, node.label)  # "same_level"|"more_specific"|"more_general"
    if d == "same_level":
        return node.parent_id
    if d == "more_specific":
        for cid in node.children:
            child = tree[cid]
            if await is_related(concept, child.label):
                return await insert(concept, cid)
        return node.id
    return await handle_promotion(concept, node.id)
```

**compare_generality** (cheap & effective):
- Signals: token length, tf‑idf rarity, noun‑phrase count (more = more specific).  
- (Optional) NLI direction: test *“Every X is a Y?”* (X⇒Y → X is more specific).  
- Apply **hysteresis margin** (e.g., 0.15) to avoid oscillations.

**is_related**
- Cosine to node **centroid** (label + assigned chunks).  
- Threshold: `sim ≥ 0.35` and `sim ≥ parent_sim + 0.05`.  
- If ambiguous → attach at current node with `status="tentative"`.

**Promotion**
- Require `support_docs ≥ k` and stable margin before promoting.  
- Recompute centroids bottom‑up; append to **event log** `{time, action, from, to, reason, scores}`.

**Micro‑summaries (≤50w)**
```python
async def merge(existing, new) -> str:
    prompt = f"Merge into ≤50 words:\n1) {existing}\n2) {new}"
    return await llm(prompt)
```
- Keep last **N=5** per node with support counts; drop oldest with lowest support.

---

## Config

**Charter flag:**
```json
{
  "memory": {
    "enabled": true,
    "use_concept_index": true,
    "persist": false
  }
}
```

**Backends**
- `faiss` (default, fast, local)
- `chroma` (easy persistence, Python)
- `lance` (append-only snapshots)

**Rerankers (optional)**
- `bge-reranker-base` (small, solid)
- disable on CPU‑starved hosts

---

## Guardrails

- **Task-local only.** No cross-charter bleed unless explicitly promoted with review.  
- **Allowed domains only.** Respect Charter allowlist; never log in.  
- **Evidence required.** If no retrieved evidence meets threshold, the assistant must state gaps + where to find them.  
- **Sanitize.** Store text/snippets only—never executable scripts from DOM.  
- **Drift control.** Hash dedup + MMR + centroids; reset on Charter edit.

---

## Evaluation (keep or cut)
A/B the *same tasks* with/without Concept Index:

**Metrics (logged per run)**
- `t_synth` — time from `/init` to `/synthesize` complete (lower is better)
- `citation_rate` — % of claims with URL + last-updated (higher)
- `contradiction_find_rate` — on seeded conflicts (higher)
- `coverage` — unique sources used (higher)
- `error_rate` — wrong-tab actions / total actions (lower)

**Stop rule**  
If after 7 tasks you don’t see **≥20–30% t_synth drop** or **≥15% citation_rate lift**, keep kNN-only and disable Concept Index via Charter flag. Tune chunking/queries, then re‑test.

---

## Failure modes & mitigations

| Failure | Symptom | Fix |
|---|---|---|
| Vector soup | near-duplicate hits | hash dedup + MMR diversity |
| Query drift | generic matches | 3 signature queries + paraphrases; vertical templates |
| Promotion churn | nodes flip parents | hysteresis + min support + event log |
| Stale memory | site updated mid‑run | check `last_updated`; invalidate and re‑harvest |
| Latency | slow synth | batch embeddings during harvest; cache centroids; turn off reranker |

---

## Integration points

**Chrome Extension orchestrator**
- Hook after each tab processed in `/harvest`: `mem.add(url, text, selector, last_updated)`  
- At `/synthesize`: `mem.search(signature_query, subtree=ci.resolve_path(section))`

**MCP Clients orchestrator**
- Use MCP tools (`navigate_page`, `take_screenshot`, `list_network_requests`, `evaluate_script`) to grab text; same Memory API.

---

## Roadmap
- Export to Sheet: evidence table with URLs + dates  
- Lightweight NLI contradiction checks (`roberta-large-mnli`)  
- JSON‑schema validation for Concept Index snapshots  
- Bench harness to replay tasks from logs

---

## License
MIT
