"""
Ablation study — measure the contribution of each feature group.

Two analyses:
  1. Incremental addition: Base → +CCI → +Macro → +Derived (full Model B)
  2. Leave-one-group-out (LOGO): remove each group from the full set
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_percentage_error

from models import CATEGORICALS, TARGET, FEATURE_GROUPS, get_available_features, create_model

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "model_ready.csv"
RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR = Path(__file__).parent.parent / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def cv_metrics(model_name, df_train, features, cat_features, n_splits=5):
    """Run CV and return fold-level R², RMSE, MAPE."""
    avail = get_available_features(df_train, features)
    avail_cats = [c for c in cat_features if c in avail]
    X = df_train[avail]
    y = df_train[TARGET].values
    regions = df_train["region"].values

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_r2, fold_rmse, fold_mape = [], [], []

    for train_idx, val_idx in skf.split(X, regions):
        model = create_model(model_name, avail, avail_cats)
        model.fit(X.iloc[train_idx], y[train_idx], X.iloc[val_idx], y[val_idx])
        preds = model.predict(X.iloc[val_idx])
        fold_r2.append(r2_score(y[val_idx], preds))
        fold_rmse.append(np.sqrt(mean_squared_error(y[val_idx], preds)))
        fold_mape.append(mean_absolute_percentage_error(y[val_idx], preds) * 100)

    return {
        "r2": fold_r2, "rmse": fold_rmse, "mape": fold_mape,
        "r2_mean": float(np.mean(fold_r2)),
        "rmse_mean": float(np.mean(fold_rmse)),
        "mape_mean": float(np.mean(fold_mape)),
        "n_features": len(avail),
    }


def run_incremental(model_name, df_train):
    """Incrementally add feature groups: Base → +CCI → +Macro → +Derived."""
    print("\n--- Incremental Addition ---")

    stages = [
        ("Base", list(FEATURE_GROUPS["base"])),
        ("+CCI", list(FEATURE_GROUPS["base"]) + list(FEATURE_GROUPS["cci"])),
        ("+Macro", list(FEATURE_GROUPS["base"]) + list(FEATURE_GROUPS["cci"]) + list(FEATURE_GROUPS["macro"])),
        ("+Derived (Full B)", list(FEATURE_GROUPS["base"]) + list(FEATURE_GROUPS["cci"])
         + list(FEATURE_GROUPS["macro"]) + list(FEATURE_GROUPS["derived"])),
    ]

    results = {}
    for label, features in stages:
        metrics = cv_metrics(model_name, df_train, features, CATEGORICALS)
        results[label] = metrics
        print(f"  {label:20s}: R²={metrics['r2_mean']:.4f}, RMSE={metrics['rmse_mean']:.2f}, "
              f"MAPE={metrics['mape_mean']:.2f}% ({metrics['n_features']} features)")

    return results


def run_logo(model_name, df_train):
    """Leave-one-group-out: remove each group from the full set."""
    print("\n--- Leave-One-Group-Out ---")

    all_features = (list(FEATURE_GROUPS["base"]) + list(FEATURE_GROUPS["cci"])
                    + list(FEATURE_GROUPS["macro"]) + list(FEATURE_GROUPS["derived"]))

    # Full model baseline
    full_metrics = cv_metrics(model_name, df_train, all_features, CATEGORICALS)
    print(f"  {'Full Model':<20s}: R²={full_metrics['r2_mean']:.4f}")

    results = {"Full Model": full_metrics}

    for group_name, group_features in FEATURE_GROUPS.items():
        if group_name == "base":
            continue  # don't remove base — model can't function without it
        reduced = [f for f in all_features if f not in group_features]
        metrics = cv_metrics(model_name, df_train, reduced, CATEGORICALS)
        delta = metrics["r2_mean"] - full_metrics["r2_mean"]
        results[f"-{group_name}"] = metrics
        print(f"  -{group_name:19s}: R²={metrics['r2_mean']:.4f} (delta={delta:+.4f})")

    return results


def plot_ablation(incremental, logo, out_dir):
    """Generate ablation plots."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Incremental plot
    ax = axes[0]
    labels = list(incremental.keys())
    r2_vals = [incremental[l]["r2_mean"] for l in labels]
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#E91E63"]
    bars = ax.bar(labels, r2_vals, color=colors, edgecolor="black", linewidth=0.5)
    for bar, val in zip(bars, r2_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                f"{val:.4f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_ylabel("Mean CV R²")
    ax.set_title("Incremental Feature Group Addition")
    ax.set_ylim(min(r2_vals) - 0.03, max(r2_vals) + 0.02)
    ax.grid(axis="y", alpha=0.3)

    # LOGO plot
    ax = axes[1]
    logo_labels = [k for k in logo if k != "Full Model"]
    full_r2 = logo["Full Model"]["r2_mean"]
    deltas = [logo[l]["r2_mean"] - full_r2 for l in logo_labels]
    colors_logo = ["#E91E63" if d < 0 else "#4CAF50" for d in deltas]
    bars = ax.barh(logo_labels, deltas, color=colors_logo, edgecolor="black", linewidth=0.5)
    for bar, val in zip(bars, deltas):
        x_pos = val - 0.001 if val < 0 else val + 0.001
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                f"{val:+.4f}", ha="right" if val < 0 else "left", va="center", fontsize=9)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Change in R² vs Full Model")
    ax.set_title("Leave-One-Group-Out Impact")
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    path = out_dir / "ablation_study.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nPlot saved: {path}")


def run_ablation(model_name="CatBoost"):
    """Run full ablation study."""
    print("=" * 60)
    print(f"ABLATION STUDY (model: {model_name})")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH)
    df_train = df[~df["year"].isin([2024, 2025])].reset_index(drop=True)
    print(f"Training data: {len(df_train)} rows")

    incremental = run_incremental(model_name, df_train)
    logo = run_logo(model_name, df_train)

    plot_ablation(incremental, logo, FIGURES_DIR)

    # Save results
    all_results = {
        "model": model_name,
        "incremental": {k: {"r2_mean": v["r2_mean"], "rmse_mean": v["rmse_mean"],
                            "mape_mean": v["mape_mean"], "n_features": v["n_features"],
                            "r2_folds": v["r2"]}
                        for k, v in incremental.items()},
        "logo": {k: {"r2_mean": v["r2_mean"], "rmse_mean": v["rmse_mean"],
                      "mape_mean": v["mape_mean"], "n_features": v["n_features"],
                      "r2_folds": v["r2"]}
                 for k, v in logo.items()},
    }
    out_path = RESULTS_DIR / "ablation_results.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Results saved: {out_path}")

    return all_results


if __name__ == "__main__":
    run_ablation()
