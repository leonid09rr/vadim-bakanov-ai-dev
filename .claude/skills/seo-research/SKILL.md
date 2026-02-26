---
name: seo-research
description: Run competitor SEO research with keyword clustering and content analysis. Use for competitive keyword research, finding content opportunities, and building SEO strategy.
---

# SEO Research Skill

Automated competitor SEO research: fetch keywords, cluster by intent, analyze content opportunities.

## Quick Start

```bash
# 1. Set API keys (one-time setup)
./scripts/cli.sh setup

# 2. Run pipeline (config path from onboarding)
./scripts/cli.sh run --config /path/to/project/seo-research/config.json
```

## Workflow

### Stage 0: USER QUESTIONATY - NEVER SKIP THIS

Before starting research, ask the user:

> Do you already have a list of competitor domains, or should I search for competitors?

Even if the user provides you with a list of compatitors ASK user if he wants to first research competitors more exhaustively. Most likely, the user provided the domains to increase the quality of the competitors discovery phase.

**Option B: Search for competitors** → Follow discovery process below

Ask what the report language should be. The default is English.

#### Discovery Process

**Step 1: Understand the product**

Use WebSearch to learn about the user's domain. If insufficient info, ask the user:
- What does your product/service do?
- What problem does it solve?
- Who are your target customers?

**Step 2: Find 2-3 market leaders**

Search for alternatives and competitors, find at least 2 (can be more):
```
"[product type] alternatives"
"best [product type] tools 2026"
"[user's product] vs"
"[product type] comparison"
```

**Step 3: Confirm with user**

Present found competitors:

> I found these potential competitors:
> - competitor1.com - [brief description]
> - competitor2.com - [brief description]
> - competitor3.com - [brief description]
>
> Does this look right? If yes, I'll search for more competitors in this space.

**Step 4: Expand competitor list**

If user confirms, launch `competitor-discovery-agent` agent:

```
Input:
  - user's domain
  - 3-5 confirmed competitors

Task: Find all similar products/services in this niche. Search for:
  - "alternatives to [each competitor]"
  - "[competitor] vs"
  - Product Hunt, G2, Capterra listings
  - Blog posts comparing tools in this space

Output: List of all found competitor domains with brief descriptions
```

**Step 5: Final confirmation**

Show complete competitor list to user. Remove any that don't fit. Proceed to Stage 1.

---

### Stage 1: Onboarding

**Step 1: Ask where to store the project**

> Where should I create the SEO research project?
>
> This directory will contain:
> - `config.json` - project settings (competitors, filters)
> - `competitors/` - per-domain analysis results
> - `strategies/` - implementation plans and final reports
>
> Example: `Projects/my-startup/marketing/seo-research`

**Step 2: Collect research parameters**

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `output_dir` | Yes | - | Where to store all project files |
| `competitors` | Yes | - | List of competitor domains |
| `project_name` | Yes | - | Name for temp data (`.tmp/seo-{name}/`) |
| `own_domain` | No | - | User's domain (for reference) |
| `keywords_per_competitor` | No | 1000 | Max keywords to fetch per domain |
| `max_position` | No | 20 | Only include keywords where competitors rank in top N positions. **Recommended: 20** for best quality, especially with many competitors. |
| `exclude_patterns` | No | [] | Keywords to filter out |
| `language_code` | Yes | en | Language for SERP results |
| `location_code` | Yes | 2840 | Country/region for SERP (see `info/dataforseo-locations.csv` for codes) |

**Choosing max_position:**

Ask the user: "What maximum position should we analyze? (We recommend **20** for best quality)"

- **Top 20 (recommended)**: Best quality, especially with multiple competitors. Captures keywords where competitors actually rank well.
- **Top 10**: Stricter filter, only top rankings. Use if you want to focus on high-performing keywords only.
- **Top 50**: More data, but includes weaker rankings. Use if you have few competitors or want broader coverage.

The position filter is applied **during data fetch**, saving API credits and time.

**Choosing location_code:**

Ask the user: "What country/region should we target for keyword research?"

Common options:
- United States (2840) - default
- United Kingdom (2826)
- Canada (2124)
- Australia (2036)
- Germany (2276)

Full list: See `info/dataforseo-locations.csv` for all available country codes.

**Note:** Russia, Belarus, Iran, North Korea, Cuba, and Syria are not available (Google Ads restrictions).

**Step 3: Create config**

Create `<output_dir>/config.json`:

