---
name: seo-content
description: |
  Keyword research and content optimization for any market. Works without paid API subscriptions using web search. Optionally integrates Ahrefs/Semrush MCP or DataForSEO (seo-research skill) for richer keyword data.
  Use when: (1) researching keywords for a topic or page, (2) creating a content brief or editorial plan, (3) optimizing existing page content for SEO+AEO, (4) analyzing SERP competitors for a keyword, (5) clustering keywords by intent, (6) user says "keyword research", "content brief", "optimize content", "seo content", "find keywords", "editorial plan", "подбери ключи", "контент-план", "оптимизируй контент".
  Supports any locale including Russia (Yandex-based research) and works even without API keys by using web search as fallback.
---

# SEO Content Skill

Keyword research + content strategy + page optimization. Works for any market with WebSearch fallback.

## Step 1: Determine Context

Ask user (use AskUserQuestion):

1. **Topic**: What topic, page, or seed keywords to research?
2. **Locale**: Target market? (Russia, USA, global, other)
3. **Goal**: New content, optimize existing page, or editorial plan?
4. **MCP**: Ahrefs or Semrush connected? (optional)

Based on locale, load locale reference:
- Russia → `~/.claude/skills/_seo-shared/references/locale-ru.md`
- English → `~/.claude/skills/_seo-shared/references/locale-en.md`
- Other → `~/.claude/skills/_seo-shared/references/locale-generic.md`

## Step 2: Detect Data Sources

Read `~/.claude/skills/_seo-shared/references/mcp-integration.md` for detection logic.

Priority order:
1. **Ahrefs MCP** → try `explore_keywords_overview`
2. **Semrush MCP** → try `keyword_overview`
3. **DataForSEO** (seo-research skill) → check if project has `.claude/skills/seo-research/` AND market is NOT sanctioned (Russia, Belarus, etc.)
4. **WebSearch** → always available

Record available sources. Proceed with the highest-priority available source.

## Step 3: Keyword Discovery

Launch `keyword-discovery-agent`:

```
Task: Find keywords related to "{topic}" for {locale} market.

Use the best available data source.

IF Ahrefs MCP available:
  - Call explore_keywords_overview for seed keywords
  - Call explore_matching_terms for expansion
  - Extract: keyword, volume, difficulty, CPC

IF Semrush MCP available:
  - Call keyword_overview for seed keywords
  - Call related_keywords for expansion
  - Extract: keyword, volume, difficulty

IF DataForSEO available AND market supported:
  - Suggest using /seo-research skill for deep pipeline
  - Provide seed keywords for the pipeline

FALLBACK (WebSearch — always works):
  - WebSearch: "{topic}" — collect related searches
  - WebSearch: "{topic} keywords" — find keyword lists
  - WebSearch: "{topic} frequently asked questions"
  - WebSearch: "{topic} popular queries {current_year}"
  - WebSearch: "people also ask {topic}"
  - WebSearch: "site:reddit.com {topic}" — real user questions

  For Russia specifically:
  - WebSearch: "wordstat {keyword}" — Yandex Wordstat data
  - WebSearch: "{keyword} частотность яндекс"
  - WebSearch: "site:vc.ru {topic}" — Russian community questions

  Estimate volume as HIGH/MEDIUM/LOW:
  - HIGH: term appears in autocomplete, many dedicated pages
  - MEDIUM: some pages, appears in related searches
  - LOW: few results, niche term

Output: JSON array of keywords
[
  {"keyword": "...", "volume": N or "HIGH|MEDIUM|LOW", "difficulty": N or null, "source": "ahrefs|semrush|websearch", "intent": "informational|transactional|navigational|commercial"}
]

Aim for 30-100 keywords minimum.
```

Model: opus. Tools: WebSearch, Ahrefs MCP (optional), Semrush MCP (optional).

## Step 4: Cluster by Intent

Launch `keyword-cluster-agent`:

