#!/usr/bin/env python3
"""Adaptive Memory CLI

Usage:
    amem index <workspace> <path> [--concepts CONCEPTS]
    amem search <workspace> <query> [--k NUM] [--explain] [--baseline]
    amem feedback <workspace> <query> <file> useful|notuseful [--dwell MS] [--rank N]
    amem stats <workspace>
    amem workspaces
    amem doctor
"""
import click
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'browser-research-toolkit' / 'packages' / 'memory-store'))

from ..smart_memory import SmartMemory


# Track workspace instances
_workspaces = {}


def get_memory(workspace: str) -> SmartMemory:
    """Get or create workspace memory."""
    if workspace not in _workspaces:
        _workspaces[workspace] = SmartMemory(workspace=workspace)
    return _workspaces[workspace]


@click.group()
def cli():
    """Adaptive Memory - Context engineering with learned-from-use relevance ranking."""
    pass


@cli.command()
@click.argument('workspace')
@click.argument('path', type=click.Path(exists=True))
@click.option('--concepts', help='Comma-separated list of concepts')
@click.option('--recursive/--no-recursive', default=True)
@click.option('--extensions', default='.py,.js,.ts,.tsx,.jsx,.go,.rs,.java,.c,.cpp')
def index(workspace: str, path: str, concepts: Optional[str], recursive: bool, extensions: str):
    """Index files or directories into a workspace."""
    memory = get_memory(workspace)
    path_obj = Path(path)

    # Parse extensions
    ext_list = [e.strip() if e.startswith('.') else f'.{e.strip()}' for e in extensions.split(',')]

    # Collect files
    files = []
    if path_obj.is_file():
        files.append(path_obj)
    elif path_obj.is_dir():
        pattern = '**/*' if recursive else '*'
        for ext in ext_list:
            files.extend(path_obj.glob(f'{pattern}{ext}'))

    click.echo(f"Found {len(files)} files to index...")

    # Index
    indexed = 0
    for file_path in files:
        try:
            content = file_path.read_text(encoding='utf-8')
            rel_path = str(file_path.relative_to(Path.cwd()))

            memory.add(
                file_path=rel_path,
                content=content,
                concept=concepts
            )
            indexed += 1

            if indexed % 10 == 0:
                click.echo(f"  Indexed {indexed} files...")

        except Exception as e:
            click.echo(f"  Warning: Failed to index {file_path}: {e}", err=True)

    click.echo(f"Indexed {indexed} files into workspace '{workspace}'")
    memory.close()


@cli.command()
@click.argument('workspace')
@click.argument('query')
@click.option('--k', default=8, help='Number of results')
@click.option('--explain', is_flag=True, help='Show score breakdown')
@click.option('--baseline', is_flag=True, help='Disable learned ranking (A/B baseline)')
def search(workspace: str, query: str, k: int, explain: bool, baseline: bool):
    """Search for files in a workspace."""
    memory = get_memory(workspace)

    results = memory.query(
        query=query,
        k=k,
        use_learned=not baseline,
        explain=explain
    )

    if not results:
        click.echo(f"No results found for '{query}' in workspace '{workspace}'")
        memory.close()
        return

    click.echo(f"Results for '{query}' in '{workspace}' ({len(results)}):\n")

    if explain:
        for i, (hit, explanation) in enumerate(results, 1):
            file_path = hit.metadata.get('selector', 'unknown')
            click.echo(f"{i}. {file_path}  score={explanation['total']:.2f}")
            click.echo(f"   S_sem={explanation['S_sem']:.2f}  "
                      f"W_learned={explanation['W_learned']:.2f}  "
                      f"C_concept={explanation['C_concept']:.2f}  "
                      f"R_recency={explanation['R_recency']:.2f}")
            click.echo()
    else:
        for i, hit in enumerate(results, 1):
            file_path = hit.metadata.get('selector', 'unknown')
            score = hit.score
            snippet = hit.snippet[:150] + '...' if len(hit.snippet) > 150 else hit.snippet
            click.echo(f"{i}. {file_path} (score: {score:.3f})")
            click.echo(f"   {snippet}\n")

    memory.close()


