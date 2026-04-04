# Regional Construction Cost Estimation via Ensemble ML

**Research Question:** Can integrating city-level cost indices (RSMeans CCI) and macroeconomic signals (FRED PPI/CPI/GDP) into a CatBoost ensemble model significantly improve regional construction cost prediction accuracy over national baseline models?

## Hypotheses

- **H₁:** Adding RSMeans CCI as continuous features improves per-region R² by ≥0.02 over flat categorical encoding
- **H₂:** Incorporating PPI and regional GDP reduces MAPE in high-volatility regions by ≥15%
- **H₃:** Regional SHAP decomposition reveals different top feature drivers per Census Division

## Project Structure

```
├── data/
│   ├── raw/            # Original datasets (RSMeans, FRED, BEA)
│   └── processed/      # Cleaned, merged, feature-engineered
├── notebooks/          # EDA and analysis notebooks
├── src/
│   ├── data_collection.py    # FRED API + data loading
│   ├── preprocessing.py      # Clean, merge, encode
│   ├── features.py           # Feature engineering
│   ├── train.py              # Model A (baseline) & Model B (regional)
│   ├── evaluate.py           # Metrics + comparison
│   └── explain.py            # SHAP analysis
├── models/             # Saved model artifacts
├── figures/            # Generated plots
└── requirements.txt
```

## Data Sources

| Source | Description | Access |
|--------|------------|--------|
| RSMeans CCI | City-level cost indices (318 US cities) | Gordian/RSMeans |
| FRED PPI | Producer Price Index for construction | FRED API (free) |
| BEA GDP | Regional GDP by MSA | BEA API (free) |
| BLS CPI | Consumer Price Index, regional | BLS API (free) |

## Quick Start

```bash
pip install -r requirements.txt
python src/data_collection.py    # Pull FRED + BLS data
python src/preprocessing.py      # Clean and merge
python src/features.py           # Engineer features
python src/train.py              # Train Model A & B
python src/evaluate.py           # Compare and report
python src/explain.py            # SHAP analysis
```

## Models

- **Model A (Baseline):** CatBoost on national dataset, region as flat categorical
- **Model B (Regional-Aware):** CatBoost with CCI continuous features, PPI lags, regional GDP, interaction terms, region-stratified CV
