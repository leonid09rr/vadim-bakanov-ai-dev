# MCP Tool Detection & Usage

## Detection Pattern

Try calling each MCP tool with a minimal query. Success = tool available. Error = skip, use fallback.

Claude does not have a "list MCP tools" function. The skill must attempt a call and handle failure gracefully.

## Ahrefs MCP

### Setup
In `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "ahrefs": {
      "command": "npx",
      "args": ["-y", "@ahrefs/mcp"]
    }
  }
}
```
Requires Ahrefs subscription with API access.

### Key Tools
| Tool | Purpose | Input Example |
|------|---------|---------------|
| `domain_rating` | Domain authority score | `{"target": "domain.com"}` |
| `explore_keywords_overview` | Volume, difficulty, CPC for keywords | `{"keywords": ["keyword"], "country": "us"}` |
| `explore_matching_terms` | Related keywords expansion | `{"keyword": "seed term", "country": "us"}` |
| `batch_url_analysis` | Metrics for multiple URLs | `{"urls": ["url1", "url2"]}` |
| `get_serp_overview` | SERP analysis for keyword | `{"keyword": "query", "country": "us"}` |
| `fetch_competitors_overview` | Organic competitors | `{"target": "domain.com"}` |

### Detection Test
Try: `domain_rating` with target domain. If succeeds → Ahrefs available.

## Semrush MCP

### Setup
Follow semrush.com MCP setup guide. Typical config:
```json
{
  "mcpServers": {
    "semrush": {
      "command": "npx",
      "args": ["-y", "@semrush/mcp-server"]
    }
  }
}
```
Requires Semrush subscription.

### Key Tools
| Tool | Purpose | Input Example |
|------|---------|---------------|
| `domain_overview` | Traffic estimates, keywords count | `{"domain": "domain.com"}` |
| `keyword_overview` | Volume, difficulty for keyword | `{"keyword": "...", "database": "us"}` |
| `related_keywords` | Keyword expansion | `{"keyword": "seed"}` |
| `organic_keywords` | Keywords a domain ranks for | `{"domain": "domain.com"}` |

### Detection Test
Try: `domain_overview` with target domain. If succeeds → Semrush available.

## Google Search Console MCP

### Setup
Community MCP server (not official Google):
```json
{
  "mcpServers": {
    "gsc": {
      "command": "npx",
      "args": ["-y", "gsc-mcp-server"],
      "env": {
        "GSC_SERVICE_ACCOUNT_KEY": "/path/to/service-account.json"
      }
    }
  }
}
```
Requires: Google Cloud service account with Search Console API access.

### Key Tools
| Tool | Purpose |
|------|---------|
| `search_analytics` | Query performance: clicks, impressions, position, CTR |
| `list_sitemaps` | Sitemap status |
| `inspect_url` | URL indexation status |

### Detection Test
Try: `search_analytics` with site URL and date range. If succeeds → GSC available.

## DataForSEO (via seo-research skill)

### Availability Check
1. Check if project has `.claude/skills/seo-research/SKILL.md`
2. Check if target market is supported (NOT in sanctions list)
3. Verify API keys: `DATAFORSEO_LOGIN` + `DATAFORSEO_PASSWORD`

### Sanctions List (DataForSEO unavailable)
Russia, Belarus, Iran, North Korea, Cuba, Syria

### When to Use
- Large-scale keyword research (1000+ keywords per competitor)
- Non-sanctioned markets only
- User has DataForSEO API keys

## Fallback: WebSearch

Always available. Works for ALL markets including Russia.

### Priority Order for Data Sources
1. Ahrefs MCP (if available) — best for keyword data + backlinks
2. Semrush MCP (if available) — best for traffic estimates + competitor analysis
3. Google Search Console MCP (if available) — best for real position data (free)
4. DataForSEO / seo-research skill (if available + market supported)
5. **WebSearch** — always works, provides approximate data

### Combining Sources
When multiple sources available:
- Use Ahrefs for keyword volumes and difficulty
- Use Semrush for competitor traffic estimates
- Use GSC for actual position data (most accurate)
- Use WebSearch to fill gaps and validate