@cli.command()
@click.argument('workspace')
@click.argument('query')
@click.argument('file_path')
@click.argument('usefulness', type=click.Choice(['useful', 'notuseful']))
@click.option('--dwell', type=int, help='Dwell time in milliseconds')
@click.option('--rank', type=int, help='Click rank (1-based)')
def feedback(workspace: str, query: str, file_path: str, usefulness: str, dwell: Optional[int], rank: Optional[int]):
    """Log feedback about a file's usefulness."""
    memory = get_memory(workspace)

    useful_value = +1 if usefulness == 'useful' else -1

    memory.log_feedback(
        query=query,
        file_path=file_path,
        useful=useful_value,
        dwell_ms=dwell or 0,
        click_rank=rank or 0
    )

    feedback_parts = [f"'{file_path}' was {usefulness} for query '{query}'"]
    if dwell:
        feedback_parts.append(f"dwell={dwell}ms")
    if rank:
        feedback_parts.append(f"rank={rank}")

    click.echo(f"Logged: {', '.join(feedback_parts)}")
    memory.close()


@cli.command()
@click.argument('workspace')
def stats(workspace: str):
    """Show statistics for a workspace."""
    memory = get_memory(workspace)
    stats = memory.get_stats()

    click.echo(f"=== Stats for '{workspace}' ===\n")
    click.echo(f"Queries: {stats.get('total_queries', 0)}")
    click.echo(f"Interactions: {stats.get('total_interactions', 0)}")
    click.echo(f"Items: {stats.get('total_items', 0)}")
    click.echo(f"Avg useful: {stats.get('avg_useful', 0):.2f}")
    click.echo(f"Avg dwell: {stats.get('avg_dwell_ms', 0):.0f}ms")
    click.echo(f"Avg click rank: {stats.get('avg_click_rank', 0):.1f}")

    if stats.get('last_activity_ts'):
        import time
        last_ts = stats['last_activity_ts'] / 1000
        last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_ts))
        click.echo(f"Last activity: {last_time}")

    memory.close()


@cli.command()
def workspaces():
    """List all workspaces."""
    from ..access_tracker import AccessTracker

    tracker = AccessTracker()
    ws_list = tracker.list_workspaces()
    tracker.close()

    if not ws_list:
        click.echo("No workspaces found. Use 'amem index' to create one.")
        return

    click.echo(f"=== Workspaces ({len(ws_list)}) ===\n")
    for ws in ws_list:
        click.echo(f"  - {ws}")


@cli.command()
def doctor():
    """Run health checks on the system."""
    click.echo("=== Adaptive Memory Health Check ===\n")

    # Check 1: SQLite
    try:
        from ..access_tracker import AccessTracker
        tracker = AccessTracker()
        tracker.close()
        click.echo("[OK] SQLite database accessible")
    except Exception as e:
        click.echo(f"[FAIL] SQLite: {e}", err=True)

    # Check 2: BRT import
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'browser-research-toolkit' / 'packages' / 'memory-store'))
        from embeddings import embed_one
        from memory import Memory
        click.echo("[OK] BRT memory-store imports working")
    except Exception as e:
        click.echo(f"[FAIL] BRT import: {e}", err=True)

    # Check 3: Embeddings
    try:
        from embeddings import embed_one
        vec = embed_one("test")
        if len(vec) > 0:
            click.echo(f"[OK] Embeddings functional (dim={len(vec)})")
        else:
            click.echo("[FAIL] Embeddings returned empty vector", err=True)
    except Exception as e:
        click.echo(f"[FAIL] Embeddings: {e}", err=True)

    # Check 4: SmartMemory
    try:
        from ..smart_memory import SmartMemory
        click.echo("[OK] SmartMemory import successful")
    except Exception as e:
        click.echo(f"[FAIL] SmartMemory: {e}", err=True)

    click.echo("\nHealth check complete.")


if __name__ == '__main__':
    cli()
