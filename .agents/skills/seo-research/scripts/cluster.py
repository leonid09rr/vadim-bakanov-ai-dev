#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scikit-learn", "polars"]
# ///
"""
K-means clustering with automatic tuning and ranked export.

Usage: uv run cluster.py config.json [--k N]
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
from sklearn.cluster import KMeans


def log(step: int, total: int, msg: str):
    """Print with step number and flush."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{step}/{total}] {msg}", flush=True)


def calculate_cluster_score(keywords_df: pl.DataFrame) -> float:
    """Calculate cluster opportunity score as sum of unique keyword scores."""
    unique = keywords_df.unique(subset=["keyword"])
    return unique["score"].sum()


def get_cluster_stats(keywords_df: pl.DataFrame) -> dict:
    """Calculate statistics for a cluster."""
    unique = keywords_df.unique(subset=["keyword"])
    return {
        "unique_keywords": len(unique),
        "total_records": len(keywords_df),
        "total_volume": int(unique["search_volume"].sum()),
        "avg_difficulty": round(unique["keyword_difficulty"].mean(), 1),
        "top_keyword": unique.row(0, named=True)["keyword"] if len(unique) > 0 else "",
    }


def generate_cluster_name(keywords_df: pl.DataFrame) -> str:
    """Generate a simple name based on top keywords."""
    unique = keywords_df.unique(subset=["keyword"]).head(5)
    top_keywords = unique["keyword"].to_list()

    all_words = []
    for kw in top_keywords:
        all_words.extend(kw.split())

    word_counts = defaultdict(int)
    for word in all_words:
        if len(word) > 2:
            word_counts[word] += 1

    sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])
    name_parts = [w[0] for w in sorted_words[:2]]

    if name_parts:
        # Remove filesystem-unsafe characters
        name = "-".join(name_parts)
        return name.replace("/", "-").replace("\\", "-").replace(":", "-")
    return "misc"


