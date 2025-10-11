# Constitutional Debate Trees

**Multi-LLM Knowledge Distillation with Learned Evidence Ranking**

Orchestrates debates between multiple LLMs (Claude, GPT, Gemini, Llama) with constitutional rules enforcing evidence-based reasoning. Integrates with Adaptive Memory to learn which evidence actually settles debates.

## The Vision

```
User Query → Constitutional Charter → Multi-LLM Debate → Verified Answer
                                            ↓
                                    Adaptive Memory
                                    (learns which evidence works)
```

**Problem**: Single LLMs hallucinate, lack sources, cannot self-verify

**Solution**: Multi-LLM constitutional debates with enforced evidence citation

## Architecture

```
┌─────────────────────────────────────────┐
│   CONSTITUTIONAL CHARTER                 │
│   1. Must cite evidence from memory      │
│   2. Claims require source attribution   │
│   3. Challenges need prior node refs     │
│   4. Consensus = 3/4 agreement          │
│   5. Dissent must document reasoning     │
└─────────────────────────────────────────┘
              ↓
    ┌─────────────────┐
    │  ORCHESTRATOR   │
    │  - Round mgmt   │
    │  - Rule enforce │
    │  - Tree build   │
    └─────────────────┘
              ↓
┌─────────────┴─────────────┐
│                           │
│  MULTI-LLM POOL          │  ←──────┐
│  - Claude (Anthropic)    │         │
│  - GPT-4/5 (OpenAI)      │    Evidence
│  - Gemini (Google)       │    Citations
│  - Llama 3 (Local)       │         │
│                           │         │
└───────────────────────────┘         │
              ↓                       │
    ┌─────────────────┐              │
    │  DEBATE TREE    │              │
    │  - Claims       │              │
    │  - Evidence     │──────────────┘
    │  - Challenges   │
    │  - Consensus    │
    └─────────────────┘
              ↓
    ┌─────────────────┐
    │ ADAPTIVE MEMORY │
    │ Learns:          │
    │ - Which evidence │
    │   settles debates│
    │ - Cross-debate   │
    │   patterns       │
    └─────────────────┘
```

## Key Innovations

1. **Constitutional Enforcement**: Rules coded as verifiable constraints
2. **Multi-Model Diversity**: Different models = different biases revealed
3. **Learned Evidence Ranking**: Memory learns which sources actually work
4. **Verifiable Provenance**: Full chain from claim → evidence → source
5. **Knowledge Distillation**: Debate trees become high-quality training data

## Quick Start

```bash
# Install
cd /path/to/llm-playground/constitutional-debate
pip install -e .

# Set API keys
export ANTHROPIC_API_KEY=sk-...
export OPENAI_API_KEY=sk-...
export GOOGLE_API_KEY=...

# Run debate
debate start "What's the best authentication approach for microservices?" \
  --models claude,gpt4,gemini \
  --workspace microservices \
  --rounds 3

# View tree
debate show <debate_id> --format tree

# Export results
debate export <debate_id> --format markdown
```

## Example Debate

**Query**: "What's the best authentication approach for microservices?"

```
Round 1: Initial Claims
├─ Claude: "OAuth 2.1 with PKCE"
│  Evidence: [RFC 6749, auth0.com/docs/oauth2]
│
├─ GPT-5: "mTLS for zero-trust architecture"
│  Evidence: [NIST SP 800-204, Google BeyondCorp paper]
│
├─ Gemini: "API Gateway with JWT validation"
│  Evidence: [Kong docs, jwt.io/introduction]
│
└─ Llama: "Service mesh (Istio) with mutual TLS"
   Evidence: [Istio security docs, CNCF whitepaper]

Round 2: Challenges
├─ Claude → GPT-5: "mTLS has poor developer UX"
│  Evidence: [Stack Overflow developer survey 2024]
│
├─ GPT-5 → Claude: "OAuth requires centralized auth server"
│  Evidence: [microservices.io/patterns/security]
│
└─ Gemini: "Both valid - depends on threat model"
   Evidence: [OWASP API Security Top 10]

Round 3: Convergence
├─ Consensus (3/4): "OAuth 2.1 for external APIs, mTLS for internal services"
│  Supporting Evidence:
│  - Netflix Tech Blog: "Securing Microservices" [high memory score: 0.92]
│  - Google Cloud Security Whitepaper [cited 3x in past debates]
│  - Kubernetes Security Best Practices [relevance: 0.88]
│
└─ Dissent (Llama): "Service mesh simplifies both"
   Evidence: [Istio case studies, Linkerd security model]
   Reasoning: "Disagrees on operational complexity threshold"
```

