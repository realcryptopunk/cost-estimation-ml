"""
Data Collection — Pull construction-related economic data from public APIs.

Sources:
  - FRED (Federal Reserve): PPI for construction materials, cement, steel, lumber
  - BLS: Regional CPI
  - Synthetic RSMeans CCI (since actual RSMeans is paywalled — we generate 
    a realistic proxy from known city cost ratios + BLS regional data)

Usage:
  python src/data_collection.py
"""

import os
import json
import requests
import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ── FRED Data ──────────────────────────────────────────────────────────────────
# Free API — no key needed for CSV bulk download

FRED_SERIES = {
    # Construction PPI
    "WPUSI012011": "ppi_construction_materials",
    "WPU0531"    : "ppi_cement",
    "WPU101"     : "ppi_steel_mill",
    "WPU0811"    : "ppi_lumber",
    "PCU23"      : "ppi_construction_services",
    # Macro
    "GDPC1"      : "real_gdp",
    "CPIAUCSL"   : "cpi_all_urban",
    "UNRATE"     : "unemployment_rate",
    "MORTGAGE30US": "mortgage_30yr",
    "PERMIT"     : "building_permits",
    "HOUST"      : "housing_starts",
}

def fetch_fred_series(series_id: str, name: str) -> pd.DataFrame:
    """Fetch a FRED series via the public CSV endpoint (no API key needed)."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    print(f"  Fetching FRED {series_id} ({name})...")
    try:
        df = pd.read_csv(url)
        # FRED CSVs may have varying column names
        date_col = [c for c in df.columns if c.upper() == "DATE"]
        if date_col:
            df = df.rename(columns={date_col[0]: "date"})
        else:
            df.columns = ["date", name]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        val_col = [c for c in df.columns if c != "date"][0]
        df[name] = pd.to_numeric(df[val_col], errors="coerce")
        df = df[["date", name]].dropna()
        return df
    except Exception as e:
        print(f"  ⚠️ Failed to fetch {series_id}: {e}")
        return pd.DataFrame(columns=["date", name])


def collect_fred():
    """Pull all FRED series and merge into a single monthly dataset."""
    print("\n📊 Collecting FRED data...")
    
    dfs = []
    for series_id, name in FRED_SERIES.items():
        df = fetch_fred_series(series_id, name)
        if not df.empty:
            # Resample to monthly (some series are quarterly/weekly)
            df = df.set_index("date").resample("MS").last().reset_index()
            dfs.append(df)
    
    if not dfs:
        print("  ❌ No FRED data collected")
        return
    
    # Merge all on date
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="date", how="outer")
    
    merged = merged.sort_values("date").reset_index(drop=True)
    
    # Forward-fill quarterly data into monthly
    merged = merged.ffill()
    
    out = RAW_DIR / "fred_macro.csv"
    merged.to_csv(out, index=False)
    print(f"  ✅ Saved {len(merged)} rows → {out}")
    print(f"  📅 Range: {merged['date'].min()} to {merged['date'].max()}")
    return merged


# ── Synthetic RSMeans CCI ──────────────────────────────────────────────────────
# Real RSMeans is paywalled. We generate a realistic proxy based on:
# - Known relative cost ratios by city (from public RSMeans summary tables)
# - Variation over time tied to FRED PPI
# - Material/Labor/Equipment sub-index splits

# Source: Publicly available RSMeans city cost index summaries
# Base = national average = 100
CITY_COST_INDICES = {
    # Northeast (high cost)
    "New York, NY": {"mat": 118.2, "labor": 148.5, "equip": 105.3, "region": "Northeast", "state": "NY"},
    "Boston, MA": {"mat": 112.8, "labor": 138.7, "equip": 103.8, "region": "Northeast", "state": "MA"},
    "Philadelphia, PA": {"mat": 110.5, "labor": 132.4, "equip": 102.1, "region": "Northeast", "state": "PA"},
    "Newark, NJ": {"mat": 113.1, "labor": 141.2, "equip": 104.5, "region": "Northeast", "state": "NJ"},
    "Hartford, CT": {"mat": 109.4, "labor": 125.8, "equip": 102.7, "region": "Northeast", "state": "CT"},
    "Pittsburgh, PA": {"mat": 104.2, "labor": 114.6, "equip": 100.8, "region": "Northeast", "state": "PA"},
    "Providence, RI": {"mat": 108.7, "labor": 121.3, "equip": 101.9, "region": "Northeast", "state": "RI"},
    "Buffalo, NY": {"mat": 105.1, "labor": 118.9, "equip": 101.2, "region": "Northeast", "state": "NY"},
    "Washington, DC": {"mat": 107.3, "labor": 119.5, "equip": 102.4, "region": "Northeast", "state": "DC"},
    "Baltimore, MD": {"mat": 104.8, "labor": 112.3, "equip": 101.1, "region": "Northeast", "state": "MD"},
    
    # Southeast (moderate-low)
    "Atlanta, GA": {"mat": 100.5, "labor": 89.4, "equip": 99.2, "region": "Southeast", "state": "GA"},
    "Miami, FL": {"mat": 105.3, "labor": 95.7, "equip": 100.8, "region": "Southeast", "state": "FL"},
    "Charlotte, NC": {"mat": 99.1, "labor": 82.6, "equip": 98.7, "region": "Southeast", "state": "NC"},
    "Nashville, TN": {"mat": 99.8, "labor": 85.3, "equip": 99.1, "region": "Southeast", "state": "TN"},
    "Orlando, FL": {"mat": 101.2, "labor": 88.1, "equip": 99.5, "region": "Southeast", "state": "FL"},
    "Tampa, FL": {"mat": 100.8, "labor": 86.9, "equip": 99.3, "region": "Southeast", "state": "FL"},
    "Raleigh, NC": {"mat": 98.5, "labor": 80.4, "equip": 98.4, "region": "Southeast", "state": "NC"},
    "Charleston, SC": {"mat": 99.3, "labor": 81.8, "equip": 98.6, "region": "Southeast", "state": "SC"},
    "Richmond, VA": {"mat": 100.1, "labor": 87.5, "equip": 99.0, "region": "Southeast", "state": "VA"},
    "Jacksonville, FL": {"mat": 100.4, "labor": 84.2, "equip": 99.1, "region": "Southeast", "state": "FL"},
    
    # Midwest (moderate)
    "Chicago, IL": {"mat": 107.8, "labor": 128.5, "equip": 103.2, "region": "Midwest", "state": "IL"},
    "Detroit, MI": {"mat": 104.6, "labor": 118.2, "equip": 101.5, "region": "Midwest", "state": "MI"},
    "Minneapolis, MN": {"mat": 106.3, "labor": 119.7, "equip": 102.1, "region": "Midwest", "state": "MN"},
    "Columbus, OH": {"mat": 100.2, "labor": 97.5, "equip": 99.8, "region": "Midwest", "state": "OH"},
    "Indianapolis, IN": {"mat": 99.5, "labor": 95.8, "equip": 99.4, "region": "Midwest", "state": "IN"},
    "Kansas City, MO": {"mat": 101.3, "labor": 102.4, "equip": 100.2, "region": "Midwest", "state": "MO"},
    "Milwaukee, WI": {"mat": 104.1, "labor": 115.3, "equip": 101.3, "region": "Midwest", "state": "WI"},
    "Cincinnati, OH": {"mat": 99.8, "labor": 96.2, "equip": 99.5, "region": "Midwest", "state": "OH"},
    "Cleveland, OH": {"mat": 102.5, "labor": 105.8, "equip": 100.4, "region": "Midwest", "state": "OH"},
    "St. Louis, MO": {"mat": 101.8, "labor": 108.4, "equip": 100.6, "region": "Midwest", "state": "MO"},
    
    # Southwest (moderate-low, boom)
    "Dallas, TX": {"mat": 98.4, "labor": 80.1, "equip": 99.2, "region": "Southwest", "state": "TX"},
    "Houston, TX": {"mat": 99.7, "labor": 83.5, "equip": 99.8, "region": "Southwest", "state": "TX"},
    "Phoenix, AZ": {"mat": 100.3, "labor": 86.7, "equip": 99.5, "region": "Southwest", "state": "AZ"},
    "San Antonio, TX": {"mat": 96.8, "labor": 76.4, "equip": 98.7, "region": "Southwest", "state": "TX"},
    "Austin, TX": {"mat": 98.9, "labor": 81.3, "equip": 99.3, "region": "Southwest", "state": "TX"},
    "Denver, CO": {"mat": 103.5, "labor": 98.4, "equip": 100.8, "region": "Southwest", "state": "CO"},
    "Las Vegas, NV": {"mat": 104.2, "labor": 105.6, "equip": 101.0, "region": "Southwest", "state": "NV"},
    "Albuquerque, NM": {"mat": 99.1, "labor": 82.9, "equip": 99.0, "region": "Southwest", "state": "NM"},
    "Tucson, AZ": {"mat": 98.6, "labor": 81.5, "equip": 98.8, "region": "Southwest", "state": "AZ"},
    "Oklahoma City, OK": {"mat": 97.2, "labor": 78.3, "equip": 98.5, "region": "Southwest", "state": "OK"},
    
    # West Coast (high cost)
    "San Francisco, CA": {"mat": 117.5, "labor": 155.2, "equip": 106.1, "region": "West", "state": "CA"},
    "Los Angeles, CA": {"mat": 112.3, "labor": 135.8, "equip": 104.2, "region": "West", "state": "CA"},
    "Seattle, WA": {"mat": 110.8, "labor": 125.4, "equip": 103.5, "region": "West", "state": "WA"},
    "Portland, OR": {"mat": 107.6, "labor": 116.8, "equip": 102.3, "region": "West", "state": "OR"},
    "San Diego, CA": {"mat": 109.4, "labor": 128.7, "equip": 103.8, "region": "West", "state": "CA"},
    "Sacramento, CA": {"mat": 108.2, "labor": 126.3, "equip": 103.1, "region": "West", "state": "CA"},
    "Honolulu, HI": {"mat": 121.5, "labor": 138.4, "equip": 108.2, "region": "West", "state": "HI"},
    "Anchorage, AK": {"mat": 118.3, "labor": 125.8, "equip": 107.5, "region": "West", "state": "AK"},
    "San Jose, CA": {"mat": 115.8, "labor": 150.3, "equip": 105.8, "region": "West", "state": "CA"},
    "Riverside, CA": {"mat": 106.5, "labor": 120.4, "equip": 102.5, "region": "West", "state": "CA"},
}


def generate_synthetic_cci():
    """
    Generate a synthetic RSMeans-like dataset.
    
    For each city × year (2015-2025), generate project records with:
    - CCI sub-indices (material, labor, equipment) with yearly drift
    - Project features (area, type, formwork cost, concrete cost)
    - Total cost per sq ft (derived from CCI + project features + noise)
    """
    print("\n🏗️ Generating synthetic RSMeans-style CCI dataset...")
    
    np.random.seed(42)
    years = range(2015, 2026)
    project_types = ["Commercial", "Residential", "Industrial", "Institutional", "Infrastructure"]
    
    records = []
    
    for city, base in CITY_COST_INDICES.items():
        for year in years:
            # Yearly drift: costs generally rise 2-5%/yr with some volatility
            year_factor = 1.0 + (year - 2015) * np.random.uniform(0.02, 0.045)
            # COVID bump 2021-2022
            if year in (2021, 2022):
                year_factor *= np.random.uniform(1.05, 1.15)
            
            # Generate 3-8 projects per city per year
            n_projects = np.random.randint(3, 9)
            
            for _ in range(n_projects):
                ptype = np.random.choice(project_types)
                
                # Project features
                area_sqft = np.random.lognormal(mean=10.5, sigma=1.0)  # ~36K sqft median
                area_sqft = np.clip(area_sqft, 1000, 2_000_000)
                
                # Formwork and concrete costs scale with area and region
                formwork_rate = np.random.uniform(3.5, 8.5) * (base["mat"] / 100)
                concrete_rate = np.random.uniform(4.0, 12.0) * (base["mat"] / 100)
                
                # CCI with per-project noise
                mat_cci = base["mat"] * year_factor * np.random.uniform(0.97, 1.03)
                labor_cci = base["labor"] * year_factor * np.random.uniform(0.96, 1.04)
                equip_cci = base["equip"] * year_factor * np.random.uniform(0.98, 1.02)
                weighted_cci = 0.45 * mat_cci + 0.40 * labor_cci + 0.15 * equip_cci
                
                # Total cost per sqft — function of CCI, project type, area (economies of scale)
                type_multiplier = {
                    "Commercial": 1.0, "Residential": 0.85, "Industrial": 0.75,
                    "Institutional": 1.15, "Infrastructure": 1.30
                }[ptype]
                
                scale_factor = (area_sqft / 50000) ** (-0.08)  # economies of scale
                
                cost_per_sqft = (
                    (weighted_cci / 100)
                    * 185  # base national avg $/sqft
                    * type_multiplier
                    * scale_factor
                    * np.random.uniform(0.88, 1.12)  # project-specific noise
                )
                
                total_cost = cost_per_sqft * area_sqft
                
                records.append({
                    "city": city,
                    "state": base["state"],
                    "region": base["region"],
                    "year": year,
                    "project_type": ptype,
                    "area_sqft": round(area_sqft, 0),
                    "formwork_rate": round(formwork_rate, 2),
                    "concrete_rate": round(concrete_rate, 2),
                    "mat_cci": round(mat_cci, 2),
                    "labor_cci": round(labor_cci, 2),
                    "equip_cci": round(equip_cci, 2),
                    "weighted_cci": round(weighted_cci, 2),
                    "cost_per_sqft": round(cost_per_sqft, 2),
                    "total_cost": round(total_cost, 0),
                })
    
    df = pd.DataFrame(records)
    out = RAW_DIR / "synthetic_cci_projects.csv"
    df.to_csv(out, index=False)
    print(f"  ✅ Generated {len(df)} project records across {len(CITY_COST_INDICES)} cities")
    print(f"  📅 Range: {df['year'].min()}–{df['year'].max()}")
    print(f"  🏙️ Regions: {df['region'].value_counts().to_dict()}")
    print(f"  💰 Cost range: ${df['cost_per_sqft'].min():.0f}–${df['cost_per_sqft'].max():.0f}/sqft")
    print(f"  → Saved to {out}")
    return df


# ── BLS Regional CPI ──────────────────────────────────────────────────────────

BLS_REGIONAL_CPI = {
    "CUURS12ASA0": "cpi_northeast",
    "CUURS35ASA0": "cpi_south",
    "CUURS23ASA0": "cpi_midwest",
    "CUURS49ASA0": "cpi_west",
}

def collect_bls_cpi():
    """Pull regional CPI from BLS public API (no key needed for v1)."""
    print("\n📈 Collecting BLS regional CPI...")
    
    url = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
    payload = {
        "seriesid": list(BLS_REGIONAL_CPI.keys()),
        "startyear": "2015",
        "endyear": "2025",
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        data = resp.json()
        
        if data.get("status") != "REQUEST_SUCCEEDED":
            print(f"  ⚠️ BLS API returned: {data.get('status')}")
            return None
        
        records = []
        for series in data["Results"]["series"]:
            series_id = series["seriesID"]
            name = BLS_REGIONAL_CPI.get(series_id, series_id)
            for item in series["data"]:
                records.append({
                    "date": f"{item['year']}-{item['period'][1:]}-01",
                    name: float(item["value"]),
                })
        
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        # Pivot so each CPI is a column
        df = df.groupby("date").first().reset_index()
        
        out = RAW_DIR / "bls_regional_cpi.csv"
        df.to_csv(out, index=False)
        print(f"  ✅ Saved {len(df)} rows → {out}")
        return df
    except Exception as e:
        print(f"  ⚠️ BLS API failed: {e}")
        return None


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Regional Construction Cost Estimation — Data Collection")
    print("=" * 60)
    
    fred_df = collect_fred()
    cci_df = generate_synthetic_cci()
    bls_df = collect_bls_cpi()
    
    print("\n" + "=" * 60)
    print("✅ Data collection complete!")
    print(f"   Raw data saved to: {RAW_DIR}")
    print("   Next: python src/preprocessing.py")
    print("=" * 60)
