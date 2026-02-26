---
name: seo-audit
description: |
  Full SEO + AEO audit for any website page or entire site. Auto-detects framework (Astro, Next.js, Hugo, plain HTML), asks about target market/locale, and generates scored report with actionable fixes and Schema.org JSON-LD markup.
  Use when: (1) auditing a page or site for SEO issues, (2) generating Schema.org structured data, (3) checking technical SEO (robots.txt, sitemap, Core Web Vitals), (4) evaluating AEO readiness (AI crawler access, autonomous fragments), (5) user says "seo audit", "check seo", "audit my site", "schema markup", "structured data", "проверь seo", "аудит сайта".
  Optionally uses Ahrefs/Semrush MCP for backlink and domain authority data when available.
---

# SEO Audit Skill

Full technical + on-page + AEO audit with scored report and ready-to-paste fixes.

## Step 1: Detect Project Context

Detect the framework by checking config files in the project root.
Read `~/.claude/skills/_seo-shared/references/framework-detection.md` for detection rules.

```
Glob: astro.config.* → Astro (SSG)
Glob: next.config.* → Next.js (SSR/SSG)
Glob: nuxt.config.* → Nuxt (SSR)
Glob: hugo.toml → Hugo (SSG)
Glob: angular.json → Angular (CSR — SEO warning!)
Glob: index.html in root → Plain HTML
```

Record: framework name, rendering strategy (SSG/SSR/CSR), site URL from config.

## Step 2: Ask User

Ask these questions (use AskUserQuestion, max 4):

1. **Scope**: Audit the entire site or a specific page? If specific — which URL?
2. **Locale**: What is the target market? (Russia, USA, global, other)
3. **Language**: What is the primary language of the site?
4. **MCP access**: Do you have Ahrefs or Semrush connected? (optional, for richer data)

Based on locale answer, load the appropriate locale reference:
- Russia → `~/.claude/skills/_seo-shared/references/locale-ru.md`
- English markets → `~/.claude/skills/_seo-shared/references/locale-en.md`
- Other → `~/.claude/skills/_seo-shared/references/locale-generic.md`

## Step 3: Detect MCP Tools

Read `~/.claude/skills/_seo-shared/references/mcp-integration.md` for tool names.

Try calling each MCP tool with a minimal query. Record which are available.

```
Ahrefs: try domain_rating for the site domain
Semrush: try domain_overview for the site domain
GSC: try search_analytics for the site URL
```

If none available — proceed with WebFetch-based audit only.

## Step 4: Discover Pages

**If scope = entire site:**

1. Try WebFetch `{domain}/sitemap.xml` — extract all page URLs
2. If no sitemap: Glob `src/pages/**/*.astro` (Astro) or `app/**/page.tsx` (Next.js) or equivalent
3. If neither: ask user for page list

**If scope = single page:**

Use the URL provided by user.

## Step 5: Run Audit Sub-Agents

### For each page — launch `page-audit-agent` (parallel, max 10):

```
Task: Audit the page at {url} for SEO + AEO compliance.

Read these references first:
- ~/.claude/skills/seo-audit/references/technical-seo.md
- ~/.claude/skills/seo-audit/references/on-page-seo.md
- ~/.claude/skills/_seo-shared/references/aeo-checklist.md
- ~/.claude/skills/_seo-shared/references/locale-{locale}.md

Steps:
1. WebFetch the live URL to get rendered HTML
2. Also Read the source file if this is a local project (e.g., src/pages/index.astro)
3. Check against technical-seo.md criteria:
   - Title tag: exists? length 50-60 chars? contains keyword?
   - Meta description: exists? length 150-160 chars? has CTA?
   - Canonical URL: <link rel="canonical"> present?
   - Open Graph tags: og:title, og:description, og:image, og:url
   - Viewport meta tag
   - HTTPS
4. Check against on-page-seo.md criteria:
   - H1: exactly one? contains keyword? 20-70 chars?
   - H2-H6 hierarchy: logical, no skips?
   - Content: word count, keyword in first 100 words, lists/tables?
   - Images: all have alt text? descriptive file names?
   - Internal links: count, anchor text quality?
   - External links: rel="nofollow" for ads? rel="noopener" for _blank?
5. Check Schema.org JSON-LD:
   - Any <script type="application/ld+json"> present?
   - If yes: validate type, required fields, dates
   - If no: note as CRITICAL finding, suggest appropriate schema type
6. Check AEO (from aeo-checklist.md):
   - Are paragraphs autonomous (understandable alone)?
   - Semantic HTML elements used (dl, figure, blockquote, details)?
   - Terminology consistent throughout?
   - datePublished/dateModified in Schema?
7. Check locale-specific requirements (from locale file)

Output as JSON:
{
  "url": "...",
  "source_file": "...",
  "scores": {"seo": 0-100, "aeo": 0-100},
  "findings": [
    {"category": "technical|on-page|schema|aeo|locale",
     "severity": "critical|high|medium",
     "description": "...",
     "fix": "exact code or instruction to fix"}
  ],
  "schema_suggestion": null or "JSON-LD string if schema is missing"
}
```

