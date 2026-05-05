"""
RSMeans CCI Calculator — Compute City Cost Indices from RSMeans Online data.

How to use:
  1. In RSMeans Online, go to "Search Data"
  2. Pick a common line item (e.g., concrete footing)
  3. Record the cost at "National Average" location
  4. Change the Location dropdown to each city, record the cost
  5. Paste the data into the CSV template below
  6. Run this script to compute CCI and update the project data

Input CSV format (rsmeans_raw_costs.csv):
  city,state,region,year,line_item,national_material,national_labor,national_equipment,city_material,city_labor,city_equipment

Output: data/raw/real_cci_from_rsmeans.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ── The 50 cities we need (matching the existing synthetic data) ──────────────

CITIES = {
    # Northeast
    "New York": {"state": "NY", "region": "Northeast"},
    "Boston": {"state": "MA", "region": "Northeast"},
    "Philadelphia": {"state": "PA", "region": "Northeast"},
    "Newark": {"state": "NJ", "region": "Northeast"},
    "Hartford": {"state": "CT", "region": "Northeast"},
    "Pittsburgh": {"state": "PA", "region": "Northeast"},
    "Providence": {"state": "RI", "region": "Northeast"},
    "Buffalo": {"state": "NY", "region": "Northeast"},
    "Washington": {"state": "DC", "region": "Northeast"},
    "Baltimore": {"state": "MD", "region": "Northeast"},
    # Southeast
    "Atlanta": {"state": "GA", "region": "Southeast"},
    "Miami": {"state": "FL", "region": "Southeast"},
    "Charlotte": {"state": "NC", "region": "Southeast"},
    "Nashville": {"state": "TN", "region": "Southeast"},
    "Orlando": {"state": "FL", "region": "Southeast"},
    "Tampa": {"state": "FL", "region": "Southeast"},
    "Raleigh": {"state": "NC", "region": "Southeast"},
    "Charleston": {"state": "SC", "region": "Southeast"},
    "Richmond": {"state": "VA", "region": "Southeast"},
    "Jacksonville": {"state": "FL", "region": "Southeast"},
    # Midwest
    "Chicago": {"state": "IL", "region": "Midwest"},
    "Detroit": {"state": "MI", "region": "Midwest"},
    "Minneapolis": {"state": "MN", "region": "Midwest"},
    "Columbus": {"state": "OH", "region": "Midwest"},
    "Indianapolis": {"state": "IN", "region": "Midwest"},
    "Kansas City": {"state": "MO", "region": "Midwest"},
    "Milwaukee": {"state": "WI", "region": "Midwest"},
    "Cincinnati": {"state": "OH", "region": "Midwest"},
    "Cleveland": {"state": "OH", "region": "Midwest"},
    "St. Louis": {"state": "MO", "region": "Midwest"},
    # Southwest
    "Dallas": {"state": "TX", "region": "Southwest"},
    "Houston": {"state": "TX", "region": "Southwest"},
    "Phoenix": {"state": "AZ", "region": "Southwest"},
    "San Antonio": {"state": "TX", "region": "Southwest"},
    "Austin": {"state": "TX", "region": "Southwest"},
    "Denver": {"state": "CO", "region": "Southwest"},
    "Las Vegas": {"state": "NV", "region": "Southwest"},
    "Albuquerque": {"state": "NM", "region": "Southwest"},
    "Tucson": {"state": "AZ", "region": "Southwest"},
    "Oklahoma City": {"state": "OK", "region": "Southwest"},
    # West
    "San Francisco": {"state": "CA", "region": "West"},
    "Los Angeles": {"state": "CA", "region": "West"},
    "Seattle": {"state": "WA", "region": "West"},
    "Portland": {"state": "OR", "region": "West"},
    "San Diego": {"state": "CA", "region": "West"},
    "Sacramento": {"state": "CA", "region": "West"},
    "Honolulu": {"state": "HI", "region": "West"},
    "Anchorage": {"state": "AK", "region": "West"},
    "San Jose": {"state": "CA", "region": "West"},
    "Riverside": {"state": "CA", "region": "West"},
}


def generate_input_template():
    """Generate a blank CSV template for manual data entry from RSMeans Online."""
    template_path = RAW_DIR / "rsmeans_input_template.csv"

    rows = []
    header = (
        "city,state,region,year,line_item,"
        "national_material,national_labor,national_equipment,"
        "city_material,city_labor,city_equipment"
    )

    # Pre-fill city/state/region, leave costs blank
    for city, info in CITIES.items():
        rows.append(f"{city},{info['state']},{info['region']},2018,concrete_footing,,,,,, ")

    with open(template_path, "w") as f:
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")

    print(f"Template saved: {template_path}")
    print(f"  {len(CITIES)} cities to fill in")
    print()
    print("Instructions:")
    print("  1. Open RSMeans Online → Search Data")
    print("  2. Set Cost Data = 'Commercial New Construction'")
    print("  3. Expand '3 Concrete' → find a standard footing line item")
    print("  4. Set Location = 'National Average', record Bare Material, Bare Labor, Bare Equipment")
    print("  5. Change Location to each city, record the same 3 values")
    print("  6. Fill in the CSV and run: python rsmeans_cci_calculator.py --compute")
    print()
    print("Shortcut: You can use fewer line items (even just 1) and fewer cities.")
    print("  More line items = more accurate CCI. 3-5 line items across divisions is ideal.")

    return template_path


def compute_cci_from_raw(input_path=None):
    """Compute CCI from raw RSMeans cost data."""
    if input_path is None:
        input_path = RAW_DIR / "rsmeans_input_template.csv"

    print(f"Loading raw RSMeans data from: {input_path}")
    df = pd.read_csv(input_path)

    # Clean up whitespace
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()

    # Drop rows with missing cost data
    cost_cols = ["national_material", "national_labor", "national_equipment",
                 "city_material", "city_labor", "city_equipment"]
    df[cost_cols] = df[cost_cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=cost_cols)

    if len(df) == 0:
        print("ERROR: No valid cost data found. Fill in the template first.")
        return None

    print(f"  Found {len(df)} valid cost entries across {df['city'].nunique()} cities")

    # Compute per-line-item CCI
    df["mat_cci"] = (df["city_material"] / df["national_material"]) * 100
    df["labor_cci"] = (df["city_labor"] / df["national_labor"]) * 100
    df["equip_cci"] = (df["city_equipment"] / df["national_equipment"]) * 100

    # Average across line items per city/year (if multiple line items provided)
    cci = df.groupby(["city", "state", "region", "year"]).agg(
        mat_cci=("mat_cci", "mean"),
        labor_cci=("labor_cci", "mean"),
        equip_cci=("equip_cci", "mean"),
        n_line_items=("line_item", "count"),
    ).reset_index()

    # Compute weighted CCI (standard RSMeans weighting: 45% mat, 40% labor, 15% equip)
    cci["weighted_cci"] = 0.45 * cci["mat_cci"] + 0.40 * cci["labor_cci"] + 0.15 * cci["equip_cci"]

    # Round for readability
    for col in ["mat_cci", "labor_cci", "equip_cci", "weighted_cci"]:
        cci[col] = cci[col].round(1)

    # Save
    out_path = RAW_DIR / "real_cci_from_rsmeans.csv"
    cci.to_csv(out_path, index=False)

    print(f"\nCCI computed for {len(cci)} city-year combinations")
    print(f"Saved: {out_path}")
    print(f"\nSample:")
    print(cci.head(10).to_string(index=False))

    # Summary by region
    print(f"\nRegion averages:")
    region_avg = cci.groupby("region")[["mat_cci", "labor_cci", "equip_cci", "weighted_cci"]].mean()
    print(region_avg.round(1).to_string())

    return cci


def compute_cci_from_sqft_estimator(input_path=None):
    """
    Alternative: compute CCI from Square Foot Estimator data.

    If you use the Square Foot Estimator tab instead of Search Data,
    the input CSV format is simpler:

    city,state,region,year,building_type,national_cost_per_sqft,city_cost_per_sqft

    This gives you a single weighted CCI per city (not broken into mat/labor/equip).
    """
    if input_path is None:
        input_path = RAW_DIR / "rsmeans_sqft_costs.csv"

    print(f"Loading Square Foot Estimator data from: {input_path}")
    df = pd.read_csv(input_path)

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()

    df["national_cost_per_sqft"] = pd.to_numeric(df["national_cost_per_sqft"], errors="coerce")
    df["city_cost_per_sqft"] = pd.to_numeric(df["city_cost_per_sqft"], errors="coerce")
    df = df.dropna(subset=["national_cost_per_sqft", "city_cost_per_sqft"])

    if len(df) == 0:
        print("ERROR: No valid data found.")
        return None

    # CCI = city / national * 100
    df["weighted_cci"] = (df["city_cost_per_sqft"] / df["national_cost_per_sqft"]) * 100

    # Average across building types per city
    cci = df.groupby(["city", "state", "region", "year"]).agg(
        weighted_cci=("weighted_cci", "mean"),
        avg_cost_per_sqft=("city_cost_per_sqft", "mean"),
        n_building_types=("building_type", "count"),
    ).reset_index()

    cci["weighted_cci"] = cci["weighted_cci"].round(1)
    cci["avg_cost_per_sqft"] = cci["avg_cost_per_sqft"].round(2)

    out_path = RAW_DIR / "real_cci_from_sqft.csv"
    cci.to_csv(out_path, index=False)

    print(f"\nCCI computed for {len(cci)} city-year combinations")
    print(f"Saved: {out_path}")
    print(f"\nSample:")
    print(cci.head(10).to_string(index=False))

    return cci


def generate_sqft_template():
    """Generate template for Square Foot Estimator data entry."""
    template_path = RAW_DIR / "rsmeans_sqft_template.csv"

    building_types = ["Commercial", "Residential", "Industrial", "Institutional"]
    rows = []
    header = "city,state,region,year,building_type,national_cost_per_sqft,city_cost_per_sqft"

    for city, info in CITIES.items():
        for btype in building_types:
            rows.append(f"{city},{info['state']},{info['region']},2018,{btype},,")

    with open(template_path, "w") as f:
        f.write(header + "\n")
        for row in rows:
            f.write(row + "\n")

    print(f"Template saved: {template_path}")
    print(f"  {len(CITIES)} cities x {len(building_types)} building types = {len(rows)} rows")
    print()
    print("Instructions:")
    print("  1. Open RSMeans Online → Square Foot Estimator tab")
    print("  2. Select a building type (e.g., 'Office, 5-10 Story')")
    print("  3. Set Location = 'National Average', record the $/sqft total")
    print("  4. Change Location to each city, record the $/sqft total")
    print("  5. Repeat for each building type")
    print("  6. Run: python rsmeans_cci_calculator.py --compute-sqft")

    return template_path


if __name__ == "__main__":
    import sys

    if "--compute" in sys.argv:
        compute_cci_from_raw()
    elif "--compute-sqft" in sys.argv:
        compute_cci_from_sqft_estimator()
    elif "--template-sqft" in sys.argv:
        generate_sqft_template()
    else:
        # Default: generate the line-item template
        generate_input_template()
        print("\n" + "=" * 60)
        print("Also generating Square Foot Estimator template (easier method):")
        print("=" * 60 + "\n")
        generate_sqft_template()
