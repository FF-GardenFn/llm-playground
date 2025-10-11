#!/usr/bin/env python3
"""Constitutional Debate CLI

Usage:
    debate start <query> --models <models> --workspace <name> [--rounds N]
    debate show <debate_id> [--format tree|json|markdown]
    debate validate <debate_id>
"""
import click
import asyncio
from pathlib import Path
from typing import Optional

from ..orchestrator import Orchestrator, DebateConfig
from ..charter import Charter
from ..debate_tree import ModelType
from ..config import get_config, load_config


@click.group()
def cli():
    """Constitutional Debate Trees - Multi-LLM knowledge distillation."""
    pass


@cli.command()
@click.argument('query')
@click.option('--models', default=None, help='Comma-separated list: claude,gpt4,gemini,llama (overrides config)')
@click.option('--workspace', default=None, help='Workspace name (overrides config)')
@click.option('--rounds', default=None, type=int, help='Maximum rounds (overrides config)')
@click.option('--strict/--lenient', default=None, help='Strict constitutional enforcement (overrides config)')
@click.option('--config-path', default=None, help='Path to config.yaml')
def start(query: str, models: Optional[str], workspace: Optional[str], rounds: Optional[int], strict: Optional[bool], config_path: Optional[str]):
    """Start a new constitutional debate."""

    # Load main config
    try:
        main_config = load_config(config_path) if config_path else get_config()
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        click.echo("Make sure config.yaml exists and .env has API keys set", err=True)
        return

    # Parse models (from CLI or config)
    if models:
        model_list = []
        for m in models.split(','):
            m = m.strip().lower()
            if m == 'claude':
                model_list.append(ModelType.CLAUDE)
            elif m in ['gpt4', 'gpt-4']:
                model_list.append(ModelType.GPT4)
            elif m == 'gemini':
                model_list.append(ModelType.GEMINI)
            elif m == 'llama':
                model_list.append(ModelType.LLAMA)
    else:
        # Use from config
        model_list = [ModelType(m) for m in main_config.enabled_models]

    if not model_list:
        click.echo("Error: No valid models specified", err=True)
        return

    # Use workspace from CLI or config
    workspace = workspace or main_config.debate.workspace
    rounds = rounds or main_config.debate.max_rounds
    strict = strict if strict is not None else main_config.debate.strict_constitutional

    click.echo(f"Starting debate with {len(model_list)} models: {[m.value for m in model_list]}")
    click.echo(f"Query: {query}")
    click.echo(f"Workspace: {workspace}")
    click.echo(f"Max rounds: {rounds}")
    click.echo()

    # Create orchestrator
    charter = Charter.default() if strict else Charter.lenient()
    debate_config = DebateConfig(
        models=model_list,
        workspace=workspace,
        max_rounds=rounds,
        enable_memory=main_config.memory.enabled
    )

    orchestrator = Orchestrator(charter=charter, config=debate_config, main_config=main_config)

    # Run debate
    try:
        tree = asyncio.run(orchestrator.run_full_debate(query))

        click.echo(f"\n=== Debate Complete ===")
        click.echo(f"Debate ID: {tree.debate_id}")
        click.echo(f"Rounds: {len(tree.rounds)}")

        if tree.final_consensus:
            click.echo(f"\nConsensus reached:")
            click.echo(f"  Position: {tree.final_consensus.position}")
            click.echo(f"  Agreement: {tree.final_consensus.agreement_pct:.0f}%")
            click.echo(f"  Supporting: {', '.join(m.value for m in tree.final_consensus.supporting_models)}")
        else:
            click.echo("\nNo consensus reached.")

        # Save to file
        output_dir = main_config.output_dir
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{tree.debate_id}.md"
        output_path.write_text(tree.to_markdown())
        click.echo(f"\nSaved to: {output_path}")

    except Exception as e:
        click.echo(f"Error running debate: {e}", err=True)
        import traceback
        traceback.print_exc()


@cli.command()
@click.argument('debate_id')
@click.option('--format', 'fmt', type=click.Choice(['tree', 'json', 'markdown']), default='markdown')
def show(debate_id: str, fmt: str):
    """Show debate tree."""
    debate_path = Path(f"debates/{debate_id}.md")

    if not debate_path.exists():
        click.echo(f"Debate {debate_id} not found", err=True)
        return

    content = debate_path.read_text()
    click.echo(content)


@cli.command()
@click.argument('debate_id')
def validate(debate_id: str):
    """Validate debate against constitutional rules."""
    click.echo("Validation not yet implemented (TODO)")


@cli.command()
def demo():
    """Run demo debate on microservices authentication."""
    query = "What's the best authentication approach for microservices?"

    click.echo("=== Constitutional Debate Demo ===\n")
    click.echo("This demo shows the framework structure.")
    click.echo("LLM API calls are stubs (TODO: implement actual API calls)\n")

    ctx = click.get_current_context()
    ctx.invoke(
        start,
        query=query,
        models='claude,gpt4',
        workspace='demo',
        rounds=2,
        strict=True
    )


if __name__ == '__main__':
    cli()