```json
{
  "project_name": "my-project",
  "output_dir": "<output_dir>",
  "competitors": ["competitor1.com", "competitor2.com"],
  "own_domain": "mydomain.com",
  "exclude_patterns": [],
  "keywords_per_competitor": 1000,
  "max_position": 20,
  "cluster_count": "auto",
  "dataforseo_params": {
    "language_code": "en",
    "location_code": 2840
  }
}
```

All subsequent commands use `--config <output_dir>/config.json`.

### Stage 2: Data Collection

```bash
./scripts/cli.sh fetch --config config.json
```

Fetches ranked keywords from DataForSEO API for each competitor. Saves raw JSON to `.tmp/seo-{project}/raw/`.

**Checkpoint:** Show keyword counts per competitor. Confirm before proceeding.

### Stage 3: Preprocessing

```bash
./scripts/cli.sh preprocess --config config.json
```

- Merges all keyword files
- Applies exclusion filters
- Calculates opportunity score: `(Volume × 100) / (Difficulty + 1)`
- Extracts unique keywords for embedding
- **Counts unique URLs** (baseline for cluster count)

**Checkpoint:** Show stats including unique URL count. Confirm filters are correct.

### Stage 4: Embeddings

```bash
./scripts/cli.sh embed --config config.json
```

Generates embeddings via OpenRouter (google/gemini-embedding-001). Caches in numpy format.

### Stage 5: Iterative Clustering

Clustering is iterative - clean up garbage, then validate quality.

#### 5.1: Run Clustering

```bash
./scripts/cli.sh cluster --config config.json --k N
```

**Starting k:**
- k = unique_urls (from Stage 3)
- Minimum: 100
- Maximum: 500

#### 5.2: Cluster Review

**Coverage requirement:** Review at least 30% of clusters to assess quality.

**Use `cluster-report` to review multiple clusters at once:**

```bash
./scripts/cli.sh cluster-report --config config.json \
  .cache/clusters/4-dictation.json \
  .cache/clusters/10-text-app.json \
  .cache/clusters/15-voice-mac.json
```

Options:
- `--top N` - limit keywords shown per cluster (default: 15)
- Pass as many .json files as needed

**What to review:**
1. Top 10-15 clusters by score (highest opportunity)
2. Clusters with suspicious names (random words, brand-like names)
3. Random sample from middle and bottom of the list

**Cluster categories:**

**A) Brand cluster** (competitor brand names, typos)
- Action: Skip, don't count as reviewed
- Example: "wispr", "wispr flow", "willow app"

**B) Garbage cluster** (random unrelated keywords)
- Action: Add characteristic words to `exclude_patterns` in config.json
- Example: "avalon nails", "little delhi sf" → add to exclude
- Don't count as reviewed

**C) Mixed intent cluster** (different intents in one cluster)
- Action: Count as RED FLAG
- Example: "medical dictation" + "podcast editing" in same cluster
- This means k is too low

**D) Coherent cluster** (single clear intent)
- Action: Count as VALID
- This is what we want

#### 5.3: Decision

After reviewing clusters:

1. **If added new exclude_patterns:**
   - Go back to Stage 3 (preprocess) to apply filters
   - Then re-run from Stage 5.1

2. **If >3 RED FLAGS (mixed intent clusters):**
   - Increase k by 50%
   - Go back to 5.1

3. **If most clusters are VALID:**
   - Proceed to Stage 6

**Max iterations:** 5

#### 5.4: Output

- `.tmp/seo-{project}/clusters/cluster-index.json`
- Individual cluster files: `{index}-{name}.json`
- Index 0 = highest opportunity cluster

### Stage 6: Strategy Discovery

Analyze competitor pages to identify content strategies using sub-agents.

#### 6.1: Per-Domain Analysis

Run `seo-strategy-reserach-agent` agent for each competitor domain:

```
Input: domain name (e.g., "wisprflow.ai")
Output: JSON files in <output_dir>/competitors/<domain>/
```

The agent categorizes each content page into strategy types:
- `comparison-pages` - "vs", "alternative", competitor names
- `integration-pages` - product integrations (notion, slack, gmail)
- `vertical-landing` - industry niches (medical, legal, academic)
- `best-of-content` - "best X", "top Y" listicles
- `platform-pages` - OS/device specific (android, ios, windows)
- `segment-pages` - user types (students, business, enterprise)
- `how-to-guides` - tutorials, guides
- `case-studies` - customer stories

**Run in parallel** - launch one agent per domain simultaneously.

