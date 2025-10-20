# Adaptive Memory - Implementation Summary

## Completed (v0.2.0)

### Core Implementation

**access_tracker.py** - SQLite schema with proper normalization
- Items table: `workspace, item_id, path, content_hash, concept, created_ts`
- Queries table: `qid, workspace, query, issued_ts, qhash, qembedding`
- Interactions table: `id, qid, item_id, useful, dwell_ms, click_rank, ts`
- Workspaces table: `name, created_ts`
- Content hash deduplication (handles renames)
- Query clustering via embedding similarity
- SQLite WAL mode, proper indices, foreign keys

**smart_memory.py** - Multi-factor scoring with time decay
- Scoring: `α*S_sem + β*W_learned + γ*C_concept + δ*R_recency`
- Learned weight: `sigmoid(a1*votes + a2*dwell + a3*rank - a5*decay)`
- Exponential half-life decay (default 14 days)
- Configurable ScoringConfig with all coefficients
- Explicit feedback: +1 (useful), -1 (not useful), 0 (neutral)
- Implicit feedback: dwell_ms, click_rank
- Query clustering for pattern transfer

**CLI (amem)** - Complete command-line interface
```bash
amem index <workspace> <path> [--concepts X]
amem search <workspace> <query> [--k N] [--explain] [--baseline]
amem feedback <workspace> <query> <file> useful|notuseful [--dwell MS] [--rank N]
amem stats <workspace>
amem workspaces
amem doctor
```

### Features

- [x] Access pattern learning without training
- [x] Time-aware decay (exponential half-life)
- [x] Implicit feedback (dwell, click rank)
- [x] Content hash for rename tracking
- [x] Query embedding similarity for clustering
- [x] Multi-factor scoring framework
- [x] Score breakdown with `--explain`
- [x] A/B baseline comparison with `--baseline`
- [x] Health check with `amem doctor`

### Architecture

```
playbooks/
├── browser-research-toolkit/  # Sibling dependency (imported)
└── adaptive-memory/
    ├── adaptive_memory/
    │   ├── __init__.py         # Clean exports
    │   ├── access_tracker.py   # Schema + queries
    │   ├── smart_memory.py     # Scoring engine
    │   └── cli/amem.py         # CLI tool
    ├── README.md               # Comprehensive docs
    ├── TODO.md                 # Future work
    └── pyproject.toml          # Package config
```

## TODO (See TODO.md)

### High Priority
- C_concept term (concept hierarchy boost)
- R_recency term (freshness boost)
- Cross-query transfer (a4)
- Cross-workspace transfer (a6)

### Medium Priority
- Adaptive β coefficient
- Metrics collection (nDCG@10, Recall@10)
- Path rename handling improvements
- Query normalization

### Low Priority
- Multi-workspace CLI restoration
- Concept tree CLI
- Testing suite
- Performance optimization

## Usage Example

```bash
# Index codebase
amem index myapp ./src --concepts "Backend,API"

# Search with learned ranking
amem search myapp "JWT authentication"

# Search with score breakdown
amem search myapp "auth flow" --explain

# Provide feedback
amem feedback myapp "JWT auth" src/auth.py useful --dwell 1200 --rank 1

# Compare baseline vs learned
amem search myapp "JWT tokens" --baseline  # semantic only
amem search myapp "JWT tokens"              # with learning

# Stats
amem stats myapp

# Health check
amem doctor
```

## Scoring Formula

```
score(item|query) =
  0.6 * semantic_similarity +
  0.3 * sigmoid(
    1.0*(pos_votes - neg_votes) +
    0.8*(dwell_ms/1000) +
    0.6*(1/click_rank) -
    0.5*(1 - exp_decay)
  ) +
  0.1 * concept_similarity +
  0.0 * recency_boost
```

Time decay: `2^(-Δt / 14_days_ms)`

## Performance Targets

- **Recall@10**: +10-20% vs semantic-only baseline
- **nDCG@10**: +10-20% on warm queries (after 1 week of feedback)
- **Time-to-useful**: Reduced latency to first useful result

## Key Innovations

1. **No training required**: Learns directly from access logs
2. **Time-aware**: Recent signals weighted more heavily
3. **Implicit + explicit**: Captures both intentional and behavioral feedback
4. **Content-based dedup**: Handles file renames gracefully
5. **Query clustering**: Transfers learning across similar queries
6. **Explainable**: `--explain` shows exact score components
7. **A/B ready**: `--baseline` for controlled comparison

## Credits

Built on Browser Research Toolkit (BRT) by @anthropics.

Scoring inspired by learning-to-rank and implicit feedback research.