Model: opus. Tools: WebFetch, Read, Grep, Glob.

### Site-wide — launch `site-technical-agent` (once):

```
Task: Check site-wide technical SEO for {domain}.

Steps:
1. WebFetch {domain}/robots.txt
   - Exists?
   - AI crawlers allowed? (GPTBot, Google-Extended, PerplexityBot, anthropic-ai, CCBot)
   - Sitemap reference present?
   - Locale-specific directives (e.g., Yandex Host, Clean-param for RU)
2. WebFetch {domain}/sitemap.xml
   - Exists?
   - Page count?
   - lastmod dates present and recent?
   - Any 404 URLs?
3. Check HTTPS
   - All pages redirect HTTP → HTTPS?
4. Check canonical consistency
   - Same pattern across all pages (trailing slash or not)?
5. Check for duplicate title/description across pages

Output as JSON:
{
  "domain": "...",
  "robots_txt": {"exists": bool, "ai_crawlers": {"GPTBot": "allowed|blocked|not_mentioned", ...}, "issues": []},
  "sitemap": {"exists": bool, "page_count": N, "issues": []},
  "https": bool,
  "findings": [...]
}
```

Model: opus. Tools: WebFetch, Read, Glob.

### Optional — launch `backlink-agent` (only if Ahrefs or Semrush MCP available):

```
Task: Get domain authority and backlink profile for {domain}.

If Ahrefs available:
  - Call domain_rating for DR score and referring domains count
  - Call batch_url_analysis for top pages

If Semrush available:
  - Call domain_overview for traffic estimates and keyword count

Output as JSON:
{
  "domain_rating": N,
  "referring_domains": N,
  "organic_keywords": N,
  "estimated_traffic": N,
  "source": "ahrefs|semrush"
}
```

Model: opus. Tools: Ahrefs MCP or Semrush MCP tools.

## Step 6: Compile Report

Read `references/report-template.md` for the output format.

1. Merge all sub-agent results
2. Calculate aggregate scores:
   - **SEO Score**: average of page SEO scores, weighted by severity of site-wide issues
   - **AEO Score**: average of page AEO scores
   - **Combined Score**: (SEO × 0.6) + (AEO × 0.4)
3. Deduplicate findings (same issue across pages → one finding with affected pages list)
4. Sort by severity: CRITICAL → HIGH → MEDIUM
5. For each page missing Schema.org → include generated JSON-LD from sub-agent

## Step 7: Present Results

Output the full report in Markdown format (see report-template.md).

For each CRITICAL and HIGH finding, include **exact code to fix it** — ready to copy-paste.

If Schema.org is missing → provide complete JSON-LD blocks for each page, considering the page type:
- Homepage → Organization + WebSite
- Course page → Course + Offer
- Event page → Event
- Blog post → Article or TechArticle
- FAQ section → FAQPage

Read `~/.claude/skills/_seo-shared/references/schema-patterns.md` for templates.

## Scoring Guide

### SEO Score (0-100)
| Check | Weight | Deduction if Missing |
|-------|--------|---------------------|
| Title tag (proper length + keyword) | 10 | -10 |
| Meta description (proper length + CTA) | 8 | -8 |
| H1 (one, proper, with keyword) | 8 | -8 |
| H2-H6 structure | 5 | -5 |
| Canonical URL | 5 | -5 |
| Open Graph tags | 4 | -4 |
| HTTPS | 10 | -10 |
| Mobile viewport | 5 | -5 |
| Image alt text (all images) | 5 | -5 per missing |
| Internal links (3+) | 5 | -5 |
| robots.txt proper | 5 | -5 |
| Sitemap exists | 5 | -5 |
| Schema.org present | 10 | -10 |
| Content word count (500+ for main, 300+ for service) | 5 | -5 |
| No broken links | 5 | -5 |
| Page speed (< 3s load) | 5 | -5 |

### AEO Score (0-100)
| Check | Weight | Deduction if Missing |
|-------|--------|---------------------|
| AI crawlers allowed in robots.txt | 15 | -15 |
| SSG/SSR rendering (not CSR) | 15 | -15 |
| Autonomous paragraphs | 15 | -15 |
| Semantic HTML elements | 10 | -10 |
| Terminology consistency | 10 | -10 |
| datePublished in Schema | 10 | -10 |
| dateModified in Schema | 5 | -5 |
| Author info in Schema | 5 | -5 |
| Content originality signals | 10 | -10 |
| FAQ/HowTo structured data | 5 | -5 |
