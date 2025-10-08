#!/usr/bin/env python3
"""Adaptive Memory CLI - Day 5

Command-line interface for the adaptive memory system.

Usage:
    amem index <workspace> <path> [--concepts CONCEPTS]
    amem search <workspace> <query> [--k NUM] [--no-learn]
    amem feedback <workspace> <query> <file> (useful|not-useful)
    amem stats <workspace>
    amem concepts <workspace> [--tree]
    amem workspaces
    amem compare <ws1> <ws2> [<ws3>...]
    amem demo

Examples:
    # Index a codebase
    amem index myapp ./src --concepts "Web,Backend,API"

    # Search with learned ranking
    amem search myapp "JWT authentication"

    # Provide feedback
    amem feedback myapp "JWT auth" middleware/auth.py useful

    # View statistics
    amem stats myapp

    # Show concept tree
    amem concepts myapp --tree

    # Compare workspaces
    amem compare backend frontend

    # Run interactive demo
    amem demo
"""
import click
from pathlib import Path
from typing import Optional, List
import sys

from ..multi_workspace import MultiWorkspaceMemory


# Global manager instance
_manager: Optional[MultiWorkspaceMemory] = None


def get_manager() -> MultiWorkspaceMemory:
    """Get or create the global manager instance."""
    global _manager
    if _manager is None:
        _manager = MultiWorkspaceMemory()
    return _manager


@click.group()
def cli():
    """Adaptive Memory - Learning context management for codebases."""
    pass


@cli.command()
@click.argument('workspace')
@click.argument('path', type=click.Path(exists=True))
@click.option('--concepts', help='Comma-separated list of concepts')
@click.option('--recursive/--no-recursive', default=True, help='Recursively index directories')
@click.option('--extensions', default='.py,.js,.ts,.tsx,.jsx,.go,.rs,.java,.c,.cpp', help='File extensions to index')
def index(workspace: str, path: str, concepts: Optional[str], recursive: bool, extensions: str):
    """Index files or directories into a workspace.

    \b
    Examples:
        amem index myapp ./src --concepts "Backend,API"
        amem index frontend ./components --concepts "React,UI"
    """
    manager = get_manager()
    path_obj = Path(path)

    # Parse concepts
    concept_list = [c.strip() for c in concepts.split(',')] if concepts else None

    # Parse extensions
    ext_list = [e.strip() if e.startswith('.') else f'.{e.strip()}' for e in extensions.split(',')]

    # Collect files
    files_to_index = []
    if path_obj.is_file():
        files_to_index.append(path_obj)
    elif path_obj.is_dir():
        pattern = '**/*' if recursive else '*'
        for ext in ext_list:
            files_to_index.extend(path_obj.glob(f'{pattern}{ext}'))

    click.echo(f"Found {len(files_to_index)} files to index...")

    # Index files
    indexed = 0
    for file_path in files_to_index:
        try:
            content = file_path.read_text(encoding='utf-8')
            rel_path = str(file_path.relative_to(Path.cwd()) if path_obj != file_path else file_path)

            manager.add_file(
                workspace=workspace,
                file_path=rel_path,
                content=content,
                concepts=concept_list,
                metadata={'last_updated': None}
            )
            indexed += 1

            if indexed % 10 == 0:
                click.echo(f"  Indexed {indexed} files...")

        except Exception as e:
            click.echo(f"  Warning: Failed to index {file_path}: {e}", err=True)

    click.echo(f"✅ Indexed {indexed} files into workspace '{workspace}'")


@cli.command()
@click.argument('workspace')
@click.argument('query')
@click.option('--k', default=8, help='Number of results to return')
@click.option('--no-learn', is_flag=True, help='Disable learned ranking')
@click.option('--no-concepts', is_flag=True, help='Disable concept boosting')
@click.option('--snippet/--full', default=True, help='Show snippet or full text')
def search(workspace: str, query: str, k: int, no_learn: bool, no_concepts: bool, snippet: bool):
    """Search for files in a workspace.

    \b
    Examples:
        amem search myapp "JWT authentication"
        amem search myapp "error handling" --k 5 --no-learn
    """
    manager = get_manager()

    results = manager.query(
        query=query,
        workspace=workspace,
        k=k,
        use_learned=not no_learn,
        use_concepts=not no_concepts
    )

    if not results:
        click.echo(f"No results found for '{query}' in workspace '{workspace}'")
        return

    click.echo(f"Results for '{query}' in '{workspace}' ({len(results)}):\n")
    for i, hit in enumerate(results, 1):
        file_path = hit.metadata.get('selector', 'unknown')
        score = hit.score
        text = hit.snippet if snippet else hit.text

        click.echo(f"{i}. {file_path} (score: {score:.3f})")
        click.echo(f"   {text[:200]}...\n" if len(text) > 200 else f"   {text}\n")


