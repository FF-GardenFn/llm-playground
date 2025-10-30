#!/usr/bin/env python3
"""
Tool Name: Schema Validator
Purpose: Validate data schemas, check constraints, detect schema drift
Usage: python schema_validator.py --data dataset.csv --schema schema.json --validate

This tool is part of the data-profiler agent's toolkit.
It validates data against expected schemas, checks type constraints, range validation,
and detects schema drift.

Examples:
    # Infer schema from data
    python schema_validator.py --infer --data train.csv --output schema.json

    # Validate data against schema
    python schema_validator.py --validate --data test.csv --schema schema.json

    # Strict validation with all checks
    python schema_validator.py --validate --data test.csv --schema schema.json --strict --type_check --range_check --null_check
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SchemaValidator:
    """Schema validation and inference tool."""

    def __init__(self, strict=False):
        self.strict = strict

    def infer_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Infer schema from DataFrame."""
        logger.info("Inferring schema from data...")

        schema = {
            'n_rows': len(df),
            'n_columns': len(df.columns),
            'columns': {}
        }

        for col in df.columns:
            col_data = df[col]
            col_schema = {
                'dtype': str(col_data.dtype),
                'nullable': bool(col_data.isnull().any()),
                'unique_count': int(col_data.nunique())
            }

            if pd.api.types.is_numeric_dtype(col_data):
                col_schema['type'] = 'numeric'
                if col_data.notna().any():
                    col_schema['min'] = float(col_data.min())
                    col_schema['max'] = float(col_data.max())
                    col_schema['mean'] = float(col_data.mean())
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                col_schema['type'] = 'datetime'
                if col_data.notna().any():
                    col_schema['min'] = str(col_data.min())
                    col_schema['max'] = str(col_data.max())
            else:
                col_schema['type'] = 'categorical'
                if col_data.nunique() <= 20:
                    col_schema['allowed_values'] = col_data.dropna().unique().tolist()

            schema['columns'][col] = col_schema

        return schema

    def validate_schema(self, df: pd.DataFrame, schema: Dict[str, Any],
                       type_check=True, range_check=True, null_check=True) -> Dict[str, Any]:
        """Validate DataFrame against schema."""
        logger.info("Validating data against schema...")

        results = {
            'valid': True,
            'violations': [],
            'warnings': []
        }

        # Check column presence
        expected_cols = set(schema['columns'].keys())
        actual_cols = set(df.columns)

        missing_cols = expected_cols - actual_cols
        extra_cols = actual_cols - expected_cols

        if missing_cols:
            results['valid'] = False
            results['violations'].append({
                'type': 'MISSING_COLUMNS',
                'columns': list(missing_cols)
            })

        if extra_cols:
            results['warnings'].append({
                'type': 'EXTRA_COLUMNS',
                'columns': list(extra_cols)
            })

        # Validate each column
        for col, col_schema in schema['columns'].items():
            if col not in df.columns:
                continue

            col_data = df[col]

            # Type check
            if type_check:
                expected_dtype = col_schema.get('dtype')
                actual_dtype = str(col_data.dtype)

                if expected_dtype and expected_dtype != actual_dtype:
                    results['violations'].append({
                        'type': 'TYPE_MISMATCH',
                        'column': col,
                        'expected': expected_dtype,
                        'actual': actual_dtype
                    })
                    if self.strict:
                        results['valid'] = False

            # Null check
            if null_check:
                has_nulls = col_data.isnull().any()
                nullable = col_schema.get('nullable', True)

                if has_nulls and not nullable:
                    results['violations'].append({
                        'type': 'NULL_VIOLATION',
                        'column': col,
                        'null_count': int(col_data.isnull().sum())
                    })
                    if self.strict:
                        results['valid'] = False

            # Range check for numeric columns
            if range_check and pd.api.types.is_numeric_dtype(col_data):
                if 'min' in col_schema:
                    violations = col_data[col_data < col_schema['min']].count()
                    if violations > 0:
                        results['violations'].append({
                            'type': 'RANGE_VIOLATION_MIN',
                            'column': col,
                            'expected_min': col_schema['min'],
                            'actual_min': float(col_data.min()),
                            'violation_count': int(violations)
                        })

                if 'max' in col_schema:
                    violations = col_data[col_data > col_schema['max']].count()
                    if violations > 0:
                        results['violations'].append({
                            'type': 'RANGE_VIOLATION_MAX',
                            'column': col,
                            'expected_max': col_schema['max'],
                            'actual_max': float(col_data.max()),
                            'violation_count': int(violations)
                        })

            # Allowed values check for categorical
            if 'allowed_values' in col_schema:
                allowed = set(col_schema['allowed_values'])
                actual = set(col_data.dropna().unique())
                invalid = actual - allowed

                if invalid:
                    results['violations'].append({
                        'type': 'INVALID_VALUES',
                        'column': col,
                        'invalid_values': list(invalid)[:10]  # Limit output
                    })

        return results


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--data', required=True, help='Path to dataset')
    parser.add_argument('--schema', help='Path to schema JSON file')
    parser.add_argument('--infer', action='store_true', help='Infer schema from data')
    parser.add_argument('--validate', action='store_true', help='Validate data against schema')
    parser.add_argument('--strict', action='store_true', help='Strict validation mode')
    parser.add_argument('--type_check', action='store_true', help='Check data types')
    parser.add_argument('--range_check', action='store_true', help='Check numeric ranges')
    parser.add_argument('--null_check', action='store_true', help='Check null constraints')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    validator = SchemaValidator(strict=args.strict)
    df = pd.read_csv(args.data)

    if args.infer:
        schema = validator.infer_schema(df)
        output = json.dumps(schema, indent=2)

        if args.output:
            Path(args.output).write_text(output)
            logger.info(f"Schema written to {args.output}")
        else:
            print(output)

    elif args.validate:
        if not args.schema:
            logger.error("--schema required for validation")
            return 1

        schema = json.loads(Path(args.schema).read_text())
        results = validator.validate_schema(df, schema, args.type_check, args.range_check, args.null_check)

        output = json.dumps(results, indent=2)

        if args.output:
            Path(args.output).write_text(output)
        else:
            print(output)

        return 0 if results['valid'] else 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
