# Position Tracking Setup Guide

## Yandex XML API (Free)

### What It Is
Free API from Yandex that returns search results in XML format. Allows checking actual positions in Yandex search.

### Requirements
- Yandex ID (Яндекс аккаунт)
- Site verified in Yandex Webmaster (webmaster.yandex.ru)

### Setup Steps

1. **Create Yandex ID** (if you don't have one)
   - Go to passport.yandex.ru and register

2. **Verify your site in Yandex Webmaster**
   - Go to webmaster.yandex.ru
   - Add your site
   - Verify ownership (HTML file, meta tag, or DNS record)

3. **Get Yandex XML credentials**
   - Go to xml.yandex.ru
   - Sign in with your Yandex ID
   - Accept terms of service
   - Your `user` and `key` will be displayed on the dashboard

4. **Save credentials**
   Create `~/.claude/skills/seo-positions/.env.local`:
   ```
   YANDEX_XML_USER=your-yandex-login
   YANDEX_XML_KEY=your-api-key-here
   ```

5. **Test**
   ```bash
   cd ~/.claude/skills/seo-positions
   uv run scripts/yandex-xml-check.py --domain yourdomain.com --keywords "test keyword" --region 213
   ```

### Free Limits
- 10 to 1000 requests per day (depends on your site's ICS/IKS rating)
- New sites typically get 10-100 requests/day
- Limit increases as your site grows
- Check your limit at xml.yandex.ru dashboard

### Region Codes
| Code | Region |
|------|--------|
| 213 | Moscow |
| 2 | Saint Petersburg |
| 54 | Yekaterinburg |
| 43 | Kazan |
| 0 | All Russia |

Full list: xml.yandex.ru/settings

### Important Notes
- Yandex Cloud (console.yandex.cloud) is a DIFFERENT service — you do NOT need it for XML API
- Yandex XML is completely free
- Results match actual Yandex search output
- Rate limit: 1 request per second recommended

---

## Google Search Console (Free)

### What It Is
Google's free tool showing your site's performance in Google search: queries, clicks, impressions, average position.

### Setup Steps

1. **Go to** search.google.com/search-console
2. **Add property** → Enter your domain
3. **Verify ownership** (DNS record, HTML file, meta tag, or Google Analytics)
4. **Wait for data** — takes a few days to accumulate

### MCP Integration (Optional)
For automated access from Claude Code, set up GSC MCP server.
See `~/.claude/skills/_seo-shared/references/mcp-integration.md` for config.

### Without MCP
Manually check positions at search.google.com/search-console:
- Performance → Search Results
- Filter by query, date range, country
- Export CSV for analysis

---

## Ahrefs / Semrush (Paid, Optional)

### Ahrefs
- Subscription required (from $99/month)
- MCP: `@ahrefs/mcp` — see mcp-integration.md
- Provides: keyword positions, domain rating, backlinks, competitor analysis

### Semrush
- Subscription required (from $129/month)
- MCP: see mcp-integration.md
- Provides: keyword positions, traffic estimates, competitor keywords

Both provide more comprehensive data than free tools, but free tools (Yandex XML + GSC) cover the basics for position monitoring.

---

## WebSearch Spot-Check (Always Available)

When no API is set up, the skill uses Claude's WebSearch to check positions:
- Search for each keyword
- Check if your domain appears in results
- Estimate position based on result order

This is approximate but works immediately without any setup. Good for quick checks.

---

## Recommended Setup for Russian Market

| Priority | Tool | Cost | What You Get |
|----------|------|------|-------------|
| 1 | Yandex Webmaster | Free | Yandex indexation, errors, basic queries |
| 2 | Yandex XML API | Free | Exact Yandex positions for any keyword |
| 3 | Google Search Console | Free | Google positions, clicks, impressions |
| 4 | Ahrefs or Semrush MCP | Paid | Full competitive intelligence |
