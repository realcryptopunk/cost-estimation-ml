"""
Preprocessing — Clean, merge, and prepare data for modeling.

Merges:
  - Synthetic CCI project data (city-level)
  - FRED macro data (national monthly)
  - BLS regional CPI (regional monthly)

Output: data/processed/model_ready.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROC_DIR = Path(__file__).parent.parent / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)


def load_raw():
    """Load all raw data files."""
    print("📂 Loading raw data...")
    
    # Use real CCI if available, otherwise fall back to synthetic
    real_path = RAW_DIR / "real_cci_projects.csv"
    synth_path = RAW_DIR / "synthetic_cci_projects.csv"
    cci_path = real_path if real_path.exists() else synth_path
    cci = pd.read_csv(cci_path)
    print(f"  Source: {cci_path.name}")
    print(f"  CCI projects: {len(cci)} rows")
    
    fred = pd.read_csv(RAW_DIR / "fred_macro.csv", parse_dates=["date"])
    print(f"  FRED macro: {len(fred)} rows, {len(fred.columns)-1} series")
    
    bls_path = RAW_DIR / "bls_regional_cpi.csv"
    bls = pd.read_csv(bls_path, parse_dates=["date"]) if bls_path.exists() else None
    if bls is not None:
        print(f"  BLS CPI: {len(bls)} rows")
    else:
        print("  BLS CPI: not available (skipping)")
    
    return cci, fred, bls


def merge_macro(cci: pd.DataFrame, fred: pd.DataFrame) -> pd.DataFrame:
    """Merge FRED macro data into project records by year-month."""
    print("\n🔗 Merging FRED macro data...")
    
    # Create a date column for CCI projects (use July of each year as midpoint)
    cci["date"] = pd.to_datetime(cci["year"].astype(str) + "-07-01")
    
    # Get annual averages from FRED
    fred["year"] = fred["date"].dt.year
    fred_annual = fred.groupby("year").mean(numeric_only=True).reset_index()
    fred_annual = fred_annual.drop(columns=["date"], errors="ignore")
    
    merged = cci.merge(fred_annual, on="year", how="left")
    print(f"  ✅ Merged: {len(merged)} rows with {len(fred_annual.columns)-1} macro features")
    
    return merged


def merge_regional_cpi(df: pd.DataFrame, bls: pd.DataFrame) -> pd.DataFrame:
    """Merge regional CPI based on region mapping."""
    if bls is None:
        print("\n⏭️ Skipping BLS CPI merge (data not available)")
        return df
    
    print("\n🔗 Merging BLS regional CPI...")
    
    region_cpi_map = {
        "Northeast": "cpi_northeast",
        "Southeast": "cpi_south",
        "Midwest": "cpi_midwest",
        "Southwest": "cpi_south",  # BLS groups South together
        "West": "cpi_west",
    }
    
    # Get annual average CPI per region
    bls["year"] = bls["date"].dt.year
    bls_annual = bls.groupby("year").mean(numeric_only=True).reset_index()
    
    # Map each project to its regional CPI
    for region, cpi_col in region_cpi_map.items():
        if cpi_col in bls_annual.columns:
            mapping = bls_annual.set_index("year")[cpi_col]
            mask = df["region"] == region
            df.loc[mask, "regional_cpi"] = df.loc[mask, "year"].map(mapping)
    
    print(f"  ✅ Added regional CPI for {df['regional_cpi'].notna().sum()} rows")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate the merged dataset."""
    print("\n🧹 Cleaning...")
    
    initial = len(df)
    
    # Drop rows with missing target
    df = df.dropna(subset=["cost_per_sqft"])
    
    # Clip extreme outliers (beyond 3 std)
    for col in ["cost_per_sqft", "area_sqft"]:
        mean, std = df[col].mean(), df[col].std()
        df = df[(df[col] >= mean - 3*std) & (df[col] <= mean + 3*std)]
    
    # Fill remaining NaN in macro features with column median
    macro_cols = [c for c in df.columns if c.startswith("ppi_") or c.startswith("real_") 
                  or c.startswith("cpi_") or c in ["unemployment_rate", "mortgage_30yr", 
                  "building_permits", "housing_starts", "regional_cpi"]]
    for col in macro_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    print(f"  Rows: {initial} → {len(df)} ({initial - len(df)} removed)")
    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add computed features for modeling."""
    print("\n⚙️ Adding derived features...")
    
    # CCI spread (labor premium over materials)
    df["cci_labor_premium"] = df["labor_cci"] - df["mat_cci"]
    
    # CCI deviation from national avg (100)
    df["cci_deviation"] = df["weighted_cci"] - 100
    
    # Cost intensity (formwork + concrete as combined rate)
    df["combined_material_rate"] = df["formwork_rate"] + df["concrete_rate"]
    
    # Log area (for scale effects)
    df["log_area"] = np.log1p(df["area_sqft"])
    
    # Year as numeric for trend
    df["year_num"] = df["year"] - 2015
    
    # PPI change YoY (if available)
    if "ppi_construction_materials" in df.columns:
        df["ppi_yoy_change"] = df.groupby("city")["ppi_construction_materials"].pct_change()
        df["ppi_yoy_change"] = df["ppi_yoy_change"].fillna(0)
    
    print(f"  ✅ Added {6} derived features")
    return df


def save(df: pd.DataFrame):
    """Save the processed dataset."""
    # Drop temp columns
    df = df.drop(columns=["date"], errors="ignore")
    
    out = PROC_DIR / "model_ready.csv"
    df.to_csv(out, index=False)
    
    print(f"\n💾 Saved processed data: {out}")
    print(f"   Shape: {df.shape}")
    print(f"   Features: {list(df.columns)}")
    print(f"\n   Target: cost_per_sqft")
    print(f"   Mean: ${df['cost_per_sqft'].mean():.2f}/sqft")
    print(f"   Std:  ${df['cost_per_sqft'].std():.2f}/sqft")
    print(f"   Range: ${df['cost_per_sqft'].min():.2f} – ${df['cost_per_sqft'].max():.2f}")
    
    # Summary by region
    print(f"\n   By region:")
    for region, group in df.groupby("region"):
        print(f"     {region:12s}: {len(group):4d} projects, avg ${group['cost_per_sqft'].mean():.0f}/sqft")


if __name__ == "__main__":
    print("=" * 60)
    print("Regional Construction Cost Estimation — Preprocessing")
    print("=" * 60)
    
    cci, fred, bls = load_raw()
    df = merge_macro(cci, fred)
    df = merge_regional_cpi(df, bls)
    df = clean(df)
    df = add_derived_features(df)
    save(df)
    
    print("\n" + "=" * 60)
    print("✅ Preprocessing complete!")
    print("   Next: python src/train.py")
    print("=" * 60)
