#!/usr/bin/env python3
"""
Tool Name: Metrics Analyzer
Purpose: Compute metrics with statistical significance testing between models
Usage: python metrics_analyzer.py --model_a preds_a.csv --model_b preds_b.csv --labels labels.csv

This tool is part of the ml-evaluator agent's toolkit.
It helps compare models statistically, perform significance tests, and generate comparison reports.

Examples:
    # Compare two models with paired test
    python metrics_analyzer.py --model_a preds_a.csv --model_b preds_b.csv --labels labels.csv --paired_test

    # Multiple comparison correction
    python metrics_analyzer.py --model_a preds_a.csv --model_b preds_b.csv --labels labels.csv --paired_test --correction bonferroni

    # Cost-benefit analysis
    python metrics_analyzer.py --predictions preds.csv --labels labels.csv --cost_fp 10 --cost_fn 500 --threshold_scan 0.1,0.9,100
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
from scipy import stats

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsAnalyzer:
    """
    Statistical metrics analyzer for model comparison.

    Provides:
    - Paired statistical tests (McNemar, paired t-test, Wilcoxon)
    - Effect size calculations (Cohen's d, odds ratio)
    - Multiple comparison corrections (Bonferroni, Holm)
    - Cost-benefit analysis with threshold scanning
    - Metric comparison reports
    """

    def __init__(self, alpha=0.05):
        """
        Initialize the metrics analyzer.

        Args:
            alpha: Significance level for hypothesis testing (default: 0.05)
        """
        self.alpha = alpha
        logger.debug(f"Initialized MetricsAnalyzer with alpha={alpha}")

    def mcnemar_test(self, y_true: np.ndarray, y_pred_a: np.ndarray,
                    y_pred_b: np.ndarray) -> Dict[str, Any]:
        """
        Perform McNemar's test for paired binary predictions.

        Args:
            y_true: True labels
            y_pred_a: Predictions from model A
            y_pred_b: Predictions from model B

        Returns:
            dict: Test results including statistic, p-value, and interpretation
        """
        # Create contingency table
        # Rows: Model A (correct/incorrect), Cols: Model B (correct/incorrect)
        correct_a = (y_pred_a == y_true)
        correct_b = (y_pred_b == y_true)

        n_both_correct = np.sum(correct_a & correct_b)
        n_both_incorrect = np.sum(~correct_a & ~correct_b)
        n_a_correct_b_incorrect = np.sum(correct_a & ~correct_b)
        n_b_correct_a_incorrect = np.sum(~correct_a & correct_b)

        # McNemar test focuses on discordant pairs
        n_discordant = n_a_correct_b_incorrect + n_b_correct_a_incorrect

        if n_discordant == 0:
            return {
                "test": "mcnemar",
                "statistic": 0.0,
                "p_value": 1.0,
                "conclusion": "No discordant pairs - models perform identically",
                "contingency_table": {
                    "both_correct": int(n_both_correct),
                    "both_incorrect": int(n_both_incorrect),
                    "only_a_correct": int(n_a_correct_b_incorrect),
                    "only_b_correct": int(n_b_correct_a_incorrect)
                }
            }

        # Calculate test statistic
        if n_discordant < 25:
            # Exact binomial test for small samples
            p_value = stats.binom_test(n_a_correct_b_incorrect, n_discordant, 0.5)
            statistic = abs(n_a_correct_b_incorrect - n_b_correct_a_incorrect)
        else:
            # Chi-square approximation with continuity correction
            statistic = (abs(n_a_correct_b_incorrect - n_b_correct_a_incorrect) - 1)**2 / n_discordant
            p_value = 1 - stats.chi2.cdf(statistic, df=1)

        # Determine which model is better
        if p_value < self.alpha:
            if n_a_correct_b_incorrect > n_b_correct_a_incorrect:
                conclusion = f"Model A significantly better (p={p_value:.4f})"
            else:
                conclusion = f"Model B significantly better (p={p_value:.4f})"
        else:
            conclusion = f"No significant difference (p={p_value:.4f})"

        return {
            "test": "mcnemar",
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": p_value < self.alpha,
            "conclusion": conclusion,
            "contingency_table": {
                "both_correct": int(n_both_correct),
                "both_incorrect": int(n_both_incorrect),
                "only_a_correct": int(n_a_correct_b_incorrect),
                "only_b_correct": int(n_b_correct_a_incorrect)
            }
        }

    def paired_ttest(self, scores_a: np.ndarray, scores_b: np.ndarray) -> Dict[str, Any]:
        """
        Perform paired t-test on metric scores.

        Args:
            scores_a: Metric scores from model A
            scores_b: Metric scores from model B

        Returns:
            dict: Test results including statistic, p-value, and effect size
        """
        # Calculate differences
        differences = scores_a - scores_b

        # Paired t-test
        statistic, p_value = stats.ttest_rel(scores_a, scores_b)

        # Cohen's d effect size
        std_diff = np.std(differences, ddof=1)
        cohens_d = np.mean(differences) / std_diff if std_diff > 0 else 0.0

        # Interpret effect size
        if abs(cohens_d) < 0.2:
            effect_interpretation = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_interpretation = "small"
        elif abs(cohens_d) < 0.8:
            effect_interpretation = "medium"
        else:
            effect_interpretation = "large"

        # Conclusion
        if p_value < self.alpha:
            if np.mean(differences) > 0:
                conclusion = f"Model A significantly better (p={p_value:.4f}, d={cohens_d:.3f} [{effect_interpretation}])"
            else:
                conclusion = f"Model B significantly better (p={p_value:.4f}, d={cohens_d:.3f} [{effect_interpretation}])"
        else:
            conclusion = f"No significant difference (p={p_value:.4f}, d={cohens_d:.3f} [{effect_interpretation}])"

        return {
            "test": "paired_t_test",
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": p_value < self.alpha,
            "cohens_d": float(cohens_d),
            "effect_size": effect_interpretation,
            "mean_difference": float(np.mean(differences)),
            "conclusion": conclusion
        }

    def wilcoxon_test(self, scores_a: np.ndarray, scores_b: np.ndarray) -> Dict[str, Any]:
        """
        Perform Wilcoxon signed-rank test (non-parametric paired test).

        Args:
            scores_a: Metric scores from model A
            scores_b: Metric scores from model B

        Returns:
            dict: Test results
        """
        try:
            statistic, p_value = stats.wilcoxon(scores_a, scores_b)

            if p_value < self.alpha:
                median_diff = np.median(scores_a - scores_b)
                if median_diff > 0:
                    conclusion = f"Model A significantly better (p={p_value:.4f}, median_diff={median_diff:.4f})"
                else:
                    conclusion = f"Model B significantly better (p={p_value:.4f}, median_diff={median_diff:.4f})"
            else:
                conclusion = f"No significant difference (p={p_value:.4f})"

            return {
                "test": "wilcoxon",
                "statistic": float(statistic),
                "p_value": float(p_value),
                "significant": p_value < self.alpha,
                "conclusion": conclusion
            }
        except Exception as e:
            return {
                "test": "wilcoxon",
                "error": str(e),
                "conclusion": "Test failed - may be insufficient variance in differences"
            }

    def apply_correction(self, p_values: List[float], correction: str = 'bonferroni') -> List[float]:
        """
        Apply multiple comparison correction to p-values.

        Args:
            p_values: List of p-values
            correction: Correction method ('bonferroni', 'holm', 'none')

        Returns:
            List of corrected p-values
        """
        n = len(p_values)

        if correction == 'none':
            return p_values

        elif correction == 'bonferroni':
            return [min(p * n, 1.0) for p in p_values]

        elif correction == 'holm':
            # Holm-Bonferroni method
            sorted_indices = np.argsort(p_values)
            sorted_p = np.array(p_values)[sorted_indices]
            corrected = np.zeros(n)

            for i, p in enumerate(sorted_p):
                corrected[sorted_indices[i]] = min(p * (n - i), 1.0)

            # Enforce monotonicity
            for i in range(1, n):
                corrected[sorted_indices[i]] = max(corrected[sorted_indices[i]],
                                                   corrected[sorted_indices[i-1]])

            return corrected.tolist()

        else:
            raise ValueError(f"Unknown correction method: {correction}")

    def cost_benefit_analysis(self, y_true: np.ndarray, y_prob: np.ndarray,
                             cost_fp: float, cost_fn: float,
                             thresholds: np.ndarray) -> Dict[str, Any]:
        """
        Perform cost-benefit analysis across different classification thresholds.

        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities (for positive class)
            cost_fp: Cost of false positive
            cost_fn: Cost of false negative
            thresholds: Array of thresholds to evaluate

        Returns:
            dict: Cost analysis results including optimal threshold
        """
        results = []

        for threshold in thresholds:
            y_pred = (y_prob >= threshold).astype(int)

            # Confusion matrix elements
            tp = np.sum((y_pred == 1) & (y_true == 1))
            tn = np.sum((y_pred == 0) & (y_true == 0))
            fp = np.sum((y_pred == 1) & (y_true == 0))
            fn = np.sum((y_pred == 0) & (y_true == 1))

            # Calculate metrics
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            # Calculate costs
            total_cost_fp = fp * cost_fp
            total_cost_fn = fn * cost_fn
            total_cost = total_cost_fp + total_cost_fn

            results.append({
                "threshold": float(threshold),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
                "tp": int(tp),
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "cost_fp": float(total_cost_fp),
                "cost_fn": float(total_cost_fn),
                "total_cost": float(total_cost)
            })

        # Find optimal threshold (minimum total cost)
        optimal_idx = np.argmin([r["total_cost"] for r in results])
        optimal = results[optimal_idx]

        return {
            "cost_fp_per_instance": float(cost_fp),
            "cost_fn_per_instance": float(cost_fn),
            "optimal_threshold": optimal["threshold"],
            "optimal_total_cost": optimal["total_cost"],
            "optimal_metrics": {
                "precision": optimal["precision"],
                "recall": optimal["recall"],
                "f1": optimal["f1"]
            },
            "threshold_analysis": results
        }

    def compare_models(self, y_true: np.ndarray, y_pred_a: np.ndarray,
                      y_pred_b: np.ndarray, test_type: str = 'mcnemar',
                      correction: str = 'none') -> Dict[str, Any]:
        """
        Compare two models with statistical testing.

        Args:
            y_true: True labels
            y_pred_a: Predictions from model A
            y_pred_b: Predictions from model B
            test_type: Type of test ('mcnemar', 'paired_t', 'wilcoxon')
            correction: Multiple comparison correction method

        Returns:
            dict: Comparison results
        """
        result = {
            "status": "success",
            "test_type": test_type,
            "correction": correction,
            "alpha": self.alpha
        }

        try:
            if test_type == 'mcnemar':
                test_result = self.mcnemar_test(y_true, y_pred_a, y_pred_b)

            elif test_type == 'paired_t':
                # For paired t-test, we need per-sample scores
                # Use 1 for correct, 0 for incorrect as simple scores
                scores_a = (y_pred_a == y_true).astype(float)
                scores_b = (y_pred_b == y_true).astype(float)
                test_result = self.paired_ttest(scores_a, scores_b)

            elif test_type == 'wilcoxon':
                scores_a = (y_pred_a == y_true).astype(float)
                scores_b = (y_pred_b == y_true).astype(float)
                test_result = self.wilcoxon_test(scores_a, scores_b)

            else:
                return {
                    "status": "error",
                    "error": f"Unknown test type: {test_type}"
                }

            result["test_result"] = test_result

            # Apply correction if needed
            if correction != 'none' and "p_value" in test_result:
                original_p = test_result["p_value"]
                corrected_p = self.apply_correction([original_p], correction)[0]
                result["test_result"]["p_value_corrected"] = float(corrected_p)
                result["test_result"]["significant_after_correction"] = corrected_p < self.alpha

            return result

        except Exception as e:
            logger.error(f"Model comparison failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    def format_output(self, result: Dict[str, Any], output_format: str = "json") -> str:
        """
        Format the output for display.

        Args:
            result: The analysis result
            output_format: Output format (json, text, markdown)

        Returns:
            Formatted output string
        """
        if output_format == "json":
            return json.dumps(result, indent=2)

        elif output_format == "text":
            if result.get("status") == "error":
                return f"ERROR: {result['error']}"

            lines = ["Metrics Analysis Results\n"]

            if "test_result" in result:
                test = result["test_result"]
                lines.append(f"Test: {test.get('test', 'unknown')}")
                lines.append(f"Statistic: {test.get('statistic', 'N/A'):.4f}")
                lines.append(f"P-value: {test.get('p_value', 'N/A'):.4f}")
                if "p_value_corrected" in test:
                    lines.append(f"P-value (corrected): {test['p_value_corrected']:.4f}")
                lines.append(f"Conclusion: {test.get('conclusion', 'N/A')}")

            if "optimal_threshold" in result:
                lines.append(f"\nOptimal Threshold: {result['optimal_threshold']:.3f}")
                lines.append(f"Total Cost: ${result['optimal_total_cost']:.2f}")

            return "\n".join(lines)

        elif output_format == "markdown":
            if result.get("status") == "error":
                return f"## Error\n\n{result['error']}"

            lines = ["## Metrics Analysis Results\n"]

            if "test_result" in result:
                test = result["test_result"]
                lines.append("### Statistical Test\n")
                lines.append(f"**Test:** {test.get('test', 'unknown')}")
                lines.append(f"**Statistic:** {test.get('statistic', 'N/A'):.4f}")
                lines.append(f"**P-value:** {test.get('p_value', 'N/A'):.4f}")
                if "p_value_corrected" in test:
                    lines.append(f"**P-value (corrected):** {test['p_value_corrected']:.4f}")
                lines.append(f"**Conclusion:** {test.get('conclusion', 'N/A')}\n")

            if "optimal_threshold" in result:
                lines.append("### Cost-Benefit Analysis\n")
                lines.append(f"**Optimal Threshold:** {result['optimal_threshold']:.3f}")
                lines.append(f"**Total Cost:** ${result['optimal_total_cost']:.2f}")
                lines.append(f"**Precision:** {result['optimal_metrics']['precision']:.3f}")
                lines.append(f"**Recall:** {result['optimal_metrics']['recall']:.3f}")

            return "\n".join(lines)

        return str(result)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Model comparison mode
    parser.add_argument(
        "--model_a",
        help="CSV file with predictions from model A"
    )

    parser.add_argument(
        "--model_b",
        help="CSV file with predictions from model B"
    )

    parser.add_argument(
        "--labels",
        help="CSV file with true labels"
    )

    parser.add_argument(
        "--paired_test",
        action="store_true",
        help="Perform paired statistical test"
    )

    parser.add_argument(
        "--test_type",
        choices=["mcnemar", "paired_t", "wilcoxon"],
        default="mcnemar",
        help="Type of statistical test (default: mcnemar)"
    )

    parser.add_argument(
        "--correction",
        choices=["none", "bonferroni", "holm"],
        default="none",
        help="Multiple comparison correction (default: none)"
    )

    # Cost-benefit analysis mode
    parser.add_argument(
        "--predictions",
        help="CSV file with predictions for cost analysis"
    )

    parser.add_argument(
        "--probabilities",
        help="CSV file with prediction probabilities for cost analysis"
    )

    parser.add_argument(
        "--cost_fp",
        type=float,
        help="Cost of false positive"
    )

    parser.add_argument(
        "--cost_fn",
        type=float,
        help="Cost of false negative"
    )

    parser.add_argument(
        "--threshold_scan",
        help="Threshold scan parameters: min,max,n_points (e.g., 0.1,0.9,100)"
    )

    # General parameters
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level (default: 0.05)"
    )

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
    """Main entry point."""
    try:
        args = parse_arguments()

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        analyzer = MetricsAnalyzer(alpha=args.alpha)

        # Model comparison mode
        if args.paired_test:
            if not args.model_a or not args.model_b or not args.labels:
                logger.error("--model_a, --model_b, and --labels required for paired test")
                return 1

            logger.info("Loading model predictions and labels...")
            y_pred_a = pd.read_csv(args.model_a).values.ravel()
            y_pred_b = pd.read_csv(args.model_b).values.ravel()
            y_true = pd.read_csv(args.labels).values.ravel()

            result = analyzer.compare_models(
                y_true, y_pred_a, y_pred_b,
                test_type=args.test_type,
                correction=args.correction
            )

        # Cost-benefit analysis mode
        elif args.cost_fp is not None and args.cost_fn is not None:
            if not args.probabilities or not args.labels or not args.threshold_scan:
                logger.error("--probabilities, --labels, and --threshold_scan required for cost analysis")
                return 1

            logger.info("Loading data for cost-benefit analysis...")
            y_prob = pd.read_csv(args.probabilities).values.ravel()
            y_true = pd.read_csv(args.labels).values.ravel()

            # Parse threshold scan
            try:
                min_t, max_t, n_points = map(float, args.threshold_scan.split(','))
                thresholds = np.linspace(min_t, max_t, int(n_points))
            except Exception as e:
                logger.error(f"Invalid threshold_scan format: {e}")
                return 1

            result = analyzer.cost_benefit_analysis(
                y_true, y_prob, args.cost_fp, args.cost_fn, thresholds
            )
            result["status"] = "success"

        else:
            logger.error("Must specify either --paired_test or cost analysis parameters")
            return 1

        # Format and output
        output = analyzer.format_output(result, args.format)

        if args.output:
            Path(args.output).write_text(output)
            logger.info(f"Output written to: {args.output}")
        else:
            print(output)

        return 0 if result.get("status") == "success" else 1

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
