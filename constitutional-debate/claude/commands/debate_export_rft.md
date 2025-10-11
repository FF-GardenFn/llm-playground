# Export Debates to RFT Format

Goal: Convert debate trees into Reinforcement Fine-Tuning (RFT) training data for OpenAI's API.

What this does:
- Converts debate trees into JSONL format for RFT
- Creates grader configuration for OpenAI API
- Exports to rft_train.jsonl and rft_validation.jsonl
- Generates rft_grader_config.json with multi-grader setup

Command:
```bash
cd constitutional-debate
debate export-rft --input debates/ --output rft_data/
```

Options:
```bash
debate export-rft <input_dir> --output <output_dir> \
  --train-split 0.8 \
  --strict  # Use strict constitutional validation
```

What gets exported:
1. **rft_train.jsonl**: Training examples with:
   - `messages`: The debate query/context
   - `constitutional_compliance`: Rule adherence score (0-1)
   - `evidence_quality`: Evidence quality score (0-1)
   - `consensus_participation`: Consensus contribution score (0-1)
   - Metadata: debate_id, model, node_id, round_num

2. **rft_validation.jsonl**: Same format for validation set

3. **rft_grader_config.json**: Multi-grader configuration for OpenAI RFT API:
   - Constitutional compliance grader (40% weight)
   - Evidence quality grader (30% weight)
   - Consensus participation grader (30% weight)

Using the exported data with OpenAI RFT:
```bash
# 1. Upload files to OpenAI
openai api files.create -f rft_train.jsonl -p fine-tune
openai api files.create -f rft_validation.jsonl -p fine-tune

# 2. Create RFT job with grader config
# See: https://platform.openai.com/docs/guides/reinforcement-fine-tuning
```

Notes:
- Requires debates/ directory with completed debate trees
- Each debate becomes multiple training examples (one per claim)
- Grader scores are pre-computed during export for reference
- Python graders in config validate responses during training
