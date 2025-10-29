#!/usr/bin/env python3
"""
agent_selector.py - Match tasks to specialist cognitive models

Usage:
    python agent_selector.py --task "Implement JWT auth" --context context.json
    python agent_selector.py --tasks tasks.json --context context.json
    python agent_selector.py --interactive
"""

import argparse
import json
import sys
from typing import Dict, List, Optional, Tuple


# Specialist definitions with cognitive models
SPECIALISTS = {
    "code-generator": {
        "cognitive_model": "TDD Practitioner",
        "domains": ["backend", "frontend", "api", "implementation"],
        "processes": ["test-first", "incremental implementation", "minimal diffs"],
        "outputs": ["code files", "tests", "implementation notes"],
        "capabilities": [
            "write tests first",
            "implement features incrementally",
            "follow existing patterns",
            "run and verify tests"
        ]
    },
    "code-reviewer": {
        "cognitive_model": "Production Code Auditor",
        "domains": ["security", "quality", "performance", "architecture"],
        "processes": ["security-first audit", "quality assessment", "vulnerability detection"],
        "outputs": ["review report", "issue classifications", "actionable recommendations"],
        "capabilities": [
            "identify security vulnerabilities",
            "assess code quality",
            "detect performance issues",
            "provide constructive feedback"
        ]
    },
    "data-profiler": {
        "cognitive_model": "ML Data Quality Engineer",
        "domains": ["data", "ml", "quality assessment", "bias detection"],
        "processes": ["quantify everything", "ML risk detection", "bias analysis"],
        "outputs": ["profiling report", "statistical findings", "verification code"],
        "capabilities": [
            "profile datasets comprehensively",
            "detect target leakage",
            "identify bias and disparities",
            "quantify all findings"
        ]
    },
    "react-architect": {
        "cognitive_model": "Component Composition Expert",
        "domains": ["frontend", "react", "architecture", "performance"],
        "processes": ["component design", "state management", "performance optimization"],
        "outputs": ["component design", "architecture diagrams", "recommendations"],
        "capabilities": [
            "design component hierarchies",
            "recommend state management",
            "optimize rendering",
            "ensure accessibility"
        ]
    },
    "refactoring-engineer": {
        "cognitive_model": "Technical Debt Manager",
        "domains": ["refactoring", "code quality", "debt tracking"],
        "processes": ["code smell detection", "safe refactoring", "pattern application"],
        "outputs": ["refactored code", "smell report", "debt assessment"],
        "capabilities": [
            "identify code smells",
            "apply safe refactorings",
            "ensure test coverage",
            "track technical debt"
        ]
    },
    "ml-evaluator": {
        "cognitive_model": "Statistical Rigor Enforcer",
        "domains": ["ml", "evaluation", "statistics"],
        "processes": ["statistical testing", "calibration analysis", "significance testing"],
        "outputs": ["evaluation report", "statistical tests", "metric recommendations"],
        "capabilities": [
            "evaluate experiments rigorously",
            "compute statistical significance",
            "assess model calibration",
            "recommend metrics"
        ]
    },
    "ml-research-planner": {
        "cognitive_model": "Experiment Designer",
        "domains": ["ml", "research", "experiment design"],
        "processes": ["experiment design", "ablation planning", "reproducibility"],
        "outputs": ["experiment plan", "ablation design", "reproducibility checklist"],
        "capabilities": [
            "design rigorous experiments",
            "plan ablation studies",
            "select baselines",
            "ensure reproducibility"
        ]
    },
    "ml-trainer": {
        "cognitive_model": "Reproducible Trainer",
        "domains": ["ml", "training", "model development"],
        "processes": ["reproducible training", "overfitting diagnosis", "baseline comparison"],
        "outputs": ["trained models", "training logs", "diagnostics"],
        "capabilities": [
            "train models reproducibly",
            "diagnose overfitting",
            "compare against baselines",
            "track experiments"
        ]
    },
    "mech-interp-researcher": {
        "cognitive_model": "Hypothesis Formalizer",
        "domains": ["research", "interpretability", "hypothesis testing"],
        "processes": ["hypothesis formalization", "causal claim evaluation", "literature synthesis"],
        "outputs": ["formalized hypotheses", "causal evaluations", "literature synthesis"],
        "capabilities": [
            "formalize research hypotheses",
            "evaluate causal claims",
            "synthesize literature",
            "design interpretability experiments"
        ]
    }
}


