# Start Constitutional Debate

Goal: Launch a multi-LLM constitutional debate with enforced evidence rules.

Prerequisites:
- Python 3.10+
- Set API keys in your shell environment if using live models:
  - ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY
- Install the package:
  - cd constitutional-debate && pip install -e .

Steps:
1) Choose models and workspace
2) Set max rounds and strict mode
3) Execute the command below

Command:
```bash
cd constitutional-debate
# Example: 3 rounds, strict constitution, two models
debate start "<your question>" \
  --models claude,gpt4 \
  --workspace default \
  --rounds 3 --strict
```

Output:
- Debate ID, round stats, consensus summary if reached
- Markdown export saved under debates/<debate_id>.md

Notes:
- Use --lenient to collect outputs even with minor rule violations.
- Configure defaults via constitutional-debate/config.yaml.