def main():
    TOTAL_STEPS = 7

    if len(sys.argv) < 2:
        print("Usage: uv run cluster.py config.json [--k N]")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    with open(config_path) as f:
        config = json.load(f)

    forced_k = None
    if "--k" in sys.argv:
        k_idx = sys.argv.index("--k")
        if k_idx + 1 < len(sys.argv):
            forced_k = int(sys.argv[k_idx + 1])

    project_dir = config_path.parent
    cluster_count = config.get("cluster_count", "auto")

    processed_dir = project_dir / ".cache" / "processed"
    embeddings_dir = project_dir / ".cache" / "embeddings"
    output_dir = project_dir / ".cache" / "clusters"

    # Clean up old cluster files before writing new ones
    if output_dir.exists():
        for f in output_dir.glob("*.json"):
            f.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Load data
    log(1, TOTAL_STEPS, "Loading keywords CSV...")
    keywords_df = pl.read_csv(processed_dir / "all-keywords.csv")
    print(f"    {len(keywords_df):,} records", flush=True)

    # Step 2: Load embeddings
    log(2, TOTAL_STEPS, "Loading embeddings cache...")
    cache = np.load(embeddings_dir / "cache.npz", allow_pickle=True)
    keyword_order = cache["keywords"].tolist()
    embeddings = cache["embeddings"]
    print(f"    {embeddings.shape[0]:,} embeddings, dim={embeddings.shape[1]}", flush=True)

    kw_to_idx = {kw: i for i, kw in enumerate(keyword_order)}

    # Step 3: Prepare unique keywords embeddings
    log(3, TOTAL_STEPS, "Preparing unique keyword embeddings...")
    unique_keywords = keywords_df.unique(subset=["keyword"])["keyword"].to_list()

    unique_embeddings = []
    missing = 0
    for kw in unique_keywords:
        if kw in kw_to_idx:
            unique_embeddings.append(embeddings[kw_to_idx[kw]])
        else:
            unique_embeddings.append(np.zeros(embeddings.shape[1]))
            missing += 1

    unique_embeddings = np.array(unique_embeddings)
    print(f"    {len(unique_keywords):,} unique keywords", flush=True)
    if missing:
        print(f"    WARNING: {missing} keywords missing embeddings", flush=True)

    # Step 4: Determine k (--k flag takes priority)
    if forced_k:
        k = forced_k
        log(4, TOTAL_STEPS, f"Using k={k} (from --k flag)")
    elif cluster_count != "auto":
        k = int(cluster_count)
        log(4, TOTAL_STEPS, f"Using k={k} (from config)")
    else:
        # Default: use unique URLs count, clamped to 100-500
        unique_urls = keywords_df["ranked_url"].n_unique()
        k = max(100, min(500, unique_urls))
        log(4, TOTAL_STEPS, f"Using k={k} (auto: based on {unique_urls} URLs)")

    # Step 5: Run K-means
    log(5, TOTAL_STEPS, f"Running K-means clustering (k={k})...")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(unique_embeddings)
    print(f"    Done", flush=True)

    # Create keyword -> cluster mapping
    keyword_to_cluster = {kw: int(label) for kw, label in zip(unique_keywords, labels)}
    keywords_df = keywords_df.with_columns(
        pl.col("keyword").replace_strict(keyword_to_cluster, default=-1).alias("cluster")
    )

    # Step 6: Calculate cluster scores and stats
    log(6, TOTAL_STEPS, "Calculating cluster scores...")
    cluster_data = []

    for cluster_id in range(k):
        cluster_keywords = keywords_df.filter(pl.col("cluster") == cluster_id)
        score = calculate_cluster_score(cluster_keywords)
        stats = get_cluster_stats(cluster_keywords)
        name = generate_cluster_name(cluster_keywords)

        cluster_data.append({
            "original_id": cluster_id,
            "name": name,
            "cluster_score": score,
            **stats,
        })

    cluster_data.sort(key=lambda x: -x["cluster_score"])
    for idx, cluster in enumerate(cluster_data):
        cluster["index"] = idx

    print(f"    {k} clusters ranked by score", flush=True)

    # Step 7: Export clusters
    log(7, TOTAL_STEPS, "Exporting cluster files...")

    cluster_index = {
        "generated_at": datetime.now().isoformat(),
        "total_clusters": k,
        "clusters": [],
    }

    for cluster in cluster_data:
        idx = cluster["index"]
        name = cluster["name"]
        score = cluster["cluster_score"]
        stats = {k: v for k, v in cluster.items() if k not in ["original_id", "index", "name", "cluster_score"]}

        original_id = cluster["original_id"]
        cluster_keywords = keywords_df.filter(pl.col("cluster") == original_id)

        # Group by keyword
        grouped = []
        for kw in cluster_keywords.unique(subset=["keyword"])["keyword"].to_list():
            kw_rows = cluster_keywords.filter(pl.col("keyword") == kw)

            competitors = [
                {
                    "domain": row["competitor"],
                    "url": row["ranked_url"],
                    "position": int(row["position"]),
                }
                for row in kw_rows.iter_rows(named=True)
            ]

            first = kw_rows.row(0, named=True)
            grouped.append({
                "keyword": kw,
                "volume": int(first["search_volume"]),
                "difficulty": int(first["keyword_difficulty"]),
                "score": float(first["score"]),
                "competitors": competitors,
            })

        grouped.sort(key=lambda x: -x["score"])

        filename = f"{idx}-{name}.json"
        cluster_file = {
            "index": idx,
            "name": name,
            "cluster_score": score,
            "stats": stats,
            "keywords": grouped,
        }

        with open(output_dir / filename, "w") as f:
            json.dump(cluster_file, f, indent=2)

        cluster_index["clusters"].append({
            "index": idx,
            "name": name,
            "cluster_score": score,
            **stats,
            "file": filename,
        })

    with open(output_dir / "cluster-index.json", "w") as f:
        json.dump(cluster_index, f, indent=2)

    print(f"\nResults:", flush=True)
    print(f"  {output_dir}/cluster-index.json", flush=True)
    print(f"  {k} cluster files\n", flush=True)

    print("Top 5 clusters by score:", flush=True)
    for c in cluster_data[:5]:
        print(f"  {c['index']}: {c['name']} (score: {c['cluster_score']:,.0f}, keywords: {c['unique_keywords']})", flush=True)


if __name__ == "__main__":
    main()
