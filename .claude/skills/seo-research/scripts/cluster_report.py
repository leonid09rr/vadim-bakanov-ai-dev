# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Cluster report - show summary of multiple clusters at once.

Usage:
    uv run cluster_report.py cluster1.json cluster2.json ... [--top N]
"""

import json
import sys
from pathlib import Path


def load_cluster(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def format_cluster(data: dict, top_n: int = 15) -> str:
    """Format single cluster for report."""
    name = data.get("name", "unknown")
    index = data.get("index", "?")
    score = data.get("cluster_score", 0)
    stats = data.get("stats", {})
    total_volume = stats.get("total_volume", 0)
    keywords = data.get("keywords", [])

    # Get unique domains from competitors
    domains = set()
    for kw in keywords:
        for comp in kw.get("competitors", []):
            if comp.get("domain"):
                domains.add(comp["domain"].replace(".com", "").replace(".ai", "").replace(".app", "")[:12])

    lines = []
    lines.append(f"#{index} {name} | score:{score/1_000_000:.1f}M | kw:{len(keywords)} | vol:{total_volume:,}")
    lines.append("-" * 70)

    for kw in keywords[:top_n]:
        keyword = kw.get("keyword", "")[:40]
        volume = kw.get("volume", 0)
        # Get first competitor domain
        comps = kw.get("competitors", [])
        domain = comps[0]["domain"][:12] if comps else ""
        domain = domain.replace(".com", "").replace(".ai", "").replace(".app", "")
        lines.append(f"  {keyword:<40} {volume:>6}  {domain}")

    if len(keywords) > top_n:
        lines.append(f"  ... +{len(keywords) - top_n} more")

    lines.append("")
    lines.append(f"Domains: {', '.join(sorted(domains))}")

    return "\n".join(lines)


def main():
    args = sys.argv[1:]

    # Parse --top flag
    top_n = 15
    if "--top" in args:
        idx = args.index("--top")
        top_n = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    if not args:
        print("Usage: cluster_report.py <cluster1.json> [cluster2.json ...] [--top N]")
        print()
        print("Example:")
        print("  cluster_report.py 4-dictation.json 5-whisper.json 10-iphone.json")
        sys.exit(1)

    # Load and display each cluster
    for i, path_str in enumerate(args):
        path = Path(path_str)
        if not path.exists():
            print(f"[SKIP] File not found: {path}")
            continue

        try:
            data = load_cluster(path)
            print(format_cluster(data, top_n))
            if i < len(args) - 1:
                print()
                print("=" * 70)
                print()
        except Exception as e:
            print(f"[ERROR] {path}: {e}")


if __name__ == "__main__":
    main()
