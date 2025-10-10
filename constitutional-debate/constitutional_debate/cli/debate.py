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

from ..orchestrator import Orchestrator, DebateConfig
from ..charter import Charter
from ..debate_tree import ModelType


@click.group()
def cli():
    """Constitutional Debate Trees - Multi-LLM knowledge distillation."""
    pass


@cli.command()
@click.argument('query')
@click.option('--models', default='claude,gpt4', help='Comma-separated list: claude,gpt4,gemini,llama')
@click.option('--workspace', default='default', help='Workspace name')
@click.option('--rounds', default=3, help='Maximum rounds')
@click.option('--strict/--lenient', default=True, help='Strict constitutional enforcement')
def start(query: str, models: str, workspace: str, rounds: int, strict: bool):
    """Start a new constitutional debate."""
    # Parse models
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

    if not model_list:
        click.echo("Error: No valid models specified", err=True)
        return

    click.echo(f"Starting debate with {len(model_list)} models: {[m.value for m in model_list]}")
    click.echo(f"Query: {query}")
    click.echo(f"Workspace: {workspace}")
    click.echo(f"Max rounds: {rounds}")
    click.echo()

    # Create orchestrator
    charter = Charter.default() if strict else Charter.lenient()
    config = DebateConfig(
        models=model_list,
        workspace=workspace,
        max_rounds=rounds,
        enable_memory=True
    )

    orchestrator = Orchestrator(charter=charter, config=config)

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
        output_path = Path(f"debates/{tree.debate_id}.md")
        output_path.parent.mkdir(exist_ok=True)
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
