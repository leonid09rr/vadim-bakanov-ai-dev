#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "numpy"]
# ///
"""
Generate embeddings for keywords using OpenRouter API.
Uses numpy for fast cache serialization.

Usage: uv run embed.py config.json
"""

import json
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from datetime import datetime

import numpy as np
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/embeddings"
MODEL = "intfloat/multilingual-e5-large"
BATCH_SIZE = 500
MAX_WORKERS = 10
REQUEST_TIMEOUT = 30


def log(msg: str):
    """Print with timestamp and flush."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def get_embeddings(keywords: list[str], api_key: str) -> list[list[float]]:
    """Get embeddings for a batch of keywords."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "input": keywords,
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()

    data = response.json()

    if "data" not in data:
        raise ValueError(f"Unexpected response: {data}")

    embeddings = [item["embedding"] for item in data["data"]]
    return embeddings


def process_batch(batch_num: int, keywords: list[str], api_key: str) -> tuple[int, list[str], list[list[float]], str | None]:
    """Process a single batch. Returns (batch_num, keywords, embeddings, error_msg)."""
    try:
        embeddings = get_embeddings(keywords, api_key)
        return batch_num, keywords, embeddings, None
    except requests.Timeout:
        return batch_num, keywords, [], "timeout"
    except requests.HTTPError as e:
        return batch_num, keywords, [], f"HTTP {e.response.status_code}: {e.response.text[:100]}"
    except Exception as e:
        return batch_num, keywords, [], str(e)[:100]


def load_cache(output_dir: Path) -> tuple[list[str], np.ndarray | None]:
    """Load cached keywords and embeddings from single .npz file."""
    cache_file = output_dir / "cache.npz"

    if cache_file.exists():
        data = np.load(cache_file, allow_pickle=True)
        keywords = data["keywords"].tolist()
        matrix = data["embeddings"]
        return keywords, matrix

    return [], None


def save_cache(output_dir: Path, keywords: list[str], matrix: np.ndarray):
    """Save cache atomically to single .npz file."""
    tmp_file = output_dir / "cache.tmp.npz"
    final_file = output_dir / "cache.npz"

    np.savez(tmp_file, keywords=np.array(keywords, dtype=object), embeddings=matrix)
    tmp_file.rename(final_file)


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run embed.py config.json")
        sys.exit(1)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable required")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    with open(config_path) as f:
        config = json.load(f)

    project_dir = config_path.parent
    processed_dir = project_dir / ".cache" / "processed"
    output_dir = project_dir / ".cache" / "embeddings"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load unique keywords to embed
    keywords_file = processed_dir / "unique-keywords.txt"
    if not keywords_file.exists():
        print(f"ERROR: {keywords_file} not found. Run preprocess first.")
        sys.exit(1)

    with open(keywords_file) as f:
        all_keywords = [line.strip() for line in f if line.strip()]

    log(f"Total keywords to embed: {len(all_keywords)}")

    # Load cache
    cached_keywords, cached_matrix = load_cache(output_dir)
    cached_set = set(cached_keywords)
    log(f"Cached embeddings: {len(cached_set)}")

    # Find keywords that need embedding
    to_embed = [kw for kw in all_keywords if kw not in cached_set]
    log(f"Keywords to fetch: {len(to_embed)}")

    # Collect new embeddings
    new_keywords = []
    new_embeddings = []

    if to_embed:
        # Create batches
        batches = []
        for i in range(0, len(to_embed), BATCH_SIZE):
            batch = to_embed[i : i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            batches.append((batch_num, batch))

        total_batches = len(batches)
        completed = 0
        errors = 0

        log(f"Processing {total_batches} batches ({BATCH_SIZE} keywords each, {MAX_WORKERS} workers)")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(process_batch, batch_num, kws, api_key): batch_num
                for batch_num, kws in batches
            }

            for future in as_completed(futures):
                batch_num = futures[future]
                try:
                    _, kws, embs, error = future.result(timeout=60)
                    completed += 1

                    if error:
                        errors += 1
                        log(f"  Batch {batch_num} FAILED: {error}")
                    else:
                        new_keywords.extend(kws)
                        new_embeddings.extend(embs)

                    # Progress update every 10 batches
                    if completed % 10 == 0:
                        log(f"  Progress: {completed}/{total_batches} batches, {len(new_keywords)} new, {errors} errors")

                except TimeoutError:
                    completed += 1
                    errors += 1
                    log(f"  Batch {batch_num} TIMEOUT (future)")

        log(f"  Done: {completed}/{total_batches} batches, {len(new_keywords)} new, {errors} errors")

    # Merge with cache
    if new_embeddings:
        new_matrix = np.array(new_embeddings)

        if cached_matrix is not None:
            final_keywords = cached_keywords + new_keywords
            final_matrix = np.vstack([cached_matrix, new_matrix])
        else:
            final_keywords = new_keywords
            final_matrix = new_matrix

        log(f"Saving cache: {len(final_keywords)} embeddings, shape {final_matrix.shape}")
        save_cache(output_dir, final_keywords, final_matrix)

        cached_keywords = final_keywords
        cached_matrix = final_matrix

    log(f"Done. Cache: {output_dir}/cache.npz ({len(cached_keywords)} embeddings)")


if __name__ == "__main__":
    main()
