/**
 * Structured content for the GEO / AI-search knowledge & market pages.
 *
 * This is DATA only — render it with your existing premium GSAP / 3D / animated
 * components. Each page exposes: SEO metadata, breadcrumb, hero, rich sections
 * (prose, card grids, comparison tables, icon stats), an FAQ (also emitted as
 * FAQPage JSON-LD), and CTA blocks. Nothing here touches your animation system.
 */

export type CardItem = { title: string; body: string; icon?: string };

export type TableBlock = {
  kind: "table";
  heading?: string;
  columns: string[];
  rows: string[][];
  note?: string;
};

export type CardsBlock = {
  kind: "cards";
  heading?: string;
  items: CardItem[];
};

export type ProseBlock = {
  kind: "prose";
  heading?: string;
  paragraphs: string[];
};

export type StatsBlock = {
  kind: "stats";
  heading?: string;
  items: { value: string; label: string }[];
};

export type StepsBlock = {
  kind: "steps";
  heading?: string;
  steps: { title: string; body: string }[];
};

export type ContentBlock =
  | ProseBlock
  | CardsBlock
  | TableBlock
  | StatsBlock
  | StepsBlock;

export type Faq = { q: string; a: string };

export type CtaBlock = {
  heading: string;
  body: string;
  primaryLabel: string;
  primaryHref: string;
  secondaryLabel?: string;
  secondaryHref?: string;
};

export type KnowledgePage = {
  /** Canonical path, e.g. "/knowledge/stargo-factory-profile". */
  path: string;
  seo: { title: string; description: string; ogImage?: string };
  breadcrumb: { name: string; path: string }[];
  hero: { eyebrow: string; h1: string; subtitle: string };
  blocks: ContentBlock[];
  faq: Faq[];
  cta: CtaBlock;
  /** For Article/BlogPosting schema where the page is editorial. */
  article?: { datePublished: string; section: string };
};
