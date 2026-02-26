#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["polars"]
# ///
"""
Calculate opportunity scores for SEO strategies.

Usage: uv run strategy_scores.py config.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import polars as pl


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run strategy_scores.py config.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    with open(config_path) as f:
        config = json.load(f)

    project_dir = config_path.parent
    competitors_dir = project_dir / "competitors"
    processed_dir = project_dir / ".cache" / "processed"
    output_dir = project_dir / "strategies"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load keyword data
    keywords_file = processed_dir / "all-keywords.csv"
    if not keywords_file.exists():
        print(f"ERROR: Keywords file not found: {keywords_file}")
        print("Run 'preprocess' first.")
        sys.exit(1)

    print("Loading keyword data...")
    df = pl.read_csv(keywords_file)

    # Scan competitors directory for strategies
    print("Scanning competitor strategies...")
    strategy_data = defaultdict(lambda: {
        "urls": set(),
        "competitors": set(),
    })

    for comp_dir in competitors_dir.iterdir():
        if not comp_dir.is_dir():
            continue

        domain = comp_dir.name

        for strategy_file in comp_dir.glob("*.json"):
            # Skip homepage.json
            if strategy_file.name == "homepage.json":
                continue

            strategy_name = strategy_file.stem

            with open(strategy_file) as f:
                data = json.load(f)

            urls = data.get("urls", [])
            strategy_data[strategy_name]["urls"].update(urls)
            strategy_data[strategy_name]["competitors"].add(domain)

    print(f"Found {len(strategy_data)} strategies")
    print()

    # Calculate scores for each strategy
    results = []

    for strategy_name, data in strategy_data.items():
        urls = list(data["urls"])
        competitors = sorted(data["competitors"])

        if not urls:
            continue

        # Filter keywords for URLs in this strategy
        strategy_df = df.filter(pl.col("ranked_url").is_in(urls))

        if len(strategy_df) == 0:
            total_score = 0
            unique_keywords = 0
        else:
            total_score = strategy_df["score"].sum()
            unique_keywords = strategy_df["keyword"].n_unique()

        results.append({
            "name": strategy_name,
            "total_score": float(total_score),
            "unique_keywords": int(unique_keywords),
            "total_urls": len(urls),
            "competitors_using": len(competitors),
            "competitors": competitors,
        })

    # Sort by score descending
    results.sort(key=lambda x: -x["total_score"])

    # Save to JSON
    output_file = output_dir / "strategy_scores.json"
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_strategies": len(results),
        "strategies": results,
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Saved: {output_file}")
    print()

    # Print table
    print("=" * 100)
    print("STRATEGY OPPORTUNITY RANKING")
    print("=" * 100)
    print()
    print(f"{'Rank':<6} {'Strategy':<30} {'Score':>15} {'Keywords':>10} {'URLs':>8} {'Competitors':>12}")
    print("-" * 100)

    for idx, strategy in enumerate(results, 1):
        score_str = f"{strategy['total_score']:,.0f}"
        print(
            f"{idx:<6} "
            f"{strategy['name']:<30} "
            f"{score_str:>15} "
            f"{strategy['unique_keywords']:>10} "
            f"{strategy['total_urls']:>8} "
            f"{strategy['competitors_using']:>12}"
        )

    print("-" * 100)
    print()

    # Summary
    print("COMPETITOR USAGE:")
    print()
    for strategy in results:
        comp_count = strategy["competitors_using"]
        comp_list = ", ".join(strategy["competitors"][:3])
        if len(strategy["competitors"]) > 3:
            comp_list += f", +{len(strategy['competitors']) - 3} more"

        print(f"  {strategy['name']:<30} ({comp_count}/10): {comp_list}")

    print()
    print("=" * 100)


if __name__ == "__main__":
    main()
