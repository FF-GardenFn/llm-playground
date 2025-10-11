# Quick Start Guide

Get your first constitutional debate running in 5 minutes.

## Prerequisites

- Python 3.10+
- API keys for at least one LLM (Claude recommended)

## Installation

```bash
cd /path/to/llm-playground/constitutional-debate

# Install package
pip install -e .

# Copy environment template
cp .env.example .env
```

## Configuration

### 1. Add Your API Keys

Edit `.env` and add at least one API key:

```bash
# Required for Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional: For GPT-4
OPENAI_API_KEY=sk-xxxxx

# Optional: For Gemini
GOOGLE_API_KEY=xxxxx
```

### 2. Configure Models (Optional)

Edit `config.yaml` to customize settings:

```yaml
models:
  enabled:
    - claude  # Enable/disable models
    - gpt4

  claude:
    model: "claude-3-5-sonnet-20241022"
    temperature: 0.7
    max_tokens: 2000
```

## Run Your First Debate

### Simple Start

```bash
debate start "What's the best authentication approach for microservices?"
```

This will:
- Use models from `config.yaml` (claude, gpt4 by default)
- Run 3 rounds of debate
- Save results to `debates/debate_xxxxx.md`

### Custom Models

```bash
debate start "Should we use TypeScript or JavaScript?" --models claude,gpt4
```

### Custom Rounds

```bash
debate start "Best database for microservices?" --rounds 5
```

## View Results

```bash
# Show latest debate
debate show debate_xxxxx

# Or just open the markdown file
cat debates/debate_xxxxx.md
```

## Example Output

```
=== Debate Complete ===
Debate ID: debate_a1b2c3d4e5f6
Rounds: 3

Consensus reached:
  Position: Use OAuth 2.1 for external APIs, mTLS for internal services
  Agreement: 100%
  Supporting: claude, gpt4

Saved to: debates/debate_a1b2c3d4e5f6.md
```

## What Happens During a Debate

### Round 1: Initial Claims
Each model makes an initial claim with evidence citations:
- Claude: "OAuth 2.1 with PKCE..." [cites RFC 6749, Auth0 docs]
- GPT-4: "mTLS for zero-trust..." [cites NIST SP 800-204]

### Round 2: Challenges
Models review each other's claims and challenge if they disagree:
- Claude challenges GPT-4: "mTLS has poor developer UX" [cites Stack Overflow survey]
- GPT-4 challenges Claude: "OAuth needs centralized server" [cites microservices.io]

### Round 3: Consensus
Models converge on agreement or document dissent:
- Consensus (100%): "Use OAuth externally, mTLS internally"
- Evidence combined from all models
- Constitutional compliance checked

## Configuration Options

### Debate Settings (config.yaml)

```yaml
debate:
  workspace: "default"          # Workspace name
  max_rounds: 3                 # Max debate rounds
  consensus_threshold: 0.75     # 75% agreement = consensus
  strict_constitutional: true   # Enforce rules strictly
```

### Memory Integration

```yaml
memory:
  enabled: true                       # Use Adaptive Memory
  workspace: "constitutional-debates" # Memory workspace
  evidence_top_k: 10                  # Top evidence to retrieve
```

## CLI Commands

```bash
# Start debate
debate start <query> [options]
  --models "claude,gpt4"      # Override config models
  --workspace "myproject"     # Workspace name
  --rounds 5                  # Max rounds
  --strict/--lenient          # Constitutional enforcement
  --config-path config.yaml   # Custom config file

# View debate
debate show <debate_id>
  --format markdown|json|tree # Output format

# Run demo
debate demo                   # Pre-configured example debate

# List workspaces
debate workspaces

# Validate debate
debate validate <debate_id>   # Check constitutional compliance
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
```bash
# Check .env file exists and has key
cat .env | grep ANTHROPIC_API_KEY

# Make sure .env is in the right directory
ls -la .env  # Should be in constitutional-debate/
```

### "No results"
Check API key has credits and model name is correct in config.yaml

### "Import error: anthropic"
```bash
pip install anthropic openai
```

### "Config file not found"
```bash
# Use full path
debate start "query" --config-path /full/path/to/config.yaml
```

## Next Steps

1. **Customize Constitutional Rules**
   - Edit `charter.py` to modify rules
   - Adjust `config.yaml` charter settings

2. **Integrate Adaptive Memory**
   - Set `memory.enabled: true` in config
   - Memory learns which evidence works over time

3. **Add More Models**
   - Implement Gemini in `debater.py`
   - Add local Llama via Ollama

4. **Visualize Debates**
   - Build web UI
   - Generate debate graphs

## Example Workflow

```bash
# 1. Index your codebase context (future: with Adaptive Memory)
# amem index myapp ./src

# 2. Run debate on technical decision
debate start "Should we migrate from REST to GraphQL?" --workspace myapp

# 3. Review results
cat debates/debate_*.md

# 4. Run related debate (benefits from learned patterns)
debate start "Best API versioning strategy?" --workspace myapp

# 5. Compare multiple debates
debate compare debate_1 debate_2
```

## Production Tips

1. **API Rate Limits**: Adjust `rate_limits` in config.yaml
2. **Costs**: Monitor token usage in API dashboards
3. **Caching**: Enable `dev.use_cache: true` for testing
4. **Logging**: Set `logging.level: DEBUG` for troubleshooting

## Help

```bash
debate --help
debate start --help
```

## Ready?

```bash
debate demo
```

This runs a pre-configured debate showcasing the full system.

Enjoy constitutional debates! 🏛️
