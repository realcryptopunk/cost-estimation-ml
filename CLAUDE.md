# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ML research project (CS/ML master's thesis) comparing multiple regression models for predicting US construction costs ($/sqft). Tests whether integrating city-level cost indices (CCI) and macroeconomic signals (FRED PPI, BLS CPI, BEA GDP) improves regional accuracy over a national baseline.

- **Feature Set A (Baseline):** 7 features — project attributes + region/state as flat categoricals
- **Feature Set B (Regional-Aware):** 28 features — adds CCI continuous, macro indicators, derived features

Models compared: CatBoost, XGBoost, LightGBM, Random Forest, MLP (PyTorch).
Target variable: `cost_per_sqft`. Evaluation: temporal holdout (2024-2025) + region-stratified 5-fold CV on training data (2015-2023). Metrics: R², RMSE, MAPE per region.

Planned iOS app: CoreML-exported model for on-device cost estimation with regional intelligence.

## Commands

**Data pipeline** (sequential):
```bash
pip install -r requirements.txt
python src/data_collection.py    # Fetches FRED/BLS data + generates synthetic CCI dataset
python src/preprocessing.py      # Merges, cleans, engineers features → data/processed/model_ready.csv
python src/train.py              # Original CatBoost A vs B (legacy)
python src/evaluate.py           # Generates comparison charts → figures/*.png
python src/explain.py            # CatBoost PredictionValuesChange importance (legacy)
```

**Thesis experiment pipeline** (new, run from `src/`):
```bash
python experiment.py             # Multi-model comparison with holdout test → results/
python optimize.py               # Optuna hyperparameter tuning → results/optuna_best_params.json
python ablation.py               # Feature group ablation study → results/ + figures/
python significance.py           # Statistical significance tests → results/
python explain_shap.py           # SHAP TreeExplainer analysis → figures/ + results/
```

No test suite exists. No linter configured.

## Architecture

**Data flow:** Raw APIs/synthetic data → `data/raw/` → preprocessing merge → `data/processed/model_ready.csv` → train → `models/` → evaluate/explain → `figures/`

**Key design decisions:**
- RSMeans CCI data is **synthetic** (real data is paywalled). Generated in `data_collection.py` from known city cost ratios with yearly drift, COVID bumps, and per-project noise. 50 cities across 5 regions, ~2750 project records.
- FRED data is fetched via public CSV endpoint (no API key). BLS uses public v1 API (no key). Both may fail silently — preprocessing handles missing BLS gracefully.
- Feature sets and model definitions centralized in `models.py`. `FEATURES_A` (7), `FEATURES_B` (28), `FEATURE_GROUPS` for ablation. Model wrappers: CatBoost, XGBoost, LightGBM, RandomForest, MLP.
- `explain.py` uses CatBoost's PredictionValuesChange (legacy). `explain_shap.py` uses SHAP TreeExplainer (Python 3.9 supports numba/SHAP fine).
- Matplotlib uses `Agg` backend (headless) in `evaluate.py` and `explain.py`.
- Region-stratified CV uses `StratifiedKFold` on the `region` column to ensure balanced regional representation per fold.

**Categorical handling:** `project_type`, `region`, `state` are CatBoost native categoricals (passed via `cat_features` index list to `Pool`).

**Derived features** (added in `preprocessing.py`): `cci_labor_premium`, `cci_deviation`, `combined_material_rate`, `log_area`, `year_num`, `ppi_yoy_change`.
