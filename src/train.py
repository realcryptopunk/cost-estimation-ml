"""
Train — Model A (national baseline) vs Model B (regional-aware).

Model A: CatBoost with region/state as flat categoricals, no CCI integration
Model B: CatBoost with CCI as continuous features, macro signals, derived features

Both use region-stratified 5-fold CV.
"""

import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_percentage_error
from catboost import CatBoostRegressor, Pool

PROC_DIR = Path(__file__).parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ── Feature Sets ───────────────────────────────────────────────────────────────

# Model A: baseline — no CCI continuous features, no macro
FEATURES_A = [
    "area_sqft", "formwork_rate", "concrete_rate",
    "project_type", "region", "state", "year",
]

# Model B: regional-aware — CCI + macro + derived
FEATURES_B = [
    "area_sqft", "formwork_rate", "concrete_rate",
    "project_type", "region", "state", "year",
    # CCI continuous
    "mat_cci", "labor_cci", "equip_cci", "weighted_cci",
    # Derived
    "cci_labor_premium", "cci_deviation", "combined_material_rate",
    "log_area", "year_num",
    # Macro (if available)
    "ppi_construction_materials", "ppi_cement", "ppi_steel_mill", "ppi_lumber",
    "real_gdp", "cpi_all_urban", "unemployment_rate",
    "mortgage_30yr", "building_permits", "housing_starts",
    "ppi_yoy_change",
    # Regional CPI
    "regional_cpi",
]

CATEGORICALS_A = ["project_type", "region", "state"]
CATEGORICALS_B = ["project_type", "region", "state"]

TARGET = "cost_per_sqft"


def load_data():
    """Load processed data."""
    df = pd.read_csv(PROC_DIR / "model_ready.csv")
    print(f"📂 Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


def get_features(df, feature_list):
    """Filter to available features only."""
    available = [f for f in feature_list if f in df.columns]
    missing = [f for f in feature_list if f not in df.columns]
    if missing:
        print(f"  ⚠️ Missing features (skipped): {missing}")
    return available


def train_model(df, features, cat_features, model_name, verbose=True):
    """Train CatBoost with region-stratified 5-fold CV."""
    print(f"\n{'='*50}")
    print(f"🏋️ Training {model_name}")
    print(f"{'='*50}")
    
    avail_features = get_features(df, features)
    avail_cats = [c for c in cat_features if c in avail_features]
    
    print(f"  Features: {len(avail_features)}")
    print(f"  Categoricals: {avail_cats}")
    
    X = df[avail_features].copy()
    y = df[TARGET].values
    regions = df["region"].values
    
    # Encode categoricals as string for CatBoost
    for col in avail_cats:
        X[col] = X[col].astype(str)
    
    cat_indices = [avail_features.index(c) for c in avail_cats]
    
    # Region-stratified 5-fold CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    fold_metrics = []
    region_metrics = {r: {"r2": [], "rmse": [], "mape": []} for r in df["region"].unique()}
    best_model = None
    best_r2 = -1
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, regions)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        regions_val = regions[val_idx]
        
        model = CatBoostRegressor(
            iterations=1000,
            learning_rate=0.05,
            depth=8,
            l2_leaf_reg=3,
            random_seed=42 + fold,
            cat_features=cat_indices,
            verbose=0,
            early_stopping_rounds=50,
        )
        
        train_pool = Pool(X_train, y_train, cat_features=cat_indices)
        val_pool = Pool(X_val, y_val, cat_features=cat_indices)
        
        model.fit(train_pool, eval_set=val_pool)
        
        y_pred = model.predict(X_val)
        
        # Overall metrics
        r2 = r2_score(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mape = mean_absolute_percentage_error(y_val, y_pred) * 100
        
        fold_metrics.append({"fold": fold+1, "r2": r2, "rmse": rmse, "mape": mape})
        
        if verbose:
            print(f"  Fold {fold+1}: R²={r2:.4f}, RMSE={rmse:.2f}, MAPE={mape:.2f}%")
        
        # Per-region metrics
        for region in df["region"].unique():
            mask = regions_val == region
            if mask.sum() > 0:
                r2_r = r2_score(y_val[mask], y_pred[mask])
                rmse_r = np.sqrt(mean_squared_error(y_val[mask], y_pred[mask]))
                mape_r = mean_absolute_percentage_error(y_val[mask], y_pred[mask]) * 100
                region_metrics[region]["r2"].append(r2_r)
                region_metrics[region]["rmse"].append(rmse_r)
                region_metrics[region]["mape"].append(mape_r)
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
    
    # Aggregate
    avg = {
        "r2": np.mean([m["r2"] for m in fold_metrics]),
        "rmse": np.mean([m["rmse"] for m in fold_metrics]),
        "mape": np.mean([m["mape"] for m in fold_metrics]),
    }
    
    print(f"\n  📊 {model_name} — 5-Fold Average:")
    print(f"     R²   = {avg['r2']:.4f} (±{np.std([m['r2'] for m in fold_metrics]):.4f})")
    print(f"     RMSE = {avg['rmse']:.2f}")
    print(f"     MAPE = {avg['mape']:.2f}%")
    
    # Per-region summary
    region_summary = {}
    print(f"\n  📍 Per-Region Performance:")
    for region in sorted(region_metrics.keys()):
        rm = region_metrics[region]
        summary = {
            "r2": float(np.mean(rm["r2"])),
            "rmse": float(np.mean(rm["rmse"])),
            "mape": float(np.mean(rm["mape"])),
        }
        region_summary[region] = summary
        print(f"     {region:12s}: R²={summary['r2']:.4f}, RMSE={summary['rmse']:.2f}, MAPE={summary['mape']:.2f}%")
    
    # Save model and metrics
    model_path = MODEL_DIR / f"{model_name.lower().replace(' ', '_')}.cbm"
    best_model.save_model(str(model_path))
    
    results = {
        "model_name": model_name,
        "features": avail_features,
        "categoricals": avail_cats,
        "n_features": len(avail_features),
        "n_samples": len(df),
        "cv_folds": 5,
        "avg_metrics": avg,
        "fold_metrics": fold_metrics,
        "region_metrics": region_summary,
    }
    
    results_path = MODEL_DIR / f"{model_name.lower().replace(' ', '_')}_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n  💾 Model saved: {model_path}")
    print(f"  💾 Results saved: {results_path}")
    
    return best_model, results


