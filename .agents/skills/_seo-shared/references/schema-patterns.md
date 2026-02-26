# Schema.org JSON-LD Templates

Ready-to-use templates. Replace `{placeholders}` with actual values.

## Organization (homepage)

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{Company Name}",
  "url": "{https://domain.com}",
  "logo": "{https://domain.com/logo.png}",
  "description": "{Company description}",
  "sameAs": [
    "{https://t.me/channel}",
    "{https://youtube.com/@channel}"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "email": "{email@domain.com}"
  }
}
```

## Course (education product)

```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "{Course Title}",
  "description": "{Course description}",
  "url": "{https://domain.com/course}",
  "provider": {
    "@type": "Organization",
    "name": "{Provider Name}",
    "url": "{https://domain.com}"
  },
  "instructor": {
    "@type": "Person",
    "name": "{Instructor Name}"
  },
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "online",
    "startDate": "{2026-03-01}",
    "duration": "{P10W}"
  },
  "offers": {
    "@type": "Offer",
    "price": "{price}",
    "priceCurrency": "{RUB}",
    "availability": "https://schema.org/InStock",
    "url": "{https://domain.com/course/checkout}"
  }
}
```

## Event (conference, webinar)

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "{Event Title}",
  "description": "{Event description}",
  "url": "{https://domain.com/events}",
  "startDate": "{2026-01-22T18:00:00+03:00}",
  "endDate": "{2026-01-23T20:00:00+03:00}",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
  "location": {
    "@type": "VirtualLocation",
    "url": "{https://domain.com/events}"
  },
  "organizer": {
    "@type": "Organization",
    "name": "{Organizer Name}",
    "url": "{https://domain.com}"
  },
  "performer": [
    {
      "@type": "Person",
      "name": "{Speaker Name}"
    }
  ],
  "image": "{https://domain.com/event-og.jpg}"
}
```

## Article / TechArticle (blog posts)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{Article Title}",
  "description": "{Short description}",
  "url": "{https://domain.com/blog/article-slug}",
  "datePublished": "{2026-02-23}",
  "dateModified": "{2026-02-23}",
  "author": {
    "@type": "Person",
    "name": "{Author Name}",
    "url": "{https://domain.com/about}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "{Publisher Name}",
    "logo": {
      "@type": "ImageObject",
      "url": "{https://domain.com/logo.png}"
    }
  },
  "image": "{https://domain.com/blog/article-og.jpg}",
  "mainEntityOfPage": "{https://domain.com/blog/article-slug}"
}
```

Use `"@type": "TechArticle"` for technical guides and tutorials.

## FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{Question text?}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{Answer text}"
      }
    }
  ]
}
```

Note: Google deprecated FAQPage rich results for most sites (Aug 2023), but the markup still helps AI search engines extract Q&A pairs.

## BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "{Home}",
      "item": "{https://domain.com}"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "{Section}",
      "item": "{https://domain.com/section}"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "{Current Page}"
    }
  ]
}
```

## VideoObject

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "{Video Title}",
  "description": "{Video description}",
  "thumbnailUrl": "{https://domain.com/video-thumb.jpg}",
  "uploadDate": "{2026-01-22}",
  "duration": "{PT2H8M}",
  "contentUrl": "{video-url}",
  "embedUrl": "{embed-url}"
}
```

## Product (purchase page)

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{Product Name}",
  "description": "{Product description}",
  "url": "{https://domain.com/product}",
  "image": "{https://domain.com/product.jpg}",
  "offers": {
    "@type": "Offer",
    "price": "{price}",
    "priceCurrency": "{RUB}",
    "availability": "https://schema.org/InStock",
    "url": "{https://domain.com/product/checkout}"
  }
}
```

## WebSite + SearchAction (site-wide, for sitelinks searchbox)

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{Site Name}",
  "url": "{https://domain.com}",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "{https://domain.com/search?q={search_term_string}}",
    "query-input": "required name=search_term_string"
  }
}
```

Only use SearchAction if the site has a search function.

## Combining Multiple Schemas

Place multiple schemas in an array on the same page:

```html
<script type="application/ld+json">
[
  { "@context": "https://schema.org", "@type": "Organization", ... },
  { "@context": "https://schema.org", "@type": "BreadcrumbList", ... }
]
</script>
```

Or use separate `<script>` tags for each schema — both are valid.
