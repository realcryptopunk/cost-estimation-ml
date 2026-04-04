"""
Feature Importance — Global and regional analysis using CatBoost built-in importance.

(SHAP requires numba which doesn't support Python 3.14 yet. 
 Using CatBoost's PredictionValuesChange instead — conceptually similar.)

Generates:
  - Global feature importance bar chart
  - Per-region feature importance comparison
  - Feature importance JSON
"""

import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from catboost import CatBoostRegressor, Pool
from pathlib import Path

PROC_DIR = Path(__file__).parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent.parent / "models"
FIG_DIR = Path(__file__).parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_model_and_data(model_name="model_b_regional"):
    """Load the trained model and processed data."""
    model = CatBoostRegressor()
    model.load_model(str(MODEL_DIR / f"{model_name}.cbm"))
    
    with open(MODEL_DIR / f"{model_name}_results.json") as f:
        results = json.load(f)
    
    df = pd.read_csv(PROC_DIR / "model_ready.csv")
    
    features = results["features"]
    cats = results["categoricals"]
    
    X = df[features].copy()
    for col in cats:
        X[col] = X[col].astype(str)
    
    return model, df, X, features, cats


def global_importance(model, features):
    """Plot global feature importance."""
    print("\n🔍 Computing global feature importance...")
    
    importance = model.get_feature_importance()
    sorted_idx = np.argsort(importance)
    top_n = min(15, len(features))
    top_idx = sorted_idx[-top_n:]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(range(top_n), importance[top_idx], color="#00d2ff", alpha=0.85)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels([features[i] for i in top_idx], fontsize=10)
    ax.set_xlabel("Feature Importance (PredictionValuesChange)", fontsize=11)
    ax.set_title("Global Feature Importance — Model B (Regional-Aware)", fontsize=13)
    ax.grid(axis="x", alpha=0.3)
    
    plt.tight_layout()
    out = FIG_DIR / "global_feature_importance.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ Saved: {out}")
    
    # Print top features
    print(f"\n  Top-10 Features (Global):")
    for i in sorted_idx[-10:][::-1]:
        print(f"    {features[i]:30s}: {importance[i]:.2f}")
    
    return dict(zip(features, importance.tolist()))


def regional_importance(model, df, X, features, cats):
    """Train per-region models and compare feature importance."""
    print("\n🗺️ Computing per-region feature importance...")
    
    cat_indices = [features.index(c) for c in cats if c in features]
    regions = sorted(df["region"].unique())
    region_imp = {}
    
    fig, axes = plt.subplots(1, len(regions), figsize=(5*len(regions), 8), sharey=False)
    colors = ["#00d2ff", "#ff6b6b", "#00c853", "#ffa726", "#a855f7"]
    
    for i, region in enumerate(regions):
        mask = df["region"] == region
        X_r = X[mask]
        y_r = df.loc[mask, "cost_per_sqft"].values
        
        # Train a quick regional sub-model
        regional_model = CatBoostRegressor(
            iterations=500, learning_rate=0.05, depth=6,
            cat_features=cat_indices, verbose=0, random_seed=42
        )
        pool = Pool(X_r, y_r, cat_features=cat_indices)
        regional_model.fit(pool)
        
        imp = regional_model.get_feature_importance()
        sorted_idx = np.argsort(imp)[-10:]
        
        region_imp[region] = {features[j]: float(imp[j]) for j in sorted_idx}
        
        axes[i].barh(range(10), imp[sorted_idx], color=colors[i % len(colors)], alpha=0.85)
        axes[i].set_yticks(range(10))
        axes[i].set_yticklabels([features[j] for j in sorted_idx], fontsize=8)
        axes[i].set_title(f"{region}\n({mask.sum()} projects)", fontsize=11)
        axes[i].set_xlabel("Importance")
    
    plt.suptitle("Feature Importance by Region (Per-Region CatBoost Models)", fontsize=13, y=1.02)
    plt.tight_layout()
    out = FIG_DIR / "regional_feature_importance.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ Saved: {out}")
    
    # Save JSON
    out_json = FIG_DIR / "regional_feature_importance.json"
    with open(out_json, "w") as f:
        json.dump(region_imp, f, indent=2)
    print(f"  ✅ Saved: {out_json}")
    
    # Print top-3 per region
    print(f"\n  📊 Top-3 Features by Region:")
    for region in regions:
        top3 = sorted(region_imp[region].items(), key=lambda x: -x[1])[:3]
        feats = ", ".join([f"{n} ({v:.1f})" for n, v in top3])
        print(f"    {region:12s}: {feats}")
    
    return region_imp


if __name__ == "__main__":
    print("=" * 60)
    print("Regional Construction Cost Estimation — Feature Importance")
    print("=" * 60)
    
    model, df, X, features, cats = load_model_and_data()
    
    global_imp = global_importance(model, features)
    regional_imp = regional_importance(model, df, X, features, cats)
    
    print("\n" + "=" * 60)
    print("✅ Feature importance analysis complete!")
    print(f"   Figures saved to: {FIG_DIR}")
    print("=" * 60)
