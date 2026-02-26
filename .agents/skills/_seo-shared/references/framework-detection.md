# Framework Detection

Detect project framework by checking for config files. Read the first match.

## Detection Rules (check in order)

| Priority | Glob Pattern | Framework | Rendering | SEO Impact |
|----------|-------------|-----------|-----------|------------|
| 1 | `astro.config.*` | Astro | SSG (default) | Excellent |
| 2 | `next.config.*` | Next.js | SSR/SSG hybrid | Excellent |
| 3 | `nuxt.config.*` | Nuxt | SSR (default) | Excellent |
| 4 | `gatsby-config.*` | Gatsby | SSG | Excellent |
| 5 | `hugo.toml` or `config.toml` with `[markup]` | Hugo | SSG | Excellent |
| 6 | `svelte.config.*` | SvelteKit | SSR/SSG | Good |
| 7 | `angular.json` | Angular | CSR | Poor (warn!) |
| 8 | `vite.config.*` + no framework | Vite SPA | CSR | Poor (warn!) |
| 9 | `index.html` in root | Plain HTML | Static | Good |
| 10 | None matched | Unknown | Ask user | — |

## Framework-Specific SEO Notes

### Astro
- Meta tags: in `Layout.astro` via `<head>` section or Astro.props
- `site` property in `astro.config.mjs` required for sitemap
- Sitemap: `@astrojs/sitemap` integration
- All pages are `.astro` files in `src/pages/`
- Static by default — HTML available to all crawlers

### Next.js
- **App Router** (Next 13+): `metadata` export in `layout.tsx`/`page.tsx`, or `generateMetadata()`
- **Pages Router**: `<Head>` component or `next-seo` package
- Sitemap: `next-sitemap` package or `app/sitemap.ts`
- Check `next.config.js` for `images`, `redirects`, `rewrites`
- Hybrid rendering: pages can be SSG, SSR, or CSR

### Nuxt
- Meta tags: `useHead()` composable or `nuxt.config.ts` app.head
- Sitemap: `@nuxtjs/sitemap` module
- SSR by default

### Hugo
- Meta tags: in `layouts/partials/head.html`
- Sitemap: built-in (auto-generated)
- Templates in `layouts/`, content in `content/`

### Plain HTML
- Meta tags: directly in `<head>` of each HTML file
- No build step — changes are immediate
- Sitemap: must be created manually (or via script)

### CSR Frameworks (Angular, Vite SPA)
- **SEO WARNING**: Content invisible to crawlers without JS execution
- Recommend: add SSR/SSG layer (Angular Universal, Vite SSR plugin)
- Or: prerender critical pages to static HTML
