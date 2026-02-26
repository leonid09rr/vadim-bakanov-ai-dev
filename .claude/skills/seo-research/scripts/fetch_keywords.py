#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Fetch ranked keywords from DataForSEO API for competitor domains.

Usage: uv run fetch_keywords.py config.json
"""

import json
import os
import sys
import base64
from pathlib import Path
from time import sleep

import requests

API_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live"


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


API_MAX_LIMIT = 1000  # DataForSEO max per request


def fetch_keywords_page(domain: str, params: dict, offset: int = 0) -> tuple[list[dict], int]:
    """Fetch a single page of ranked keywords. Returns (results, total_count)."""
    headers = {
        "Authorization": get_auth_header(),
        "Content-Type": "application/json",
    }

    # Build filters - position filter only (search_volume filter not supported by API)
    filters = []

    # Add position filter if max_position is specified
    max_position = params.get("max_position")
    if max_position:
        filters.append(["ranked_serp_element.serp_item.rank_absolute", "<=", max_position])

    payload = [
        {
            "target": domain,
            "language_code": params.get("language_code", "en"),
            "location_code": params.get("location_code", 2840),
            "limit": min(params.get("limit", API_MAX_LIMIT), API_MAX_LIMIT),
            "offset": offset,
            "order_by": ["keyword_data.keyword_info.search_volume,desc"],
            "filters": filters,
        }
    ]

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()

    if data.get("status_code") != 20000:
        return [], 0

    results = []
    total_count = 0
    tasks = data.get("tasks", [])

    for task in tasks:
        if task.get("status_code") != 20000:
            continue

        result_data = task.get("result", [{}])[0] if task.get("result") else {}
        total_count = result_data.get("total_count", 0)
        items = result_data.get("items") or []

        for item in items:
            kw_data = item.get("keyword_data", {})
            kw_info = kw_data.get("keyword_info", {})

            results.append(
                {
                    "keyword": kw_data.get("keyword", ""),
                    "search_volume": kw_info.get("search_volume", 0),
                    "keyword_difficulty": kw_info.get("keyword_difficulty", 0),
                    "competition_level": kw_info.get("competition_level", ""),
                    "cpc": kw_info.get("cpc", 0),
                    "competitor": domain,
                    "ranked_url": item.get("ranked_serp_element", {})
                    .get("serp_item", {})
                    .get("url", ""),
                    "position": item.get("ranked_serp_element", {})
                    .get("serp_item", {})
                    .get("rank_absolute", 0),
                    "is_featured_snippet": item.get("ranked_serp_element", {})
                    .get("serp_item", {})
                    .get("is_featured_snippet", False),
                }
            )

    return results, total_count


def fetch_keywords(domain: str, params: dict) -> list[dict]:
    """Fetch ranked keywords for a single domain with pagination."""
    target_limit = params.get("limit", API_MAX_LIMIT)
    all_results = []
    offset = 0

    while len(all_results) < target_limit:
        page_results, total_count = fetch_keywords_page(domain, params, offset)

        if not page_results:
            break

        all_results.extend(page_results)
        offset += len(page_results)

        # Stop if we got all available or reached target
        if offset >= total_count or offset >= target_limit:
            break

        # Rate limiting between pages
        sleep(0.5)

    return all_results[:target_limit]


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run fetch_keywords.py config.json [--force]")
        sys.exit(1)

    force = "--force" in sys.argv
    config_path = Path(sys.argv[1])
    with open(config_path) as f:
        config = json.load(f)

    project_dir = config_path.parent
    competitors = config["competitors"]
    keywords_limit = config.get("keywords_per_competitor", 1000)
    max_position = config.get("max_position", 20)  # Default to top 20
    api_params = config.get("dataforseo_params", {})
    api_params["limit"] = keywords_limit  # Override with top-level setting
    api_params["max_position"] = max_position  # Add position filter

    output_dir = project_dir / ".cache" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    total_keywords = 0

    print(f"Fetching keywords for {len(competitors)} competitors (top {max_position} positions)...\n")

    for domain in competitors:
        # Check if already downloaded
        safe_name = domain.replace(".", "-")
        output_file = output_dir / f"{safe_name}-keywords.json"

        if output_file.exists() and not force:
            with open(output_file) as f:
                cached = json.load(f)
            print(f"  {domain}... CACHED ({len(cached)} keywords)")
            total_keywords += len(cached)
            continue

        print(f"  {domain}...", end=" ", flush=True)

        try:
            keywords = fetch_keywords(domain, api_params)
            count = len(keywords)
            total_keywords += count

            with open(output_file, "w") as f:
                json.dump(keywords, f, indent=2)

            print(f"{count} keywords")

            # Rate limiting - be nice to API
            sleep(1)

        except requests.RequestException as e:
            print(f"FAILED: {e}")
            continue

    print(f"\nTotal: {total_keywords} keyword records")
    print(f"Saved to: {output_dir}/")


if __name__ == "__main__":
    main()
