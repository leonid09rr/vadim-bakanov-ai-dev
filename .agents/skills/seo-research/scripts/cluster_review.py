#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Cluster Review - Quick view of cluster contents.

Usage:
    uv run cluster_review.py <cluster_file.json> [--top N]
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: cluster_review.py <cluster.json> [--top N]")
        sys.exit(1)

    cluster_path = Path(sys.argv[1])
    top_n = 20

    # Parse --top flag
    if "--top" in sys.argv:
        idx = sys.argv.index("--top")
        if idx + 1 < len(sys.argv):
            top_n = int(sys.argv[idx + 1])

    if not cluster_path.exists():
        print(f"Error: {cluster_path}")
        sys.exit(1)

    with open(cluster_path) as f:
        cluster = json.load(f)

    # Header
    print(f"\n#{cluster['index']} {cluster['name']} | score:{cluster['cluster_score']/1e6:.1f}M | kw:{cluster['stats']['unique_keywords']} | vol:{cluster['stats']['total_volume']:,}")
    print("-" * 70)

    # Keywords table
    keywords = cluster.get("keywords", [])[:top_n]

    for kw in keywords:
        keyword = kw["keyword"][:35].ljust(35)
        volume = str(kw["volume"]).rjust(6)
        domains = ", ".join(c["domain"].replace(".com", "").replace(".ai", "").replace(".app", "")[:10]
                           for c in kw.get("competitors", [])[:2])
        print(f"  {keyword} {volume}  {domains}")

    total = cluster['stats']['unique_keywords']
    if total > top_n:
        print(f"  ... +{total - top_n} more")

    # Unique domains
    all_domains = set()
    for kw in cluster.get("keywords", []):
        for c in kw.get("competitors", []):
            all_domains.add(c["domain"])

    print(f"\nDomains: {', '.join(sorted(all_domains))}")


if __name__ == "__main__":
    main()