if __name__ == "__main__":
    print("=" * 60)
    print("Regional Construction Cost Estimation — Training")
    print("=" * 60)
    
    df = load_data()
    
    # Model A: National baseline
    model_a, results_a = train_model(df, FEATURES_A, CATEGORICALS_A, "Model_A_Baseline")
    
    # Model B: Regional-aware
    model_b, results_b = train_model(df, FEATURES_B, CATEGORICALS_B, "Model_B_Regional")
    
    # Comparison
    print("\n" + "=" * 60)
    print("📊 MODEL COMPARISON: A (Baseline) vs B (Regional-Aware)")
    print("=" * 60)
    
    a_avg = results_a["avg_metrics"]
    b_avg = results_b["avg_metrics"]
    
    print(f"\n  {'Metric':<10} {'Model A':>10} {'Model B':>10} {'Δ':>10}")
    print(f"  {'-'*42}")
    print(f"  {'R²':<10} {a_avg['r2']:>10.4f} {b_avg['r2']:>10.4f} {b_avg['r2']-a_avg['r2']:>+10.4f}")
    print(f"  {'RMSE':<10} {a_avg['rmse']:>10.2f} {b_avg['rmse']:>10.2f} {b_avg['rmse']-a_avg['rmse']:>+10.2f}")
    print(f"  {'MAPE':<10} {a_avg['mape']:>9.2f}% {b_avg['mape']:>9.2f}% {b_avg['mape']-a_avg['mape']:>+9.2f}%")
    
    print(f"\n  Per-Region ΔR² (B − A):")
    for region in sorted(results_a["region_metrics"].keys()):
        r2_a = results_a["region_metrics"][region]["r2"]
        r2_b = results_b["region_metrics"][region]["r2"]
        delta = r2_b - r2_a
        bar = "█" * int(max(0, delta) * 200)
        print(f"    {region:12s}: {delta:>+.4f} {bar}")
    
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print("   Next: python src/evaluate.py")
    print("=" * 60)
