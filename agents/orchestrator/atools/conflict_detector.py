#!/usr/bin/env python3
"""
conflict_detector.py - Detect conflicts in task outputs

Usage:
    python conflict_detector.py --outputs outputs.json
    python conflict_detector.py --outputs outputs.json --type file
    python conflict_detector.py --outputs outputs.json --report conflicts_report.md
"""

import argparse
import json
import sys
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from itertools import combinations


def detect_file_conflicts(task_outputs: Dict) -> List[Dict]:
    """Detect if multiple tasks modified same files."""
    file_map = defaultdict(list)

    for task_id, outputs in task_outputs.items():
        for file_path in outputs.get('modified_files', []):
            file_map[file_path].append(task_id)

    conflicts = []
    for file_path, tasks in file_map.items():
        if len(tasks) > 1:
            conflicts.append({
                'type': 'file_conflict',
                'severity': 'medium',
                'tasks': tasks,
                'details': {
                    'file': file_path,
                    'conflict_type': 'both_modified'
                },
                'resolution_strategies': [
                    f"serialize (execute {' then '.join(tasks)})",
                    f"partition file into separate files",
                    "careful coordination (non-overlapping regions)"
                ],
                'recommended': 'serialize'
            })

    return conflicts


def detect_semantic_conflicts(task_outputs: Dict) -> List[Dict]:
    """Detect logical incompatibilities between task outputs."""
    conflicts = []

    # Check API contract mismatches
    api_contracts = {}
    for task_id, outputs in task_outputs.items():
        for endpoint, contract in outputs.get('api_contracts', {}).items():
            if endpoint not in api_contracts:
                api_contracts[endpoint] = []
            api_contracts[endpoint].append((task_id, contract))

    for endpoint, contracts in api_contracts.items():
        if len(contracts) > 1:
            # Check if contracts are compatible
            for (task1, contract1), (task2, contract2) in combinations(contracts, 2):
                if not contracts_compatible(contract1, contract2):
                    conflicts.append({
                        'type': 'semantic_conflict',
                        'subtype': 'api_contract_mismatch',
                        'severity': 'high',
                        'tasks': [task1, task2],
                        'details': {
                            'endpoint': endpoint,
                            'contract1': contract1,
                            'contract2': contract2
                        },
                        'resolution_strategies': [
                            "align contracts (update one to match the other)",
                            "add adapter layer",
                            "version endpoints (v1, v2)"
                        ],
                        'recommended': 'align contracts'
                    })

    return conflicts


def contracts_compatible(contract1: Dict, contract2: Dict) -> bool:
    """Check if two API contracts are compatible."""
    # Check HTTP method
    if contract1.get('method') != contract2.get('method'):
        return False

    # Check request schema compatibility
    req1 = contract1.get('request', {})
    req2 = contract2.get('request', {})
    if set(req1.keys()) != set(req2.keys()):
        return False

    # Check response schema compatibility
    resp1 = contract2.get('response', {})
    resp2 = contract2.get('response', {})
    if set(resp1.keys()) != set(resp2.keys()):
        return False

    return True


def detect_dependency_conflicts(task_outputs: Dict) -> List[Dict]:
    """Detect dependency version conflicts."""
    dependencies = defaultdict(dict)

    for task_id, outputs in task_outputs.items():
        for package, version in outputs.get('dependencies', {}).items():
            dependencies[package][task_id] = version

    conflicts = []
    for package, versions_by_task in dependencies.items():
        unique_versions = set(versions_by_task.values())
        if len(unique_versions) > 1:
            conflicts.append({
                'type': 'dependency_conflict',
                'severity': 'high',
                'tasks': list(versions_by_task.keys()),
                'details': {
                    'package': package,
                    'versions_by_task': versions_by_task
                },
                'resolution_strategies': [
                    "choose single version (latest or most compatible)",
                    "use version ranges if compatible",
                    "separate into different environments"
                ],
                'recommended': 'choose single version'
            })

    return conflicts


