#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["polars"]
# ///
"""
Show which clusters each URL ranks in, with top keywords per cluster.

Usage:
    uv run url_clusters.py config.json                    # All URLs
    uv run url_clusters.py config.json --url <url>        # Specific URL
    uv run url_clusters.py config.json --domain <domain>  # Filter by domain
    uv run url_clusters.py config.json --top N            # Limit URLs
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

import polars as pl


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run url_clusters.py config.json [--url URL] [--domain DOMAIN] [--top N]")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    with open(config_path) as f:
        config = json.load(f)

    # Parse optional args
    filter_url = None
    filter_domain = None
    top_n = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--url" and i + 1 < len(args):
            filter_url = args[i + 1]
            i += 2
        elif args[i] == "--domain" and i + 1 < len(args):
            filter_domain = args[i + 1]
            i += 2
        elif args[i] == "--top" and i + 1 < len(args):
            top_n = int(args[i + 1])
            i += 2
        else:
            i += 1

    project_dir = config_path.parent
    processed_dir = project_dir / ".cache" / "processed"
    clusters_dir = project_dir / ".cache" / "clusters"

    # Load keyword data
    df = pl.read_csv(processed_dir / "all-keywords.csv")

    # Load cluster index
    with open(clusters_dir / "cluster-index.json") as f:
        cluster_index = json.load(f)

    # Build keyword -> cluster mapping
    keyword_to_cluster = {}
    cluster_info = {}

    for c in cluster_index["clusters"]:
        cluster_file = clusters_dir / c["file"]
        if cluster_file.exists():
            with open(cluster_file) as f:
                cluster_data = json.load(f)

            cluster_info[c["index"]] = {
                "name": c["name"],
                "score": c["cluster_score"],
                "keywords": [(kw["keyword"], kw["volume"]) for kw in cluster_data["keywords"]]
            }

            for kw in cluster_data["keywords"]:
                keyword_to_cluster[kw["keyword"]] = c["index"]

    # Apply filters
    if filter_url:
        df = df.filter(pl.col("ranked_url") == filter_url)
    if filter_domain:
        df = df.filter(pl.col("competitor") == filter_domain)

    # Identify homepage vs content pages
    # Homepage = domain root only (e.g., https://example.com/ or https://example.com)
    df = df.with_columns(
        pl.col("ranked_url")
          .str.replace(r"https?://[^/]+/?$", "HOME")
          .alias("is_home_check")
    )
    df = df.with_columns(
        (pl.col("is_home_check") == "HOME").alias("is_homepage")
    )

    # Group by URL
    url_groups = df.group_by(["competitor", "ranked_url", "is_homepage"]).agg([
        pl.col("keyword").alias("keywords"),
        pl.col("search_volume").alias("volumes"),
        pl.col("score").sum().alias("total_score"),
    ]).sort("total_score", descending=True)

    # Apply top N limit
    if top_n:
        url_groups = url_groups.head(top_n)

    # Output
    print("# URL Cluster Analysis")
    print()
    print(f"Total URLs: {len(url_groups)}")
    print(f"Total clusters: {len(cluster_info)}")
    print()

    for row in url_groups.iter_rows(named=True):
        url = row["ranked_url"]
        is_homepage = row["is_homepage"]

        # Find which clusters this URL's keywords belong to
        url_clusters = defaultdict(list)
        for kw, vol in zip(row["keywords"], row["volumes"]):
            if kw in keyword_to_cluster:
                cluster_id = keyword_to_cluster[kw]
                url_clusters[cluster_id].append((kw, vol))

        if not url_clusters:
            continue

        # Sort clusters by total volume from this URL
        sorted_clusters = sorted(
            url_clusters.items(),
            key=lambda x: sum(v for _, v in x[1]),
            reverse=True
        )

        # Display URL (compact)
        url_short = url.replace("https://", "").replace("http://", "")
        if len(url_short) > 70:
            url_short = url_short[:67] + "..."

        page_type = "HOME" if is_homepage else "PAGE"
        print(f"## [{page_type}] {url_short}")
        print(f"Score: {row['total_score']:,.0f} | Clusters: {len(sorted_clusters)}")
        print()

        # Show clusters with all keywords (compact format)
        for cluster_id, cluster_kws in sorted_clusters[:15]:
            info = cluster_info.get(cluster_id, {})
            cluster_name = info.get("name", f"cluster-{cluster_id}")

            # Sort keywords by volume
            cluster_kws.sort(key=lambda x: -x[1])

            print(f"**{cluster_id}-{cluster_name}.json**")
            for kw, vol in cluster_kws:
                print(f"  {kw} ({vol:,})")
            print()

        print("---")
        print()


if __name__ == "__main__":
    main()
