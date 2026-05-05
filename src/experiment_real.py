"""
Real data experiment — train models on USASpending federal construction contracts.

Joins real contract data with real CCI (BLS wages) and FRED macro signals.
Target: award_amount (total project cost).
Compares the same models and runs the same ablation to validate findings
from the synthetic pipeline on fully real data.
"""

import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_percentage_error

from models import CATEGORICALS, TARGET, FEATURE_GROUPS, get_available_features, create_model

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROC_DIR = Path(__file__).parent.parent / "data" / "processed"
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

REAL_TARGET = "log_award_amount"

# Features available in the real data (no area_sqft, no formwork/concrete rates)
REAL_FEATURES_BASE = ["project_type", "region", "state", "year"]

REAL_FEATURES_CCI = ["mat_cci", "labor_cci", "equip_cci", "weighted_cci"]

REAL_FEATURES_MACRO = [
    "ppi_construction_materials", "ppi_cement", "ppi_steel_mill", "ppi_lumber",
    "real_gdp", "cpi_all_urban", "unemployment_rate",
    "mortgage_30yr", "building_permits", "housing_starts",
    "regional_cpi",
]

REAL_FEATURES_DERIVED = [
    "cci_labor_premium", "cci_deviation", "year_num",
]

REAL_FEATURES_ALL = REAL_FEATURES_BASE + REAL_FEATURES_CCI + REAL_FEATURES_MACRO + REAL_FEATURES_DERIVED

REAL_CATEGORICALS = ["project_type", "region", "state"]

ALL_MODELS = ["CatBoost", "XGBoost", "LightGBM", "RandomForest"]


def build_real_dataset():
    """Join USASpending contracts with real CCI and FRED macro data."""
    print("Building real dataset...")

    # Load USASpending contracts
    contracts = pd.read_csv(RAW_DIR / "usaspending_construction.csv")
    contracts = contracts[contracts["year"].between(2020, 2025)]
    contracts = contracts[contracts["award_amount"] > 0]
    contracts = contracts.dropna(subset=["state", "region", "year"])
    contracts["year"] = contracts["year"].astype(int)
    print(f"  Contracts: {len(contracts)} records")

    # Load real CCI (state-level averages by year)
    cci = pd.read_csv(RAW_DIR / "real_cci_table.csv")
    # Aggregate CCI to state-year level (multiple cities per state)
    cci_state = cci.groupby(["state", "year"])[
        ["mat_cci", "labor_cci", "equip_cci", "weighted_cci"]
    ].mean().reset_index()
    print(f"  CCI: {len(cci_state)} state-year combinations")

    # Load FRED macro data
    fred = pd.read_csv(RAW_DIR / "fred_macro.csv", parse_dates=["date"])
    fred["year"] = fred["date"].dt.year
    fred_annual = fred.groupby("year").mean(numeric_only=True).reset_index()
    fred_annual = fred_annual.drop(columns=["date"], errors="ignore")
    print(f"  FRED macro: {len(fred_annual)} years")

    # Load BLS regional CPI
    bls_path = RAW_DIR / "bls_regional_cpi.csv"
    if bls_path.exists():
        bls = pd.read_csv(bls_path, parse_dates=["date"])
        bls["year"] = bls["date"].dt.year
        bls_annual = bls.groupby("year").mean(numeric_only=True).reset_index()

        region_cpi_map = {
            "Northeast": "cpi_northeast",
            "Southeast": "cpi_south",
            "Midwest": "cpi_midwest",
            "Southwest": "cpi_south",
            "West": "cpi_west",
        }
    else:
        bls_annual = None

    # ── Merge ─────────────────────────────────────────────────────────
    # Join CCI by state + year
    merged = contracts.merge(cci_state, on=["state", "year"], how="left")
    print(f"  After CCI merge: {merged['mat_cci'].notna().sum()}/{len(merged)} have CCI")

    # Join FRED macro by year
    merged = merged.merge(fred_annual, on="year", how="left")

    # Join regional CPI
    if bls_annual is not None:
        for region, cpi_col in region_cpi_map.items():
            if cpi_col in bls_annual.columns:
                mapping = bls_annual.set_index("year")[cpi_col]
                mask = merged["region"] == region
                merged.loc[mask, "regional_cpi"] = merged.loc[mask, "year"].map(mapping)

    # ── Derived features ──────────────────────────────────────────────
    merged["cci_labor_premium"] = merged["labor_cci"] - merged["mat_cci"]
    merged["cci_deviation"] = merged["weighted_cci"] - 100
    merged["year_num"] = merged["year"] - 2015

    # Log-transform the target (award amounts are heavily right-skewed)
    merged["log_award_amount"] = np.log1p(merged["award_amount"])

    # Fill missing CCI/macro with medians
    fill_cols = REAL_FEATURES_CCI + REAL_FEATURES_MACRO + REAL_FEATURES_DERIVED
    for col in fill_cols:
        if col in merged.columns:
            merged[col] = merged[col].fillna(merged[col].median())

    # Drop rows still missing essentials
    merged = merged.dropna(subset=[REAL_TARGET])

    print(f"\n  Final dataset: {len(merged)} records, {merged['state'].nunique()} states, "
          f"{merged['region'].nunique()} regions")
    print(f"  Award amount range: ${merged['award_amount'].min():,.0f} - ${merged['award_amount'].max():,.0f}")
    print(f"  Log target range: {merged[REAL_TARGET].min():.2f} - {merged[REAL_TARGET].max():.2f}")

    # Save
    out_path = PROC_DIR / "real_model_ready.csv"
    merged.to_csv(out_path, index=False)
    print(f"  Saved: {out_path}")

    return merged