@cli.command()
@click.argument('workspace')
@click.argument('query')
@click.argument('file_path')
@click.argument('usefulness', type=click.Choice(['useful', 'not-useful']))
def feedback(workspace: str, query: str, file_path: str, usefulness: str):
    """Log feedback about a file's usefulness for a query.

    \b
    Examples:
        amem feedback myapp "JWT auth" middleware/auth.py useful
        amem feedback myapp "JWT auth" models/user.py not-useful
    """
    manager = get_manager()
    useful = (usefulness == 'useful')

    manager.log_feedback(
        workspace=workspace,
        query=query,
        file_path=file_path,
        useful=useful
    )

    click.echo(f"✅ Logged: '{file_path}' was {usefulness} for query '{query}'")


@cli.command()
@click.argument('workspace')
def stats(workspace: str):
    """Show statistics for a workspace.

    \b
    Examples:
        amem stats myapp
    """
    manager = get_manager()
    memory = manager.get_workspace(workspace)

    if not memory:
        click.echo(f"Workspace '{workspace}' not found", err=True)
        return

    stats = memory.get_stats()

    click.echo(f"=== Stats for '{workspace}' ===\n")
    click.echo(f"Queries: {stats.get('total_queries', 0)}")
    click.echo(f"Accesses: {stats.get('total_accesses', 0)}")
    click.echo(f"Useful %: {stats.get('useful_percentage', 0)}%")
    click.echo(f"Concepts: {stats.get('total_concepts', 0)}")
    click.echo(f"Tree depth: {stats.get('concept_tree_depth', 0)}")
    click.echo(f"Files with concepts: {stats.get('files_with_concepts', 0)}")

    top_files = stats.get('top_files', [])
    if top_files:
        click.echo(f"\nTop useful files:")
        for file_info in top_files[:5]:
            path = file_info['path']
            usefulness = file_info['usefulness']
            accesses = file_info['accesses']
            click.echo(f"  - {path} ({usefulness:.2f} useful, {accesses} accesses)")


@cli.command()
@click.argument('workspace')
@click.option('--tree', is_flag=True, help='Show concept tree hierarchy')
@click.option('--query', help='Show path for specific concept/query')
def concepts(workspace: str, tree: bool, query: Optional[str]):
    """Show concepts in a workspace.

    \b
    Examples:
        amem concepts myapp
        amem concepts myapp --tree
        amem concepts myapp --query "JWT validation"
    """
    manager = get_manager()
    memory = manager.get_workspace(workspace)

    if not memory:
        click.echo(f"Workspace '{workspace}' not found", err=True)
        return

    if query:
        path = memory.get_concept_path(query)
        click.echo(f"Concept path for '{query}':")
        click.echo(f"  {path}")
        return

    if tree:
        click.echo(f"=== Concept Tree for '{workspace}' ===\n")
        tree_data = memory.get_concept_tree()
        _print_tree(tree_data, indent=0)
    else:
        concepts_set = manager.get_workspace_concepts(workspace)
        click.echo(f"=== Concepts in '{workspace}' ({len(concepts_set)}) ===\n")
        for concept in sorted(concepts_set):
            click.echo(f"  - {concept}")


def _print_tree(node: dict, indent: int = 0):
    """Recursively print concept tree."""
    label = node['label']
    support = node.get('support_docs', 0)
    prefix = "  " * indent

    if label == "root":
        click.echo(f"{prefix}[root]")
    else:
        click.echo(f"{prefix}- {label} ({support} docs)")

    for child in node.get('children', []):
        _print_tree(child, indent + 1)


@cli.command()
def workspaces():
    """List all workspaces.

    \b
    Examples:
        amem workspaces
    """
    manager = get_manager()
    ws_list = manager.list_workspaces()

    if not ws_list:
        click.echo("No workspaces found. Use 'amem index' to create one.")
        return

    click.echo(f"=== Workspaces ({len(ws_list)}) ===\n")
    for ws in ws_list:
        click.echo(f"  - {ws}")