def calculate_domain_fit(task: Dict, specialist: Dict) -> Tuple[float, str]:
    """
    Calculate how well task domain matches specialist expertise.

    Args:
        task: Task dictionary with 'domain' field
        specialist: Specialist definition

    Returns:
        (score, explanation)
    """
    task_domain = task.get('domain', '').lower()
    specialist_domains = specialist['domains']

    # Exact match
    if task_domain in specialist_domains:
        return 1.0, f"Exact domain match: {task_domain}"

    # Partial match (substring)
    for sd in specialist_domains:
        if task_domain in sd or sd in task_domain:
            return 0.7, f"Partial domain match: {task_domain} ~ {sd}"

    # No match
    return 0.0, f"No domain match: {task_domain} not in {specialist_domains}"


def calculate_process_fit(task: Dict, specialist: Dict) -> Tuple[float, str]:
    """
    Calculate how well task requirements match specialist processes.

    Args:
        task: Task dictionary with 'requirements' field
        specialist: Specialist definition

    Returns:
        (score, explanation)
    """
    requirements = [r.lower() for r in task.get('requirements', [])]
    processes = specialist['processes']

    if not requirements:
        return 0.5, "No specific requirements stated"

    matches = sum(1 for r in requirements for p in processes if r in p or p in r)
    score = min(matches / len(requirements), 1.0)

    if score > 0.7:
        return score, f"Strong process alignment: {matches}/{len(requirements)} requirements matched"
    elif score > 0.3:
        return score, f"Moderate process alignment: {matches}/{len(requirements)} requirements matched"
    else:
        return score, f"Weak process alignment: {matches}/{len(requirements)} requirements matched"


def calculate_output_fit(task: Dict, specialist: Dict) -> Tuple[float, str]:
    """
    Calculate how well specialist outputs match task needs.

    Args:
        task: Task dictionary with 'outputs_needed' field
        specialist: Specialist definition

    Returns:
        (score, explanation)
    """
    outputs_needed = [o.lower() for o in task.get('outputs_needed', [])]
    specialist_outputs = specialist['outputs']

    if not outputs_needed:
        return 0.5, "No specific outputs stated"

    matches = sum(1 for needed in outputs_needed for output in specialist_outputs if needed in output or output in needed)
    score = min(matches / len(outputs_needed), 1.0)

    if score == 1.0:
        return score, "All required outputs match"
    elif score > 0.5:
        return score, f"Most outputs match: {matches}/{len(outputs_needed)}"
    else:
        return score, f"Few outputs match: {matches}/{len(outputs_needed)}"


def detect_anti_patterns(task: Dict, specialist_name: str, specialist: Dict) -> List[str]:
    """
    Detect assignment anti-patterns.

    Args:
        task: Task dictionary
        specialist_name: Name of specialist
        specialist: Specialist definition

    Returns:
        List of detected anti-patterns
    """
    anti_patterns = []

    task_desc = task.get('description', '').lower()

    # Domain mismatch anti-patterns
    if specialist_name == "data-profiler" and "frontend" in task_desc:
        anti_patterns.append("Domain mismatch: data-profiler assigned to frontend work")

    if specialist_name == "code-reviewer" and "implement" in task_desc:
        anti_patterns.append("Role confusion: code-reviewer asked to implement (should review only)")

    if specialist_name == "code-generator" and ("research" in task_desc or "literature review" in task_desc):
        anti_patterns.append("Cognitive mismatch: code-generator assigned research task")

    if specialist_name == "ml-evaluator" and "train" in task_desc:
        anti_patterns.append("Premature assignment: ml-evaluator before model training")

    if specialist_name == "refactoring-engineer" and "new feature" in task_desc:
        anti_patterns.append("Role confusion: refactoring-engineer assigned new feature (should refactor existing)")

    return anti_patterns


