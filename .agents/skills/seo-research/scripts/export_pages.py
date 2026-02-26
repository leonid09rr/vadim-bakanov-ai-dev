#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["polars"]
# ///
"""
Export competitor pages with their ranking keywords.

Usage: uv run export_pages.py config.json [--domain domain.com] [--top N]
"""

import json
import sys
from pathlib import Path

import polars as pl


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run export_pages.py config.json [--domain domain.com] [--top N]")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    with open(config_path) as f:
        config = json.load(f)

    # Parse optional args
    filter_domain = None
    top_n = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--domain" and i + 1 < len(args):
            filter_domain = args[i + 1]
            i += 2
        elif args[i] == "--top" and i + 1 < len(args):
            top_n = int(args[i + 1])
            i += 2
        else:
            i += 1

    project_dir = config_path.parent
    processed_dir = project_dir / ".cache" / "processed"

    # Load data
    df = pl.read_csv(processed_dir / "all-keywords.csv")

    # Filter by domain if specified
    if filter_domain:
        df = df.filter(pl.col("competitor") == filter_domain)

    # Identify homepages (root URLs with 3 or fewer slashes)
    df = df.with_columns(
        pl.col("ranked_url").str.replace(r"https?://", "").str.count_matches("/").alias("slash_count")
    )

    # Separate homepage and content pages
    df_homepage = df.filter(pl.col("slash_count") <= 1)
    df_content = df.filter(pl.col("slash_count") > 1)

    # Group content pages by URL
    pages = df_content.group_by(["competitor", "ranked_url"]).agg([
        pl.col("keyword").alias("keywords"),
        pl.col("search_volume").alias("volumes"),
        pl.col("score").sum().alias("total_score"),
        pl.col("keyword").n_unique().alias("keyword_count"),
    ]).sort("total_score", descending=True)

    # Apply top N limit
    if top_n:
        pages = pages.head(top_n)

    # Group by domain for output
    domains = pages["competitor"].unique().sort().to_list()

    # Output markdown format
    print("# Competitor Content Pages Analysis")
    print()
    print(f"Total content pages: {len(pages)}")
    print(f"Domains: {len(domains)}")
    print()

    for domain in domains:
        domain_pages = pages.filter(pl.col("competitor") == domain).sort("total_score", descending=True)

        if len(domain_pages) == 0:
            continue

        total_score = domain_pages["total_score"].sum()
        total_kw = domain_pages["keyword_count"].sum()

        print(f"## {domain}")
        print(f"Pages: {len(domain_pages)} | Keywords: {total_kw} | Score: {total_score:,.0f}")
        print()

        for row in domain_pages.iter_rows(named=True):
            url = row["ranked_url"]
            # Shorten URL for display
            display_url = url.replace("https://", "").replace("http://", "")
            if len(display_url) > 70:
                display_url = display_url[:67] + "..."

            print(f"### {display_url}")
            print(f"Score: {row['total_score']:,.0f} | Keywords: {row['keyword_count']}")
            print()

            # Show top 20 keywords by volume
            kw_vol = list(zip(row["keywords"], row["volumes"]))
            kw_vol.sort(key=lambda x: -x[1])

            print("| Keyword | Volume |")
            print("|---------|--------|")
            for kw, vol in kw_vol[:20]:
                print(f"| {kw} | {vol:,} |")

            if len(kw_vol) > 20:
                print(f"| ... +{len(kw_vol) - 20} more | |")
            print()

    # Summary: Homepage clusters
    if len(df_homepage) > 0:
        print("---")
        print()
        print("## Homepage Keywords Summary")
        print("(Analyze separately via clusters)")
        print()

        hp_summary = df_homepage.group_by("competitor").agg([
            pl.col("keyword").n_unique().alias("keywords"),
            pl.col("search_volume").sum().alias("volume"),
        ]).sort("volume", descending=True)

        print("| Domain | Keywords | Total Volume |")
        print("|--------|----------|--------------|")
        for row in hp_summary.iter_rows(named=True):
            print(f"| {row['competitor']} | {row['keywords']} | {row['volume']:,} |")


if __name__ == "__main__":
    main()
