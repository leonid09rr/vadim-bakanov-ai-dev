#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Fetch available locations from DataForSEO API and save as CSV.

Usage: uv run fetch_locations.py
"""

import json
import os
import sys
import base64
import csv
from pathlib import Path

import requests

API_URL = "https://api.dataforseo.com/v3/keywords_data/google/locations"


def get_auth_header() -> str:
    """Get Basic Auth header from environment variables."""
    login = os.environ.get("DATAFORSEO_LOGIN")
    password = os.environ.get("DATAFORSEO_PASSWORD")

    if not login or not password:
        print("ERROR: DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD environment variables required")
        sys.exit(1)

    credentials = f"{login}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def fetch_locations() -> list[dict]:
    """Fetch all available locations from DataForSEO Keywords Data API."""
    headers = {
        "Authorization": get_auth_header(),
    }

    # GET request to get all locations
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()

    data = response.json()

    if data.get("status_code") != 20000:
        print(f"API Error: {data.get('status_message')}")
        sys.exit(1)

    locations = []
    tasks = data.get("tasks", [])

    for task in tasks:
        if task.get("status_code") != 20000:
            continue

        result_data = task.get("result", [])
        for item in result_data:
            # Extract location info
            location_info = {
                "location_code": item.get("location_code"),
                "location_name": item.get("location_name"),
                "location_type": item.get("location_type"),
                "country_iso_code": item.get("country_iso_code"),
                "location_code_parent": item.get("location_code_parent"),
            }
            locations.append(location_info)

    return locations


def save_as_csv(locations: list[dict], output_path: Path):
    """Save locations as CSV file."""
    if not locations:
        print("No locations to save")
        return

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=locations[0].keys())
        writer.writeheader()
        writer.writerows(locations)


def save_as_json(locations: list[dict], output_path: Path):
    """Save locations as JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)


def main():
    script_dir = Path(__file__).parent
    info_dir = script_dir.parent / "info"
    info_dir.mkdir(exist_ok=True)

    print("Fetching locations from DataForSEO API...")
    locations = fetch_locations()

    print(f"Found {len(locations)} locations")

    # Save as CSV (easier to read/search)
    csv_path = info_dir / "dataforseo-locations.csv"
    save_as_csv(locations, csv_path)
    print(f"Saved CSV: {csv_path}")

    # Save as JSON (for programmatic use)
    json_path = info_dir / "dataforseo-locations.json"
    save_as_json(locations, json_path)
    print(f"Saved JSON: {json_path}")

    # Show some examples
    print("\nExample locations:")
    countries = [loc for loc in locations if loc["location_type"] == "Country"][:10]
    for loc in countries:
        print(
            f"  {loc['location_code']:6} | {loc['location_name']:30} | {loc['country_iso_code']}"
        )


if __name__ == "__main__":
    main()
