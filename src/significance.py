"""
Statistical significance testing for model comparisons.

Implements:
  - Wilcoxon signed-rank test on fold-level metrics
  - Corrected resampled t-test (Nadeau & Bengio, 2003)
  - Cohen's d effect size
  - Bootstrap 95% confidence intervals
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from itertools import combinations

RESULTS_DIR = Path(__file__).parent.parent / "results"


def cohens_d(a, b):
    """Cohen's d for paired samples."""
    diff = np.array(a) - np.array(b)
    return np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0.0


def corrected_t_test(a, b, n_train, n_test):
    """
    Corrected resampled t-test (Nadeau & Bengio, 2003).
    Accounts for non-independence of CV folds by adjusting variance.
    """
    diff = np.array(a) - np.array(b)
    k = len(diff)
    mean_diff = np.mean(diff)
    var_diff = np.var(diff, ddof=1)
    # Correction factor: accounts for overlap between train/test folds
    corrected_var = (1/k + n_test/n_train) * var_diff
    if corrected_var <= 0:
        return 0.0, 1.0
    t_stat = mean_diff / np.sqrt(corrected_var)
    p_val = 2 * stats.t.sf(abs(t_stat), df=k-1)
    return float(t_stat), float(p_val)


def bootstrap_ci(a, b, n_boot=10000, alpha=0.05):
    """Bootstrap 95% CI for the difference in means."""
    diff = np.array(a) - np.array(b)
    rng = np.random.RandomState(42)
    boot_means = [np.mean(rng.choice(diff, size=len(diff), replace=True)) for _ in range(n_boot)]
    lower = np.percentile(boot_means, 100 * alpha / 2)
    upper = np.percentile(boot_means, 100 * (1 - alpha / 2))
    return float(lower), float(upper)


def run_significance(experiment_path=None):
    """
    Load experiment results and run pairwise significance tests.

    Expects a JSON file with structure:
      {model_name: {cv_folds: [{fold, r2, rmse, mape}, ...], ...}}
    """
    if experiment_path is None:
        experiment_path = RESULTS_DIR / "experiment_featureset_B.json"

    print("=" * 60)
    print("STATISTICAL SIGNIFICANCE TESTING")
    print("=" * 60)

    with open(experiment_path) as f:
        results = json.load(f)

    model_names = list(results.keys())
    print(f"Models: {model_names}\n")

    # Extract fold-level R² for each model
    fold_r2 = {}
    for name, data in results.items():
        fold_r2[name] = [fold["r2"] for fold in data["cv_folds"]]

    n_folds = len(list(fold_r2.values())[0])

    # Estimate train/test sizes per fold (for corrected t-test)
    n_total = results[model_names[0]].get("n_features", 2479)  # fallback
    # Actual sample sizes from the data
    n_test_per_fold = n_total // n_folds
    n_train_per_fold = n_total - n_test_per_fold

    # ── Pairwise comparisons ──────────────────────────────────────────
    comparisons = []

    print(f"{'Comparison':<30s} {'Mean diff':>10s} {'Wilcoxon p':>12s} {'Corrected-t p':>14s} "
          f"{'Cohen d':>9s} {'95% CI':>20s} {'Sig?':>6s}")
    print("-" * 105)

    for a, b in combinations(model_names, 2):
        r2_a = fold_r2[a]
        r2_b = fold_r2[b]

        mean_diff = float(np.mean(r2_a) - np.mean(r2_b))

        # Wilcoxon signed-rank (non-parametric)
        try:
            w_stat, w_p = stats.wilcoxon(r2_a, r2_b)
            w_p = float(w_p)
        except ValueError:
            w_p = 1.0  # identical values

        # Corrected t-test
        t_stat, ct_p = corrected_t_test(r2_a, r2_b, n_train_per_fold, n_test_per_fold)

        # Effect size
        d = cohens_d(r2_a, r2_b)

        # Bootstrap CI
        ci_lo, ci_hi = bootstrap_ci(r2_a, r2_b)

        sig = "***" if w_p < 0.001 else "**" if w_p < 0.01 else "*" if w_p < 0.05 else "ns"

        comp = {
            "model_a": a, "model_b": b,
            "mean_diff_r2": mean_diff,
            "wilcoxon_p": w_p,
            "corrected_t_p": ct_p,
            "cohens_d": float(d),
            "ci_95_lower": ci_lo,
            "ci_95_upper": ci_hi,
            "significant_005": w_p < 0.05,
        }
        comparisons.append(comp)

        label = f"{a} vs {b}"
        print(f"  {label:<28s} {mean_diff:>+10.4f} {w_p:>12.4f} {ct_p:>14.4f} "
              f"{d:>+9.3f} [{ci_lo:>+.4f}, {ci_hi:>+.4f}] {sig:>6s}")

    # ── Summary ───────────────────────────────────────────────────────
    print(f"\n  Note: With n={n_folds} folds, statistical power is limited.")
    print(f"  Interpret effect sizes (Cohen's d) alongside p-values.")
    print(f"  |d| < 0.2 = negligible, 0.2-0.5 = small, 0.5-0.8 = medium, > 0.8 = large")

    # Save
    out = {"comparisons": comparisons, "n_folds": n_folds}
    out_path = RESULTS_DIR / "significance_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Results saved: {out_path}")

    return comparisons


if __name__ == "__main__":
    run_significance()
