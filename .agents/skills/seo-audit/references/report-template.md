# SEO Audit Report Template

Use this format for all audit reports.

```markdown
# SEO + AEO Audit: {Site Name or Page Title}

## Summary
- **Framework**: {detected framework} ({rendering strategy})
- **Locale**: {market} ({language})
- **Pages audited**: {N}
- **Date**: {YYYY-MM-DD}
- **SEO Score**: {X}/100
- **AEO Score**: {X}/100
- **Combined Score**: {X}/100

{If MCP data available:}
- **Domain Rating**: {X} (Ahrefs)
- **Referring Domains**: {N}
- **Organic Keywords**: {N} (Semrush)

## Passes
### SEO
- {List of passed checks}

### AEO
- {List of passed checks}

## Findings

### CRITICAL — fix immediately
1. **{Issue title}** — {affected pages} — [{SEO|AEO}]
   {Why it matters: 1 sentence}
   ```{language}
   {Exact code/instruction to fix}
   ```

### HIGH — fix soon
1. **{Issue title}** — {affected pages} — [{SEO|AEO}]
   {Description}
   ```{language}
   {Fix}
   ```

### MEDIUM — nice to have
1. **{Issue title}** — {affected pages} — [{SEO|AEO}]
   {Description}

## Page-by-Page Scores
| Page | URL | SEO | AEO | Critical | High | Medium |
|------|-----|-----|-----|----------|------|--------|
| {name} | {url} | {X} | {X} | {N} | {N} | {N} |

## Generated Schema.org Markup

### {Page Name} — {Schema Type}
```json
{Complete JSON-LD ready to paste}
```

### {Page Name} — {Schema Type}
```json
{Complete JSON-LD ready to paste}
```

## Recommendations

### Quick Wins (1-2 days)
- {Actionable item}

### Medium-term (1-2 weeks)
- {Actionable item}

### Long-term (1+ month)
- {Actionable item}
```

## Scoring Notes

When calculating scores:
- Start at 100, subtract for each missing/failed check
- Weight by severity (critical checks worth more)
- See SKILL.md Scoring Guide for exact weights
- Round to nearest integer
- Combined = (SEO × 0.6) + (AEO × 0.4)
