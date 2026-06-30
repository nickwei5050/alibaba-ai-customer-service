# STARGO Upgrade Kit — Integration Guide

This `kit/` folder is a **portable, drop-in set of SEO / GEO / data-consistency
assets** for the STARGO website. It was authored in a session that did **not**
have access to the live `stargo` Next.js repo, so it is intentionally
**framework-agnostic data + helpers** rather than edits to your existing pages.

It does **not** touch, replace, or weaken your GSAP / React Bits / 3D / particle
animation system. It supplies the content and metadata layer the upgrade brief
asks for; you render it with **your existing premium components**.

> Recommended home for the real work: `nickwei5050/stargo`. Copy these files in,
> then wire them into your pages.

## What's inside

| File | Purpose |
|------|---------|
| `lib/companyFacts.ts` | **Single source of truth.** Brand, legal entity, MOQ, contact, export modes, OBSIDIAN spec, normalized model-range statement. Import everywhere. |
| `lib/schema.ts` | JSON-LD generators: Organization, WebSite, BreadcrumbList, Product, FAQPage, BlogPosting (no fake prices/certs). |
| `lib/seo.ts` | Next.js `Metadata` builder: unique title/description, canonical, OG, Twitter, robots, hreflang (en/es/id/x-default). |
| `lib/useReducedMotion.ts` | `useAnimationTier()` → `full` (desktop) / `lite` (mobile) / `static` (reduced-motion). Degrades effects, never deletes them. |
| `lib/content/*` | Structured content for the 5 GEO/AI pages (factory profile, export docs, battery comparison, Vietnam, Indonesia). |
| `components/KnowledgePageView.tsx` | **Optional** reference renderer showing how to render the content data + dynamic-import a heavy effect. Swap `<Reveal>`/`<Particles>` for your real components. |
| `public/llms.txt` | The AI-search summary file. Serve at `/llms.txt`. |
| `app/llms.txt/route.ts` | Optional dynamic route for `/llms.txt` (use this OR the static file, not both). |

## Step-by-step integration (in the `stargo` repo)

1. **Copy** `kit/lib/*` into your `src/lib/` (or `lib/`), `kit/public/llms.txt`
   into `public/`, and `kit/components/*` into your components dir. Adjust the
   `@/` import paths to match your alias.
2. **Replace inconsistent claims.** Search the repo for `60+`, `80+`, `83`,
   and any OBSIDIAN voltage/power/range numbers, and replace with
   `modelRange.statement` / `obsidian.statement` from `companyFacts.ts`.
   See `NORMALIZATION.md`.
3. **Wire SEO.** In each `page.tsx`, add
   `export const metadata = buildMetadata({ ... })` using `lib/seo.ts`.
4. **Add JSON-LD.** Render `organizationSchema()` + `websiteSchema()` on the
   homepage, `breadcrumbSchema()` on inner pages, `productSchema()` on product
   pages, `faqSchema()` where FAQs are visible, `articleSchema()` on news.
5. **Create the 5 GEO pages** at the paths in each content file's `path`, e.g.
   `app/knowledge/stargo-factory-profile/page.tsx`, rendering the content with
   your premium components (or the reference `KnowledgePageView`).
6. **Ship `/llms.txt`** (keep the static `public/llms.txt`; delete the route, or
   vice-versa).
7. **Localization:** for `/es` and `/id`, either translate fully (then set
   `availableLocales: ["en","es","id"]` in `buildMetadata`) or pass
   `noindex: true` until translated. Never serve English metadata on a
   localized URL.
8. **Performance:** wrap heavy effects with `useAnimationTier()` and
   `next/dynamic(() => import(...), { ssr:false })`; convert large images to
   WebP/AVIF; preload only the true hero image; add width/height to all images.

## Guardrails (from the brief)
- Do **not** flatten the design or remove animations.
- Performance only via lazy-load / dynamic import / image compression / mobile-lite.
- No fake certifications, prices, awards, customer cases, or factory numbers.
