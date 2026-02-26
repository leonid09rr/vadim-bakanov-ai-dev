#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["polars"]
# ///
"""
Preprocess keyword data: merge, filter, calculate scores.

Usage: uv run preprocess.py config.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import polars as pl


def log(msg: str):
    """Print with timestamp and flush."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def calculate_score(volume: int, difficulty: int) -> float:
    """Calculate keyword opportunity score."""
    return (volume * 100) / (difficulty + 1)


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run preprocess.py config.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    with open(config_path) as f:
        config = json.load(f)

    project_dir = config_path.parent
    exclude_patterns = config.get("exclude_patterns", [])
    max_position = config.get("max_position", 10)

    raw_dir = project_dir / ".cache" / "raw"
    output_dir = project_dir / ".cache" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all raw JSON files
    json_files = list(raw_dir.glob("*-keywords.json"))

    if not json_files:
        print(f"ERROR: No keyword files found in {raw_dir}")
        sys.exit(1)

    log(f"Loading {len(json_files)} keyword files...")

    all_keywords = []
    for json_file in json_files:
        with open(json_file) as f:
            keywords = json.load(f)
            all_keywords.extend(keywords)

    log(f"Total records: {len(all_keywords):,}")

    # Convert to DataFrame
    df = pl.DataFrame(all_keywords)

    # Filter by position (only keep keywords where competitor ranks in top N)
    before_pos = len(df)
    df = df.filter(pl.col("position") <= max_position)
    log(f"Position filter (top {max_position}): {before_pos:,} → {len(df):,}")

    # Normalize keywords
    df = df.with_columns(pl.col("keyword").str.to_lowercase().str.strip_chars().alias("keyword"))

    # Filter by exclusion patterns
    if exclude_patterns:
        pattern = "|".join(exclude_patterns)
        mask = df["keyword"].str.contains(f"(?i){pattern}")
        filtered_out = df.filter(mask)
        df = df.filter(~mask)

        if len(filtered_out) > 0:
            filtered_out.write_csv(output_dir / "filtered-out.csv")
            log(f"Filtered out: {len(filtered_out):,} (patterns: {', '.join(exclude_patterns)})")

    log(f"Remaining: {len(df):,} records")

    # Calculate scores
    df = df.with_columns(
        ((pl.col("search_volume") * 100) / (pl.col("keyword_difficulty") + 1)).alias("score")
    )

    # Sort by score descending
    df = df.sort("score", descending=True)

    # Save full dataset
    df.write_csv(output_dir / "all-keywords.csv")

    # Extract unique keywords for embedding
    unique_keywords = df["keyword"].unique().to_list()
    with open(output_dir / "unique-keywords.txt", "w") as f:
        for kw in unique_keywords:
            f.write(f"{kw}\n")

    # Count unique URLs (for cluster count baseline)
    unique_urls = df["ranked_url"].n_unique()

    # Summary stats
    log("Summary:")
    print(f"  Unique keywords: {len(unique_keywords):,}", flush=True)
    print(f"  Unique URLs: {unique_urls:,}", flush=True)
    print(f"  Recommended initial k: {max(100, min(500, unique_urls))}", flush=True)

    # Top keywords by score
    print("\nTop 10 keywords by score:", flush=True)
    top_10 = df.unique(subset=["keyword"]).head(10)
    for row in top_10.iter_rows(named=True):
        print(f"  {row['score']:,.0f} | {row['keyword']} (vol: {row['search_volume']}, diff: {row['keyword_difficulty']})", flush=True)

    print(f"\nSaved to: {output_dir}/", flush=True)
    print(f"  - all-keywords.csv", flush=True)
    print(f"  - unique-keywords.txt", flush=True)
    if exclude_patterns:
        print(f"  - filtered-out.csv", flush=True)


if __name__ == "__main__":
    main()
