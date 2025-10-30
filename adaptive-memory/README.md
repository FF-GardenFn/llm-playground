# Adaptive Memory for BRT

**Context engineering with learned-from-use relevance ranking**

No-training learning loop: access logs → ranking boost = instant compounding utility.

## Overview

Adaptive Memory builds on Browser Research Toolkit (BRT) to provide intelligent, self-improving search through actual usage patterns. It combines semantic search with learned access patterns, time-aware decay, and implicit feedback signals.

### Core Features

**Access Pattern Learning**
- Tracks which files were useful for which queries
- Content-based deduplication (handles renames via content hash)
- No ML training required

**Multi-Factor Scoring**
```
score(i|q) = α*S_sem + β*W_learned + γ*C_concept + δ*R_recency
```
- S_sem: Semantic similarity (BRT kNN + MMR)
- W_learned: Learned weight with time decay
- C_concept: Concept hierarchy boost
- R_recency: Freshness boost

**Learned Weight Function**
```
W_learned = sigmoid(
  a1*(pos_votes - neg_votes) +
  a2*zscore(dwell_ms) +
  a3*(1/mean_click_rank) +
  a4*transfer_from_similar_queries -
  a5*time_decay
)
```

**Feedback Signals**
- Explicit: useful (+1), not useful (-1), neutral (0)
- Implicit: dwell time (ms), click rank (1-based)

**Time-Aware Decay**
- Exponential half-life (default: 14 days)
- Recent signals weighted more heavily
- Prevents stale patterns from dominating

## Quick Start

```bash
# Install (from playbooks directory)
cd /path/to/llm-playground/playbooks/adaptive-memory
pip install -e .

# Index a codebase
amem index myapp ./src --concepts "Backend,API"

# Search with learned ranking
amem search myapp "authentication flow"

# Search with score breakdown
amem search myapp "JWT validation" --explain

# Provide explicit feedback
amem feedback myapp "authentication" src/auth.py useful

# Implicit feedback (dwell + rank)
amem feedback myapp "auth flow" src/auth.py useful --dwell 1200 --rank 2

# View statistics
amem stats myapp

# Compare workspaces
amem compare backend frontend

# Health check
amem doctor
```

## Architecture

```
playbooks/
├── browser-research-toolkit/    # BRT dependency (imported)
│   └── packages/memory-store/   # embeddings, memory, concept_index, chunking
└── adaptive-memory/
    ├── adaptive_memory/
    │   ├── access_tracker.py    # SQLite schema: items, queries, interactions, workspaces
    │   ├── smart_memory.py      # Multi-factor scoring with time decay
    │   ├── concept_memory.py    # Hierarchy integration
    │   ├── multi_workspace.py   # Cross-workspace support
    │   └── cli/amem.py          # CLI with --explain flag
    └── README.md
```

## Schema

**items** (content hash + path deduplication)
```sql
workspace, item_id, path, content_hash, concept, created_ts
```

**queries** (with embeddings for similarity)
```sql
qid, workspace, query, issued_ts, qhash, qembedding
```

**interactions** (explicit + implicit feedback)
```sql
id, qid, item_id, useful, dwell_ms, click_rank, ts
```

**workspaces** (partition by codebase)
```sql
name, created_ts
```

## Scoring Configuration

Default coefficients (tunable):
```python
from adaptive_memory.smart_memory import ScoringConfig

config = ScoringConfig(
    alpha=0.6,      # Semantic weight
    beta=0.3,       # Learned weight
    gamma=0.1,      # Concept weight
    delta=0.0,      # Recency weight

    a1=1.0,         # Explicit votes
    a2=0.8,         # Dwell time
    a3=0.6,         # Click rank
    a4=0.4,         # Transfer
    a5=0.5,         # Decay penalty
    a6=0.2,         # Cross-workspace

    half_life_days=14
)

memory = SmartMemory(workspace="myapp", config=config)
```

## CLI Reference

```
amem index <workspace> <path> [--concepts "A,B,C"] [--extensions ".py,.js"]
amem search <workspace> "<query>" [--k 20] [--explain] [--baseline]
amem feedback <workspace> "<query>" <path> useful|notuseful [--dwell MS] [--rank N]
amem stats <workspace>
amem concepts <workspace> [--tree] [--query "concept"]
amem compare <ws1> <ws2> [<ws3>...]
amem workspaces
amem doctor
```

### --explain Output

```
auth/middleware.py  score=0.87
  S_sem=0.62  W_learned=0.21  C_concept=0.04  R_recency=0.00
  signals: +3 useful, -1 not useful (14d half-life)
  dwell +0.8σ, mean rank 2.1, decay 0.92
```

## Python API

```python
from adaptive_memory import SmartMemory

# Initialize
memory = SmartMemory(workspace="myapp")

# Add files with concepts
item_id = memory.add(
    file_path="src/auth.py",
    content=open("src/auth.py").read(),
    concept="Authentication"
)

# Query with multi-factor scoring
results = memory.query(
    query="JWT validation",
    k=10,
    use_learned=True,
    use_concepts=True,
    explain=False
)

# Query with score breakdown
results_explained = memory.query(
    query="JWT tokens",
    k=5,
    explain=True
)

for hit, explanation in results_explained:
    print(f"{hit.metadata['selector']}: {explanation}")

# Log feedback (explicit + implicit)
memory.log_feedback(
    query="JWT validation",
    file_path="src/auth.py",
    useful=+1,
    dwell_ms=1200,
    click_rank=2
)

# Get statistics
stats = memory.get_stats()
print(f"Queries: {stats['total_queries']}")
print(f"Avg useful: {stats['avg_useful']}")
print(f"Avg dwell: {stats['avg_dwell_ms']}ms")

memory.close()
```

## Metrics (Target for MVP)

Track per-workspace, per-week:
- Recall@10 and nDCG@10 vs user-marked useful items
- Time-to-useful (ms to first click marked "useful")
- Lift over semantic-only baseline (A/B with `--baseline`)

**Target**: +10-20% nDCG@10 on "warm" queries within 1 week of feedback

## Mitigations

**Feedback loops**: Learned weight capped by β coefficient, time decay prevents stale items from dominating

**Sparse signals**: Automatically reduce β and increase α when interaction count < N

**Path churn**: Items keyed by content_hash:path, maintains hash → latest path mapping

**Privacy**: Never stores file content in logs, only IDs/paths

**Concurrency**: SQLite WAL mode, batched writes, proper indices

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Format
ruff format .
```

## License

MIT

## Credits

Built on [Browser Research Toolkit](../browser-research-toolkit) 

Scoring approach inspired by learning-to-rank and implicit feedback research.