Output structure:
```
<output_dir>/competitors/
├── wisprflow.ai/
│   ├── comparison-pages.json
│   ├── integration-pages.json
│   └── vertical-landing.json
├── superwhisper.com/
│   ├── comparison-pages.json    # Same strategy, different domain
│   └── platform-pages.json
└── ...
```

Each JSON file:
```json
{
  "strategy": "comparison-pages",
  "description": "How this competitor executes the strategy...",
  "urls": ["https://domain.com/comparison/x", "https://domain.com/comparison/y"]
}
```

**IMPORTANT:** Always use full URLs with https:// protocol. Never use relative paths like "/comparison/x". This makes links clickable and immediately actionable.

#### 6.2: Review All Strategies

List all strategy files:
```bash
ls <output_dir>/competitors/*/
```

Read all JSON files (they're tiny - just strategy name, description, urls array).

Group by strategy name - same name = same strategy type.

#### 6.3: Strategy Plans

For each unique strategy (e.g., `comparison-pages` found in 5 competitors):

Run `seo-strategy-planner` agent:

```
Input:
  - strategy name (e.g., "comparison-pages")
  - paths to strategy JSON files from competitors

Output: strategies/<strategy-name>.md
```

The planner will:
1. WebFetch the competitor pages to understand how they execute the strategy
2. Analyze patterns across competitors
3. Write detailed implementation plan

Output format with frontmatter for ranking:

```markdown
---
strategy: comparison-pages
competitors: [wisprflow.ai, superwhisper.com]
pages_count: 12
---

# Strategy: Comparison Pages

## What It Is
[Description based on competitor examples]

## Competitor Examples
| Domain | URL | Approach |
|--------|-----|----------|
| wisprflow.ai | https://wisprflow.ai/comparison/x | [how they do it] |

**Note:** Always include full URLs with https:// in all documentation and reports for easy access.

## Implementation Plan
- URL pattern
- Page template
- Keywords to target
- Content structure
```

#### 6.4: Homepage Analysis

Run `seo-homepage-analyst` agent for key competitors:

```
Input: domain name (e.g., "wisprflow.ai")
Output: competitors/<domain>/homepage.json
```

The agent analyzes:
- **Keywords**: What clusters/intents the homepage ranks for
- **Positioning**: Headline, value props, target audience
- **Page structure**: Sections, CTAs, social proof
- **Keyword-copy alignment**: Do they mention what they rank for?

**Run for top competitors** - those with highest homepage scores.

Output:
```json
{
  "positioning": {"headline": "...", "key_value_props": [...]},
  "keyword_strategy": {"primary_terms": [...], "platforms": [...]},
  "top_keywords": [{"keyword": "...", "volume": N}],
  "insights": ["...", "..."]
}
```

Then run `seo-strategy-planner` with all homepage.json files to create:
```
strategies/homepage.md
```

This plan covers how to structure and position our own homepage for maximum keyword coverage.

### Stage 7: Final Reports

Create two final documents:

#### 7.1: SEO Master Plan

File: `<output_dir>/strategies/0_SEO_Master_Plan.md`

Structure:
```markdown
# SEO Master Plan

## Executive Summary
- Market state (how developed is competitor SEO)
- Total opportunity size
- Key insight (1 sentence)

## Competitive Landscape
| Competitor | Homepage Score | Clusters | Strategies |
|------------|---------------|----------|------------|
| leader.com | 125M | 80 | 8 |
| ...

## Strategy Ranking

Ranked by opportunity score (highest first):

### #1: [Strategy Name]
**Opportunity Score:** X
**Competitors Using:** N/22
**Why:** [1 sentence on why this strategy works]
**Details:** [[strategy-name]]

### #2: [Strategy Name]
...

## Key Learnings
- What patterns work across competitors
- What competitors miss (gaps)
- Unique angles for differentiation
```

**Do NOT include:**
- Timeline-based roadmaps (weeks, months)
- Specific page counts per phase
- Prescriptive task lists

The ranking speaks for itself - execute strategies in order of opportunity.

#### 7.2: Homepage Optimization Plan

File: `<output_dir>/strategies/homepage.md`

Structure:
```markdown
# Homepage Optimization Plan

## Competitor Benchmark
| Metric | Leader | #2 | #3 |
|--------|--------|-----|-----|
| Score | 125M | 19M | 1.2M |
| Clusters | 80 | 59 | 12 |

## What Makes [Leader] Win
- Key positioning elements
- Page structure analysis
- Keyword coverage strategy

## Recommendations
### Positioning
- Headline formula
- Value propositions

### Structure
- Sections to include
- Trust signals needed

### Keywords
- Primary terms to target
- Platform coverage
```

## File Locations

### Temporary (`.tmp/` - not committed)

```
.tmp/seo-{project}/
├── raw/                    # DataForSEO responses
├── processed/              # Merged CSV, filtered
├── embeddings/             # Embedding cache, matrix
└── clusters/               # Cluster JSONs, index
```

### Project Output (`<output_dir>/`)

```
<output_dir>/
├── config.json                 # Project config (committed to git)
├── competitors/
│   ├── domain.com/
│   │   ├── homepage.json       # Homepage analysis
│   │   ├── comparison-pages.json
│   │   └── ...                 # Strategy JSONs
│   └── ...
└── strategies/
    ├── 0_SEO_Master_Plan.md    # Executive summary + ranking
    ├── homepage.md             # Homepage optimization
    ├── comparison-pages.md     # Detailed strategy plans
    ├── platform-pages.md
    └── ...
```

The config file lives with the research output - it's part of the project, not the skill.

## API Keys Required

| Variable | Service | Purpose |
|----------|---------|---------|
| `DATAFORSEO_LOGIN` | DataForSEO | API login |
| `DATAFORSEO_PASSWORD` | DataForSEO | API password |
| `OPENROUTER_API_KEY` | OpenRouter | Embeddings |

## Embedding Model Selection

Default model: `intfloat/multilingual-e5-large` (1024 dimensions)

To change the model, edit `scripts/embed.py` and update the `MODEL` constant.

**How to choose:**
1. Check [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) for quality rankings
2. Lower dimension = faster clustering (1024 vs 3072 is ~3x faster)
3. Trade-off: higher dimension = better quality, but slower and more memory

**Recommendations:**
- For large datasets (50k+ keywords): use 1024-dim models (e5-large, etc.)
- For smaller datasets or better quality: use 3072-dim models (gemini-embedding-001)
- If clustering is too slow, switch to a smaller model

## Scripts Reference

All scripts are self-contained with UV inline dependencies.

| Script | Purpose |
|--------|---------|
| `cli.sh` | Main entry point, UV management |
| `fetch_keywords.py` | DataForSEO API calls (supports --force) |
| `preprocess.py` | Merge, filter, score calculation |
| `embed.py` | OpenRouter embeddings with cache |
| `cluster.py` | K-means, ranking, export |
| `cluster_report.py` | Review multiple clusters at once (preferred) |
| `cluster_review.py` | Review single cluster (legacy) |
| `export_pages.py` | Export competitor pages for strategy analysis |
| `url_clusters.py` | Show which clusters each URL ranks in |

## Agents

| Agent | Purpose |
|-------|---------|
| `competitor-discovery-agent` | Find all competitors in a niche given user's domain and 3-5 seed competitors |
| `seo-strategy-reserach-agent` | Analyze one competitor domain, output strategy JSONs |
| `seo-strategy-planner` | Create implementation plan for one strategy type |
| `seo-homepage-analyst` | Deep analysis of competitor homepage positioning and keywords |

## Troubleshooting

### Too few keywords after filtering

If preprocessing results in too few keywords (<1000), try:
1. **Increase `max_position`** to 30 or 50 - includes more keywords where competitors rank lower. Edit config.json and re-run fetch with `--force` to fetch more positions.
2. **Add more competitors** - especially larger sites with more rankings
3. **Increase `keywords_per_competitor`** - fetch more data from API

### Too many garbage clusters

If many clusters contain irrelevant keywords:
1. **Decrease `max_position`** to 10 or 15 - stricter filter, only top rankings. Edit config.json and re-run fetch with `--force` to apply new position filter.
2. **Add terms to `exclude_patterns`** - filter out specific garbage
3. **Add niche-specific competitors** - more focused keyword set

**Note:** The `max_position` filter is applied during data fetch from the API, not after. This saves API credits and time by only downloading relevant data.

## Tips

- Start with 3-5 direct competitors
- Review filtered keywords before proceeding
- Initial cluster count = unique URLs from competitors (min 100, max 500)
- If clusters contain mixed intents, increase k and re-cluster
- Analyze highest-priority clusters first
- Focus on low difficulty + high volume keywords for quick wins
- **Recommended `max_position: 20`** - filters during API fetch to keywords where competitors actually rank well, saving credits and time

## Additional resources

- Template of the config.json file [templates/config.json](config.json)