#!/usr/bin/env python3
"""
Tool Name: Calibration Plotter
Purpose: Generate calibration diagnostics, reliability plots, and threshold analysis
Usage: python calibration_plotter.py --predictions preds.csv --labels labels.csv --probabilities probs.csv

This tool is part of the ml-evaluator agent's toolkit.
It generates calibration curves, computes ECE/MCE, creates ROC/PR curves, and performs threshold analysis.

Examples:
    # Basic calibration analysis
    python calibration_plotter.py --predictions preds.csv --labels labels.csv --probabilities probs.csv --num_bins 10

    # With calibration correction
    python calibration_plotter.py --predictions preds.csv --labels labels.csv --probabilities probs.csv --calibrate temperature_scaling

    # Generate plots
    python calibration_plotter.py --predictions preds.csv --labels labels.csv --probabilities probs.csv --output calibration_report.pdf
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

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalibrationAnalyzer:
    """
    Model calibration analyzer and plotter.

    Provides:
    - Calibration curves and reliability diagrams
    - ECE (Expected Calibration Error) and MCE (Maximum Calibration Error)
    - Brier score computation
    - Temperature scaling for calibration correction
    - ROC and PR curve analysis
    - Optimal threshold selection
    """

    def __init__(self, num_bins=10):
        """
        Initialize the calibration analyzer.

        Args:
            num_bins: Number of bins for calibration curve (default: 10)
        """
        self.num_bins = num_bins
        logger.debug(f"Initialized CalibrationAnalyzer with num_bins={num_bins}")

    def compute_calibration_curve(self, y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
        """
        Compute calibration curve with binning.

        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities

        Returns:
            dict: Calibration curve data
        """
        # Create bins
        bin_edges = np.linspace(0, 1, self.num_bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        calibration_data = []

        for i in range(self.num_bins):
            # Find samples in this bin
            mask = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i + 1])

            # Handle last bin edge
            if i == self.num_bins - 1:
                mask = (y_prob >= bin_edges[i]) & (y_prob <= bin_edges[i + 1])

            if np.sum(mask) > 0:
                bin_prob = np.mean(y_prob[mask])
                bin_true_freq = np.mean(y_true[mask])
                bin_count = np.sum(mask)

                calibration_data.append({
                    "bin_center": float(bin_centers[i]),
                    "predicted_prob": float(bin_prob),
                    "true_freq": float(bin_true_freq),
                    "count": int(bin_count),
                    "error": float(abs(bin_prob - bin_true_freq))
                })

        return {
            "num_bins": self.num_bins,
            "bins": calibration_data
        }

    def compute_ece_mce(self, y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
        """
        Compute Expected Calibration Error and Maximum Calibration Error.

        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities

        Returns:
            dict: ECE and MCE values
        """
        calibration = self.compute_calibration_curve(y_true, y_prob)
        bins = calibration["bins"]

        if len(bins) == 0:
            return {"ece": np.nan, "mce": np.nan}

        total_samples = len(y_true)
        ece = 0.0
        mce = 0.0

        for bin_data in bins:
            bin_error = bin_data["error"]
            bin_weight = bin_data["count"] / total_samples

            ece += bin_weight * bin_error
            mce = max(mce, bin_error)

        return {
            "ece": float(ece),
            "mce": float(mce)
        }

    def compute_brier_score(self, y_true: np.ndarray, y_prob: np.ndarray) -> float:
        """
        Compute Brier score (mean squared error of probabilities).

        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities

        Returns:
            float: Brier score
        """
        return float(np.mean((y_prob - y_true) ** 2))

    def temperature_scaling(self, y_true: np.ndarray, y_logits: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Perform temperature scaling calibration.

        Args:
            y_true: True binary labels
            y_logits: Model logits (before sigmoid)

        Returns:
            tuple: (optimal_temperature, calibrated_probabilities)
        """
        from scipy.optimize import minimize_scalar

        def nll(temperature):
            """Negative log-likelihood for temperature scaling."""
            scaled_probs = 1 / (1 + np.exp(-y_logits / temperature))
            scaled_probs = np.clip(scaled_probs, 1e-7, 1 - 1e-7)
            return -np.mean(y_true * np.log(scaled_probs) + (1 - y_true) * np.log(1 - scaled_probs))

        # Find optimal temperature
        result = minimize_scalar(nll, bounds=(0.1, 10.0), method='bounded')
        optimal_temp = result.x

        # Apply temperature scaling
        calibrated_probs = 1 / (1 + np.exp(-y_logits / optimal_temp))

        return float(optimal_temp), calibrated_probs

    def compute_roc_curve(self, y_true: np.ndarray, y_prob: np.ndarray, n_points: int = 100) -> Dict[str, Any]:
        """
        Compute ROC curve.

        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities
            n_points: Number of points on curve

        Returns:
            dict: ROC curve data
        """
        from sklearn.metrics import roc_curve, auc

        fpr, tpr, thresholds = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)

        # Subsample to n_points for cleaner output
        if len(fpr) > n_points:
            indices = np.linspace(0, len(fpr) - 1, n_points, dtype=int)
            fpr = fpr[indices]
            tpr = tpr[indices]
            thresholds = thresholds[indices]

        return {
            "auc": float(roc_auc),
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist()
        }

    def compute_pr_curve(self, y_true: np.ndarray, y_prob: np.ndarray, n_points: int = 100) -> Dict[str, Any]:
        """
        Compute Precision-Recall curve.

        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities
            n_points: Number of points on curve

        Returns:
            dict: PR curve data
        """
        from sklearn.metrics import precision_recall_curve, average_precision_score

        precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)

        # Subsample
        if len(precision) > n_points:
            indices = np.linspace(0, len(precision) - 1, n_points, dtype=int)
            precision = precision[indices]
            recall = recall[indices]
            # thresholds has one fewer element
            if len(thresholds) > n_points:
                indices_t = np.linspace(0, len(thresholds) - 1, n_points, dtype=int)
                thresholds = thresholds[indices_t]

        return {
            "auc": float(pr_auc),
            "precision": precision.tolist(),
            "recall": recall.tolist(),
            "thresholds": thresholds.tolist()
        }

    def analyze_calibration(self, y_true: np.ndarray, y_prob: np.ndarray,
                          compute_curves: bool = False) -> Dict[str, Any]:
        """
        Comprehensive calibration analysis.

        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities
            compute_curves: Whether to compute ROC/PR curves

        Returns:
            dict: Complete calibration analysis
        """
        try:
            results = {
                "status": "success",
                "n_samples": len(y_true),
                "positive_rate": float(np.mean(y_true))
            }

            # Calibration metrics
            logger.info("Computing calibration metrics...")
            ece_mce = self.compute_ece_mce(y_true, y_prob)
            results["ece"] = ece_mce["ece"]
            results["mce"] = ece_mce["mce"]
            results["brier_score"] = self.compute_brier_score(y_true, y_prob)

            # Calibration curve
            logger.info("Computing calibration curve...")
            results["calibration_curve"] = self.compute_calibration_curve(y_true, y_prob)

            # Interpretation
            if ece_mce["ece"] < 0.05:
                calibration_quality = "well-calibrated"
            elif ece_mce["ece"] < 0.10:
                calibration_quality = "moderately calibrated"
            else:
                calibration_quality = "poorly calibrated"

            results["calibration_quality"] = calibration_quality

            # Optional: ROC and PR curves
            if compute_curves:
                logger.info("Computing ROC curve...")
                results["roc_curve"] = self.compute_roc_curve(y_true, y_prob)

                logger.info("Computing PR curve...")
                results["pr_curve"] = self.compute_pr_curve(y_true, y_prob)

            return results

        except Exception as e:
            logger.error(f"Calibration analysis failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    def format_output(self, result: Dict[str, Any], output_format: str = "json") -> str:
        """Format the output for display."""
        if output_format == "json":
            return json.dumps(result, indent=2)

        elif output_format == "text":
            if result.get("status") == "error":
                return f"ERROR: {result['error']}"

            lines = ["Calibration Analysis Results\n"]
            lines.append(f"Samples: {result.get('n_samples', 'N/A')}")
            lines.append(f"Positive Rate: {result.get('positive_rate', 0):.3f}")
            lines.append(f"\nCalibration Metrics:")
            lines.append(f"  ECE: {result.get('ece', 'N/A'):.4f}")
            lines.append(f"  MCE: {result.get('mce', 'N/A'):.4f}")
            lines.append(f"  Brier Score: {result.get('brier_score', 'N/A'):.4f}")
            lines.append(f"  Quality: {result.get('calibration_quality', 'N/A')}")

            if "roc_curve" in result:
                lines.append(f"\nROC AUC: {result['roc_curve']['auc']:.4f}")
            if "pr_curve" in result:
                lines.append(f"PR AUC: {result['pr_curve']['auc']:.4f}")

            return "\n".join(lines)

        elif output_format == "markdown":
            if result.get("status") == "error":
                return f"## Error\n\n{result['error']}"

            lines = [
                "## Calibration Analysis Results\n",
                f"**Samples:** {result.get('n_samples', 'N/A')}",
                f"**Positive Rate:** {result.get('positive_rate', 0):.3f}\n",
                "### Calibration Metrics\n",
                f"- **ECE:** {result.get('ece', 'N/A'):.4f}",
                f"- **MCE:** {result.get('mce', 'N/A'):.4f}",
                f"- **Brier Score:** {result.get('brier_score', 'N/A'):.4f}",
                f"- **Quality:** {result.get('calibration_quality', 'N/A')}"
            ]

            if "roc_curve" in result:
                lines.append(f"\n### ROC Analysis\n")
                lines.append(f"**AUC:** {result['roc_curve']['auc']:.4f}")

            if "pr_curve" in result:
                lines.append(f"\n### Precision-Recall Analysis\n")
                lines.append(f"**AUC:** {result['pr_curve']['auc']:.4f}")

            return "\n".join(lines)

        return str(result)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--labels",
        required=True,
        help="CSV file with true labels"
    )

    parser.add_argument(
        "--probabilities",
        required=True,
        help="CSV file with prediction probabilities"
    )

    parser.add_argument(
        "--num_bins",
        type=int,
        default=10,
        help="Number of bins for calibration curve (default: 10)"
    )

    parser.add_argument(
        "--compute_curves",
        action="store_true",
        help="Compute ROC and PR curves"
    )

    parser.add_argument(
        "--calibrate",
        choices=["none", "temperature_scaling"],
        default="none",
        help="Apply calibration method (default: none)"
    )

    parser.add_argument(
        "--logits",
        help="CSV file with model logits (required for temperature scaling)"
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

        # Load data
        logger.info("Loading labels and probabilities...")
        y_true = pd.read_csv(args.labels).values.ravel()
        y_prob = pd.read_csv(args.probabilities).values.ravel()

        # Initialize analyzer
        analyzer = CalibrationAnalyzer(num_bins=args.num_bins)

        # Apply calibration if requested
        if args.calibrate == "temperature_scaling":
            if not args.logits:
                logger.error("--logits required for temperature scaling")
                return 1

            logger.info("Applying temperature scaling...")
            y_logits = pd.read_csv(args.logits).values.ravel()
            optimal_temp, y_prob = analyzer.temperature_scaling(y_true, y_logits)
            logger.info(f"Optimal temperature: {optimal_temp:.3f}")

        # Run analysis
        result = analyzer.analyze_calibration(
            y_true, y_prob, compute_curves=args.compute_curves
        )

        # Format output
        output = analyzer.format_output(result, args.format)

        # Write output
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
