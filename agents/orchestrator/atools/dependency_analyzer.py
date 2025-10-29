#!/usr/bin/env python3
"""
dependency_analyzer.py - Analyze task dependencies and determine execution order

Usage:
    python dependency_analyzer.py --tasks tasks.json --dependencies deps.json
    python dependency_analyzer.py --tasks tasks.json --dependencies deps.json --critical-path
    python dependency_analyzer.py --tasks tasks.json --dependencies deps.json --parallel-levels
"""

import argparse
import json
import sys
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque


def topological_sort(tasks: List[str], dependencies: Dict[str, List[str]]) -> Optional[List[str]]:
    """
    Perform topological sort on task graph.

    Args:
        tasks: List of task IDs
        dependencies: Dict mapping task -> list of prerequisite tasks

    Returns:
        Ordered list of tasks, or None if cycle detected
    """
    # Build adjacency list and in-degree
    graph = defaultdict(list)
    in_degree = {task: 0 for task in tasks}

    for task, deps in dependencies.items():
        for dep in deps:
            if dep not in tasks:
                raise ValueError(f"Dependency '{dep}' not in task list for task '{task}'")
            graph[dep].append(task)
            in_degree[task] += 1

    # Kahn's algorithm
    queue = deque([t for t in tasks if in_degree[t] == 0])
    result = []

    while queue:
        task = queue.popleft()
        result.append(task)

        for neighbor in graph[task]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check if all tasks processed (no cycle)
    if len(result) == len(tasks):
        return result
    else:
        # Find cycle for debugging
        remaining = set(tasks) - set(result)
        return None


