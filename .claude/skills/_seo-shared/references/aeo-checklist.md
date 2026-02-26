# AEO (Answer Engine Optimization) Checklist

Optimization for AI search engines: ChatGPT, Perplexity, Google AI Overviews, YandexGPT, Claude.

## AI Crawler Access

### robots.txt Rules
Verify these crawlers are NOT blocked:

| Crawler | Service | User-Agent |
|---------|---------|------------|
| GPTBot | OpenAI/ChatGPT | GPTBot |
| Google-Extended | Google Gemini/AI Overviews | Google-Extended |
| PerplexityBot | Perplexity AI | PerplexityBot |
| anthropic-ai | Claude | anthropic-ai |
| CCBot | Common Crawl | CCBot |

Example allowing all AI crawlers:
```
User-agent: GPTBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: CCBot
Allow: /
```

### Rendering
- Content MUST be available without JavaScript execution
- SSG/SSR required — CSR pages are invisible to most AI crawlers
- Verify: View Page Source shows full content (not empty `<div id="root">`)

## Content Structure for AI Extraction

### Autonomous Fragments
Each paragraph/section must be understandable WITHOUT reading the rest of the page.

- Bad: "As mentioned above, this technique..."
- Good: "The XYZ technique works by..."

- Bad: "It has three advantages:"
- Good: "React Server Components have three advantages:"

AI systems extract individual fragments for answers. Context-dependent text breaks citation quality.

### Semantic HTML Elements
Use proper HTML for structure that AI systems can parse:

| Element | Use For | AI Benefit |
|---------|---------|------------|
| `<dl>`, `<dt>`, `<dd>` | Definitions, terms | Clear term-definition pairs |
| `<blockquote cite="...">` | Citations, quotes | Source attribution |
| `<code>`, `<pre>` | Code examples | Code extraction |
| `<table>` with `<caption>`, `<thead>`, `<tbody>` | Data tables | Structured data extraction |
| `<figure>`, `<figcaption>` | Images with context | Image understanding |
| `<details>`, `<summary>` | FAQ, expandable content | Q&A extraction |
| `<article>` | Main content | Content boundary detection |
| `<section>` | Logical sections | Topic segmentation |

### Terminology Consistency
- Use ONE term for each concept throughout the page
- Bad: mixing "ML", "machine learning", "AI" for the same concept
- Good: "machine learning" everywhere, with "ML" defined once as abbreviation
- Add a terminology section or glossary for complex topics

## Schema.org for AEO

Priority structured data types for AI citation:

| Schema Type | When to Use | AEO Benefit |
|-------------|------------|-------------|
| `TechArticle` | Technical guides, tutorials | Signals expertise depth |
| `FAQPage` | Pages with Q&A sections | Direct Q&A extraction |
| `HowTo` | Step-by-step instructions | Procedural extraction |
| `Article` with `dateModified` | Any article content | Freshness signal |
| `Person` (author) | Author pages | E-E-A-T signal |

Critical fields for AEO:
- `datePublished` + `dateModified` — freshness signal
- `author` with full details (name, url, credentials)
- `publisher` with logo
- `mainEntity` — clear topic definition

## Content Freshness Plan

| Timeframe | Action |
|-----------|--------|
| 30 days post-publish | Check metrics, first SERP position, AI citations |
| 90 days | Update data, add new examples, refresh statistics |
| 180 days | Full content audit: accuracy, relevance, links |

On each update:
- Update `dateModified` in Schema.org
- Add "Updated: {date}" note
- Remove outdated information
- Add fresh data/examples
- Check all external links

## Originality Test

"Can a competitor copy this tomorrow?"

- Bad: generic advice available everywhere
- Good: original data, unique research, real case studies

Original elements that AI systems prefer to cite:
- Proprietary metrics and data
- Unique code examples/scripts
- First-hand expert quotes
- Real customer stories/case studies
- Original screenshots/diagrams
- Primary research or surveys

## AEO Impact Tracking

### Check AI Citations
Periodically search for your topics in:
- ChatGPT (chat.openai.com)
- Perplexity (perplexity.ai)
- Google AI Overviews (google.com)
- Claude (claude.ai)
- Bing Copilot (bing.com)

### Track AI Referral Traffic
In analytics, monitor referrers from:
- `chat.openai.com`
- `perplexity.ai`
- `gemini.google.com`
- `claude.ai`

### Success Metrics
- AI citation count (qualitative — check monthly)
- AI platform referral traffic (quantitative)
- Mentions on authoritative platforms
- Growth of organic backlinks
- Brand search volume increase
