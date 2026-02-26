# WebSearch-Based Keyword Research

Methodology for finding keywords without paid APIs. Works for any locale.

## Query Templates

### Universal (any market)
```
"{topic}"                              → related searches, autocomplete
"{topic} guide"                        → informational intent
"{topic} vs"                           → comparison intent
"best {topic}"                         → commercial intent
"{topic} FAQ"                          → questions people ask
"{topic} how to"                       → tutorial intent
"{topic} price" / "{topic} pricing"    → transactional intent
"people also ask {topic}"              → Google PAA questions
"{topic} alternatives"                 → comparison intent
"{topic} for beginners"                → informational, low difficulty
"{topic} tools {year}"                 → commercial, fresh content
```

### Russia-Specific
```
"wordstat {keyword}"                   → Yandex Wordstat data in results
"{keyword} частотность яндекс"         → volume data from blogs/tools
"site:vc.ru {topic}"                   → VC.ru discussions (Russian HN)
"site:habr.com {topic}"               → Habr technical content
"{topic} отзывы"                       → review intent
"{topic} купить"                       → purchase intent
"{topic} сравнение"                    → comparison intent
"{topic} обучение"                     → education intent
```

### English-Specific
```
"site:reddit.com {topic}"             → Reddit discussions
"site:quora.com {topic}"              → Quora questions
"{topic} review {year}"               → fresh review intent
"{topic} tutorial"                     → education intent
```

## Volume Estimation (Without APIs)

When exact search volume is unavailable, estimate using signals:

| Signal | Volume Estimate |
|--------|----------------|
| Appears in Google/Yandex autocomplete | HIGH |
| Many dedicated pages (>10 in top results) | HIGH |
| Appears in "People Also Ask" | MEDIUM-HIGH |
| Some dedicated pages, appears in related searches | MEDIUM |
| Few results, mostly mentioned in passing | LOW |
| Very specific/niche, almost no results | VERY LOW |

## Keyword Expansion Techniques

### 1. Autocomplete Mining
Search for "{topic} a", "{topic} b", ... "{topic} z" to find autocomplete suggestions.
Also try: "how to {topic}", "why {topic}", "what {topic}"

### 2. Related Searches
At the bottom of Google/Yandex results — "Searches related to..."
Follow the chain: search → collect related → search those → collect more.
2-3 levels deep is usually sufficient.

### 3. Forum Mining
Search forums where your audience asks questions:
- Reddit (use `site:reddit.com`)
- VC.ru / Habr (for Russian tech)
- Quora (for English)
- Stack Overflow (for dev topics)
- Niche forums

### 4. Competitor Content Analysis
WebFetch competitor pages → extract H1/H2 headings → these are their target keywords.

### 5. Question Discovery
Look for patterns: "how to...", "what is...", "why does...", "can I...", "should I..."
These map directly to content opportunities.

## Deduplication

After collecting keywords:
1. Lowercase all
2. Remove exact duplicates
3. Group near-duplicates (singular/plural, slight variations)
4. Keep the highest-volume variant as primary
