#!/usr/bin/env python3
"""
Tool Name: Bias Detector
Purpose: Detect data bias, fairness issues, group disparities in datasets
Usage: python bias_detector.py --data dataset.csv --target outcome --protected_attrs gender,race

This tool is part of the data-profiler agent's toolkit.
It analyzes protected group distributions, computes disparate impact, tests for statistical
significance of group differences, and identifies fairness risks.

Examples:
    # Basic bias analysis
    python bias_detector.py --data train.csv --target approved --protected_attrs gender,race

    # With statistical testing
    python bias_detector.py --data train.csv --target hired --protected_attrs race --test_type chi2 --alpha 0.05

    # Intersectional analysis
    python bias_detector.py --data train.csv --target outcome --protected_attrs gender,race --intersectional
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BiasDetector:
    """Fairness and bias analysis tool."""

    def __init__(self, alpha=0.05):
        self.alpha = alpha

    def analyze_group_distribution(self, df: pd.DataFrame, protected_attr: str,
                                   target: str) -> Dict[str, Any]:
        """Analyze distribution and outcomes by protected group."""
        logger.info(f"Analyzing group distribution for {protected_attr}...")

        results = {
            'protected_attribute': protected_attr,
            'groups': {}
        }

        for group in df[protected_attr].unique():
            group_data = df[df[protected_attr] == group]
            group_size = len(group_data)
            group_pct = group_size / len(df) * 100

            outcome_rate = group_data[target].mean() * 100 if target in df.columns else None

            results['groups'][str(group)] = {
                'count': int(group_size),
                'percentage': float(group_pct),
                'outcome_rate': float(outcome_rate) if outcome_rate is not None else None
            }

        return results

    def compute_disparate_impact(self, df: pd.DataFrame, protected_attr: str,
                                 target: str) -> Dict[str, Any]:
        """Compute disparate impact ratios (80% rule)."""
        logger.info("Computing disparate impact...")

        outcome_rates = df.groupby(protected_attr)[target].mean()
        max_rate = outcome_rates.max()

        disparate_impact = {
            'max_selection_rate': float(max_rate),
            'ratios': {},
            'fails_80_rule': []
        }

        for group, rate in outcome_rates.items():
            ratio = rate / max_rate if max_rate > 0 else 0
            disparate_impact['ratios'][str(group)] = float(ratio)

            if ratio < 0.8:
                disparate_impact['fails_80_rule'].append(str(group))

        return disparate_impact

    def statistical_test(self, df: pd.DataFrame, protected_attr: str,
                        target: str, test_type='chi2') -> Dict[str, Any]:
        """Perform statistical significance test."""
        logger.info(f"Performing {test_type} test...")

        contingency_table = pd.crosstab(df[protected_attr], df[target])

        if test_type == 'chi2':
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

            # Cramér's V effect size
            n = contingency_table.sum().sum()
            min_dim = min(contingency_table.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

            result = {
                'test': 'chi-square',
                'statistic': float(chi2),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'cramers_v': float(cramers_v),
                'significant': p_value < self.alpha
            }

            # Interpret effect size
            if cramers_v < 0.1:
                result['effect_size_interpretation'] = 'negligible'
            elif cramers_v < 0.3:
                result['effect_size_interpretation'] = 'small'
            elif cramers_v < 0.5:
                result['effect_size_interpretation'] = 'medium'
            else:
                result['effect_size_interpretation'] = 'large'

            return result

        return {}

    def intersectional_analysis(self, df: pd.DataFrame, protected_attrs: List[str],
                                target: str) -> Dict[str, Any]:
        """Analyze intersections of protected attributes."""
        logger.info("Performing intersectional analysis...")

        # Create intersectional groups
        df['_intersection'] = df[protected_attrs].apply(lambda x: '_'.join(x.astype(str)), axis=1)

        results = {
            'intersections': {},
            'min_sample_size': 100  # Threshold for reliable analysis
        }

        for group in df['_intersection'].unique():
            group_data = df[df['_intersection'] == group]
            group_size = len(group_data)
            outcome_rate = group_data[target].mean() * 100

            results['intersections'][group] = {
                'count': int(group_size),
                'percentage': float(group_size / len(df) * 100),
                'outcome_rate': float(outcome_rate),
                'adequate_sample': group_size >= results['min_sample_size']
            }

        return results

    def full_analysis(self, df: pd.DataFrame, target: str, protected_attrs: List[str],
                     test_type='chi2', intersectional=False) -> Dict[str, Any]:
        """Perform comprehensive bias analysis."""
        report = {
            'target': target,
            'protected_attributes': protected_attrs,
            'n_samples': len(df),
            'analyses': {}
        }

        for attr in protected_attrs:
            logger.info(f"\nAnalyzing {attr}...")

            attr_analysis = {
                'distribution': self.analyze_group_distribution(df, attr, target),
                'disparate_impact': self.compute_disparate_impact(df, attr, target),
                'statistical_test': self.statistical_test(df, attr, target, test_type)
            }

            report['analyses'][attr] = attr_analysis

        if intersectional and len(protected_attrs) > 1:
            report['intersectional'] = self.intersectional_analysis(df, protected_attrs, target)

        return report


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--data', required=True, help='Path to dataset')
    parser.add_argument('--target', required=True, help='Target variable (outcome)')
    parser.add_argument('--protected_attrs', required=True, help='Comma-separated protected attributes')
    parser.add_argument('--test_type', choices=['chi2'], default='chi2', help='Statistical test type')
    parser.add_argument('--alpha', type=float, default=0.05, help='Significance level')
    parser.add_argument('--intersectional', action='store_true', help='Perform intersectional analysis')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    df = pd.read_csv(args.data)
    protected_attrs = [a.strip() for a in args.protected_attrs.split(',')]

    detector = BiasDetector(alpha=args.alpha)
    report = detector.full_analysis(df, args.target, protected_attrs, args.test_type, args.intersectional)

    output = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(output)
        logger.info(f"Report written to {args.output}")
    else:
        print(output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
