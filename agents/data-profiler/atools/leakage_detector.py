#!/usr/bin/env python3
"""
Tool Name: Leakage Detector
Purpose: Detect train/test leakage, temporal violations, and suspiciously perfect features
Usage: python leakage_detector.py --train train.csv --test test.csv --target outcome

This tool is part of the data-profiler agent's toolkit.
It identifies target leakage via correlation analysis, validates train/test split integrity,
checks temporal ordering, and flags suspiciously perfect predictors.

Examples:
    # Basic leakage detection
    python leakage_detector.py --train train.csv --test test.csv --target churned

    # Temporal validation
    python leakage_detector.py --data timeseries.csv --time_col timestamp --target sales --window 30

    # Feature correlation analysis
    python leakage_detector.py --train train.csv --target fraud --correlation_threshold 0.95
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LeakageDetector:
    """Train/test leakage and temporal validation tool."""

    def __init__(self, correlation_threshold=0.95):
        self.correlation_threshold = correlation_threshold

    def detect_target_leakage(self, df: pd.DataFrame, target: str) -> Dict[str, Any]:
        """Detect features with suspiciously high correlation to target."""
        logger.info("Detecting target leakage via correlation...")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target not in numeric_cols:
            logger.warning(f"Target {target} is not numeric, skipping correlation analysis")
            return {'suspicious_features': []}

        # Remove target from features
        feature_cols = [c for c in numeric_cols if c != target]

        suspicious = []
        correlations = {}

        for col in feature_cols:
            corr = df[[col, target]].corr().iloc[0, 1]
            correlations[col] = float(corr)

            if abs(corr) >= self.correlation_threshold:
                suspicious.append({
                    'feature': col,
                    'correlation': float(corr),
                    'risk_level': 'CRITICAL' if abs(corr) > 0.98 else 'HIGH'
                })

        return {
            'suspicious_features': suspicious,
            'all_correlations': correlations,
            'threshold': self.correlation_threshold
        }

    def check_train_test_overlap(self, train_df: pd.DataFrame, test_df: pd.DataFrame,
                                 id_col: Optional[str] = None) -> Dict[str, Any]:
        """Check for sample overlap between train and test sets."""
        logger.info("Checking train/test overlap...")

        if id_col:
            train_ids = set(train_df[id_col])
            test_ids = set(test_df[id_col])
            overlap = train_ids & test_ids

            return {
                'method': 'id_based',
                'id_column': id_col,
                'overlap_count': len(overlap),
                'overlap_ids': list(overlap)[:100],  # Limit output
                'train_size': len(train_ids),
                'test_size': len(test_ids)
            }
        else:
            # Hash-based overlap detection
            train_hashes = set(pd.util.hash_pandas_object(train_df).values)
            test_hashes = set(pd.util.hash_pandas_object(test_df).values)
            overlap = train_hashes & test_hashes

            return {
                'method': 'hash_based',
                'overlap_count': len(overlap),
                'train_size': len(train_hashes),
                'test_size': len(test_hashes)
            }

    def check_temporal_ordering(self, df: pd.DataFrame, time_col: str,
                                target: str, window: int = 30) -> Dict[str, Any]:
        """Check temporal ordering and detect future information leakage."""
        logger.info("Checking temporal ordering...")

        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(time_col)

        issues = {
            'has_temporal_violations': False,
            'violations': []
        }

        # Check if timestamps are monotonic
        if not df[time_col].is_monotonic_increasing:
            issues['has_temporal_violations'] = True
            issues['violations'].append({
                'type': 'NON_MONOTONIC_TIMESTAMPS',
                'description': 'Timestamps are not in ascending order'
            })

        # Check for large gaps
        time_diffs = df[time_col].diff()
        median_diff = time_diffs.median()
        large_gaps = time_diffs > median_diff * 10

        if large_gaps.any():
            issues['violations'].append({
                'type': 'LARGE_TIME_GAPS',
                'count': int(large_gaps.sum()),
                'median_gap': str(median_diff)
            })

        return issues

    def check_perfect_predictors(self, df: pd.DataFrame, target: str) -> Dict[str, Any]:
        """Identify features that perfectly predict the target."""
        logger.info("Checking for perfect predictors...")

        perfect_predictors = []

        for col in df.columns:
            if col == target:
                continue

            # Check if feature perfectly separates target
            if df[target].dtype in [np.int64, np.float64, bool]:
                grouped = df.groupby(col)[target].nunique()
                if (grouped == 1).all():
                    perfect_predictors.append({
                        'feature': col,
                        'type': 'PERFECT_SEPARATOR',
                        'risk': 'CRITICAL'
                    })

        return {'perfect_predictors': perfect_predictors}

    def full_analysis(self, train_df: Optional[pd.DataFrame] = None,
                     test_df: Optional[pd.DataFrame] = None,
                     target: Optional[str] = None,
                     time_col: Optional[str] = None,
                     id_col: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive leakage detection."""
        report = {'timestamp': pd.Timestamp.now().isoformat()}

        if train_df is not None and target:
            report['target_leakage'] = self.detect_target_leakage(train_df, target)
            report['perfect_predictors'] = self.check_perfect_predictors(train_df, target)

        if train_df is not None and test_df is not None:
            report['train_test_overlap'] = self.check_train_test_overlap(train_df, test_df, id_col)

        if train_df is not None and time_col and target:
            report['temporal_validation'] = self.check_temporal_ordering(train_df, time_col, target)

        return report


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--train', help='Path to training dataset')
    parser.add_argument('--test', help='Path to test dataset')
    parser.add_argument('--data', help='Path to single dataset (for temporal analysis)')
    parser.add_argument('--target', help='Target variable')
    parser.add_argument('--time_col', help='Timestamp column for temporal validation')
    parser.add_argument('--id_col', help='ID column for overlap detection')
    parser.add_argument('--correlation_threshold', type=float, default=0.95, help='Correlation threshold for leakage')
    parser.add_argument('--window', type=int, default=30, help='Time window for temporal checks (days)')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    detector = LeakageDetector(correlation_threshold=args.correlation_threshold)

    train_df = pd.read_csv(args.train) if args.train else None
    test_df = pd.read_csv(args.test) if args.test else None
    data_df = pd.read_csv(args.data) if args.data else train_df

    report = detector.full_analysis(
        train_df=data_df,
        test_df=test_df,
        target=args.target,
        time_col=args.time_col,
        id_col=args.id_col
    )

    output = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(output)
        logger.info(f"Report written to {args.output}")
    else:
        print(output)

    return 0


if __name__ == '__main__':
    sys.exit(main())
