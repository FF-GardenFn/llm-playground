# Constitutional Debate Trees - Roadmap

## Current Status (v0.1.0)

**COMPLETE**:
- [x] Core data structures (debate_tree.py)
- [x] Constitutional charter (charter.py)
- [x] LLM client abstractions (debater.py) - STUBS
- [x] Debate orchestrator (orchestrator.py)
- [x] CLI tool (cli/debate.py)
- [x] Package structure
- [x] Example debate output

**Architecture**: Working skeleton with stub LLM calls

## Phase 1: LLM Integration (Week 1)

### Priority: HIGH

**Goal**: Replace stubs with actual LLM API calls

#### Tasks:
- [ ] Implement Claude API calls (Anthropic SDK)
  - [ ] `generate_claim()` with constitutional prompt
  - [ ] `generate_challenge()` with debate context
  - [ ] Parse XML/markdown responses for evidence extraction

- [ ] Implement GPT-4 API calls (OpenAI SDK)
  - [ ] Same as Claude implementation
  - [ ] Handle function calling if needed

- [ ] Implement Gemini API calls (Google SDK)
  - [ ] Same pattern

- [ ] Implement Llama local inference (Ollama/llama.cpp)
  - [ ] Optional: lower priority

- [ ] Response parsing
  - [ ] Extract claims from LLM output
  - [ ] Extract evidence citations
  - [ ] Parse challenges and references

#### Acceptance Criteria:
- Run `debate demo` and get actual responses from Claude + GPT-4
- Responses follow constitutional format (evidence citations)
- Parse evidence into Evidence objects

## Phase 2: Adaptive Memory Integration (Week 2)

### Priority: HIGH

**Goal**: Integrate with Adaptive Memory for evidence learning

#### Tasks:
- [ ] Connect to Adaptive Memory from playbooks
  - [ ] Import SmartMemory
  - [ ] Create shared workspace for debates

- [ ] Evidence retrieval
  - [ ] Query memory for relevant evidence before debate
  - [ ] Pass evidence_pool to debaters
  - [ ] Score evidence by relevance

- [ ] Evidence learning
  - [ ] Track which evidence was cited in consensus
  - [ ] Log evidence usefulness to Adaptive Memory
  - [ ] Learn cross-debate patterns

- [ ] Citation tracking
  - [ ] Count how many times each source is cited
  - [ ] Track which debates benefited from each source
  - [ ] Boost high-citation sources in future debates

#### Acceptance Criteria:
- Debates query memory for evidence
- Evidence scores improve over multiple debates
- Can show "this evidence settled 3 debates"

## Phase 3: Consensus Detection (Week 2-3)

### Priority: MEDIUM

**Goal**: Improve consensus detection with semantic clustering

#### Tasks:
- [ ] Semantic claim clustering
  - [ ] Use embeddings to group similar positions
  - [ ] Cluster threshold tuning

- [ ] Consensus metrics
  - [ ] Calculate agreement strength
  - [ ] Identify partial consensus
  - [ ] Detect evolving positions

- [ ] Dissent extraction
  - [ ] Ask dissenting models for documentation
  - [ ] Validate dissent format
  - [ ] Track dissent reasoning

#### Acceptance Criteria:
- Consensus detection uses semantic similarity, not string matching
- Can detect 75%, 50%, 25% agreement levels
- Dissenting models properly document disagreement

## Phase 4: Visualization (Week 3)

### Priority: MEDIUM

**Goal**: Build interactive debate tree visualization

#### Tasks:
- [ ] Tree rendering
  - [ ] ASCII art tree output
  - [ ] Markdown tree output (current)
  - [ ] HTML/web tree (interactive)

- [ ] Evidence provenance graph
  - [ ] Show claim → evidence → source chains
  - [ ] Highlight high-memory-score evidence
  - [ ] Show cross-debate evidence reuse

- [ ] Stats dashboard
  - [ ] Debates per workspace
  - [ ] Consensus rate
  - [ ] Model agreement matrix
  - [ ] Top evidence sources

#### Acceptance Criteria:
- Can visualize debate as interactive tree
- Evidence provenance traceable
- Dashboard shows aggregate stats

## Phase 5: Advanced Features (Week 4)

### Priority: LOW

**Goal**: Enhancements and optimizations

#### Tasks:
- [ ] Multi-round refinement
  - [ ] Allow claims to evolve based on challenges
  - [ ] Track claim modifications
  - [ ] Convergence detection

- [ ] Cross-workspace transfer
  - [ ] Learn patterns across workspaces
  - [ ] Workspace similarity metrics
  - [ ] Recommend evidence from related debates

- [ ] Quality metrics
  - [ ] Constitutional compliance score
  - [ ] Evidence quality score
  - [ ] Consensus strength
  - [ ] Time to consensus

- [ ] Export formats
  - [ ] JSON export
  - [ ] PDF report
  - [ ] Knowledge graph export

- [ ] Web UI
  - [ ] Flask/FastAPI backend
  - [ ] React frontend
  - [ ] Live debate streaming

#### Acceptance Criteria:
- Debates improve over multiple rounds
- Can export to multiple formats
- Web UI for debate viewing

## Phase 6: Research & Publication (Week 4+)

### Priority: MEDIUM

**Goal**: Document and publish

#### Tasks:
- [ ] Blog post
  - [ ] "Constitutional Debate Trees: Verifiable Multi-LLM Reasoning"
  - [ ] Example debates
  - [ ] Comparison to single-LLM approaches

- [ ] Research paper (optional)
  - [ ] Arxiv submission
  - [ ] Constitutional AI + Multi-Agent Systems
  - [ ] Learned evidence ranking results

- [ ] Anthropic collaboration
  - [ ] MCP server integration
  - [ ] Showcase Constitutional AI
  - [ ] Partnership pitch

## Quick Wins (Do First)

1. **Claude API integration** (1 day)
   - Immediate working demo
   - Shows constitutional prompts work

2. **Evidence parsing** (1 day)
   - Extract citations from responses
   - Build Evidence objects

3. **Adaptive Memory hookup** (1 day)
   - Query for evidence
   - Log citations

4. **Demo polish** (1 day)
   - Clean up example debate
   - Better formatting
   - Add ASCII tree

## Success Metrics

**Technical**:
- [ ] 90%+ constitutional compliance
- [ ] Evidence in 95%+ of claims
- [ ] Consensus in 70%+ of debates (3 rounds)

**Impact**:
- [ ] Anthropic interest/collaboration
- [ ] 100+ GitHub stars
- [ ] Blog post views: 1K+
- [ ] Research paper acceptance (if submitted)

**Learning**:
- [ ] Evidence scores improve over 10 debates
- [ ] Cross-debate transfer demonstrable
- [ ] Memory reduces time to consensus

## Dependencies

**Required**:
- Anthropic API key (Claude)
- OpenAI API key (GPT-4)

**Optional**:
- Google API key (Gemini)
- Ollama (local Llama)

**Internal**:
- Adaptive Memory (playbooks/adaptive-memory)
- BRT (playbooks/browser-research-toolkit)

## Next Steps (Immediate)

1. Implement Claude API call in `debater.py:Claude.generate_claim()`
2. Test with `debate demo`
3. Parse evidence from response
4. Integrate Adaptive Memory
5. Run real debate and save results

The foundation is built. Time to make it real.
