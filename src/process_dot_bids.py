"""
Process real DOT bid tabulation data into project-level records.

Converts item-level bid data (TxDOT, etc.) into project-level summaries
that can be used to validate the ML model's predictions.

Output: data/raw/real_dot_projects.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

# Texas counties → city mapping (approximate, for major metro areas)
TX_COUNTY_CITY = {
    "Harris": "Houston", "Dallas": "Dallas", "Tarrant": "Dallas",
    "Bexar": "San Antonio", "Travis": "Austin", "El Paso": "El Paso",
    "Hidalgo": "McAllen", "Collin": "Dallas", "Denton": "Dallas",
    "Fort Bend": "Houston", "Williamson": "Austin", "Montgomery": "Houston",
    "Nueces": "Corpus Christi", "Lubbock": "Lubbock", "McLennan": "Waco",
    "Webb": "Laredo", "Galveston": "Houston", "Brazoria": "Houston",
    "Bell": "Temple", "Jefferson": "Beaumont", "Smith": "Tyler",
    "Hays": "Austin", "Brazos": "College Station", "Tom Green": "San Angelo",
    "Potter": "Amarillo", "Ector": "Odessa", "Midland": "Midland",
    "Taylor": "Abilene", "Wichita": "Wichita Falls", "Cameron": "Brownsville",
}


def process_txdot():
    """Process TxDOT bid tabulations into project-level records."""
    path = RAW_DIR / "txdot_bids_raw.csv"
    if not path.exists():
        print("TxDOT data not found. Download first.")
        return None

    print(f"Loading TxDOT bid data...")
    df = pd.read_csv(path, low_memory=False)
    print(f"  {len(df)} item-level rows")

    # Parse dates
    df["let_date"] = pd.to_datetime(df["PROJECT ACTUAL LET DATE"], errors="coerce")
    df["year"] = df["let_date"].dt.year

    # Filter to winning bids only and recent years
    df = df[df["LOW BIDDER FLAG"] == True]
    df = df[df["year"].between(2015, 2025)]
    print(f"  {len(df)} winning bid items (2015-2025)")

    # Get project-level totals (aggregate item-level bids)
    projects = df.groupby("PROJECT ID").agg(
        bid_total=("BID TOTAL AMOUNT", "first"),  # same for all items in a project
        engineer_estimate=("SEALED ENGINEER'S ESTIMATE PROJECT", "first"),
        county=("COUNTY", "first"),
        district=("DISTRICT/ DIVISION", "first"),
        year=("year", "first"),
        let_date=("let_date", "first"),
        project_type=("PROJECT TYPE", "first"),
        project_class=("PROJECT CLASSIFICATION", "first"),
        project_name=("PROJECT NAME", "first"),
        short_desc=("SHORT DESCRIPTION", "first"),
        n_items=("BID ITEM SEQUENCE NUMBER", "nunique"),
    ).reset_index()

    # Clean up
    projects["bid_total"] = pd.to_numeric(projects["bid_total"], errors="coerce")
    projects["engineer_estimate"] = pd.to_numeric(projects["engineer_estimate"], errors="coerce")
    projects = projects.dropna(subset=["bid_total"])
    projects = projects[projects["bid_total"] > 0]

    # Remove duplicates
    projects = projects.drop_duplicates(subset=["PROJECT ID"])

    # Map county to nearest city
    projects["city"] = projects["county"].map(TX_COUNTY_CITY).fillna("Other TX")
    projects["state"] = "TX"
    projects["region"] = "Southwest"

    # Map project classification to our 5 types
    type_map = {
        "Construction": "Infrastructure",
        "Maintenance": "Infrastructure",
        "Rehab": "Infrastructure",
        "Preventive Maintenance": "Infrastructure",
        "Pedestrian, Sidewalks & Curb Ramps": "Infrastructure",
        "Bridge": "Infrastructure",
        "Safety": "Infrastructure",
    }
    projects["mapped_type"] = projects["project_class"].map(type_map).fillna("Infrastructure")

    # Filter to reasonable project sizes
    projects = projects[projects["bid_total"].between(50000, 500_000_000)]

    print(f"  {len(projects)} unique projects")
    print(f"  Years: {projects['year'].min()}-{projects['year'].max()}")
    print(f"  Bid total range: ${projects['bid_total'].min():,.0f} - ${projects['bid_total'].max():,.0f}")
    print(f"  Median bid: ${projects['bid_total'].median():,.0f}")

    # Summary by year
    print(f"\n  Projects by year:")
    for year, group in projects.groupby("year"):
        print(f"    {year}: {len(group)} projects, median ${group['bid_total'].median():,.0f}")

    return projects


def save_validation_dataset(projects):
    """Save processed projects as a validation dataset."""
    if projects is None or projects.empty:
        return

    out = projects[[
        "PROJECT ID", "city", "state", "region", "year", "let_date",
        "mapped_type", "bid_total", "engineer_estimate",
        "project_name", "short_desc", "county", "district", "n_items",
    ]].copy()

    out = out.rename(columns={
        "PROJECT ID": "project_id",
        "mapped_type": "project_type",
        "let_date": "date",
    })

    # Compute cost accuracy ratio (bid vs engineer estimate)
    out["bid_to_estimate_ratio"] = out["bid_total"] / out["engineer_estimate"]

    out_path = RAW_DIR / "real_dot_projects.csv"
    out.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")
    print(f"  {len(out)} real project records with actual awarded costs")

    # Summary stats
    print(f"\n  Summary:")
    print(f"    Total projects: {len(out)}")
    print(f"    Median bid: ${out['bid_total'].median():,.0f}")
    print(f"    Mean bid: ${out['bid_total'].mean():,.0f}")
    print(f"    Bid/Estimate ratio: {out['bid_to_estimate_ratio'].median():.2f} (median)")
    print(f"\n  By county (top 10):")
    top_counties = out["county"].value_counts().head(10)
    for county, count in top_counties.items():
        median_bid = out[out["county"] == county]["bid_total"].median()
        print(f"    {county}: {count} projects, median ${median_bid:,.0f}")

    return out


if __name__ == "__main__":
    print("=" * 60)
    print("PROCESSING REAL DOT BID DATA")
    print("=" * 60)

    projects = process_txdot()
    validation = save_validation_dataset(projects)

    print("\n" + "=" * 60)
    print("Done! Real bid data ready for model validation.")
    print("=" * 60)
