import type { KnowledgePage } from "./types";
import { contact, ctas } from "../companyFacts";

export const marketIndonesia: KnowledgePage = {
  path: "/markets/indonesia-electric-motorcycle-importer",
  seo: {
    title: "Electric Motorcycle Importer & Supplier for Indonesia | STARGO Factory-Direct",
    description:
      "Import STARGO electric motorcycles into Indonesia factory-direct. 80+ export-ready models, mixed containers from 10 units, CBU/SKD/CKD for local assembly programs, Form E support, and OEM/ODM branding.",
    ogImage: "/og/market-indonesia.jpg",
  },
  breadcrumb: [
    { name: "Home", path: "/" },
    { name: "Markets", path: "/markets" },
    { name: "Indonesia", path: "/markets/indonesia-electric-motorcycle-importer" },
  ],
  hero: {
    eyebrow: "Indonesia",
    h1: "Electric Motorcycles for Indonesia Importers",
    subtitle:
      "Factory-direct supply for the world's largest two-wheeler markets — structured for importers and assemblers building local-content programs in Indonesia.",
  },
  blocks: [
    {
      kind: "prose",
      heading: "Why STARGO for Indonesia",
      paragraphs: [
        "Indonesia's electric two-wheeler push rewards importers who can balance price, local assembly and reliable supply. STARGO ships factory-direct and supports CKD/SKD for importers running or planning local-content assembly.",
        "Across 80+ export-ready models (83 listed configurations) and lead-acid, graphene and lithium platforms, you can serve both entry-level and premium Indonesian buyers.",
      ],
    },
    {
      kind: "cards",
      heading: "What importers get",
      items: [
        { title: "CKD / SKD for local assembly", body: "Completely or semi knocked-down kits support local-content programs and reduce import duty." },
        { title: "Form E duty advantage", body: "As an ASEAN destination, Indonesia can use Form E for preferential import duty on eligible shipments." },
        { title: "Mixed containers from 10 units", body: "MOQ is 10 units with mixed-model containers accepted — ideal for testing the market." },
        { title: "OEM / ODM branding", body: "Launch a local brand with custom colors, configurations and documentation." },
      ],
    },
    {
      kind: "steps",
      heading: "How to start as an Indonesian importer",
      steps: [
        { title: "Define your program", body: "Tell us whether you import CBU or run SKD/CKD local assembly, and your target segments." },
        { title: "Get a model & battery plan", body: "We propose models and battery platforms (lead-acid / graphene / lithium) for your price points." },
        { title: "Confirm kits & documents", body: "Lock SKD/CKD kit scope, Form E, and battery UN38.3/MSDS where lithium is involved." },
        { title: "Mixed-container proposal", body: "Receive a factory-direct quote and loading plan for your first shipment." },
      ],
    },
  ],
  faq: [
    { q: "Does STARGO support local assembly in Indonesia?", a: "Yes. STARGO supplies SKD and CKD kits that support local assembly and local-content programs, in addition to fully built CBU units." },
    { q: "Can Indonesia use Form E?", a: "Yes. Indonesia is an ASEAN destination, so eligible shipments can use Form E (the ASEAN–China FTA Certificate of Origin) for preferential import duty." },
    { q: "What is the minimum order for Indonesia?", a: "MOQ is 10 units and mixed-model containers are accepted, so importers can trial several models in one shipment." },
    { q: "Can STARGO build under our Indonesian brand?", a: "Yes. Full OEM/ODM support is available, including custom branding, colors, configurations and documentation." },
  ],
  cta: {
    heading: "Plan your Indonesia import program",
    body: "Request a factory price list and a CBU/SKD/CKD proposal for the Indonesian market.",
    primaryLabel: ctas.becomeDealer,
    primaryHref: "/contact",
    secondaryLabel: "WhatsApp sales",
    secondaryHref: contact.whatsappLink,
  },
  article: { datePublished: "2026-02-05", section: "Markets" },
};
