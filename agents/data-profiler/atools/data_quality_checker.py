#!/usr/bin/env python3
"""
Tool Name: Data Quality Checker
Purpose: Comprehensive dataset profiling - nulls, outliers, distributions, types, duplicates
Usage: python data_quality_checker.py --data dataset.csv --output report.json

This tool is part of the data-profiler agent's toolkit.
It performs rapid quality assessment across multiple dimensions to identify data issues
before modeling begins.

Examples:
    # Basic profiling
    python data_quality_checker.py --data train.csv --output profile.json

    # With outlier detection
    python data_quality_checker.py --data train.csv --outlier_method isolation_forest --outlier_threshold 0.1

    # Detailed analysis for specific columns
    python data_quality_checker.py --data train.csv --columns age,income,score --detailed

    # Large file with sampling
    python data_quality_checker.py --data large.csv --sample 10000 --output profile.json
"""

import argparse
import sys
import json
import logging
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import numpy as np
import pandas as pd
from collections import defaultdict
from datetime import datetime

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataQualityChecker:
    """
    Comprehensive data quality profiler.

    Capabilities:
    - Schema analysis (types, nulls, cardinality)
    - Distribution profiling (stats, skewness, kurtosis)
    - Outlier detection (Z-score, IQR, Isolation Forest)
    - Duplicate analysis (exact and near-duplicates)
    - Missing data patterns (MCAR, MAR, MNAR indicators)
    """

    def __init__(self, outlier_method='zscore', outlier_threshold=3.0):
        """
        Initialize the quality checker.

        Args:
            outlier_method: Method for outlier detection ('zscore', 'iqr', 'isolation_forest')
            outlier_threshold: Threshold for outlier detection
        """
        self.outlier_method = outlier_method
        self.outlier_threshold = outlier_threshold
        logger.debug(f"Initialized with method={outlier_method}, threshold={outlier_threshold}")

    def load_data(self, file_path: str, sample_size: Optional[int] = None,
                  file_format: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from various formats.

        Args:
            file_path: Path to data file
            sample_size: Number of rows to sample (None for all)
            file_format: File format (csv, parquet, json) - auto-detected if None

        Returns:
            DataFrame
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Auto-detect format
        if file_format is None:
            suffix = path.suffix.lower()
            format_map = {'.csv': 'csv', '.parquet': 'parquet', '.json': 'json'}
            file_format = format_map.get(suffix, 'csv')

        logger.info(f"Loading {file_format} file: {file_path}")

        # Load based on format
        if file_format == 'csv':
            df = pd.read_csv(file_path)
        elif file_format == 'parquet':
            df = pd.read_parquet(file_path)
        elif file_format == 'json':
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_format}")

        # Sample if requested
        if sample_size and sample_size < len(df):
            logger.info(f"Sampling {sample_size} rows from {len(df)} total")
            df = df.sample(n=sample_size, random_state=42)

        logger.info(f"Loaded data: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    def profile_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze schema: types, nulls, cardinality, uniqueness.

        Args:
            df: DataFrame to profile

        Returns:
            Schema profile dict
        """
        logger.info("Profiling schema...")

        schema = {
            'n_rows': len(df),
            'n_columns': len(df.columns),
            'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1e6),
            'columns': {}
        }

        for col in df.columns:
            col_data = df[col]

            # Basic info
            col_profile = {
                'dtype': str(col_data.dtype),
                'null_count': int(col_data.isnull().sum()),
                'null_percentage': float(col_data.isnull().sum() / len(df) * 100),
                'unique_count': int(col_data.nunique()),
                'unique_percentage': float(col_data.nunique() / len(df) * 100)
            }

            # Type-specific info
            if pd.api.types.is_numeric_dtype(col_data):
                col_profile['type_category'] = 'numeric'
                col_profile['has_negatives'] = bool((col_data < 0).any())
                col_profile['has_zeros'] = bool((col_data == 0).any())
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                col_profile['type_category'] = 'datetime'
                if col_data.notna().any():
                    col_profile['min_date'] = str(col_data.min())
                    col_profile['max_date'] = str(col_data.max())
            else:
                col_profile['type_category'] = 'categorical'
                col_profile['cardinality'] = int(col_data.nunique())
                if col_profile['cardinality'] <= 10:
                    value_counts = col_data.value_counts().head(10)
                    col_profile['top_values'] = value_counts.to_dict()

            # Flag potential issues
            col_profile['flags'] = []
            if col_profile['null_percentage'] > 50:
                col_profile['flags'].append('HIGH_NULLS')
            if col_profile['unique_percentage'] > 95:
                col_profile['flags'].append('POTENTIAL_ID')
            if col_profile['unique_count'] == 1:
                col_profile['flags'].append('CONSTANT')

            schema['columns'][col] = col_profile

        # Type distribution
        type_counts = df.dtypes.value_counts()
        schema['type_distribution'] = {str(k): int(v) for k, v in type_counts.items()}

        return schema

    def profile_distributions(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze distributions for numeric columns.

        Args:
            df: DataFrame to profile
            columns: Specific columns to analyze (None for all numeric)

        Returns:
            Distribution profile dict
        """
        logger.info("Profiling distributions...")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if columns:
            numeric_cols = [c for c in columns if c in numeric_cols]

        distributions = {}

        for col in numeric_cols:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            # Basic statistics
            dist_profile = {
                'count': int(len(col_data)),
                'mean': float(col_data.mean()),
                'median': float(col_data.median()),
                'std': float(col_data.std()),
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'q25': float(col_data.quantile(0.25)),
                'q75': float(col_data.quantile(0.75)),
                'iqr': float(col_data.quantile(0.75) - col_data.quantile(0.25))
            }

            # Distribution shape
            if len(col_data) > 3:
                dist_profile['skewness'] = float(col_data.skew())
                dist_profile['kurtosis'] = float(col_data.kurtosis())

                # Interpret skewness
                if abs(dist_profile['skewness']) < 0.5:
                    dist_profile['skew_interpretation'] = 'symmetric'
                elif dist_profile['skewness'] > 0:
                    dist_profile['skew_interpretation'] = 'right-skewed'
                else:
                    dist_profile['skew_interpretation'] = 'left-skewed'

            distributions[col] = dist_profile

        return distributions

    def detect_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Detect outliers using specified method.

        Args:
            df: DataFrame to analyze
            columns: Specific columns to check (None for all numeric)

        Returns:
            Outlier analysis dict
        """
        logger.info(f"Detecting outliers using {self.outlier_method}...")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if columns:
            numeric_cols = [c for c in columns if c in numeric_cols]

        outliers = {}

        for col in numeric_cols:
            col_data = df[col].dropna()

            if len(col_data) == 0:
                continue

            outlier_mask = np.zeros(len(col_data), dtype=bool)

            if self.outlier_method == 'zscore':
                # Z-score method
                z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
                outlier_mask = z_scores > self.outlier_threshold

            elif self.outlier_method == 'iqr':
                # IQR method
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - self.outlier_threshold * iqr
                upper_bound = q3 + self.outlier_threshold * iqr
                outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)

            elif self.outlier_method == 'isolation_forest':
                # Isolation Forest (requires sklearn)
                try:
                    from sklearn.ensemble import IsolationForest
                    iso_forest = IsolationForest(contamination=self.outlier_threshold, random_state=42)
                    outlier_mask = iso_forest.fit_predict(col_data.values.reshape(-1, 1)) == -1
                except ImportError:
                    logger.warning("sklearn not available, skipping isolation forest")
                    continue

            outlier_count = int(outlier_mask.sum())
            outlier_percentage = float(outlier_count / len(col_data) * 100)

            outliers[col] = {
                'method': self.outlier_method,
                'threshold': self.outlier_threshold,
                'outlier_count': outlier_count,
                'outlier_percentage': outlier_percentage,
                'total_non_null': int(len(col_data))
            }

            # Flag if significant outliers
            if outlier_percentage > 5:
                outliers[col]['flag'] = 'HIGH_OUTLIERS'

        return outliers

    def analyze_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze duplicate rows.

        Args:
            df: DataFrame to analyze

        Returns:
            Duplicate analysis dict
        """
        logger.info("Analyzing duplicates...")

        # Exact duplicates
        duplicate_mask = df.duplicated()
        n_duplicates = int(duplicate_mask.sum())

        analysis = {
            'exact_duplicates': {
                'count': n_duplicates,
                'percentage': float(n_duplicates / len(df) * 100)
            }
        }

        # Flag if significant
        if analysis['exact_duplicates']['percentage'] > 5:
            analysis['exact_duplicates']['flag'] = 'HIGH_DUPLICATION'

        # Per-column uniqueness (already in schema, but summarize here)
        uniqueness_summary = {}
        for col in df.columns:
            unique_pct = df[col].nunique() / len(df) * 100
            if unique_pct > 95:
                uniqueness_summary[col] = {
                    'unique_percentage': float(unique_pct),
                    'flag': 'POTENTIAL_ID'
                }

        if uniqueness_summary:
            analysis['high_uniqueness_columns'] = uniqueness_summary

        return analysis

    def analyze_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze missing data patterns.

        Args:
            df: DataFrame to analyze

        Returns:
            Missing data analysis dict
        """
        logger.info("Analyzing missing data patterns...")

        # Overall missingness
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()

        analysis = {
            'overall': {
                'total_cells': int(total_cells),
                'missing_cells': int(missing_cells),
                'missing_percentage': float(missing_cells / total_cells * 100)
            },
            'by_column': {}
        }

        # Per-column analysis
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                null_pct = float(null_count / len(df) * 100)

                col_analysis = {
                    'null_count': int(null_count),
                    'null_percentage': null_pct
                }

                # Severity flag
                if null_pct > 50:
                    col_analysis['severity'] = 'CRITICAL'
                elif null_pct > 20:
                    col_analysis['severity'] = 'HIGH'
                elif null_pct > 10:
                    col_analysis['severity'] = 'MEDIUM'
                else:
                    col_analysis['severity'] = 'LOW'

                analysis['by_column'][col] = col_analysis

        # Rows with any missing
        rows_with_missing = df.isnull().any(axis=1).sum()
        analysis['rows_with_any_missing'] = {
            'count': int(rows_with_missing),
            'percentage': float(rows_with_missing / len(df) * 100)
        }

        return analysis

    def generate_report(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                       detailed: bool = False) -> Dict[str, Any]:
        """
        Generate comprehensive quality report.

        Args:
            df: DataFrame to profile
            columns: Specific columns to focus on (None for all)
            detailed: Include detailed analysis

        Returns:
            Complete quality report dict
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'dataset_info': {
                'n_rows': len(df),
                'n_columns': len(df.columns),
                'memory_mb': float(df.memory_usage(deep=True).sum() / 1e6)
            }
        }

        # Core analyses
        report['schema'] = self.profile_schema(df)
        report['missing_data'] = self.analyze_missing_patterns(df)
        report['duplicates'] = self.analyze_duplicates(df)

        # Numeric analyses
        if detailed or columns:
            report['distributions'] = self.profile_distributions(df, columns)
            report['outliers'] = self.detect_outliers(df, columns)

        # Summary flags
        report['quality_flags'] = self._extract_quality_flags(report)

        return report

    def _extract_quality_flags(self, report: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract critical quality flags from report."""
        flags = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        }

        # Check for critical issues
        for col, info in report['schema']['columns'].items():
            if 'CONSTANT' in info.get('flags', []):
                flags['MEDIUM'].append(f"{col}: Constant value (zero variance)")
            if 'POTENTIAL_ID' in info.get('flags', []):
                flags['HIGH'].append(f"{col}: Potential identifier (>95% unique)")
            if 'HIGH_NULLS' in info.get('flags', []):
                flags['HIGH'].append(f"{col}: High null percentage ({info['null_percentage']:.1f}%)")

        # Check duplicates
        if report['duplicates']['exact_duplicates'].get('flag') == 'HIGH_DUPLICATION':
            pct = report['duplicates']['exact_duplicates']['percentage']
            flags['MEDIUM'].append(f"High duplication rate ({pct:.1f}%)")

        # Check missing data
        for col, info in report['missing_data'].get('by_column', {}).items():
            if info['severity'] == 'CRITICAL':
                flags['CRITICAL'].append(f"{col}: Critical missingness ({info['null_percentage']:.1f}%)")

        return flags

    def format_output(self, report: Dict[str, Any], output_format: str = 'json') -> str:
        """Format report for output."""
        if output_format == 'json':
            return json.dumps(report, indent=2)

        elif output_format == 'text':
            lines = ["=" * 60]
            lines.append("DATA QUALITY REPORT")
            lines.append("=" * 60)
            lines.append(f"\nDataset: {report['dataset_info']['n_rows']} rows × {report['dataset_info']['n_columns']} columns")
            lines.append(f"Memory: {report['dataset_info']['memory_mb']:.2f} MB")

            # Flags
            lines.append("\n" + "=" * 60)
            lines.append("QUALITY FLAGS")
            lines.append("=" * 60)
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if report['quality_flags'][severity]:
                    lines.append(f"\n{severity}:")
                    for flag in report['quality_flags'][severity]:
                        lines.append(f"  - {flag}")

            # Missing data summary
            lines.append("\n" + "=" * 60)
            lines.append("MISSING DATA SUMMARY")
            lines.append("=" * 60)
            overall = report['missing_data']['overall']
            lines.append(f"Overall: {overall['missing_percentage']:.2f}% of all cells")

            if report['missing_data']['by_column']:
                lines.append("\nColumns with missing data:")
                for col, info in sorted(report['missing_data']['by_column'].items(),
                                       key=lambda x: x[1]['null_percentage'], reverse=True):
                    lines.append(f"  {col}: {info['null_percentage']:.1f}% ({info['severity']})")

            # Duplicates
            lines.append("\n" + "=" * 60)
            lines.append("DUPLICATES")
            lines.append("=" * 60)
            dup_pct = report['duplicates']['exact_duplicates']['percentage']
            lines.append(f"Exact duplicates: {report['duplicates']['exact_duplicates']['count']} ({dup_pct:.2f}%)")

            return "\n".join(lines)

        return str(report)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--data',
        required=True,
        help='Path to dataset file (CSV, Parquet, or JSON)'
    )

    parser.add_argument(
        '--columns',
        help='Comma-separated list of columns to analyze in detail'
    )

    parser.add_argument(
        '--outlier_method',
        choices=['zscore', 'iqr', 'isolation_forest'],
        default='zscore',
        help='Outlier detection method (default: zscore)'
    )

    parser.add_argument(
        '--outlier_threshold',
        type=float,
        default=3.0,
        help='Outlier threshold (default: 3.0 for zscore/iqr, 0.1 for isolation_forest)'
    )

    parser.add_argument(
        '--sample',
        type=int,
        help='Sample N rows for large datasets'
    )

    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed distribution and outlier analysis'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Output file path (default: stdout)'
    )

    parser.add_argument(
        '--format',
        '-f',
        choices=['json', 'text'],
        default='json',
        help='Output format (default: json)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    try:
        args = parse_arguments()

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Initialize checker
        checker = DataQualityChecker(
            outlier_method=args.outlier_method,
            outlier_threshold=args.outlier_threshold
        )

        # Load data
        df = checker.load_data(args.data, sample_size=args.sample)

        # Parse columns if specified
        columns = None
        if args.columns:
            columns = [c.strip() for c in args.columns.split(',')]

        # Generate report
        report = checker.generate_report(df, columns=columns, detailed=args.detailed)

        # Format output
        output = checker.format_output(report, output_format=args.format)

        # Write output
        if args.output:
            Path(args.output).write_text(output)
            logger.info(f"Report written to: {args.output}")
        else:
            print(output)

        return 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
