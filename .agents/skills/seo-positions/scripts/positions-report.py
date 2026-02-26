# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Position report generator.

Compares current and previous position data, generates a Markdown report with trends.

Usage:
    uv run positions-report.py --current positions-2026-02-23.json --previous positions-2026-02-16.json
    uv run positions-report.py --current positions-2026-02-23.json  # No comparison, just current
"""

import argparse
import json
import sys
from pathlib import Path


def load_positions(filepath: str) -> dict:
    """Load position data from JSON file."""
    data = json.loads(Path(filepath).read_text())
    return data


def build_lookup(data: dict, engine: str) -> dict[str, dict]:
    """Build keyword → position lookup from position data."""
    lookup = {}
    positions = data.get("positions", {}).get(engine, [])
    for entry in positions:
        lookup[entry["keyword"]] = entry
    return lookup


def format_change(current_pos: int | None, previous_pos: int | None) -> str:
    """Format position change as arrow indicator."""
    if current_pos is None:
        return "—"
    if previous_pos is None:
        return "NEW"
    diff = previous_pos - current_pos  # positive = improvement
    if diff > 0:
        return f"↑{diff}"
    elif diff < 0:
        return f"↓{abs(diff)}"
    return "→"


def generate_report(current: dict, previous: dict | None) -> str:
    """Generate Markdown position report."""
    domain = current["domain"]
    date = current["date"]
    prev_date = previous["date"] if previous else None

    lines = [
        f"# Position Report: {domain} — {date}",
        "",
    ]

    if prev_date:
        lines.append(f"Comparison with: {prev_date}")
        lines.append("")

    # Process each search engine
    for engine in ["google", "yandex"]:
        current_positions = current.get("positions", {}).get(engine, [])
        if not current_positions:
            continue

        prev_lookup = build_lookup(previous, engine) if previous else {}

        lines.append(f"## {engine.title()} Positions")
        lines.append("")

        has_traffic_data = any("clicks" in p for p in current_positions)
        if has_traffic_data:
            lines.append("| Keyword | Position | Change | URL | Clicks | Impressions |")
            lines.append("|---------|----------|--------|-----|--------|-------------|")
        else:
            lines.append("| Keyword | Position | Change | URL |")
            lines.append("|---------|----------|--------|-----|")

        improvements = []
        drops = []
        not_found = []
        positions_list = []

        for entry in sorted(current_positions, key=lambda x: x.get("position") or 999):
            kw = entry["keyword"]
            pos = entry.get("position")
            url = entry.get("url", "—")
            prev_entry = prev_lookup.get(kw, {})
            prev_pos = prev_entry.get("position")

            change = format_change(pos, prev_pos)
            pos_str = str(pos) if pos else "> 50"

            if has_traffic_data:
                clicks = entry.get("clicks", "—")
                impressions = entry.get("impressions", "—")
                lines.append(f"| {kw} | {pos_str} | {change} | {url} | {clicks} | {impressions} |")
            else:
                lines.append(f"| {kw} | {pos_str} | {change} | {url} |")

            if pos:
                positions_list.append(pos)

            if prev_pos and pos:
                diff = prev_pos - pos
                if diff > 0:
                    improvements.append((kw, engine, diff, prev_pos, pos))
                elif diff < 0:
                    drops.append((kw, engine, abs(diff), prev_pos, pos))

            if pos is None:
                not_found.append(kw)

        lines.append("")

        # Stats
        if positions_list:
            avg = sum(positions_list) / len(positions_list)
            in_top10 = sum(1 for p in positions_list if p <= 10)
            in_top20 = sum(1 for p in positions_list if p <= 20)

            if previous:
                prev_positions = [
                    e.get("position") for e in previous.get("positions", {}).get(engine, [])
                    if e.get("position")
                ]
                if prev_positions:
                    prev_avg = sum(prev_positions) / len(prev_positions)
                    avg_change = prev_avg - avg
                    direction = "↑" if avg_change > 0 else "↓"
                    lines.append(f"**Avg position**: {avg:.1f} (was {prev_avg:.1f}, {direction}{abs(avg_change):.1f})")
                else:
                    lines.append(f"**Avg position**: {avg:.1f}")
            else:
                lines.append(f"**Avg position**: {avg:.1f}")

            lines.append(f"**In top 10**: {in_top10}/{len(positions_list)}")
            lines.append(f"**In top 20**: {in_top20}/{len(positions_list)}")
            lines.append("")

        # Top improvements
        if improvements:
            improvements.sort(key=lambda x: x[2], reverse=True)
            lines.append("### Top Improvements")
            for kw, eng, diff, old, new in improvements[:5]:
                lines.append(f"- **{kw}** — ↑{diff} ({old} → {new})")
            lines.append("")

        # Drops
        if drops:
            drops.sort(key=lambda x: x[2], reverse=True)
            lines.append("### Drops to Watch")
            for kw, eng, diff, old, new in drops[:5]:
                lines.append(f"- **{kw}** — ↓{diff} ({old} → {new})")
            lines.append("")

        # Not found
        if not_found:
            lines.append("### Not Found (not in top 50)")
            for kw in not_found:
                lines.append(f"- {kw}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SEO position report generator")
    parser.add_argument("--current", required=True, help="Current positions JSON file")
    parser.add_argument("--previous", default=None, help="Previous positions JSON file (for comparison)")
    parser.add_argument("--output", default=None, help="Output Markdown file path")
    args = parser.parse_args()

    current = load_positions(args.current)
    previous = load_positions(args.previous) if args.previous else None

    report = generate_report(current, previous)

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
