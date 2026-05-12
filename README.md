# Predicting Construction Costs with Regional Intelligence

**CS/ML Thesis** -- Navid Rohan, 2026

A multi-model machine learning approach using city-level cost indices to improve regional construction cost prediction.

## Research Question

Can integrating continuous city-level Construction Cost Indices (CCI) and macroeconomic indicators into ML models improve regional prediction accuracy over a baseline that encodes geography as flat categoricals?

## Hypotheses

- **H1:** CCI features as continuous variables improve R² over categorical-only baselines. *Confirmed: +0.85% (96.63% -> 97.48%)*
- **H2:** CatBoost outperforms XGBoost, LightGBM, Random Forest, and MLP. *Confirmed: ranks 1st across all metrics*
- **H3:** SHAP feature importance patterns vary across US regions. *Confirmed: labor CCI dominates in Southeast, material CCI in Midwest*

## Key Results

| Model | R² | RMSE ($/sqft) | MAPE (%) |
|-------|-----|---------------|----------|
| **CatBoost** | **0.9740** | **5.52** | **2.64** |
| MLP | 0.9722 | 5.69 | 2.71 |
| LightGBM | 0.9708 | 5.84 | 2.82 |
| XGBoost | 0.9675 | 6.17 | 2.95 |
| Random Forest | 0.9657 | 6.34 | 3.02 |

## Project Structure

```
├── paper/                  # Thesis paper (LaTeX + PDF)
│   ├── main.tex
│   ├── main.pdf
│   ├── references.bib
│   └── figures/
├── presentation/           # Next.js thesis presentation
├── src/
│   ├── data_collection.py  # Fetch FRED/BLS data + generate synthetic CCI
│   ├── preprocessing.py    # Merge, clean, engineer features
│   ├── models.py           # Feature sets + model wrapper definitions
│   ├── experiment.py       # Multi-model comparison with holdout test
│   ├── optimize.py         # Optuna hyperparameter tuning
│   ├── ablation.py         # Feature group ablation study
│   ├── significance.py     # Statistical significance tests
│   ├── explain_shap.py     # SHAP TreeExplainer analysis
│   ├── train.py            # Legacy CatBoost A vs B
│   ├── evaluate.py         # Legacy comparison charts
│   └── explain.py          # Legacy CatBoost feature importance
├── data/                   # Raw + processed data (gitignored)
├── models/                 # Saved model artifacts (gitignored)
├── figures/                # Generated plots
├── results/                # Experiment output (JSON/CSV)
└── requirements.txt
```

## Data Sources

| Source | Description | Access |
|--------|------------|--------|
| RSMeans CCI | City-level cost indices (50 cities, synthetic) | Generated from published ratios |
| FRED PPI | Producer Price Indices (construction materials) | Public CSV endpoint |
| BLS CPI | Consumer Price Index (national + regional) | Public API v1 |
| BEA GDP | Real GDP, housing starts, permits, mortgage rates | FRED |

## Quick Start

```bash
pip install -r requirements.txt

# Data pipeline
python src/data_collection.py    # Fetch data + generate synthetic CCI
python src/preprocessing.py      # Merge and engineer features

# Thesis experiments (run from src/)
cd src
python experiment.py             # Multi-model comparison
python ablation.py               # Feature group ablation
python significance.py           # Statistical significance tests
python explain_shap.py           # SHAP analysis
```

## Feature Sets

- **Feature Set A (Baseline):** 7 features -- project type, area, year, region, state, formwork rate, concrete rate
- **Feature Set B (Regional-Aware):** 28 features -- adds 4 CCI, 11 macroeconomic, 6 derived interaction features

## Application: BuildScan

BuildScan is an iOS app that operationalizes the thesis findings. It uses CCI lookup tables as a pricing engine combined with AI-generated quantity estimation, applying decomposed cost indices (material, labor, equipment) at the line-item level across 50 states and 17 trade categories.
