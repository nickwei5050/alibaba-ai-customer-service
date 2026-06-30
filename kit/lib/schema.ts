/**
 * schema.ts — JSON-LD (schema.org) generators for STARGO.
 *
 * Render the returned object inside:
 *   <script type="application/ld+json"
 *     dangerouslySetInnerHTML={{ __html: JSON.stringify(orgSchema()) }} />
 *
 * In Next.js App Router you can also return these from a Server Component.
 * RULE: no fake prices, no unsupported certifications.
 */

import {
  SITE_URL,
  company,
  contact,
  markets,
  productCategories,
} from "./companyFacts";

const ORG_ID = `${SITE_URL}/#organization`;
const WEBSITE_ID = `${SITE_URL}/#website`;

export function organizationSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    "@id": ORG_ID,
    name: company.brandFull,
    alternateName: company.brand,
    legalName: company.legalEntity,
    url: SITE_URL,
    logo: `${SITE_URL}/logo.png`,
    description: company.positioning,
    areaServed: markets.map((m) => ({ "@type": "Place", name: m })),
    knowsAbout: productCategories.map((c) => c.name),
    contactPoint: [
      {
        "@type": "ContactPoint",
        contactType: "sales",
        email: contact.salesEmail,
        telephone: contact.whatsappE164,
        availableLanguage: ["en", "es", "id", "zh"],
        areaServed: markets,
      },
    ],
  };
}

export function websiteSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": WEBSITE_ID,
    url: SITE_URL,
    name: company.brandFull,
    publisher: { "@id": ORG_ID },
    inLanguage: ["en", "es", "id"],
  };
}

/** items: ordered [{ name, path }] from home to current page (path starts with "/"). */
export function breadcrumbSchema(items: { name: string; path: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: `${SITE_URL}${item.path}`,
    })),
  };
}

type ProductInput = {
  name: string;
  slug: string;
  description: string;
  image?: string | string[];
  category?: string;
  /** Spec rows surfaced as additionalProperty. */
  specs?: { name: string; value: string }[];
};

/**
 * Product schema WITHOUT Offer/price — prices are quote-only for B2B export,
 * so we deliberately omit `offers` to avoid fabricating price data.
 */
export function productSchema(p: ProductInput) {
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: p.name,
    sku: p.slug,
    description: p.description,
    image: p.image
      ? Array.isArray(p.image)
        ? p.image.map((i) => (i.startsWith("http") ? i : `${SITE_URL}${i}`))
        : p.image.startsWith("http")
          ? p.image
          : `${SITE_URL}${p.image}`
      : undefined,
    brand: { "@type": "Brand", name: company.brand },
    manufacturer: { "@id": ORG_ID },
    category: p.category,
    url: `${SITE_URL}/products/${p.slug}`,
    additionalProperty: p.specs?.map((s) => ({
      "@type": "PropertyValue",
      name: s.name,
      value: s.value,
    })),
  };
}

export function faqSchema(faqs: { q: string; a: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.q,
      acceptedAnswer: { "@type": "Answer", text: f.a },
    })),
  };
}

type ArticleInput = {
  title: string;
  slug: string;
  description: string;
  datePublished: string; // ISO
  dateModified?: string; // ISO
  image?: string;
  section?: string;
};

export function articleSchema(a: ArticleInput) {
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: a.title,
    description: a.description,
    datePublished: a.datePublished,
    dateModified: a.dateModified ?? a.datePublished,
    image: a.image
      ? a.image.startsWith("http")
        ? a.image
        : `${SITE_URL}${a.image}`
      : `${SITE_URL}/og/default.jpg`,
    articleSection: a.section,
    mainEntityOfPage: `${SITE_URL}/news/${a.slug}`,
    author: { "@id": ORG_ID },
    publisher: { "@id": ORG_ID },
  };
}

/** Convenience: stringify for a <script> tag. */
export function jsonLd(obj: unknown) {
  return JSON.stringify(obj).replace(/</g, "\\u003c");
}
