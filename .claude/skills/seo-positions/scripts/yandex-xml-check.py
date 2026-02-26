# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx", "lxml"]
# ///
"""
Yandex XML API position checker.

Checks where a domain ranks in Yandex search results for given keywords.
Uses the free Yandex XML API (xml.yandex.ru).

Usage:
    uv run yandex-xml-check.py --domain example.com --keywords "kw1,kw2" --region 213

Environment variables:
    YANDEX_XML_USER - Yandex XML username
    YANDEX_XML_KEY  - Yandex XML API key

Get credentials at: https://xml.yandex.ru/
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

import httpx
from lxml import etree


def check_position(
    keyword: str,
    domain: str,
    user: str,
    key: str,
    region: int = 213,
    max_results: int = 100,
) -> dict:
    """Query Yandex XML and find domain position for a keyword."""

    url = (
        f"https://yandex.ru/search/xml"
        f"?user={user}"
        f"&key={key}"
        f"&query={quote(keyword)}"
        f"&lr={region}"
        f"&sortby=rlv"
        f"&filter=moderate"
        f"&maxpassages=0"
        f"&groupby=attr%3D%22%22.mode%3Dflat.groups-on-page%3D{max_results}.docs-in-group%3D1"
    )

    try:
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
    except httpx.HTTPError as e:
        return {
            "keyword": keyword,
            "position": None,
            "url": None,
            "error": str(e),
        }

    try:
        root = etree.fromstring(response.content)
    except etree.XMLSyntaxError as e:
        return {
            "keyword": keyword,
            "position": None,
            "url": None,
            "error": f"XML parse error: {e}",
        }

    # Check for API errors
    error = root.find(".//error")
    if error is not None:
        return {
            "keyword": keyword,
            "position": None,
            "url": None,
            "error": error.text or "Unknown API error",
        }

    # Search through results for the domain
    position = 0
    for doc in root.findall(".//doc"):
        position += 1
        url_elem = doc.find("url")
        if url_elem is not None and url_elem.text:
            result_url = url_elem.text.lower()
            if domain.lower() in result_url:
                return {
                    "keyword": keyword,
                    "position": position,
                    "url": url_elem.text,
                    "error": None,
                }

    return {
        "keyword": keyword,
        "position": None,
        "url": None,
        "error": None,  # No error, just not found in results
    }


def main():
    parser = argparse.ArgumentParser(description="Yandex XML position checker")
    parser.add_argument("--domain", required=True, help="Domain to track (e.g., example.com)")
    parser.add_argument("--keywords", required=True, help="Comma-separated keywords")
    parser.add_argument("--region", type=int, default=213, help="Yandex region code (default: 213 = Moscow)")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    args = parser.parse_args()

    # Load env from .env.local if exists
    env_file = Path(__file__).parent.parent / ".env.local"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    user = os.environ.get("YANDEX_XML_USER")
    key = os.environ.get("YANDEX_XML_KEY")

    if not user or not key:
        print("Error: YANDEX_XML_USER and YANDEX_XML_KEY must be set.", file=sys.stderr)
        print("Set them in ~/.claude/skills/seo-positions/.env.local", file=sys.stderr)
        print("Get credentials at: https://xml.yandex.ru/", file=sys.stderr)
        sys.exit(1)

    keywords = [kw.strip() for kw in args.keywords.split(",") if kw.strip()]
    results = []

    for i, keyword in enumerate(keywords):
        print(f"[{i + 1}/{len(keywords)}] Checking: {keyword}", file=sys.stderr)
        result = check_position(keyword, args.domain, user, key, args.region)
        results.append(result)

        if result["error"]:
            print(f"  Error: {result['error']}", file=sys.stderr)
        elif result["position"]:
            print(f"  Position: {result['position']} — {result['url']}", file=sys.stderr)
        else:
            print(f"  Not found in top results", file=sys.stderr)

        # Rate limiting
        if i < len(keywords) - 1:
            time.sleep(args.delay)

    output_data = {
        "domain": args.domain,
        "region": args.region,
        "date": time.strftime("%Y-%m-%d"),
        "results": results,
    }

    output_json = json.dumps(output_data, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"\nResults saved to {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
