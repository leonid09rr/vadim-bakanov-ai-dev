---
name: seo-positions
description: |
  SEO position monitoring and ranking tracker. Checks where a domain ranks in Google and Yandex for target keywords. Uses free APIs (Yandex XML, Google Search Console) and optional paid tools (Ahrefs/Semrush MCP). Tracks changes over time with historical comparison.
  Use when: (1) checking current search positions for keywords, (2) tracking ranking changes over time, (3) generating position reports, (4) user says "check positions", "track rankings", "monitor SEO", "position report", "проверь позиции", "мониторинг позиций", "отчёт по позициям".
---

# SEO Position Monitoring

Check and track search rankings in Google and Yandex.

## Step 1: Gather Parameters

Ask user (use AskUserQuestion):

1. **Domain**: What domain to track? (e.g., example.com)
2. **Keywords**: List of target keywords, OR "use previous research" (load from seo-content output)
3. **Locale**: Target market? (Russia, USA, global)
4. **Search engines**: Google, Yandex, or both?

## Step 2: Detect Available Data Sources

Read `~/.claude/skills/_seo-shared/references/mcp-integration.md` for detection.

Check availability (in priority order):

### For Google positions:
1. **Google Search Console MCP** → `search_analytics` (real data, free)
2. **Ahrefs MCP** → `get_serp_overview` (paid)
3. **Semrush MCP** → keyword position data (paid)
4. **WebSearch spot-check** → search and scan results (free, approximate)

### For Yandex positions:
1. **Yandex XML script** → `scripts/yandex-xml-check.py` (free, requires API key)
2. **WebSearch spot-check** → search yandex.ru and scan results (free, approximate)

## Step 3: Check Positions

### Google Search Console MCP (preferred for Google)
If available, call `search_analytics`:
- Site URL, date range (last 28 days)
- Filter by target keywords
- Extract: average position, clicks, impressions, CTR per keyword

### Yandex XML (preferred for Yandex)
If YANDEX_XML_USER and YANDEX_XML_KEY are set:

```bash
cd ~/.claude/skills/seo-positions
uv run scripts/yandex-xml-check.py --domain {domain} --keywords "kw1,kw2,kw3" --region 213
```

Region codes: 213 = Moscow, 2 = Saint Petersburg, 0 = all Russia.
The script outputs JSON with positions for each keyword.

### Ahrefs/Semrush MCP (if available)
- Ahrefs: `get_serp_overview` for each keyword → find domain position
- Semrush: organic position data for domain + keyword

### WebSearch Spot-Check (fallback — always works)
For each keyword:
1. WebSearch: `"{keyword}"` (with site:{domain} to check if domain appears)
2. WebSearch: `"{keyword}"` (without site: to estimate position from results)
3. Check if domain URL appears in results
4. Estimate position (1-10 if on first page, 10-20 if on second, etc.)

Note: WebSearch spot-check is approximate. For accurate data, set up GSC or Yandex XML.

## Step 4: Load History

Check for previous position reports in the project:
- Glob: `**/seo-positions-*.json` in project directory
- Or ask user for previous report path

If history exists → compare current vs previous for trend arrows (↑↓→).

## Step 5: Save Current Data

Save raw position data as JSON for future comparison:
```
{project_dir}/seo-positions-{YYYY-MM-DD}.json
```

Format:
```json
{
  "domain": "example.com",
  "date": "2026-02-23",
  "locale": "ru",
  "sources": ["yandex-xml", "websearch"],
  "positions": {
    "google": [
      {"keyword": "...", "position": N, "url": "...", "clicks": N, "impressions": N}
    ],
    "yandex": [
      {"keyword": "...", "position": N, "url": "..."}
    ]
  }
}
```

## Step 6: Generate Report

Output format:

```markdown
# Position Report: {domain} — {date}

## Data Sources
- Google: {GSC MCP | Ahrefs MCP | WebSearch spot-check}
- Yandex: {Yandex XML | WebSearch spot-check}

## Google Positions
| Keyword | Position | Change | URL | Clicks | Impressions |
|---------|----------|--------|-----|--------|-------------|
| {kw} | {N} | {↑N / ↓N / → / NEW} | {/path} | {N} | {N} |

## Yandex Positions
| Keyword | Position | Change | URL |
|---------|----------|--------|-----|
| {kw} | {N} | {↑N / ↓N / → / NEW} | {/path} |

## Summary
- **Google**: avg position {N} ({was N, change ↑N / ↓N})
- **Yandex**: avg position {N} ({was N, change ↑N / ↓N})
- **Keywords tracked**: {N}
- **In top 10**: {N} Google, {N} Yandex
- **In top 20**: {N} Google, {N} Yandex

## Top Improvements
1. "{keyword}" — {engine} position ↑{N} ({from} → {to})

## Drops to Watch
1. "{keyword}" — {engine} position ↓{N} ({from} → {to})

## Not Found (not in top 50)
- "{keyword}" — consider creating targeted content

## Recommendations
- {Based on positions data, suggest actions}
```

## Scripts

### yandex-xml-check.py
Queries Yandex XML API for each keyword and extracts domain position.

Usage:
```bash
uv run scripts/yandex-xml-check.py \
  --domain example.com \
  --keywords "ecommerce курс,вайбкоммерс,онлайн курс ecommerce" \
  --region 213 \
  --output positions.json
```

Requires env vars: `YANDEX_XML_USER`, `YANDEX_XML_KEY`
Set in `~/.claude/skills/seo-positions/.env.local`

### positions-report.py
Compares two position JSON files and generates a Markdown report with trends.

Usage:
```bash
uv run scripts/positions-report.py \
  --current positions-2026-02-23.json \
  --previous positions-2026-02-16.json \
  --output report.md
```
