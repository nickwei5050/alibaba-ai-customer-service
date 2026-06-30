import type { KnowledgePage } from "./types";
import { contact, ctas } from "../companyFacts";

export const marketVietnam: KnowledgePage = {
  path: "/markets/vietnam-electric-scooter-distributor",
  seo: {
    title: "Electric Scooter Distributor & Supplier for Vietnam | STARGO Factory-Direct",
    description:
      "Become a STARGO electric scooter distributor in Vietnam. Factory-direct pricing, 80+ export-ready models, mixed containers from 10 units, CBU/SKD/CKD, Form E support, and OEM/ODM for the Vietnamese market.",
    ogImage: "/og/market-vietnam.jpg",
  },
  breadcrumb: [
    { name: "Home", path: "/" },
    { name: "Markets", path: "/markets" },
    { name: "Vietnam", path: "/markets/vietnam-electric-scooter-distributor" },
  ],
  hero: {
    eyebrow: "Vietnam",
    h1: "Electric Scooters for Vietnam Distributors",
    subtitle:
      "Factory-direct supply for one of Asia's fastest-moving two-wheeler markets — built for dealers, distributors and fleet operators in Vietnam.",
  },
  blocks: [
    {
      kind: "prose",
      heading: "Why STARGO for the Vietnamese market",
      paragraphs: [
        "Vietnam runs on two wheels, and electric is taking share fast. STARGO supplies electric scooters and motorcycles factory-direct, so distributors capture margin instead of paying a trading-company markup.",
        "With 80+ export-ready models (83 listed configurations) and all three battery platforms, you can build a line-up that spans price-first to premium segments.",
      ],
    },
    {
      kind: "cards",
      heading: "What distributors get",
      items: [
        { title: "Form E duty advantage", body: "As an ASEAN destination, Vietnam can use Form E (ASEAN–China FTA CO) for preferential import duty." },
        { title: "Mixed containers from 10 units", body: "Test multiple models in one shipment — MOQ is 10 units with mixed-model containers accepted." },
        { title: "CBU / SKD / CKD", body: "Choose CBU to sell on arrival, or SKD/CKD to optimise duty and support local assembly." },
        { title: "OEM / ODM branding", body: "Launch under your own brand with custom colors, configurations and documentation." },
      ],
    },
    {
      kind: "steps",
      heading: "How to start as a Vietnam distributor",
      steps: [
        { title: "Share your target segment", body: "Tell us your price points and the cities or provinces you serve." },
        { title: "Get a model & battery plan", body: "We propose a model mix and battery platforms (lead-acid / graphene / lithium) to match." },
        { title: "Confirm export mode & docs", body: "Pick CBU/SKD/CKD and confirm Form E plus battery UN38.3/MSDS where lithium is involved." },
        { title: "Mixed-container proposal", body: "Receive a factory-direct quote and a mixed-container loading plan." },
      ],
    },
  ],
  faq: [
    { q: "Does STARGO support Form E for Vietnam?", a: "Yes. Vietnam is an ASEAN destination, so eligible shipments can use Form E (the ASEAN–China FTA Certificate of Origin) for preferential import duty." },
    { q: "What is the minimum order for a Vietnamese distributor?", a: "MOQ is 10 units, and mixed-model containers are accepted so you can trial several models at once." },
    { q: "Can I sell under my own brand in Vietnam?", a: "Yes. STARGO provides OEM/ODM support with custom branding, colors, configurations and documentation." },
    { q: "Which export mode is best for Vietnam?", a: "CBU lets you sell immediately on arrival; SKD or CKD can reduce import duty and support local assembly. We'll advise based on your volumes and goals." },
  ],
  cta: {
    heading: "Build your Vietnam line-up",
    body: "Request a factory price list and a mixed-container proposal for the Vietnamese market.",
    primaryLabel: ctas.becomeDealer,
    primaryHref: "/contact",
    secondaryLabel: "WhatsApp sales",
    secondaryHref: contact.whatsappLink,
  },
  article: { datePublished: "2026-02-01", section: "Markets" },
};
