# Universal SEO Principles (Any Market)

## Core SEO Fundamentals (apply everywhere)

### Technical
- HTTPS required (SSL certificate)
- Mobile-responsive design
- Fast loading (< 3 seconds)
- Valid HTML (semantic elements)
- Accessible (WCAG AA minimum)
- robots.txt properly configured
- XML sitemap submitted to search engines

### On-Page
- One unique H1 per page (50-70 chars)
- Title tag (50-60 chars) with primary keyword
- Meta description (150-160 chars) with CTA
- Logical heading hierarchy (H1 > H2 > H3, no skips)
- Alt text for all images
- 3-5+ internal links per page
- Descriptive anchor text (not "click here")
- Canonical URL specified

### Content Quality
- Unique content (> 95% originality)
- Primary keyword in first 100 words
- Natural keyword density (1-2%)
- Short paragraphs (2-4 sentences)
- Lists and tables for structured information
- Date published/updated visible
- Author information present

### AEO (Answer Engine Optimization)
- See `aeo-checklist.md` for detailed requirements
- Key: autonomous paragraphs, semantic HTML, AI crawler access

## Creating a New Locale File

When adding support for a new market, create `locale-{code}.md` with:

1. **Search engine landscape** — market share of search engines in this country
2. **Webmaster tools** — registration and verification for local search engines
3. **Keyword research** — local tools and WebSearch query templates
4. **Analytics** — standard analytics platform for this market
5. **robots.txt** — any locale-specific directives
6. **Content standards** — language, legal requirements, cultural norms
7. **AI search** — local AI assistants and their crawlers

Template:
```markdown
# SEO for {Market Name}

## Search Engines
| Engine | Market Share | Priority |
|--------|-------------|----------|
| ... | ...% | ... |

## {Primary Engine}: Specifics
### Webmaster Tools
### Indexation Notes
### robots.txt Directives

## Keyword Research
### Free Tools
### WebSearch Queries

## Analytics

## AI Crawlers (AEO)

## Content Standards
```
