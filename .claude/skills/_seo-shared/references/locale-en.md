# SEO for English-Speaking Markets

## Search Engines

| Engine | Market Share (US) | Priority |
|--------|-------------------|----------|
| Google | ~87% | Primary |
| Bing | ~7% | Secondary |
| DuckDuckGo | ~3% | Low |

Optimize primarily for Google. Bing picks up most Google optimizations automatically.

## Google-Specific

### Google Search Console (GSC)
- URL: search.google.com/search-console
- Verification: HTML file, meta tag, DNS, or Google Analytics
- Key data: search queries, click-through rates, average position, index coverage
- MCP integration: see `mcp-integration.md` for GSC MCP setup

### Core Web Vitals (Google ranking factor since 2021)
| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5-4.0s | > 4.0s |
| INP (Interaction to Next Paint) | < 200ms | 200-500ms | > 500ms |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1-0.25 | > 0.25 |

Check via: PageSpeed Insights (pagespeed.web.dev) or Lighthouse.

### Featured Snippets
- Appear at position 0 in Google results
- Formats: paragraph, list, table, video
- Optimize: answer the question directly in first paragraph, use structured headings
- FAQ schema can help trigger "People Also Ask" boxes

### Google AI Overviews (SGE)
- AI-generated summaries at the top of search results
- Optimization: clear, authoritative content with structured data
- Include facts, statistics, step-by-step instructions
- Cite sources — Google AI Overviews prefer content with references

## Keyword Research Tools

### Free
- Google Keyword Planner (requires Google Ads account)
- Google Trends (trends.google.com)
- Google Autocomplete ("people also search for")
- AnswerThePublic (limited free queries)

### Paid (with MCP integration)
- Ahrefs — see `mcp-integration.md`
- Semrush — see `mcp-integration.md`

### WebSearch Fallback
```
"{topic} keywords"
"best {topic} tools 2026"
"{topic} frequently asked questions"
"people also ask {topic}"
"reddit {topic}"
```

## Analytics
- Google Analytics 4 (GA4) — standard
- Google Tag Manager — event tracking
- Check: organic traffic, bounce rate, session duration, conversion rate

## Content Standards
- Language: English (US or UK — be consistent)
- E-E-A-T: Experience, Expertise, Authoritativeness, Trustworthiness
- Google Helpful Content Update: content must be written for humans first
- Avoid: AI-generated content without editorial review