def detect_schema_conflicts(task_outputs: Dict) -> List[Dict]:
    """Detect database schema conflicts."""
    conflicts = []

    schema_changes = defaultdict(list)
    for task_id, outputs in task_outputs.items():
        for change in outputs.get('schema_changes', []):
            table = change.get('table')
            schema_changes[table].append((task_id, change))

    for table, changes in schema_changes.items():
        if len(changes) > 1:
            # Check for conflicting operations
            for (task1, change1), (task2, change2) in combinations(changes, 2):
                op1 = change1.get('operation')
                op2 = change2.get('operation')

                # Check for DROP followed by USE
                if op1 == 'drop_column' and op2 in ['add_index', 'select']:
                    conflicts.append({
                        'type': 'schema_conflict',
                        'severity': 'critical',
                        'tasks': [task1, task2],
                        'details': {
                            'table': table,
                            'conflict': f"{task1} drops column, {task2} uses it"
                        },
                        'resolution_strategies': [
                            "serialize (ensure correct order)",
                            "remove dependency on dropped column"
                        ],
                        'recommended': 'serialize'
                    })

    return conflicts


def generate_markdown_report(conflicts: List[Dict]) -> str:
    """Generate markdown conflict report."""
    report = ["# Conflict Detection Report\n"]
    report.append(f"**Total Conflicts:** {len(conflicts)}\n")

    if not conflicts:
        report.append("✅ No conflicts detected.\n")
        return '\n'.join(report)

    # Group by severity
    by_severity = defaultdict(list)
    for conflict in conflicts:
        by_severity[conflict['severity']].append(conflict)

    for severity in ['critical', 'high', 'medium', 'low']:
        if severity in by_severity:
            report.append(f"\n## {severity.upper()} Severity Conflicts\n")
            for i, conflict in enumerate(by_severity[severity], 1):
                report.append(f"### {i}. {conflict['type'].replace('_', ' ').title()}\n")
                report.append(f"**Tasks:** {', '.join(conflict['tasks'])}\n")
                report.append(f"**Details:**\n")
                for key, value in conflict['details'].items():
                    report.append(f"  - {key}: `{value}`\n")
                report.append(f"**Resolution Strategies:**\n")
                for strategy in conflict['resolution_strategies']:
                    report.append(f"  - {strategy}\n")
                report.append(f"**Recommended:** {conflict['recommended']}\n")

    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='Detect conflicts in task outputs')
    parser.add_argument('--outputs', type=str, required=True, help='JSON file with task outputs')
    parser.add_argument('--type', choices=['file', 'semantic', 'dependency', 'schema'],
                       help='Detect specific conflict type only')
    parser.add_argument('--report', type=str, help='Generate markdown report')
    parser.add_argument('--output', type=str, help='Output file (default: stdout)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        # Load outputs
        with open(args.outputs, 'r') as f:
            outputs_data = json.load(f)

        task_outputs = outputs_data.get('outputs', outputs_data)

        # Detect conflicts
        all_conflicts = []

        if not args.type or args.type == 'file':
            all_conflicts.extend(detect_file_conflicts(task_outputs))

        if not args.type or args.type == 'semantic':
            all_conflicts.extend(detect_semantic_conflicts(task_outputs))

        if not args.type or args.type == 'dependency':
            all_conflicts.extend(detect_dependency_conflicts(task_outputs))

        if not args.type or args.type == 'schema':
            all_conflicts.extend(detect_schema_conflicts(task_outputs))

        # Build result
        by_severity = defaultdict(int)
        by_type = defaultdict(int)
        for conflict in all_conflicts:
            by_severity[conflict['severity']] += 1
            by_type[conflict['type']] += 1

        result = {
            'conflicts': all_conflicts,
            'conflict_summary': {
                'total': len(all_conflicts),
                'by_severity': dict(by_severity),
                'by_type': dict(by_type)
            }
        }

        # Generate markdown report if requested
        if args.report:
            markdown = generate_markdown_report(all_conflicts)
            with open(args.report, 'w') as f:
                f.write(markdown)
            if args.verbose:
                print(f"Report generated: {args.report}", file=sys.stderr)

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))

        # Exit with code based on severity
        if any(c['severity'] == 'critical' for c in all_conflicts):
            sys.exit(4)  # Critical conflicts found
        elif all_conflicts:
            sys.exit(0)  # Non-critical conflicts found (still success, just informational)
        else:
            sys.exit(0)  # No conflicts

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == '__main__':
    main()
