"""Example: Complete RFT Workflow

This example demonstrates the full pipeline:
1. Generate constitutional debates
2. Export to RFT format
3. Use with OpenAI's Reinforcement Fine-Tuning API

This is the "StackOverflow for LLMs" approach - using multi-model debates
to create high-quality training data for model distillation.
"""
import asyncio
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from constitutional_debate.charter import Charter
from constitutional_debate.config import load_config
from constitutional_debate.orchestrator import Orchestrator, DebateConfig
from constitutional_debate.debate_tree import ModelType
from constitutional_debate.export_rft import export_debates_for_rft


async def generate_sample_debates():
    """Generate sample debates for RFT training.

    In production, you'd generate many debates on diverse topics.
    """
    # Load configuration
    config = load_config()

    # Create charter
    charter = Charter.default()

    # Configure debate
    debate_config = DebateConfig(
        models=[ModelType.CLAUDE, ModelType.GPT4],  # Multi-model debate
        workspace="rft-training-generation",
        max_rounds=3,
        enable_memory=False,  # Disable for this example (can enable later)
        consensus_threshold=0.75
    )

    # Create orchestrator
    orchestrator = Orchestrator(charter, debate_config, config)

    # Sample queries for diverse training data
    queries = [
        "What's the best authentication approach for microservices?",
        "Should we use TypeScript or JavaScript for a new web application?",
        "What database is best for real-time analytics: PostgreSQL, MongoDB, or Cassandra?",
        "How should we implement API rate limiting?",
        "What's the optimal caching strategy for a high-traffic web application?"
    ]

    debates = []
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Starting debate: {query}")
        print('='*60)

        debate = await orchestrator.run_full_debate(query)
        debates.append(debate)

        print(f"\nDebate {debate.debate_id} complete!")
        if debate.final_consensus:
            print(f"Consensus: {debate.final_consensus.position}")
            print(f"Agreement: {debate.final_consensus.agreement_pct}%")

    return debates


def export_to_rft(debates):
    """Export debates to RFT format."""
    output_dir = Path("rft_training_data")
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("Exporting debates to RFT format...")
    print('='*60)

    stats = export_debates_for_rft(
        debates,
        output_dir,
        train_split=0.8  # 80% train, 20% validation
    )

    print(f"\nExport complete!")
    print(f"Training examples: {stats['train']}")
    print(f"Validation examples: {stats['validation']}")
    print(f"\nFiles created:")
    print(f"  - {output_dir}/rft_train.jsonl")
    print(f"  - {output_dir}/rft_validation.jsonl")
    print(f"  - {output_dir}/rft_grader_config.json")

    return output_dir


def show_rft_usage(output_dir):
    """Show how to use the exported data with OpenAI RFT."""
    print(f"\n{'='*60}")
    print("Next Steps: Use with OpenAI RFT API")
    print('='*60)

    print("""
To fine-tune a model with this data:

1. Upload training files:
   ```bash
   # Upload training data
   TRAIN_FILE_ID=$(openai api files.create \\
     -f {output_dir}/rft_train.jsonl \\
     -p fine-tune \\
     | jq -r '.id')

   # Upload validation data
   VAL_FILE_ID=$(openai api files.create \\
     -f {output_dir}/rft_validation.jsonl \\
     -p fine-tune \\
     | jq -r '.id')
   ```

2. Create RFT fine-tuning job:
   ```bash
   openai api fine_tuning.jobs.create \\
     -m o4-mini-2025-04-16 \\
     --training_file $TRAIN_FILE_ID \\
     --validation_file $VAL_FILE_ID \\
     --method reinforcement \\
     --grader_config {output_dir}/rft_grader_config.json
   ```

3. Monitor training:
   ```bash
   openai api fine_tuning.jobs.get -i <job_id>
   ```

4. Use the fine-tuned model:
   ```python
   from openai import OpenAI
   client = OpenAI()

   response = client.chat.completions.create(
       model="ft:o4-mini-2025-04-16:...",  # Your fine-tuned model
       messages=[{{"role": "user", "content": "Best auth for microservices?"}}]
   )
   ```

The resulting model will:
- Follow constitutional rules (evidence citation, source attribution)
- Generate higher quality, evidence-backed responses
- Show improved reasoning on technical debates
- Cost less to run than the ensemble (GPT-4 + Claude)

This is knowledge distillation via constitutional debates!
""".format(output_dir=output_dir))


async def main():
    """Run complete RFT workflow example."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Constitutional Debate → RFT Training Data Pipeline         ║
║                                                              ║
║  "StackOverflow for LLMs"                                   ║
║  Multi-model debates → Graded training data → Fine-tuned model║
╚══════════════════════════════════════════════════════════════╝
""")

    # Step 1: Generate debates
    print("\nSTEP 1: Generating constitutional debates...")
    debates = await generate_sample_debates()

    # Step 2: Export to RFT
    print("\nSTEP 2: Exporting to RFT format...")
    output_dir = export_to_rft(debates)

    # Step 3: Show usage
    show_rft_usage(output_dir)

    print(f"\n{'='*60}")
    print("Pipeline complete! 🎉")
    print('='*60)
    print(f"\nYou now have:")
    print(f"  ✓ {len(debates)} debates with multi-model consensus")
    print(f"  ✓ RFT training data with constitutional grading")
    print(f"  ✓ Grader config for OpenAI API")
    print(f"\nReady to fine-tune a model that learned from the ensemble!")


if __name__ == "__main__":
    # Check API keys
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set")
        print("Set it in .env file or environment")
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set")
        print("Set it in .env file or environment")
        sys.exit(1)

    # Run async main
    asyncio.run(main())