def match_task_to_specialist(task: Dict) -> Dict:
    """
    Match a task to the most appropriate specialist.

    Args:
        task: Task dictionary with description, domain, requirements, outputs_needed

    Returns:
        Assignment dictionary with specialist, confidence, rationale
    """
    best_specialist = None
    best_score = 0.0
    best_rationale = {}

    for specialist_name, specialist in SPECIALISTS.items():
        # Calculate fit scores
        domain_score, domain_explanation = calculate_domain_fit(task, specialist)
        process_score, process_explanation = calculate_process_fit(task, specialist)
        output_score, output_explanation = calculate_output_fit(task, specialist)

        # Overall confidence (weighted average)
        # Domain is most important (0.5), then process (0.3), then output (0.2)
        confidence = (domain_score * 0.5) + (process_score * 0.3) + (output_score * 0.2)

        if confidence > best_score:
            best_score = confidence
            best_specialist = specialist_name
            best_rationale = {
                "domain_fit": domain_explanation,
                "cognitive_process": process_explanation,
                "output_format": output_explanation,
                "cognitive_model": specialist['cognitive_model']
            }

    # Detect anti-patterns
    anti_patterns = []
    if best_specialist:
        anti_patterns = detect_anti_patterns(task, best_specialist, SPECIALISTS[best_specialist])

    # Reduce confidence if anti-patterns detected
    if anti_patterns:
        best_score = max(best_score - 0.2 * len(anti_patterns), 0.0)

    return {
        "task_id": task.get('id', 'unknown'),
        "task_description": task.get('description', ''),
        "specialist": best_specialist,
        "confidence": round(best_score, 2),
        "rationale": best_rationale,
        "anti_patterns": anti_patterns,
        "alternative": find_alternative(task, best_specialist) if best_score < 0.7 else None
    }


def find_alternative(task: Dict, primary_specialist: str) -> Optional[str]:
    """Find alternative specialist if primary match is low confidence."""
    scores = {}

    for specialist_name, specialist in SPECIALISTS.items():
        if specialist_name == primary_specialist:
            continue

        domain_score, _ = calculate_domain_fit(task, specialist)
        process_score, _ = calculate_process_fit(task, specialist)
        output_score, _ = calculate_output_fit(task, specialist)

        scores[specialist_name] = (domain_score * 0.5) + (process_score * 0.3) + (output_score * 0.2)

    if scores:
        best_alt = max(scores.items(), key=lambda x: x[1])
        if best_alt[1] > 0.5:
            return best_alt[0]

    return None


def main():
    parser = argparse.ArgumentParser(description='Match tasks to specialist cognitive models')
    parser.add_argument('--task', type=str, help='Single task description')
    parser.add_argument('--tasks', type=str, help='JSON file with multiple tasks')
    parser.add_argument('--context', type=str, help='JSON file with context')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--output', type=str, help='Output file (default: stdout)')
    parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        # Load context if provided
        context = {}
        if args.context:
            with open(args.context, 'r') as f:
                context = json.load(f)

        # Process tasks
        assignments = []

        if args.interactive:
            print("Interactive Mode - Agent Selector")
            print("=" * 50)
            while True:
                task_desc = input("\nTask description (or 'quit' to exit): ").strip()
                if task_desc.lower() in ['quit', 'exit', 'q']:
                    break

                domain = input("Domain (backend/frontend/data/ml/research): ").strip()
                requirements = input("Requirements (comma-separated): ").strip().split(',')
                outputs = input("Outputs needed (comma-separated): ").strip().split(',')

                task = {
                    'id': f'task_{len(assignments) + 1}',
                    'description': task_desc,
                    'domain': domain,
                    'requirements': [r.strip() for r in requirements if r.strip()],
                    'outputs_needed': [o.strip() for o in outputs if o.strip()]
                }

                assignment = match_task_to_specialist(task)
                assignments.append(assignment)

                print(f"\n✓ Matched to: {assignment['specialist']} (confidence: {assignment['confidence']})")
                print(f"  Rationale: {assignment['rationale']['domain_fit']}")
                if assignment['anti_patterns']:
                    print(f"  ⚠ Anti-patterns: {', '.join(assignment['anti_patterns'])}")

        elif args.task:
            task = {
                'id': 'task_1',
                'description': args.task,
                'domain': context.get('domain', ''),
                'requirements': context.get('requirements', []),
                'outputs_needed': context.get('outputs_needed', [])
            }
            assignment = match_task_to_specialist(task)
            assignments.append(assignment)

        elif args.tasks:
            with open(args.tasks, 'r') as f:
                tasks_data = json.load(f)

            for task in tasks_data.get('tasks', []):
                assignment = match_task_to_specialist(task)
                assignments.append(assignment)

        else:
            parser.print_help()
            sys.exit(1)

        # Output results
        result = {'assignments': assignments}

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            if args.format == 'json':
                print(json.dumps(result, indent=2))
            else:
                for assignment in assignments:
                    print(f"\nTask: {assignment['task_description']}")
                    print(f"Specialist: {assignment['specialist']}")
                    print(f"Confidence: {assignment['confidence']}")
                    print(f"Rationale:")
                    for key, value in assignment['rationale'].items():
                        print(f"  - {key}: {value}")
                    if assignment['anti_patterns']:
                        print(f"⚠ Anti-patterns:")
                        for ap in assignment['anti_patterns']:
                            print(f"  - {ap}")

        sys.exit(0)

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
