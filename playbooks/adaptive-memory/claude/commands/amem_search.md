# Search with Learned Ranking

Goal: Retrieve relevant items ranked by semantic + learned signals.

Command (standard):
```bash
cd playbooks/adaptive-memory
amem search <workspace> "<query>" --k 20
```

Command (with score breakdown):
```bash
amem search <workspace> "<query>" --k 10 --explain
```

Options:
- --baseline: Compare vs semantic-only ranking
- --k: Number of results

Tips:
- Use --explain to see S_sem, W_learned, and other terms contributing to the score.