def compute_metrics(y_true, y_pred):
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mape": float(mean_absolute_percentage_error(y_true, y_pred) * 100),
    }


def compute_region_metrics(y_true, y_pred, regions):
    result = {}
    for region in sorted(set(regions)):
        mask = regions == region
        if mask.sum() > 1:
            result[region] = compute_metrics(y_true[mask], y_pred[mask])
    return result


def run_cv(model_name, df, features, cat_features, target, n_splits=5, params=None):
    """Run region-stratified CV."""
    avail = get_available_features(df, features)
    avail_cats = [c for c in cat_features if c in avail]
    X = df[avail]
    y = df[target].values
    regions = df["region"].values

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_metrics = []
    fold_region_metrics = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, regions)):
        model = create_model(model_name, avail, avail_cats, params)
        model.fit(X.iloc[train_idx], y[train_idx], X.iloc[val_idx], y[val_idx])
        y_pred = model.predict(X.iloc[val_idx])

        metrics = compute_metrics(y[val_idx], y_pred)
        metrics["fold"] = fold + 1
        fold_metrics.append(metrics)
        fold_region_metrics.append(compute_region_metrics(y[val_idx], y_pred, regions[val_idx]))

    return fold_metrics, fold_region_metrics


def run_test_eval(model_name, df_train, df_test, features, cat_features, target, params=None):
    """Train on full train set, evaluate on test."""
    avail = get_available_features(df_train, features)
    avail_cats = [c for c in cat_features if c in avail]

    model = create_model(model_name, avail, avail_cats, params)
    model.fit(df_train[avail], df_train[target].values)
    y_pred = model.predict(df_test[avail])
    y_true = df_test[target].values

    overall = compute_metrics(y_true, y_pred)
    per_region = compute_region_metrics(y_true, y_pred, df_test["region"].values)
    return overall, per_region, model


def run_ablation_real(df_train, model_name="CatBoost"):
    """Ablation study on real data feature groups."""
    print(f"\n{'─'*50}")
    print(f"  ABLATION STUDY (real data, {model_name})")
    print(f"{'─'*50}")

    stages = [
        ("Base", REAL_FEATURES_BASE),
        ("+CCI", REAL_FEATURES_BASE + REAL_FEATURES_CCI),
        ("+Macro", REAL_FEATURES_BASE + REAL_FEATURES_CCI + REAL_FEATURES_MACRO),
        ("+Derived (Full)", REAL_FEATURES_ALL),
    ]

    results = {}
    for label, features in stages:
        fold_metrics, _ = run_cv(model_name, df_train, features, REAL_CATEGORICALS, REAL_TARGET)
        avg_r2 = np.mean([m["r2"] for m in fold_metrics])
        avg_rmse = np.mean([m["rmse"] for m in fold_metrics])
        results[label] = {"r2": avg_r2, "rmse": avg_rmse, "n_features": len(features)}
        print(f"  {label:20s}: R²={avg_r2:.4f}, RMSE={avg_rmse:.4f} ({len(features)} features)")

    return results


