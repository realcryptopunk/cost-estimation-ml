"""
Collect real federal construction contract data from USASpending.gov API.

Pulls awarded construction contracts (NAICS 236-237) across all US states.
This is real, publicly funded construction with actual awarded dollar amounts.

Output: data/raw/usaspending_construction.csv
"""

import requests
import pandas as pd
import time
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

# Construction NAICS codes
NAICS_CODES = [
    "236220",  # Commercial and Institutional Building Construction
    "236210",  # Industrial Building Construction
    "236115",  # New Single-Family Housing Construction
    "236116",  # New Multifamily Housing Construction
    "236117",  # New Housing For-Sale Builders
    "236118",  # Residential Remodelers
    "237110",  # Water and Sewer Line Construction
    "237120",  # Oil and Gas Pipeline Construction
    "237130",  # Power and Communication Line Construction
    "237210",  # Land Subdivision
    "237310",  # Highway, Street, and Bridge Construction
    "237990",  # Other Heavy and Civil Engineering Construction
    "238210",  # Electrical Contractors
    "238220",  # Plumbing, Heating, and Air-Conditioning
    "238910",  # Site Preparation Contractors
]

# Map NAICS to our project types
NAICS_TYPE_MAP = {
    "236220": "Commercial", "236210": "Industrial",
    "236115": "Residential", "236116": "Residential",
    "236117": "Residential", "236118": "Residential",
    "237110": "Infrastructure", "237120": "Infrastructure",
    "237130": "Infrastructure", "237210": "Infrastructure",
    "237310": "Infrastructure", "237990": "Infrastructure",
    "238210": "Commercial", "238220": "Commercial",
    "238910": "Infrastructure",
}

STATE_REGION = {
    "CT": "Northeast", "DC": "Northeast", "DE": "Northeast", "MA": "Northeast",
    "MD": "Northeast", "ME": "Northeast", "NH": "Northeast", "NJ": "Northeast",
    "NY": "Northeast", "PA": "Northeast", "RI": "Northeast", "VT": "Northeast",
    "AL": "Southeast", "AR": "Southeast", "FL": "Southeast", "GA": "Southeast",
    "KY": "Southeast", "LA": "Southeast", "MS": "Southeast", "NC": "Southeast",
    "SC": "Southeast", "TN": "Southeast", "VA": "Southeast", "WV": "Southeast",
    "IA": "Midwest", "IL": "Midwest", "IN": "Midwest", "KS": "Midwest",
    "MI": "Midwest", "MN": "Midwest", "MO": "Midwest", "NE": "Midwest",
    "ND": "Midwest", "OH": "Midwest", "SD": "Midwest", "WI": "Midwest",
    "AZ": "Southwest", "CO": "Southwest", "NM": "Southwest", "NV": "Southwest",
    "OK": "Southwest", "TX": "Southwest", "UT": "Southwest",
    "AK": "West", "CA": "West", "HI": "West", "ID": "West",
    "MT": "West", "OR": "West", "WA": "West", "WY": "West",
}


def fetch_page(page, year_start, year_end, min_amount=50000, max_amount=50000000):
    """Fetch one page of results from USASpending API."""
    resp = requests.post(
        "https://api.usaspending.gov/api/v2/search/spending_by_award/",
        json={
            "filters": {
                "naics_codes": {"require": NAICS_CODES},
                "time_period": [{"start_date": f"{year_start}-01-01",
                                 "end_date": f"{year_end}-12-31"}],
                "award_type_codes": ["A", "B", "C", "D"],
                "award_amounts": [{"lower_bound": min_amount, "upper_bound": max_amount}],
            },
            "fields": [
                "Award ID", "Recipient Name", "Award Amount",
                "Description", "Start Date", "End Date",
                "Awarding Agency", "Place of Performance State Code",
                "Place of Performance City Name", "NAICS Code",
            ],
            "limit": 100,
            "page": page,
            "sort": "Start Date",
            "order": "desc",
        },
        timeout=30,
    )
    return resp.json()


def collect_usaspending():
    """Pull construction contracts from USASpending API."""
    print("=" * 60)
    print("COLLECTING FEDERAL CONSTRUCTION CONTRACTS (USASpending.gov)")
    print("=" * 60)

    all_records = []

    # Pull data in year chunks to avoid API limits
    year_ranges = [(2020, 2021), (2022, 2023), (2024, 2025)]

    for year_start, year_end in year_ranges:
        print(f"\n  Fetching {year_start}-{year_end}...", end="", flush=True)
        page = 1
        page_count = 0

        while page <= 50:  # max 50 pages = 5000 records per range
            try:
                data = fetch_page(page, year_start, year_end)
                results = data.get("results", [])
                if not results:
                    break

                for r in results:
                    state = r.get("Place of Performance State Code", "")
                    naics = r.get("NAICS Code") or ""
                    amount = r.get("Award Amount", 0) or 0

                    if state and state in STATE_REGION and amount > 0:
                        all_records.append({
                            "award_id": r.get("Award ID", ""),
                            "recipient": r.get("Recipient Name", ""),
                            "award_amount": amount,
                            "description": r.get("Description", ""),
                            "start_date": r.get("Start Date", ""),
                            "end_date": r.get("End Date", ""),
                            "agency": r.get("Awarding Agency", ""),
                            "state": state,
                            "city": r.get("Place of Performance City Name", "") or "",
                            "naics": naics,
                            "project_type": NAICS_TYPE_MAP.get(naics, "Infrastructure"),
                            "region": STATE_REGION.get(state, "Unknown"),
                        })

                page_count += 1
                page += 1
                time.sleep(0.3)  # rate limit

            except Exception as e:
                print(f" error on page {page}: {e}")
                break

        print(f" {page_count} pages, {len([r for r in all_records if year_start <= int(r.get('start_date','2000')[:4]) <= year_end])} contracts")

    if not all_records:
        print("  No records collected!")
        return None

    df = pd.DataFrame(all_records)
    df["year"] = pd.to_datetime(df["start_date"], errors="coerce").dt.year
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    # Deduplicate
    df = df.drop_duplicates(subset=["award_id"])

    print(f"\n  Total: {len(df)} unique contracts")
    print(f"  States: {df['state'].nunique()}")
    print(f"  Years: {df['year'].min()}-{df['year'].max()}")
    print(f"  Amount range: ${df['award_amount'].min():,.0f} - ${df['award_amount'].max():,.0f}")
    print(f"  Median: ${df['award_amount'].median():,.0f}")

    # Summary by region
    print(f"\n  By region:")
    for region, group in df.groupby("region"):
        print(f"    {region}: {len(group)} contracts, median ${group['award_amount'].median():,.0f}")

    # Summary by project type
    print(f"\n  By type:")
    for ptype, group in df.groupby("project_type"):
        print(f"    {ptype}: {len(group)} contracts")

    # Save
    out_path = RAW_DIR / "usaspending_construction.csv"
    df.to_csv(out_path, index=False)
    print(f"\n  Saved: {out_path}")

    return df


if __name__ == "__main__":
    collect_usaspending()
