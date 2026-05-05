"""
Experiment orchestrator — multi-model comparison with proper evaluation.

Implements:
  - Temporal holdout: 2015-2023 train, 2024-2025 test
  - Region-stratified 5-fold CV on training portion
  - Multi-model comparison (CatBoost, XGBoost, LightGBM, RF, MLP)
  - Per-region and overall metrics
  - Saves all results for downstream analysis (ablation, significance, etc.)
"""

import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_percentage_error

from models import (
    FEATURES_A, FEATURES_B, CATEGORICALS, TARGET, FEATURE_GROUPS,
    get_available_features, create_model,
)

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "model_ready.csv"
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ALL_MODELS = ["CatBoost", "XGBoost", "LightGBM", "RandomForest", "MLP"]


def load_data():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def temporal_split(df, test_years=(2024, 2025)):
    """Split into train (2015-2023) and test (2024-2025)."""
    mask_test = df["year"].isin(test_years)
    df_train = df[~mask_test].reset_index(drop=True)
    df_test = df[mask_test].reset_index(drop=True)
    print(f"Temporal split: train={len(df_train)} ({df_train['year'].min()}-{df_train['year'].max()}), "
          f"test={len(df_test)} ({df_test['year'].min()}-{df_test['year'].max()})")
    return df_train, df_test


def compute_metrics(y_true, y_pred):
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mape": float(mean_absolute_percentage_error(y_true, y_pred) * 100),
    }


def compute_region_metrics(y_true, y_pred, regions):
    """Compute per-region metrics."""
    result = {}
    for region in sorted(set(regions)):
        mask = regions == region
        if mask.sum() > 1:
            result[region] = compute_metrics(y_true[mask], y_pred[mask])
    return result


def run_cv(model_name, df_train, features, cat_features, n_splits=5, params=None):
    """Run region-stratified k-fold CV. Returns fold-level metrics and predictions."""
    avail_features = get_available_features(df_train, features)
    avail_cats = [c for c in cat_features if c in avail_features]

    X = df_train[avail_features]
    y = df_train[TARGET].values
    regions = df_train["region"].values

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    fold_metrics = []
    fold_region_metrics = []
    oof_preds = np.full(len(y), np.nan)

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, regions)):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        model = create_model(model_name, avail_features, avail_cats, params)
        model.fit(X_tr, y_tr, X_val, y_val)

        y_pred = model.predict(X_val)
        oof_preds[val_idx] = y_pred

        metrics = compute_metrics(y_val, y_pred)
        metrics["fold"] = fold + 1
        fold_metrics.append(metrics)

        region_m = compute_region_metrics(y_val, y_pred, regions[val_idx])
        fold_region_metrics.append(region_m)

    return fold_metrics, fold_region_metrics, oof_preds


def run_test_eval(model_name, df_train, df_test, features, cat_features, params=None):
    """Train on full training set, evaluate on held-out test set."""
    avail_features = get_available_features(df_train, features)
    avail_cats = [c for c in cat_features if c in avail_features]

    model = create_model(model_name, avail_features, avail_cats, params)
    model.fit(df_train[avail_features], df_train[TARGET].values)

    y_pred = model.predict(df_test[avail_features])
    y_true = df_test[TARGET].values
    regions = df_test["region"].values

    overall = compute_metrics(y_true, y_pred)
    per_region = compute_region_metrics(y_true, y_pred, regions)

    return overall, per_region, model


