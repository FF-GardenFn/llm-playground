# Log Feedback (Explicit + Implicit)

Goal: Record usefulness, dwell time, and click rank to improve learned ranking.

Command:
```bash
cd playbooks/adaptive-memory
amem feedback <workspace> "<query>" <path/to/file> useful \
  --dwell 1200 --rank 2
```

Notes:
- useful can be: useful | notuseful | neutral
- dwell is milliseconds; rank is 1-based click rank
- Feedback updates learned weights via a time-decayed function