def detect_cycle(tasks: List[str], dependencies: Dict[str, List[str]]) -> Optional[List[str]]:
    """
    Detect cycle in dependency graph using DFS.

    Returns:
        Cycle path if found, None otherwise
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {task: WHITE for task in tasks}
    parent = {task: None for task in tasks}

    def dfs_visit(node: str, path: List[str]) -> Optional[List[str]]:
        color[node] = GRAY
        path.append(node)

        for dep in dependencies.get(node, []):
            if color[dep] == GRAY:
                # Back edge found - cycle detected
                cycle_start = path.index(dep)
                return path[cycle_start:] + [dep]
            elif color[dep] == WHITE:
                cycle = dfs_visit(dep, path)
                if cycle:
                    return cycle

        path.pop()
        color[node] = BLACK
        return None

    for task in tasks:
        if color[task] == WHITE:
            cycle = dfs_visit(task, [])
            if cycle:
                return cycle

    return None


def find_parallel_levels(tasks: List[str], dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """
    Group tasks into levels that can execute in parallel.

    Returns:
        List of levels, each level is list of independent tasks
    """
    in_degree = {task: len(dependencies.get(task, [])) for task in tasks}
    remaining = set(tasks)
    levels = []

    while remaining:
        # Tasks with all dependencies satisfied
        level = [t for t in remaining if in_degree[t] == 0]
        if not level:
            # Should not happen if topological sort succeeds
            raise ValueError("Cannot create levels - circular dependency or logic error")

        levels.append(level)

        # Remove completed tasks and update degrees
        for task in level:
            remaining.remove(task)
            for other in remaining:
                if task in dependencies.get(other, []):
                    in_degree[other] -= 1

    return levels


def find_critical_path(
    tasks: List[str],
    durations: Dict[str, float],
    dependencies: Dict[str, List[str]]
) -> Tuple[List[str], float]:
    """
    Find critical path (longest path through dependency graph).

    Args:
        tasks: List of task IDs
        durations: Dict mapping task -> estimated duration
        dependencies: Dict mapping task -> list of prerequisite tasks

    Returns:
        (critical_path, total_duration)
    """
    # Topological sort first
    order = topological_sort(tasks, dependencies)
    if not order:
        raise ValueError("Cannot find critical path - circular dependency")

    # Compute earliest start times
    earliest_start = {task: 0.0 for task in tasks}
    for task in order:
        for dep in dependencies.get(task, []):
            earliest_start[task] = max(
                earliest_start[task],
                earliest_start[dep] + durations.get(dep, 0.0)
            )

    # Find task with latest finish time
    finish_times = {t: earliest_start[t] + durations.get(t, 0.0) for t in tasks}
    last_task = max(tasks, key=lambda t: finish_times[t])
    total_duration = finish_times[last_task]

    # Backtrack to find critical path
    critical_path = []
    current = last_task

    while current:
        critical_path.insert(0, current)
        # Find predecessor on critical path
        predecessors = dependencies.get(current, [])
        if not predecessors:
            break

        # Critical predecessor is one with latest finish time
        current = max(
            predecessors,
            key=lambda p: finish_times[p],
            default=None
        )

    return critical_path, total_duration


def calculate_parallel_duration(
    levels: List[List[str]],
    durations: Dict[str, float]
) -> float:
    """
    Calculate total duration with parallelization.

    Args:
        levels: Parallelization levels
        durations: Task durations

    Returns:
        Total duration (sum of max duration per level)
    """
    total = 0.0
    for level in levels:
        level_duration = max(durations.get(t, 0.0) for t in level)
        total += level_duration
    return total


def main():
    parser = argparse.ArgumentParser(description='Analyze task dependencies')
    parser.add_argument('--tasks', type=str, required=True, help='JSON file with tasks')
    parser.add_argument('--dependencies', type=str, required=True, help='JSON file with dependencies')
    parser.add_argument('--critical-path', action='store_true', help='Find critical path')
    parser.add_argument('--parallel-levels', action='store_true', help='Generate parallelization levels')
    parser.add_argument('--visualize', type=str, help='Generate graph visualization (requires networkx)')
    parser.add_argument('--output', type=str, help='Output file (default: stdout)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        # Load input files
        with open(args.tasks, 'r') as f:
            tasks_data = json.load(f)

        with open(args.dependencies, 'r') as f:
            deps_data = json.load(f)

        tasks = tasks_data.get('tasks', [])
        if isinstance(tasks[0], dict):
            tasks = [t['id'] for t in tasks]

        dependencies = deps_data.get('dependencies', {})
        durations = deps_data.get('durations', {task: 1.0 for task in tasks})

        # Check for cycles
        cycle = detect_cycle(tasks, dependencies)
        if cycle:
            result = {
                'error': {
                    'code': 3,
                    'message': 'Circular dependency detected',
                    'details': {'cycle': cycle},
                    'suggestion': 'Review task decomposition to break circular dependency'
                }
            }
            print(json.dumps(result, indent=2), file=sys.stderr)
            sys.exit(3)

        # Topological sort
        topo_order = topological_sort(tasks, dependencies)
        if not topo_order:
            print("Error: Cannot create topological order (should not reach here)", file=sys.stderr)
            sys.exit(3)

        # Build result
        result = {
            'topological_order': topo_order,
            'cycles_detected': False
        }

        # Parallelization levels
        if args.parallel_levels or not (args.critical_path or args.visualize):
            levels = find_parallel_levels(tasks, dependencies)
            result['parallelization_levels'] = levels
            result['parallel_duration'] = calculate_parallel_duration(levels, durations)

        # Critical path
        if args.critical_path or not (args.parallel_levels or args.visualize):
            critical_path, critical_duration = find_critical_path(tasks, durations, dependencies)
            result['critical_path'] = {
                'path': critical_path,
                'total_duration': critical_duration
            }

        # Sequential duration
        sequential_duration = sum(durations.get(t, 0.0) for t in tasks)
        result['sequential_duration'] = sequential_duration

        # Speedup calculation
        if 'parallel_duration' in result:
            speedup = sequential_duration / result['parallel_duration'] if result['parallel_duration'] > 0 else 1.0
            result['speedup'] = round(speedup, 2)

        # Visualization
        if args.visualize:
            try:
                import networkx as nx
                import matplotlib.pyplot as plt

                G = nx.DiGraph()
                for task in tasks:
                    G.add_node(task)
                for task, deps in dependencies.items():
                    for dep in deps:
                        G.add_edge(dep, task)

                pos = nx.spring_layout(G)
                plt.figure(figsize=(12, 8))
                nx.draw(G, pos, with_labels=True, node_color='lightblue',
                       node_size=3000, font_size=10, font_weight='bold',
                       arrows=True, arrowsize=20)

                plt.title("Task Dependency Graph")
                plt.savefig(args.visualize, dpi=300, bbox_inches='tight')
                result['visualization'] = args.visualize
                if args.verbose:
                    print(f"Graph saved to: {args.visualize}", file=sys.stderr)

            except ImportError:
                print("Warning: networkx not installed, skipping visualization", file=sys.stderr)

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))

        sys.exit(0)

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == '__main__':
    main()
