# Technical SEO Checklist

## Meta Tags

### Title Tag
- **Required**: yes
- **Length**: 50-60 characters
- **Rules**: unique per page, contains primary keyword, attractive for clicks
- **Format**: "Keyword Phrase | Brand" or "Keyword Phrase - Detail | Brand"

### Meta Description
- **Required**: yes
- **Length**: 150-160 characters
- **Rules**: unique per page, contains keywords naturally, includes CTA, accurately describes page

### Meta Robots
- `<meta name="robots" content="index, follow">` for indexable pages
- `noindex, nofollow` only for service pages (checkout, success, fail)

### Canonical URL
- `<link rel="canonical" href="{full_url}">` on every page
- Must be absolute URL (with https://)
- Must match the actual URL (no trailing slash mismatch)

### Viewport
- `<meta name="viewport" content="width=device-width, initial-scale=1">`

## Open Graph & Social

### Required OG Tags
```html
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{absolute_url_to_image}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:type" content="website">
```

### Twitter Card (optional but recommended)
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{absolute_url_to_image}">
```

## URL Structure
- Short, descriptive, contains keywords
- Uses hyphens (not underscores)
- HTTPS only
- No session IDs or unnecessary parameters
- Consistent trailing slash policy

## Mobile
- Responsive design (no fixed widths)
- Touch targets >= 48x48px
- No horizontal scroll
- Text readable without zoom (>= 16px base)

## Performance
- Total load time < 3 seconds
- LCP (Largest Contentful Paint) < 2.5s
- INP (Interaction to Next Paint) < 200ms
- CLS (Cumulative Layout Shift) < 0.1

### Images
- Compressed (WebP/AVIF where possible)
- Lazy loading for below-fold images (`loading="lazy"`)
- Explicit `width` and `height` attributes
- Alt text on every image
- Size: < 200KB for regular, < 500KB for hero

### CSS/JS
- Minified in production
- Critical CSS inlined
- Non-essential scripts deferred (`defer` or `async`)
- Unused CSS/JS removed

### Fonts
- `font-display: swap`
- Preload critical fonts: `<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>`

## Rendering
- Content available without JavaScript execution
- View Page Source shows full content
- SSG or SSR for SEO-critical pages (NOT client-side rendering)

## Indexation Control

### robots.txt
- Does not block important pages
- Does not block CSS/JS needed for rendering
- References sitemap: `Sitemap: https://domain.com/sitemap.xml`
- AI crawlers explicitly allowed (see aeo-checklist.md)

### XML Sitemap
- Exists and is accessible
- Submitted to search engines (Google Search Console, Yandex Webmaster)
- No 404 URLs
- `<lastmod>` dates present and accurate
- `<priority>` and `<changefreq>` set appropriately

## Security
- HTTPS with valid SSL certificate
- No mixed content (HTTP resources on HTTPS page)
- Security headers: `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`

## HTML Validation
- Valid HTML (W3C compliant)
- No duplicate IDs
- Semantic elements: `<header>`, `<nav>`, `<main>`, `<article>`, `<aside>`, `<footer>`
