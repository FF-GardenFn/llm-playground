# Index Files into Adaptive Memory

Goal: Add source files to a workspace with optional concept labels.

Prerequisites:
- Python 3.10+
- Install package:
  - cd playbooks/adaptive-memory && pip install -e .
- Ensure BRT memory-store is available (bundled in this repo)

Command:
```bash
cd playbooks/adaptive-memory
amem index <workspace> <path> \
  --concepts "Backend,API,Auth" \
  --extensions ".py,.md,.txt"
```

Notes:
- Items are deduplicated by content hash and tracked for feedback.
- Use meaningful concepts to enable future concept boosts.
