# DataForSEO Location Codes

This directory contains reference data for DataForSEO API configuration.

## Files

- **dataforseo-locations.csv** - All available location codes (74,194+ locations)

## Location Codes

DataForSEO uses location codes to specify which country/region to use for SERP data and keyword rankings.

### Format

Each location has:
- `location_code` - Numeric code (e.g., 2840)
- `location_name` - Human-readable name (e.g., "United States")
- `location_type` - Country, State, City, County, etc.
- `country_iso_code` - 2-letter ISO code (e.g., "US")
- `location_code_parent` - Parent location code (if applicable)

### Common Countries

| Code | Country | ISO |
|------|---------|-----|
| 2840 | United States | US |
| 2826 | United Kingdom | GB |
| 2124 | Canada | CA |
| 2036 | Australia | AU |
| 2276 | Germany | DE |
| 2250 | France | FR |
| 2380 | Italy | IT |
| 2724 | Spain | ES |
| 2392 | Japan | JP |
| 2356 | India | IN |
| 2156 | China | CN |
| 2804 | Ukraine | UA |

## Missing Countries

The following countries are **NOT available** in DataForSEO (based on Google Ads geographical targeting):

- **Russia** (RU) - not available
- **Belarus** (BY) - not available
- **Iran** (IR) - not available
- **North Korea** (KP) - not available
- **Cuba** (CU) - not available
- **Syria** (SY) - not available

This is due to Google Ads restrictions in these countries (sanctions, service limitations, etc.).

## Usage

When configuring SEO research projects, use the `location_code` in the config:

```json
{
  "dataforseo_params": {
    "language_code": "en",
    "location_code": 2840
  }
}
```

## Updating Data

To refresh the location list:

```bash
cd /Users/alext/Projects/kb/.claude/skills/seo-research
source .env.local
uv run scripts/fetch_locations.py
```

**Note:** This API call is free and doesn't consume DataForSEO credits.

## References

- [DataForSEO Keywords Data Locations API](https://docs.dataforseo.com/v3/keywords_data-google-locations/)
- [Google Geographical Targeting](https://developers.google.com/google-ads/api/data/geotargets)
