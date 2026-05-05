"""
SHAP-based explainability — global and regional analysis.

Generates:
  - Global SHAP beeswarm plot
  - Per-region SHAP summary plots
  - SHAP dependence plots for top features
  - Per-prediction SHAP values export (for iOS app)
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
from catboost import CatBoostRegressor, Pool
from pathlib import Path

from models import FEATURES_B, CATEGORICALS, TARGET, get_available_features

PROC_DIR = Path(__file__).parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent.parent / "models"
FIG_DIR = Path(__file__).parent.parent / "figures"
RESULTS_DIR = Path(__file__).parent.parent / "results"
FIG_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_model_and_data():
    """Load Model B and processed data."""
    model = CatBoostRegressor()
    model.load_model(str(MODEL_DIR / "model_b_regional.cbm"))

    with open(MODEL_DIR / "model_b_regional_results.json") as f:
        results = json.load(f)

    df = pd.read_csv(PROC_DIR / "model_ready.csv")
    features = results["features"]
    cats = results["categoricals"]

    X = df[features].copy()
    for col in cats:
        X[col] = X[col].astype(str)

    return model, df, X, features, cats


def compute_shap_values(model, X, features):
    """Compute SHAP values using TreeExplainer."""
    print("Computing SHAP values (TreeExplainer)...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    print(f"  SHAP values shape: {shap_values.shape}")
    return explainer, shap_values


def plot_global_beeswarm(shap_values, X, features, out_dir):
    """Global SHAP beeswarm (summary) plot."""
    print("\nGenerating global beeswarm plot...")
    fig, ax = plt.subplots(figsize=(10, 8))
    shap.summary_plot(shap_values, X, feature_names=features, show=False, max_display=15)
    plt.title("SHAP Feature Impact — Model B (Regional-Aware)", fontsize=13)
    plt.tight_layout()
    path = out_dir / "shap_beeswarm_global.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  Saved: {path}")


def plot_global_bar(shap_values, X, features, out_dir):
    """Global SHAP bar plot (mean |SHAP|)."""
    print("Generating global bar plot...")
    fig, ax = plt.subplots(figsize=(10, 7))
    shap.summary_plot(shap_values, X, feature_names=features, plot_type="bar",
                      show=False, max_display=15)
    plt.title("Mean |SHAP| Feature Importance — Model B", fontsize=13)
    plt.tight_layout()
    path = out_dir / "shap_bar_global.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  Saved: {path}")


def plot_regional_summaries(shap_values, X, df, features, out_dir):
    """Per-region SHAP summary plots."""
    print("\nGenerating per-region SHAP plots...")
    regions = sorted(df["region"].unique())
    fig, axes = plt.subplots(1, len(regions), figsize=(5 * len(regions), 8))

    for i, region in enumerate(regions):
        mask = df["region"].values == region
        plt.sca(axes[i])
        shap.summary_plot(shap_values[mask], X[mask], feature_names=features,
                          show=False, max_display=10, plot_size=None)
        axes[i].set_title(f"{region} (n={mask.sum()})", fontsize=11)

    plt.suptitle("SHAP Feature Impact by Region", fontsize=14, y=1.02)
    plt.tight_layout()
    path = out_dir / "shap_regional_summary.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  Saved: {path}")


def plot_dependence(shap_values, X, features, out_dir, top_n=4):
    """SHAP dependence plots for top features."""
    print(f"\nGenerating dependence plots for top {top_n} features...")
    mean_abs = np.abs(shap_values).mean(axis=0)
    top_idx = np.argsort(mean_abs)[-top_n:][::-1]

    fig, axes = plt.subplots(1, top_n, figsize=(5 * top_n, 4))
    for i, idx in enumerate(top_idx):
        plt.sca(axes[i])
        shap.dependence_plot(idx, shap_values, X, feature_names=features,
                             show=False, ax=axes[i])
    plt.suptitle("SHAP Dependence Plots — Top Features", fontsize=13, y=1.02)
    plt.tight_layout()
    path = out_dir / "shap_dependence_top4.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  Saved: {path}")


def export_shap_summary(shap_values, features, df, out_dir):
    """Export mean |SHAP| per feature overall and per region for iOS app."""
    print("\nExporting SHAP summary for app integration...")

    # Global mean |SHAP|
    mean_abs = np.abs(shap_values).mean(axis=0)
    global_imp = {features[i]: float(mean_abs[i]) for i in range(len(features))}
    global_imp = dict(sorted(global_imp.items(), key=lambda x: -x[1]))

    # Per-region mean |SHAP|
    regional_imp = {}
    for region in sorted(df["region"].unique()):
        mask = df["region"].values == region
        region_mean = np.abs(shap_values[mask]).mean(axis=0)
        regional_imp[region] = {features[i]: float(region_mean[i]) for i in range(len(features))}
        regional_imp[region] = dict(sorted(regional_imp[region].items(), key=lambda x: -x[1]))

    export = {
        "global": global_imp,
        "regional": regional_imp,
        "description": "Mean absolute SHAP values. Higher = more impact on prediction."
    }

    path = out_dir / "shap_importance_export.json"
    with open(path, "w") as f:
        json.dump(export, f, indent=2)
    print(f"  Saved: {path}")

    # Print summary
    print("\n  Global Top-10 (mean |SHAP|):")
    for feat, val in list(global_imp.items())[:10]:
        print(f"    {feat:30s}: {val:.2f}")

    return export


def compare_with_catboost_builtin(model, features, shap_global):
    """Compare SHAP importance with CatBoost PredictionValuesChange."""
    print("\nComparison: SHAP vs CatBoost PredictionValuesChange")
    cb_imp = model.get_feature_importance()
    cb_dict = {features[i]: float(cb_imp[i]) for i in range(len(features))}
    cb_dict = dict(sorted(cb_dict.items(), key=lambda x: -x[1]))

    # Rank correlation
    from scipy.stats import spearmanr
    shap_ranks = {k: i for i, k in enumerate(shap_global.keys())}
    cb_ranks = {k: i for i, k in enumerate(cb_dict.keys())}
    common = set(shap_ranks.keys()) & set(cb_ranks.keys())
    r1 = [shap_ranks[k] for k in common]
    r2 = [cb_ranks[k] for k in common]
    rho, p = spearmanr(r1, r2)
    print(f"  Spearman rank correlation: rho={rho:.3f}, p={p:.4f}")
    print(f"  (High correlation validates both methods agree on feature ordering)")


def run_shap_analysis():
    """Run full SHAP analysis pipeline."""
    print("=" * 60)
    print("SHAP EXPLAINABILITY ANALYSIS")
    print("=" * 60)

    model, df, X, features, cats = load_model_and_data()
    explainer, shap_values = compute_shap_values(model, X, features)

    plot_global_beeswarm(shap_values, X, features, FIG_DIR)
    plot_global_bar(shap_values, X, features, FIG_DIR)
    plot_regional_summaries(shap_values, X, df, features, FIG_DIR)
    plot_dependence(shap_values, X, features, FIG_DIR)
    export = export_shap_summary(shap_values, features, df, RESULTS_DIR)
    compare_with_catboost_builtin(model, features, export["global"])

    print("\n" + "=" * 60)
    print("SHAP analysis complete!")
    print(f"  Figures: {FIG_DIR}")
    print(f"  Export:  {RESULTS_DIR / 'shap_importance_export.json'}")
    print("=" * 60)


if __name__ == "__main__":
    run_shap_analysis()