@cli.command()
@click.argument('workspaces', nargs=-1, required=True)
def compare(workspaces: tuple):
    """Compare statistics across multiple workspaces.

    \b
    Examples:
        amem compare backend frontend
        amem compare app1 app2 app3
    """
    manager = get_manager()
    comparison = manager.compare_workspaces(list(workspaces))

    if not comparison:
        click.echo("No data found for specified workspaces", err=True)
        return

    click.echo(f"=== Workspace Comparison ===\n")

    # Table header
    click.echo(f"{'Workspace':<20} {'Queries':<10} {'Concepts':<10} {'Files':<10} {'Useful %':<10}")
    click.echo("-" * 70)

    for ws, stats in comparison.items():
        queries = stats.get('total_queries', 0)
        concepts = stats.get('total_concepts', 0)
        files = stats.get('files_with_concepts', 0)
        useful = stats.get('useful_percentage', 0)

        click.echo(f"{ws:<20} {queries:<10} {concepts:<10} {files:<10} {useful:<10.1f}")

    # Find shared concepts
    shared = manager.find_shared_concepts(list(workspaces))
    if shared:
        click.echo(f"\nShared concepts: {', '.join(sorted(shared))}")


@cli.command()
def demo():
    """Run an interactive demo of adaptive memory.

    \b
    Examples:
        amem demo
    """
    click.echo("=== Adaptive Memory Interactive Demo ===\n")

    # Create demo workspace
    manager = get_manager()
    workspace = "demo"

    click.echo("Step 1: Adding sample files...\n")

    # Add sample files
    manager.add_file(
        workspace,
        "auth/jwt.py",
        """
def create_jwt(user_id):
    payload = {'user_id': user_id, 'exp': get_expiry()}
    return encode_token(payload, SECRET_KEY)

def verify_jwt(token):
    try:
        payload = decode_token(token, SECRET_KEY)
        return payload['user_id']
    except InvalidTokenError:
        return None
        """,
        concepts=["Authentication", "JWT", "Security"]
    )

    manager.add_file(
        workspace,
        "auth/session.py",
        """
def create_session(user_id):
    session_id = generate_session_id()
    store_in_redis(session_id, user_id)
    return session_id

def validate_session(session_id):
    return get_from_redis(session_id)
        """,
        concepts=["Authentication", "Session", "Redis"]
    )

    manager.add_file(
        workspace,
        "models/user.py",
        """
class User:
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        """,
        concepts=["Models", "User", "Database"]
    )

    click.echo("✅ Added 3 sample files\n")

    # Cold start query
    click.echo("Step 2: Cold start query (no learning yet)\n")
    click.echo("Query: 'JWT validation'\n")

    results = manager.query("JWT validation", workspace, k=3, use_learned=False)
    for i, hit in enumerate(results, 1):
        file_path = hit.metadata.get('selector', 'unknown')
        click.echo(f"  {i}. {file_path} (score: {hit.score:.3f})")

    click.echo("\nStep 3: Providing feedback...\n")

    # Simulate feedback
    manager.log_feedback(workspace, "JWT validation", "auth/jwt.py", useful=True)
    manager.log_feedback(workspace, "JWT validation", "models/user.py", useful=False)

    click.echo("  ✅ Logged: auth/jwt.py = useful")
    click.echo("  ✅ Logged: models/user.py = not useful\n")

    # Warm start query
    click.echo("Step 4: Warm start query (with learning)\n")
    click.echo("Query: 'JWT tokens' (similar to previous)\n")

    results = manager.query("JWT tokens", workspace, k=3, use_learned=True)
    for i, hit in enumerate(results, 1):
        file_path = hit.metadata.get('selector', 'unknown')
        click.echo(f"  {i}. {file_path} (score: {hit.score:.3f})")

    click.echo("\n  → Notice auth/jwt.py is boosted!\n")

    # Show concept path
    click.echo("Step 5: Concept hierarchy\n")
    path = manager.get_shared_concept_path("JWT validation")
    click.echo(f"  Concept path: {path}\n")

    # Stats
    click.echo("Step 6: Statistics\n")
    memory = manager.get_workspace(workspace)
    if memory:
        stats = memory.get_stats()
        click.echo(f"  Total queries: {stats.get('total_queries', 0)}")
        click.echo(f"  Total concepts: {stats.get('total_concepts', 0)}")
        click.echo(f"  Useful %: {stats.get('useful_percentage', 0)}%\n")

    click.echo("✅ Demo complete! Try these commands:")
    click.echo("  amem search demo 'authentication'")
    click.echo("  amem concepts demo --tree")
    click.echo("  amem stats demo")

    manager.close_all()


if __name__ == '__main__':
    cli()