```
Task: Group these keywords into semantic clusters by search intent.

Keywords: {JSON array from Step 3}

Rules:
1. Group by user INTENT, not just lexical similarity
2. Each cluster = one potential page/article
3. Assign intent type to each cluster:
   - informational: "how to", "what is", "guide", "tutorial"
   - transactional: "buy", "price", "order", "discount"
   - navigational: brand names, specific product names
   - commercial: "best", "top", "review", "comparison", "vs"
4. For each cluster, identify:
   - Primary keyword (highest volume)
   - Supporting keywords (related terms)
   - Estimated total cluster volume
5. Rank clusters by opportunity: volume × (1 / (difficulty + 1))

Output: JSON array of clusters
[
  {
    "name": "cluster short name",
    "intent": "informational|transactional|navigational|commercial",
    "primary_keyword": "...",
    "keywords": ["kw1", "kw2", ...],
    "total_volume": N or "HIGH|MEDIUM|LOW",
    "opportunity_rank": 1
  }
]
```

Model: opus. Tools: none (pure reasoning).

## Step 5: SERP Analysis

For top 5 clusters by opportunity, launch `serp-analysis-agent` (parallel):

```
Task: Analyze search results for "{primary_keyword}" in {locale} market.

Steps:
1. WebSearch for the exact keyword
2. For top 5 organic results:
   a. WebFetch each page
   b. Extract: title, H1, word count, heading structure (H2-H3), Schema types used, content format
   c. Note: unique angle, strengths, weaknesses
3. Identify content gaps — what top results MISS
4. Identify common patterns — what ALL top results DO
5. Determine recommended approach

Output: JSON
{
  "keyword": "...",
  "serp_landscape": [
    {
      "position": 1,
      "url": "...",
      "title": "...",
      "word_count": N,
      "headings": ["H2: ...", "H2: ...", "H3: ..."],
      "schema_types": ["Article", "FAQPage"],
      "content_format": "guide|listicle|comparison|tutorial|review",
      "unique_angle": "..."
    }
  ],
  "common_patterns": ["all include pricing tables", "all have FAQ section"],
  "content_gaps": ["none cover X", "outdated data on Y"],
  "recommended_approach": "...",
  "recommended_word_count": N,
  "recommended_schema": "Article|TechArticle|HowTo|FAQPage",
  "recommended_format": "guide|listicle|comparison|tutorial"
}
```

Model: opus. Tools: WebSearch, WebFetch.

## Step 6: Generate Output

Based on user's goal from Step 1:

### Goal: New Content → Content Brief

Read `references/content-brief-template.md` for format.

Generate a complete brief using SERP analysis results, keyword clusters, and AEO requirements from `~/.claude/skills/_seo-shared/references/aeo-checklist.md`.

### Goal: Optimize Existing Page

Launch `content-optimizer-agent`:

```
Task: Compare the existing page at {url_or_file} against SERP analysis for "{primary_keyword}".

Steps:
1. Read the existing page (WebFetch URL or Read local file)
2. Compare with SERP winners from serp-analysis results:
   - Title: length, keyword presence
   - Meta description: length, CTA
   - Word count vs SERP average
   - Heading structure vs SERP pattern
   - Schema.org vs what competitors use
   - Content gaps vs what competitors cover
   - AEO compliance (autonomous fragments, semantic HTML)
3. Generate specific, actionable changes

Output format:
# Content Optimization: {Page Title}

## Current State
- Word count: X (SERP average: Y)
- SEO Score: X/100
- Keywords targeting: [list]

## vs SERP Winners
| Metric | Your Page | SERP Average | Gap |
|--------|-----------|-------------|-----|

## Specific Changes

### Title
BEFORE: "..."
AFTER: "..."

### Meta Description
BEFORE: "..."
AFTER: "..."

### Content Additions
1. Add section: "[H2]" — competitors cover this, you don't
2. Expand section: "[H2]" — currently X words, recommend Y+

### Schema.org
(generated JSON-LD if missing)
```

Model: opus. Tools: WebFetch, Read, Grep.

### Goal: Editorial Plan

Generate a content calendar mapping keyword clusters to pages.

```markdown
# Editorial Plan: {Topic Area}

## Keyword Clusters (ranked by opportunity)

### Cluster 1: {Name} — {Intent} — {Volume}
| Keyword | Volume | Difficulty |
|---------|--------|-----------|
| {primary} | ... | ... |
| {supporting} | ... | ... |

### Cluster 2: ...

## Content Calendar
| # | Page Title | Target Cluster | Format | Word Count | Schema | Priority |
|---|------------|---------------|--------|------------|--------|----------|

## Internal Linking Strategy
- {Page A} links to {Page B} because...
- Hub page: {URL} links to all cluster pages

## Quick Wins (low difficulty, high volume)
1. ...

## Long-term Plays (high difficulty, high volume)
1. ...
```