def run_experiment(model_names=None, feature_set="B", params_dict=None):
    """
    Run full experiment: CV + holdout test for each model.

    Args:
        model_names: list of model names (default: all 5)
        feature_set: "A" or "B" (default "B")
        params_dict: {model_name: {param: value}} for custom hyperparams
    """
    if model_names is None:
        model_names = ALL_MODELS
    if params_dict is None:
        params_dict = {}

    features = FEATURES_B if feature_set == "B" else FEATURES_A
    cat_features = CATEGORICALS

    print("=" * 65)
    print("MULTI-MODEL EXPERIMENT")
    print(f"Feature set: {feature_set} ({len(features)} features)")
    print(f"Models: {model_names}")
    print("=" * 65)

    df = load_data()
    df_train, df_test = temporal_split(df)

    all_results = {}

    for model_name in model_names:
        print(f"\n{'─'*50}")
        print(f"  {model_name}")
        print(f"{'─'*50}")

        params = params_dict.get(model_name)
        t0 = time.time()

        # Cross-validation
        fold_metrics, fold_region_metrics, oof_preds = run_cv(
            model_name, df_train, features, cat_features, params=params
        )
        cv_time = time.time() - t0

        # Holdout test
        t1 = time.time()
        test_metrics, test_region, trained_model = run_test_eval(
            model_name, df_train, df_test, features, cat_features, params=params
        )
        test_time = time.time() - t1

        # Aggregate CV metrics
        cv_avg = {
            "r2": float(np.mean([m["r2"] for m in fold_metrics])),
            "rmse": float(np.mean([m["rmse"] for m in fold_metrics])),
            "mape": float(np.mean([m["mape"] for m in fold_metrics])),
            "r2_std": float(np.std([m["r2"] for m in fold_metrics])),
        }

        # Aggregate per-region CV metrics
        regions = sorted(fold_region_metrics[0].keys())
        cv_region_avg = {}
        for region in regions:
            cv_region_avg[region] = {
                "r2": float(np.mean([f[region]["r2"] for f in fold_region_metrics if region in f])),
                "rmse": float(np.mean([f[region]["rmse"] for f in fold_region_metrics if region in f])),
                "mape": float(np.mean([f[region]["mape"] for f in fold_region_metrics if region in f])),
            }

        result = {
            "model": model_name,
            "feature_set": feature_set,
            "n_features": len(get_available_features(df_train, features)),
            "cv_avg": cv_avg,
            "cv_folds": fold_metrics,
            "cv_region_avg": cv_region_avg,
            "cv_region_folds": [{r: m[r] for r in m} for m in fold_region_metrics],
            "test_metrics": test_metrics,
            "test_region_metrics": test_region,
            "cv_time_s": round(cv_time, 1),
            "test_time_s": round(test_time, 1),
        }
        all_results[model_name] = result

        # Print summary
        print(f"  CV:   R²={cv_avg['r2']:.4f} (+/-{cv_avg['r2_std']:.4f}), "
              f"RMSE={cv_avg['rmse']:.2f}, MAPE={cv_avg['mape']:.2f}%  [{cv_time:.1f}s]")
        print(f"  Test: R²={test_metrics['r2']:.4f}, "
              f"RMSE={test_metrics['rmse']:.2f}, MAPE={test_metrics['mape']:.2f}%  [{test_time:.1f}s]")

    # ── Comparison table ──────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("RESULTS SUMMARY")
    print("=" * 65)

    header = f"  {'Model':<14} {'CV R²':>8} {'CV RMSE':>9} {'CV MAPE':>9} {'Test R²':>8} {'Test RMSE':>10} {'Test MAPE':>10}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for name in model_names:
        r = all_results[name]
        cv = r["cv_avg"]
        te = r["test_metrics"]
        print(f"  {name:<14} {cv['r2']:>8.4f} {cv['rmse']:>9.2f} {cv['mape']:>8.2f}% "
              f"{te['r2']:>8.4f} {te['rmse']:>10.2f} {te['mape']:>9.2f}%")

    # Per-region test comparison
    print(f"\n  Per-Region Test R²:")
    regions = sorted(all_results[model_names[0]]["test_region_metrics"].keys())
    print(f"  {'Region':<14}" + "".join(f" {n:>12}" for n in model_names))
    for region in regions:
        vals = []
        for name in model_names:
            rm = all_results[name]["test_region_metrics"]
            vals.append(f"{rm[region]['r2']:>12.4f}" if region in rm else f"{'N/A':>12}")
        print(f"  {region:<14}" + "".join(vals))

    # Save results
    out_path = RESULTS_DIR / f"experiment_featureset_{feature_set}.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved: {out_path}")

    return all_results


if __name__ == "__main__":
    results = run_experiment()