def run_real_experiment(model_names=None):
    """Full experiment on real USASpending data."""
    if model_names is None:
        model_names = ALL_MODELS

    print("=" * 65)
    print("REAL DATA EXPERIMENT (USASpending Federal Construction Contracts)")
    print("=" * 65)

    # Build dataset
    df = build_real_dataset()

    # Temporal split: 2020-2023 train, 2024-2025 test
    df_train = df[df["year"] <= 2023].reset_index(drop=True)
    df_test = df[df["year"] >= 2024].reset_index(drop=True)
    print(f"\nTemporal split: train={len(df_train)} (2020-2023), test={len(df_test)} (2024-2025)")

    # ── Multi-model comparison ────────────────────────────────────────
    all_results = {}

    for model_name in model_names:
        print(f"\n{'─'*50}")
        print(f"  {model_name}")
        print(f"{'─'*50}")

        t0 = time.time()
        fold_metrics, fold_region_metrics = run_cv(
            model_name, df_train, REAL_FEATURES_ALL, REAL_CATEGORICALS, REAL_TARGET
        )
        cv_time = time.time() - t0

        t1 = time.time()
        test_metrics, test_region, _ = run_test_eval(
            model_name, df_train, df_test, REAL_FEATURES_ALL, REAL_CATEGORICALS, REAL_TARGET
        )
        test_time = time.time() - t1

        cv_avg = {
            "r2": float(np.mean([m["r2"] for m in fold_metrics])),
            "rmse": float(np.mean([m["rmse"] for m in fold_metrics])),
            "mape": float(np.mean([m["mape"] for m in fold_metrics])),
            "r2_std": float(np.std([m["r2"] for m in fold_metrics])),
        }

        all_results[model_name] = {
            "model": model_name,
            "dataset": "USASpending_real",
            "target": REAL_TARGET,
            "n_records": len(df_train),
            "cv_avg": cv_avg,
            "cv_folds": fold_metrics,
            "test_metrics": test_metrics,
            "test_region_metrics": test_region,
        }

        print(f"  CV:   R²={cv_avg['r2']:.4f} (+/-{cv_avg['r2_std']:.4f}), "
              f"RMSE={cv_avg['rmse']:.4f}  [{cv_time:.1f}s]")
        print(f"  Test: R²={test_metrics['r2']:.4f}, "
              f"RMSE={test_metrics['rmse']:.4f}  [{test_time:.1f}s]")

    # ── Comparison table ──────────────────────────────────────────────
    print(f"\n{'='*65}")
    print("RESULTS SUMMARY (Real Data)")
    print(f"{'='*65}")

    print(f"  {'Model':<14} {'CV R²':>8} {'CV RMSE':>9} {'Test R²':>8} {'Test RMSE':>10}")
    print("  " + "-" * 52)
    for name in model_names:
        cv = all_results[name]["cv_avg"]
        te = all_results[name]["test_metrics"]
        print(f"  {name:<14} {cv['r2']:>8.4f} {cv['rmse']:>9.4f} {te['r2']:>8.4f} {te['rmse']:>10.4f}")

    # Per-region
    print(f"\n  Per-Region Test R²:")
    regions = sorted(all_results[model_names[0]]["test_region_metrics"].keys())
    print(f"  {'Region':<14}" + "".join(f" {n:>12}" for n in model_names))
    for region in regions:
        vals = []
        for name in model_names:
            rm = all_results[name]["test_region_metrics"]
            vals.append(f"{rm[region]['r2']:>12.4f}" if region in rm else f"{'N/A':>12}")
        print(f"  {region:<14}" + "".join(vals))

    # ── Ablation ──────────────────────────────────────────────────────
    ablation = run_ablation_real(df_train)

    # ── Save ──────────────────────────────────────────────────────────
    output = {
        "experiment": "real_usaspending",
        "n_train": len(df_train),
        "n_test": len(df_test),
        "target": REAL_TARGET,
        "models": all_results,
        "ablation": {k: {"r2": v["r2"], "n_features": v["n_features"]} for k, v in ablation.items()},
    }
    out_path = RESULTS_DIR / "experiment_real_usaspending.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved: {out_path}")

    # ── Side-by-side with synthetic ───────────────────────────────────
    synth_path = RESULTS_DIR / "experiment_featureset_B.json"
    if synth_path.exists():
        with open(synth_path) as f:
            synth = json.load(f)

        print(f"\n{'='*65}")
        print("SYNTHETIC vs REAL DATA COMPARISON")
        print(f"{'='*65}")
        print(f"  {'':20s} {'Synthetic Pipeline':>20s} {'Real Pipeline':>20s}")
        print(f"  {'':20s} {'(cost_per_sqft)':>20s} {'(log award amount)':>20s}")
        print("  " + "-" * 60)
        print(f"  {'Training records':<20s} {'2,411':>20s} {len(df_train):>20,d}")
        print(f"  {'Test records':<20s} {'559':>20s} {len(df_test):>20,d}")

        for name in ["CatBoost", "XGBoost", "LightGBM", "RandomForest"]:
            if name in synth and name in all_results:
                s_r2 = synth[name]["cv_avg"]["r2"]
                r_r2 = all_results[name]["cv_avg"]["r2"]
                print(f"  {name + ' CV R²':<20s} {s_r2:>20.4f} {r_r2:>20.4f}")

        # Ablation comparison
        synth_abl_path = RESULTS_DIR / "ablation_results.json"
        if synth_abl_path.exists():
            with open(synth_abl_path) as f:
                synth_abl = json.load(f)
            print(f"\n  Ablation CCI lift:")
            s_base = synth_abl["incremental"]["Base"]["r2_mean"]
            s_cci = synth_abl["incremental"]["+CCI"]["r2_mean"]
            r_base = ablation["Base"]["r2"]
            r_cci = ablation["+CCI"]["r2"]
            print(f"  {'Base → +CCI':<20s} {f'+{(s_cci-s_base)*100:.2f}%':>20s} {f'+{(r_cci-r_base)*100:.2f}%':>20s}")

    return all_results


if __name__ == "__main__":
    run_real_experiment()
