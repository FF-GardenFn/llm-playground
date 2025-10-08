# Evaluation Metrics

This directory describes lightweight metrics used by the playground to assess prompt-system behaviors.

- Exact Match (EM)
  - Definition: 1 if the predicted string exactly equals the gold/reference string, else 0.
  - Use: Simple QA tasks with unambiguous answers.

- Substring Match
  - Definition: 1 if the gold/reference string is a substring of the prediction (case-insensitive), else 0.
  - Use: When predictions may contain additional context but must include a key phrase.

- Token F1 (bag-of-words)
  - Definition: Precision/Recall/F1 on lowercased, punctuation-stripped word tokens.
  - Use: Extractive QA and short-form answers where partial overlap matters.

- Accuracy (categorical)
  - Definition: Proportion of predictions that match the gold label among categorical options.
  - Use: Classification tasks, e.g., yes/no, severity levels, etc.

Notes
- For simplicity, metrics here are deterministic and local-only. No external services required.
- The eval harness writes per-run results under evals/runs/ as JSONL and summary CSV.
