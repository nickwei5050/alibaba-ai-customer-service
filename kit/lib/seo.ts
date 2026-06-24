/**
 * seo.ts — Next.js App Router Metadata helper for STARGO.
 *
 * Usage in any page.tsx / layout.tsx:
 *
 *   import { buildMetadata } from "@/lib/seo";
 *   export const metadata = buildMetadata({
 *     title: "Electric Scooters | STARGO Motor",
 *     description: "...",
 *     path: "/products/electric-scooters",
 *     ogImage: "/og/scooters.jpg",
 *     locale: "en",
 *   });
 *
 * Handles: unique title/description, canonical, Open Graph, Twitter Card,
 * robots, and hreflang alternates (en / es / id / x-default).
 */

import type { Metadata } from "next";
import { SITE_URL, company } from "./companyFacts";

export type Locale = "en" | "es" | "id";

const LOCALE_OG: Record<Locale, string> = {
  en: "en_US",
  es: "es_ES",
  id: "id_ID",
};

/** Map an English path + locale to the localized URL. en lives at root. */
function localizedUrl(path: string, locale: Locale): string {
  const clean = path.startsWith("/") ? path : `/${path}`;
  return locale === "en" ? `${SITE_URL}${clean}` : `${SITE_URL}/${locale}${clean}`;
}

type SeoInput = {
  title: string;
  description: string;
  /** English-canonical path, e.g. "/battery". Root is "/". */
  path: string;
  ogImage?: string;
  locale?: Locale;
  /** Set true for incomplete localized pages until real translation exists. */
  noindex?: boolean;
  /** Locales that actually have a translated page — controls hreflang output. */
  availableLocales?: Locale[];
  type?: "website" | "article";
};

export function buildMetadata({
  title,
  description,
  path,
  ogImage = "/og/default.jpg",
  locale = "en",
  noindex = false,
  availableLocales = ["en"],
  type = "website",
}: SeoInput): Metadata {
  const canonical = localizedUrl(path, locale);
  const ogImageUrl = ogImage.startsWith("http") ? ogImage : `${SITE_URL}${ogImage}`;

  // hreflang alternates only for locales that are genuinely translated.
  const languages: Record<string, string> = {};
  for (const loc of availableLocales) languages[loc] = localizedUrl(path, loc);
  if (availableLocales.includes("en")) {
    languages["x-default"] = localizedUrl(path, "en");
  }

  return {
    metadataBase: new URL(SITE_URL),
    title,
    description,
    alternates: { canonical, languages },
    robots: noindex
      ? { index: false, follow: true }
      : { index: true, follow: true, googleBot: { index: true, follow: true } },
    openGraph: {
      type,
      url: canonical,
      title,
      description,
      siteName: company.brandFull,
      locale: LOCALE_OG[locale],
      images: [{ url: ogImageUrl, width: 1200, height: 630, alt: title }],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [ogImageUrl],
    },
  };
}