**Memory learns**: Netflix blog has high signal for microservices auth debates

## Constitutional Rules

Rules are enforced via LLM prompts + programmatic validation:

### Rule 1: Evidence Citation
```python
"Every claim must cite at least one source from memory or provide a URL.
Format: [source_name, url/path]"
```

### Rule 2: Source Attribution
```python
"Quotes must attribute original author and publication date.
No anonymous claims allowed."
```

### Rule 3: Challenge References
```python
"Challenges must reference specific node IDs from the debate tree.
Format: @node_id: [your challenge]"
```

### Rule 4: Consensus Threshold
```python
"Consensus requires 75% (3/4) model agreement.
Dissenting models must document reasoning."
```

### Rule 5: Dissent Documentation
```python
"Dissent requires:
1. Which consensus point you disagree with
2. Alternative position
3. Supporting evidence
4. Reasoning for disagreement"
```

## CLI Reference

```bash
# Start new debate
debate start <query> --models <model_list> --workspace <name> [--rounds N]

# Continue existing debate
debate continue <debate_id> --rounds N

# Show debate tree
debate show <debate_id> [--format tree|json|markdown]

# Export results
debate export <debate_id> --format <markdown|json|html>

# List debates
debate list [--workspace <name>]

# Get stats
debate stats <debate_id>

# Validate debate (check constitutional compliance)
debate validate <debate_id>
```

## Python API

```python
from constitutional_debate import Orchestrator, Charter, DebateConfig
from constitutional_debate.models import Claude, GPT4, Gemini

# Configure
charter = Charter.default()  # Load constitutional rules
config = DebateConfig(
    models=[Claude(), GPT4(), Gemini()],
    workspace="microservices",
    rounds=3,
    evidence_memory=True  # Use Adaptive Memory
)

# Start debate
orchestrator = Orchestrator(charter=charter, config=config)
debate = orchestrator.start_debate(
    query="What's the best authentication for microservices?"
)

# Run rounds
for round_num in range(3):
    orchestrator.run_round(debate)

# Get consensus
consensus = orchestrator.get_consensus(debate)
print(f"Agreement: {consensus.agreement_pct}%")
print(f"Position: {consensus.position}")

# Show evidence scores (from Adaptive Memory)
for evidence in consensus.supporting_evidence:
    print(f"{evidence.source}: score={evidence.memory_score:.2f}")
```

## Why This Matters

### For Anthropic
- Showcases Constitutional AI at scale
- Perfect MCP use case (persistent learned context)
- Model-agnostic but highlights Claude's strengths
- Publication-ready research

### For Developers
- Verifiable AI reasoning (full provenance)
- Multi-model redundancy (no single-vendor risk)
- Learned memory (gets better over time)
- High-quality knowledge distillation

### For Research
- Constitutional AI + Multi-Agent Systems
- Learned evidence ranking
- Debate-driven knowledge graphs
- LLM ensemble methods

## Roadmap

**Phase 1** (Week 1): Core
- [x] Directory structure
- [ ] Debate tree data models
- [ ] Constitutional charter
- [ ] Basic orchestrator

**Phase 2** (Week 2): Multi-LLM
- [x] LLM client abstractions (modularized debaters package)
- [ ] Multi-agent coordination
- [ ] Round management
- [ ] CLI tool

**Phase 3** (Week 3): Memory
- [ ] Adaptive Memory integration
- [ ] Evidence citation tracking
- [ ] Cross-debate learning
- [ ] Memory scoring

**Phase 4** (Week 4): Polish
- [ ] Consensus detection
- [ ] Tree visualization
- [ ] Example debates
- [ ] Blog post / paper

## License

MIT

## Credits

Built on:
- Browser Research Toolkit (BRT)
- Adaptive Memory
- Constitutional AI (Anthropic)
