#!/usr/bin/env python3
"""
Tool Name: Evaluation Runner
Purpose: Execute comprehensive model evaluation with multiple metrics, stratification, and confidence intervals
Usage: python evaluation_runner.py --predictions preds.csv --labels labels.csv --metrics accuracy,f1,auc

This tool is part of the ml-evaluator agent's toolkit.
It helps the agent perform rigorous model evaluation by computing metrics with statistical rigor,
supporting stratification, bootstrap confidence intervals, and multiple evaluation sets.

Examples:
    # Basic evaluation
    python evaluation_runner.py --predictions preds.csv --labels labels.csv --metrics accuracy,f1_macro,auc_roc

    # With confidence intervals
    python evaluation_runner.py --predictions preds.csv --labels labels.csv --metrics accuracy,f1,auc --bootstrap 1000 --seed 42

    # Stratified evaluation
    python evaluation_runner.py --predictions preds.csv --labels labels.csv --features features.csv --stratify_by category --metrics accuracy,f1

    # Data integrity check only
    python evaluation_runner.py --data_check --test_set test.csv --label target
"""

import argparse
import sys
import json
import logging
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from collections import defaultdict

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvaluationRunner:
    """
    Comprehensive model evaluation runner.

    This class provides:
    - Multiple classification and regression metrics
    - Bootstrap confidence intervals
    - Stratified evaluation by subgroups
    - Data integrity checks
    - Reproducible results with seed control
    """

    CLASSIFICATION_METRICS = {
        'accuracy', 'precision', 'recall', 'f1', 'f1_macro', 'f1_weighted',
        'auc_roc', 'auc_pr', 'mcc', 'cohen_kappa'
    }

    REGRESSION_METRICS = {
        'mae', 'mse', 'rmse', 'r2', 'mape', 'median_ae'
    }

    def __init__(self, task_type='classification', seed=42, bootstrap_samples=1000):
        """
        Initialize the evaluation runner.

        Args:
            task_type: 'classification' or 'regression'
            seed: Random seed for reproducibility
            bootstrap_samples: Number of bootstrap samples for CI calculation
        """
        self.task_type = task_type
        self.seed = seed
        self.bootstrap_samples = bootstrap_samples
        np.random.seed(seed)
        logger.debug(f"Initialized EvaluationRunner with task_type={task_type}, seed={seed}")

    def validate_input(self, predictions: np.ndarray, labels: np.ndarray,
                       probabilities: Optional[np.ndarray] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate input data before processing.

        Args:
            predictions: Model predictions
            labels: Ground truth labels
            probabilities: Prediction probabilities (optional, for AUC metrics)

        Returns:
            tuple: (is_valid, error_message)
        """
        if len(predictions) != len(labels):
            return False, f"Length mismatch: predictions ({len(predictions)}) vs labels ({len(labels)})"

        if len(predictions) == 0:
            return False, "Empty predictions/labels arrays"

        if probabilities is not None and len(probabilities) != len(predictions):
            return False, f"Probabilities length ({len(probabilities)}) doesn't match predictions ({len(predictions)})"

        # Check for NaN or infinite values
        if np.any(np.isnan(predictions)) or np.any(np.isinf(predictions)):
            return False, "Predictions contain NaN or infinite values"

        if np.any(np.isnan(labels)) or np.any(np.isinf(labels)):
            return False, "Labels contain NaN or infinite values"

        return True, None

    def data_integrity_check(self, data: pd.DataFrame, label_col: str) -> Dict[str, Any]:
        """
        Perform comprehensive data integrity checks.

        Args:
            data: DataFrame containing test data
            label_col: Name of the label column

        Returns:
            dict: Integrity check results
        """
        logger.info("Running data integrity checks...")

        results = {
            'status': 'success',
            'n_samples': len(data),
            'n_features': len(data.columns) - 1,
            'checks': {}
        }

        # Check for missing values
        missing_counts = data.isnull().sum()
        results['checks']['missing_values'] = {
            'has_missing': missing_counts.sum() > 0,
            'columns_with_missing': missing_counts[missing_counts > 0].to_dict()
        }

        # Check label distribution
        if label_col in data.columns:
            label_dist = data[label_col].value_counts().to_dict()
            results['checks']['label_distribution'] = label_dist
            results['checks']['n_classes'] = len(label_dist)

            # Check for class imbalance
            if self.task_type == 'classification':
                max_count = max(label_dist.values())
                min_count = min(label_dist.values())
                imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
                results['checks']['imbalance_ratio'] = imbalance_ratio
                results['checks']['is_imbalanced'] = imbalance_ratio > 3.0
        else:
            results['status'] = 'warning'
            results['warning'] = f"Label column '{label_col}' not found"

        # Check for duplicates
        n_duplicates = data.duplicated().sum()
        results['checks']['duplicates'] = {
            'n_duplicates': int(n_duplicates),
            'duplicate_percentage': float(n_duplicates / len(data) * 100)
        }

        # Check feature types
        results['checks']['feature_types'] = {
            'numeric': int((data.select_dtypes(include=[np.number]).columns != label_col).sum()),
            'categorical': int((data.select_dtypes(exclude=[np.number]).columns != label_col).sum())
        }

        # Basic statistics for numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            results['checks']['numeric_summary'] = {
                'mean_range': [float(data[numeric_cols].mean().min()),
                              float(data[numeric_cols].mean().max())],
                'std_range': [float(data[numeric_cols].std().min()),
                             float(data[numeric_cols].std().max())]
            }

        logger.info(f"Data integrity check complete: {results['n_samples']} samples, {results['n_features']} features")
        return results

    def compute_classification_metric(self, metric: str, y_true: np.ndarray,
                                     y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None) -> float:
        """
        Compute a single classification metric.

        Args:
            metric: Metric name
            y_true: True labels
            y_pred: Predicted labels
            y_prob: Prediction probabilities (for AUC metrics)

        Returns:
            float: Metric value
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            roc_auc_score, average_precision_score, matthews_corrcoef,
            cohen_kappa_score
        )

        if metric == 'accuracy':
            return accuracy_score(y_true, y_pred)

        elif metric == 'precision':
            return precision_score(y_true, y_pred, average='binary', zero_division=0)

        elif metric == 'recall':
            return recall_score(y_true, y_pred, average='binary', zero_division=0)

        elif metric == 'f1':
            return f1_score(y_true, y_pred, average='binary', zero_division=0)

        elif metric == 'f1_macro':
            return f1_score(y_true, y_pred, average='macro', zero_division=0)

        elif metric == 'f1_weighted':
            return f1_score(y_true, y_pred, average='weighted', zero_division=0)

        elif metric == 'mcc':
            return matthews_corrcoef(y_true, y_pred)

        elif metric == 'cohen_kappa':
            return cohen_kappa_score(y_true, y_pred)

        elif metric == 'auc_roc':
            if y_prob is None:
                logger.warning("AUC-ROC requires probabilities, returning NaN")
                return np.nan
            try:
                # Handle binary and multi-class
                if len(np.unique(y_true)) == 2:
                    # Binary case - use positive class probability
                    if y_prob.ndim == 2:
                        y_prob = y_prob[:, 1]
                    return roc_auc_score(y_true, y_prob)
                else:
                    # Multi-class case
                    return roc_auc_score(y_true, y_prob, multi_class='ovr', average='macro')
            except Exception as e:
                logger.warning(f"Failed to compute AUC-ROC: {e}")
                return np.nan

        elif metric == 'auc_pr':
            if y_prob is None:
                logger.warning("AUC-PR requires probabilities, returning NaN")
                return np.nan
            try:
                if y_prob.ndim == 2:
                    y_prob = y_prob[:, 1]
                return average_precision_score(y_true, y_prob)
            except Exception as e:
                logger.warning(f"Failed to compute AUC-PR: {e}")
                return np.nan

        else:
            raise ValueError(f"Unknown classification metric: {metric}")

    def compute_regression_metric(self, metric: str, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Compute a single regression metric.

        Args:
            metric: Metric name
            y_true: True values
            y_pred: Predicted values

        Returns:
            float: Metric value
        """
        from sklearn.metrics import (
            mean_absolute_error, mean_squared_error, r2_score,
            median_absolute_error
        )

        if metric == 'mae':
            return mean_absolute_error(y_true, y_pred)

        elif metric == 'mse':
            return mean_squared_error(y_true, y_pred)

        elif metric == 'rmse':
            return np.sqrt(mean_squared_error(y_true, y_pred))

        elif metric == 'r2':
            return r2_score(y_true, y_pred)

        elif metric == 'mape':
            # Mean Absolute Percentage Error
            mask = y_true != 0
            return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

        elif metric == 'median_ae':
            return median_absolute_error(y_true, y_pred)

        else:
            raise ValueError(f"Unknown regression metric: {metric}")

    def bootstrap_ci(self, y_true: np.ndarray, y_pred: np.ndarray,
                    metric: str, y_prob: Optional[np.ndarray] = None,
                    confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate bootstrap confidence interval for a metric.

        Args:
            y_true: True labels/values
            y_pred: Predictions
            metric: Metric name
            y_prob: Probabilities (optional)
            confidence: Confidence level (default 0.95)

        Returns:
            tuple: (lower_bound, upper_bound)
        """
        n = len(y_true)
        bootstrap_scores = []

        for _ in range(self.bootstrap_samples):
            # Resample with replacement
            indices = np.random.choice(n, size=n, replace=True)
            y_true_boot = y_true[indices]
            y_pred_boot = y_pred[indices]
            y_prob_boot = y_prob[indices] if y_prob is not None else None

            # Compute metric on bootstrap sample
            try:
                if self.task_type == 'classification':
                    score = self.compute_classification_metric(metric, y_true_boot, y_pred_boot, y_prob_boot)
                else:
                    score = self.compute_regression_metric(metric, y_true_boot, y_pred_boot)

                if not np.isnan(score):
                    bootstrap_scores.append(score)
            except Exception as e:
                logger.debug(f"Bootstrap sample failed: {e}")
                continue

        if len(bootstrap_scores) == 0:
            return np.nan, np.nan

        # Calculate confidence interval
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        ci_lower = np.percentile(bootstrap_scores, lower_percentile)
        ci_upper = np.percentile(bootstrap_scores, upper_percentile)

        return float(ci_lower), float(ci_upper)

    def evaluate(self, predictions: np.ndarray, labels: np.ndarray,
                metrics: List[str], probabilities: Optional[np.ndarray] = None,
                compute_ci: bool = False) -> Dict[str, Any]:
        """
        Main evaluation function.

        Args:
            predictions: Model predictions
            labels: Ground truth labels
            metrics: List of metrics to compute
            probabilities: Prediction probabilities (optional)
            compute_ci: Whether to compute bootstrap confidence intervals

        Returns:
            dict: Evaluation results
        """
        # Validate input
        is_valid, error = self.validate_input(predictions, labels, probabilities)
        if not is_valid:
            return {
                "status": "error",
                "error": error,
                "data": None
            }

        try:
            results = {
                "status": "success",
                "task_type": self.task_type,
                "n_samples": len(predictions),
                "seed": self.seed,
                "metrics": {}
            }

            # Compute each metric
            for metric in metrics:
                logger.info(f"Computing {metric}...")

                try:
                    if self.task_type == 'classification':
                        value = self.compute_classification_metric(metric, labels, predictions, probabilities)
                    else:
                        value = self.compute_regression_metric(metric, labels, predictions)

                    metric_result = {
                        "value": float(value) if not np.isnan(value) else None
                    }

                    # Compute confidence interval if requested
                    if compute_ci and not np.isnan(value):
                        logger.info(f"Computing bootstrap CI for {metric}...")
                        ci_lower, ci_upper = self.bootstrap_ci(labels, predictions, metric, probabilities)
                        metric_result["ci_lower"] = float(ci_lower) if not np.isnan(ci_lower) else None
                        metric_result["ci_upper"] = float(ci_upper) if not np.isnan(ci_upper) else None
                        metric_result["ci_width"] = float(ci_upper - ci_lower) if not (np.isnan(ci_lower) or np.isnan(ci_upper)) else None

                    results["metrics"][metric] = metric_result

                except Exception as e:
                    logger.error(f"Failed to compute {metric}: {e}")
                    results["metrics"][metric] = {
                        "value": None,
                        "error": str(e)
                    }

            return results

        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }

    def stratified_evaluate(self, predictions: np.ndarray, labels: np.ndarray,
                          features: pd.DataFrame, stratify_by: str, metrics: List[str],
                          probabilities: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Evaluate with stratification by a feature.

        Args:
            predictions: Model predictions
            labels: Ground truth labels
            features: DataFrame containing features including stratification column
            stratify_by: Column name to stratify by
            metrics: List of metrics to compute
            probabilities: Prediction probabilities (optional)

        Returns:
            dict: Stratified evaluation results
        """
        if stratify_by not in features.columns:
            return {
                "status": "error",
                "error": f"Stratification column '{stratify_by}' not found in features",
                "data": None
            }

        results = {
            "status": "success",
            "task_type": self.task_type,
            "stratified_by": stratify_by,
            "strata": {}
        }

        # Get unique strata
        strata_values = features[stratify_by].unique()
        logger.info(f"Stratifying by {stratify_by}: found {len(strata_values)} strata")

        for stratum in strata_values:
            logger.info(f"Evaluating stratum: {stratum}")

            # Get indices for this stratum
            mask = features[stratify_by] == stratum
            stratum_indices = np.where(mask)[0]

            if len(stratum_indices) == 0:
                continue

            # Extract data for this stratum
            stratum_preds = predictions[stratum_indices]
            stratum_labels = labels[stratum_indices]
            stratum_probs = probabilities[stratum_indices] if probabilities is not None else None

            # Evaluate this stratum
            stratum_results = self.evaluate(
                stratum_preds, stratum_labels, metrics, stratum_probs, compute_ci=False
            )

            if stratum_results["status"] == "success":
                results["strata"][str(stratum)] = {
                    "n_samples": int(len(stratum_indices)),
                    "metrics": stratum_results["metrics"]
                }

        return results

    def format_output(self, result: Dict[str, Any], output_format: str = "json") -> str:
        """
        Format the output for display.

        Args:
            result: The evaluation result
            output_format: Output format (json, text, markdown)

        Returns:
            Formatted output string
        """
        if output_format == "json":
            return json.dumps(result, indent=2)

        elif output_format == "text":
            if result["status"] == "error":
                return f"ERROR: {result['error']}"

            lines = [f"Evaluation Results ({result.get('task_type', 'unknown')} task)"]
            lines.append(f"Samples: {result.get('n_samples', 'N/A')}")
            lines.append(f"Seed: {result.get('seed', 'N/A')}")
            lines.append("\nMetrics:")

            for metric, data in result.get("metrics", {}).items():
                if data.get("value") is not None:
                    line = f"  {metric}: {data['value']:.4f}"
                    if "ci_lower" in data and data["ci_lower"] is not None:
                        line += f" [{data['ci_lower']:.4f}, {data['ci_upper']:.4f}]"
                    lines.append(line)
                else:
                    lines.append(f"  {metric}: ERROR - {data.get('error', 'N/A')}")

            return "\n".join(lines)

        elif output_format == "markdown":
            if result["status"] == "error":
                return f"## Error\n\n{result['error']}"

            lines = [
                f"## Evaluation Results",
                f"\n**Task Type:** {result.get('task_type', 'unknown')}",
                f"**Samples:** {result.get('n_samples', 'N/A')}",
                f"**Seed:** {result.get('seed', 'N/A')}",
                f"\n### Metrics\n",
                "| Metric | Value | 95% CI |",
                "|--------|-------|--------|"
            ]

            for metric, data in result.get("metrics", {}).items():
                if data.get("value") is not None:
                    value_str = f"{data['value']:.4f}"
                    ci_str = f"[{data['ci_lower']:.4f}, {data['ci_upper']:.4f}]" if "ci_lower" in data else "N/A"
                    lines.append(f"| {metric} | {value_str} | {ci_str} |")
                else:
                    lines.append(f"| {metric} | ERROR | {data.get('error', 'N/A')} |")

            return "\n".join(lines)

        return str(result)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Operation mode
    parser.add_argument(
        "--data_check",
        action="store_true",
        help="Run data integrity check only"
    )

    # Input files
    parser.add_argument(
        "--predictions",
        help="CSV file containing predictions"
    )

    parser.add_argument(
        "--labels",
        help="CSV file containing true labels"
    )

    parser.add_argument(
        "--probabilities",
        help="CSV file containing prediction probabilities (optional, for AUC metrics)"
    )

    parser.add_argument(
        "--test_set",
        help="CSV file for data integrity check"
    )

    parser.add_argument(
        "--label",
        help="Label column name for data integrity check"
    )

    parser.add_argument(
        "--features",
        help="CSV file containing features (for stratified evaluation)"
    )

    # Evaluation parameters
    parser.add_argument(
        "--metrics",
        default="accuracy,f1",
        help="Comma-separated list of metrics (default: accuracy,f1)"
    )

    parser.add_argument(
        "--task_type",
        choices=["classification", "regression"],
        default="classification",
        help="Task type (default: classification)"
    )

    parser.add_argument(
        "--stratify_by",
        help="Column name to stratify evaluation by"
    )

    # Statistical parameters
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=0,
        help="Number of bootstrap samples for CI (0 to disable, default: 0)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    # Output parameters
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)"
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "text", "markdown"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the tool.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        args = parse_arguments()

        # Set logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Data integrity check mode
        if args.data_check:
            if not args.test_set or not args.label:
                logger.error("--test_set and --label required for data integrity check")
                return 1

            test_path = Path(args.test_set)
            if not test_path.exists():
                logger.error(f"Test set file not found: {args.test_set}")
                return 1

            logger.info(f"Loading test set: {args.test_set}")
            test_data = pd.read_csv(test_path)

            runner = EvaluationRunner(task_type=args.task_type, seed=args.seed)
            result = runner.data_integrity_check(test_data, args.label)
            output = json.dumps(result, indent=2)

            if args.output:
                Path(args.output).write_text(output)
                logger.info(f"Output written to: {args.output}")
            else:
                print(output)

            return 0

        # Standard evaluation mode
        if not args.predictions or not args.labels:
            logger.error("--predictions and --labels required for evaluation")
            return 1

        # Load data
        pred_path = Path(args.predictions)
        label_path = Path(args.labels)

        if not pred_path.exists():
            logger.error(f"Predictions file not found: {args.predictions}")
            return 1

        if not label_path.exists():
            logger.error(f"Labels file not found: {args.labels}")
            return 1

        logger.info(f"Loading predictions: {args.predictions}")
        predictions = pd.read_csv(pred_path).values.ravel()

        logger.info(f"Loading labels: {args.labels}")
        labels = pd.read_csv(label_path).values.ravel()

        probabilities = None
        if args.probabilities:
            prob_path = Path(args.probabilities)
            if prob_path.exists():
                logger.info(f"Loading probabilities: {args.probabilities}")
                probabilities = pd.read_csv(prob_path).values
            else:
                logger.warning(f"Probabilities file not found: {args.probabilities}")

        # Parse metrics
        metrics = [m.strip() for m in args.metrics.split(',')]

        # Initialize runner
        runner = EvaluationRunner(
            task_type=args.task_type,
            seed=args.seed,
            bootstrap_samples=args.bootstrap if args.bootstrap > 0 else 1000
        )

        # Stratified evaluation
        if args.stratify_by:
            if not args.features:
                logger.error("--features required for stratified evaluation")
                return 1

            features_path = Path(args.features)
            if not features_path.exists():
                logger.error(f"Features file not found: {args.features}")
                return 1

            logger.info(f"Loading features: {args.features}")
            features = pd.read_csv(features_path)

            result = runner.stratified_evaluate(
                predictions, labels, features, args.stratify_by,
                metrics, probabilities
            )
        else:
            # Standard evaluation
            result = runner.evaluate(
                predictions, labels, metrics, probabilities,
                compute_ci=(args.bootstrap > 0)
            )

        # Format output
        output = runner.format_output(result, args.format)

        # Write output
        if args.output:
            Path(args.output).write_text(output)
            logger.info(f"Output written to: {args.output}")
        else:
            print(output)

        return 0 if result["status"] == "success" else 1

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
