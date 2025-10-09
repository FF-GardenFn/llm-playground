# Adaptive Memory TODO

## High Priority

### C_concept Term (Concept Hierarchy Boost)
- [ ] Implement concept tree from BRT concept_index
- [ ] Add ancestor propagation with λ attenuation (λ=0.6)
- [ ] Compute C_concept(i,q) = similarity(query→concept) * accumulated_weight
- [ ] Update smart_memory.py to populate c_concept in query()

### R_recency Term (Freshness Boost)
- [ ] Add last_modified_ts to items table
- [ ] Implement recency_score = exp(-Δt / T_recency)
- [ ] Make T_recency configurable in ScoringConfig
- [ ] Update smart_memory.py to populate r_recency in query()

### Cross-Query Transfer (a4 coefficient)
- [ ] Implement transfer_weight calculation in _learned_weight()
- [ ] Average learned weights from similar queries in cluster
- [ ] Weight by similarity threshold (cosine >= τ)
- [ ] Add transfer_term = a4 * avg_transfer to sigmoid

### Cross-Workspace Transfer (a6 coefficient)
- [ ] Extend get_similar_queries() to accept cross_workspace flag
- [ ] Query similar patterns from other workspaces
- [ ] Apply small coefficient (a6=0.2) for cross-workspace signals
- [ ] Add workspace overlap threshold check

## Medium Priority

### Adaptive β Coefficient
- [ ] Auto-reduce β when interaction_count < N (e.g., N=10)
- [ ] Auto-increase α proportionally to maintain total weight
- [ ] Implement in SmartMemory.__init__ or query()

### Metrics Collection
- [ ] Add metrics table: workspace, week, recall@10, ndcg@10, time_to_useful
- [ ] Implement calc_ndcg() helper
- [ ] Add amem metrics <workspace> command
- [ ] Track baseline vs learned performance

### Path Rename Handling
- [ ] Maintain content_hash → latest_path mapping
- [ ] Update path on add() if hash exists with different path
- [ ] Show "renamed from X" in stats

### Query Normalization
- [ ] Implement canonicalize(query) for consistent qhash
- [ ] Lowercase, strip, collapse whitespace
- [ ] Store normalized form in queries table

## Low Priority

### Multi-Workspace CLI
- [ ] Restore multi_workspace.py with SmartMemory backend
- [ ] Add amem compare <ws1> <ws2> back
- [ ] Add amem search-all <query> for cross-workspace search

### Concept Tree CLI
- [ ] Restore concept_memory.py with SmartMemory backend
- [ ] Add amem concepts <workspace> --tree
- [ ] Show weighted concept tree with propagated signals

### Testing
- [ ] Unit tests for AccessTracker
- [ ] Unit tests for SmartMemory scoring
- [ ] Integration tests for full workflow
- [ ] A/B test harness for baseline comparison

### Documentation
- [ ] Add RESULTS.md with example metrics
- [ ] Add ARCHITECTURE.md with detailed design
- [ ] Add examples/ directory with notebooks
- [ ] Video demo of cold→warm improvement

## Refactoring

### Clean Up Old Files
- [ ] Remove or simplify concept_memory.py
- [ ] Remove or simplify multi_workspace.py
- [ ] Remove demo code from __main__ blocks
- [ ] Consolidate imports

### Optimization
- [ ] Batch interaction queries
- [ ] Cache query embeddings
- [ ] Add connection pooling for SQLite
- [ ] Profile scoring function

## Future 

### Sparse Autoencoders (Post-MVP)
- [ ] Train sparse autoencoder on access patterns
- [ ] Use learned features as additional boost
- [ ] Compare vs hand-crafted features

### LLM Integration
- [ ] Add LLM-based query expansion
- [ ] Generate concept labels automatically
- [ ] Summarize learned patterns
- [ ] debugger with --explain

