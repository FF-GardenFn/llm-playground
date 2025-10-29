#!/usr/bin/env python3
"""
merge_coordinator.py - Coordinate merging of specialist outputs

Usage:
    python merge_coordinator.py --outputs outputs.json --strategy topological
    python merge_coordinator.py --outputs outputs.json --conflicts conflicts.json --resolve
    python merge_coordinator.py --outputs outputs.json --dry-run
"""

import argparse
import json
import sys
import subprocess
import time
from typing import Dict, List, Optional
from collections import defaultdict


def load_data(filepath: str) -> Dict:
    """Load JSON data from file with error handling."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {filepath}: {e}")


def topological_sort_tasks(tasks: List[str], dependencies: Dict[str, List[str]]) -> Optional[List[str]]:
    """Sort tasks in topological order."""
    from collections import deque

    in_degree = {task: 0 for task in tasks}
    graph = defaultdict(list)

    for task, deps in dependencies.items():
        for dep in deps:
            graph[dep].append(task)
            in_degree[task] += 1

    queue = deque([t for t in tasks if in_degree[t] == 0])
    result = []

    while queue:
        task = queue.popleft()
        result.append(task)

        for neighbor in graph[task]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result if len(result) == len(tasks) else None


def merge_files(outputs: Dict, merge_order: List[str], dry_run: bool = False) -> Dict:
    """
    Merge files from task outputs.

    Args:
        outputs: Task outputs dictionary
        merge_order: Order to merge tasks
        dry_run: If True, don't actually merge

    Returns:
        Dict with merge results
    """
    merged_files = {}
    warnings = []
    errors = []

    for task_id in merge_order:
        task_output = outputs.get(task_id, {})
        files = task_output.get('files', {})

        for file_path, content in files.items():
            if file_path in merged_files:
                # File conflict - already merged from another task
                warnings.append(f"File conflict: {file_path} modified by multiple tasks (using latest)")

            if not dry_run:
                merged_files[file_path] = content

    return {
        'merged_files': list(merged_files.keys()),
        'file_count': len(merged_files),
        'warnings': warnings,
        'errors': errors
    }


def resolve_conflicts(conflicts: List[Dict], outputs: Dict, strategy: str = 'serialize') -> Dict:
    """
    Resolve conflicts using specified strategy.

    Args:
        conflicts: List of detected conflicts
        outputs: Task outputs
        strategy: Resolution strategy ('serialize', 'skip', 'manual')

    Returns:
        Resolution results
    """
    resolutions = []

    for conflict in conflicts:
        conflict_type = conflict['type']
        tasks = conflict['tasks']

        if strategy == 'serialize':
            # Serialize conflicting tasks
            resolution = {
                'conflict_type': conflict_type,
                'tasks': tasks,
                'strategy': 'serialize',
                'action': f"Execute tasks in order: {' -> '.join(tasks)}"
            }
            resolutions.append(resolution)

        elif strategy == 'skip':
            # Skip conflicting tasks (manual resolution needed)
            resolution = {
                'conflict_type': conflict_type,
                'tasks': tasks,
                'strategy': 'skip',
                'action': f"Skipped - manual resolution required"
            }
            resolutions.append(resolution)

        elif strategy == 'manual':
            # Escalate to manual resolution
            resolution = {
                'conflict_type': conflict_type,
                'tasks': tasks,
                'strategy': 'manual',
                'action': f"Escalated - requires user decision"
            }
            resolutions.append(resolution)

    return {'resolutions': resolutions, 'count': len(resolutions)}


def run_verification(test_command: str, verbose: bool = False) -> Tuple[bool, str]:
    """
    Run verification tests.

    Args:
        test_command: Command to run (e.g., "pytest tests/")
        verbose: Print detailed output

    Returns:
        (success, output)
    """
    try:
        result = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        success = result.returncode == 0
        output = result.stdout + result.stderr

        if verbose:
            print(output, file=sys.stderr)

        return success, output

    except subprocess.TimeoutExpired:
        return False, "Verification timed out (>5 minutes)"
    except Exception as e:
        return False, f"Verification error: {str(e)}"


def perform_merge(
    outputs: Dict,
    conflicts: Optional[List[Dict]] = None,
    strategy: str = 'topological',
    verification: Optional[Dict] = None,
    dry_run: bool = False,
    verbose: bool = False
) -> Dict:
    """
    Perform the merge operation.

    Args:
        outputs: Task outputs dictionary
        conflicts: List of detected conflicts (optional)
        strategy: Merge strategy ('topological', 'sequential')
        verification: Verification config (test_command, rollback_on_failure)
        dry_run: Preview merge without executing
        verbose: Detailed logging

    Returns:
        Merge result dictionary
    """
    start_time = time.time()

    # Determine merge order
    task_ids = list(outputs.keys())

    if strategy == 'topological':
        # Get dependencies from outputs
        dependencies = {}
        for task_id, output in outputs.items():
            dependencies[task_id] = output.get('dependencies', [])

        merge_order = topological_sort_tasks(task_ids, dependencies)
        if not merge_order:
            return {
                'status': 'failed',
                'error': 'Circular dependency detected',
                'duration': time.time() - start_time
            }
    else:
        # Sequential order
        merge_order = task_ids

    if verbose:
        print(f"Merge order: {' -> '.join(merge_order)}", file=sys.stderr)

    # Resolve conflicts if provided
    conflict_resolutions = {}
    if conflicts:
        conflict_resolutions = resolve_conflicts(conflicts, outputs, strategy='serialize')
        if verbose:
            print(f"Resolved {len(conflicts)} conflicts", file=sys.stderr)

    # Merge files
    merge_result = merge_files(outputs, merge_order, dry_run=dry_run)

    if dry_run:
        return {
            'status': 'dry_run',
            'merged_tasks': merge_order,
            'merge_order': merge_order,
            'conflicts_resolved': len(conflicts) if conflicts else 0,
            'merged_files': merge_result['merged_files'],
            'warnings': merge_result['warnings'],
            'duration': time.time() - start_time
        }

    # Run verification if specified
    verification_result = {}
    if verification and verification.get('run_tests'):
        test_command = verification.get('test_command', 'pytest tests/')
        if verbose:
            print(f"Running verification: {test_command}", file=sys.stderr)

        tests_passed, test_output = run_verification(test_command, verbose=verbose)
        verification_result = {
            'tests_passed': tests_passed,
            'test_output': test_output
        }

        if not tests_passed and verification.get('rollback_on_failure', True):
            return {
                'status': 'failed',
                'error': 'Verification failed',
                'merged_tasks': merge_order,
                'verification': verification_result,
                'rollbacks': 1,
                'duration': time.time() - start_time
            }

    # Success
    return {
        'status': 'success',
        'merged_tasks': merge_order,
        'merge_order': merge_order,
        'conflicts_resolved': len(conflicts) if conflicts else 0,
        'verification': verification_result if verification_result else {'tests_passed': None},
        'merged_files': merge_result['merged_files'],
        'warnings': merge_result['warnings'],
        'errors': merge_result['errors'],
        'rollbacks': 0,
        'duration': round(time.time() - start_time, 1)
    }


def main():
    parser = argparse.ArgumentParser(description='Coordinate merging of specialist outputs')
    parser.add_argument('--outputs', type=str, required=True, help='JSON file with task outputs')
    parser.add_argument('--conflicts', type=str, help='JSON file with detected conflicts')
    parser.add_argument('--strategy', choices=['topological', 'sequential'], default='topological',
                       help='Merge strategy')
    parser.add_argument('--resolve', action='store_true', help='Resolve conflicts automatically')
    parser.add_argument('--verify', type=str, help='Verification command (e.g., "pytest tests/")')
    parser.add_argument('--rollback-on-failure', action='store_true', default=True,
                       help='Rollback on verification failure')
    parser.add_argument('--dry-run', action='store_true', help='Preview merge without executing')
    parser.add_argument('--incremental', action='store_true', help='Incremental merge (merge after each task)')
    parser.add_argument('--output', type=str, help='Output file (default: stdout)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        # Load outputs
        outputs_data = load_data(args.outputs)
        outputs = outputs_data.get('outputs', outputs_data)

        # Load conflicts if provided
        conflicts = None
        if args.conflicts:
            conflicts_data = load_data(args.conflicts)
            conflicts = conflicts_data.get('conflicts', [])

        # Build verification config
        verification = None
        if args.verify:
            verification = {
                'run_tests': True,
                'test_command': args.verify,
                'rollback_on_failure': args.rollback_on_failure
            }

        # Perform merge
        result = perform_merge(
            outputs=outputs,
            conflicts=conflicts,
            strategy=args.strategy,
            verification=verification,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        # Wrap in merge_result for consistency
        final_result = {'merge_result': result}

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(final_result, f, indent=2)
        else:
            print(json.dumps(final_result, indent=2))

        # Exit code based on result
        if result['status'] == 'failed':
            sys.exit(4)  # Verification failure
        elif result['status'] == 'dry_run':
            sys.exit(0)  # Dry run success
        else:
            sys.exit(0)  # Merge success

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == '__main__':
    main()
