import type { KnowledgePage } from "./types";
import { contact, ctas } from "../companyFacts";

export const exportDocuments: KnowledgePage = {
  path: "/knowledge/electric-vehicle-export-documents",
  seo: {
    title: "Electric Vehicle Export Documents Explained | CI, PL, CO, Form E, B/L, UN38.3 & MSDS",
    description:
      "A dealer's guide to the documents needed to import electric scooters, motorcycles and EV batteries: Commercial Invoice, Packing List, Certificate of Origin, Form E, Bill of Lading, plus battery UN38.3 and MSDS.",
    ogImage: "/og/export-documents.jpg",
  },
  breadcrumb: [
    { name: "Home", path: "/" },
    { name: "Knowledge", path: "/knowledge" },
    { name: "EV Export Documents", path: "/knowledge/electric-vehicle-export-documents" },
  ],
  hero: {
    eyebrow: "Export Guide",
    h1: "Electric Vehicle Export Documents, Explained",
    subtitle:
      "What every importer needs when bringing electric two-wheelers, three-wheelers and EV batteries across borders — and how STARGO prepares each document.",
  },
  blocks: [
    {
      kind: "prose",
      heading: "Why documentation makes or breaks a shipment",
      paragraphs: [
        "Customs clearance for electric vehicles depends on accurate paperwork. Missing or inconsistent documents are the most common cause of delays, demurrage charges and duty disputes.",
        "STARGO prepares shipping documents in-house and confirms battery documents per battery model and configuration, so the paperwork matches the goods in the container.",
      ],
    },
    {
      kind: "table",
      heading: "Core shipping documents",
      columns: ["Document", "Full name", "What it does"],
      rows: [
        ["CI", "Commercial Invoice", "States the commercial value and terms of sale for customs valuation."],
        ["PL", "Packing List", "Lists cartons, quantities, weights and dimensions for inspection."],
        ["CO", "Certificate of Origin", "Certifies where the goods were manufactured."],
        ["Form E", "ASEAN–China FTA Certificate of Origin", "Enables preferential import duty for eligible ASEAN destinations."],
        ["B/L", "Bill of Lading", "Carrier's contract and title document for the cargo."],
      ],
    },
    {
      kind: "table",
      heading: "Battery documents (lithium)",
      columns: ["Document", "Purpose"],
      rows: [
        ["UN38.3", "Transport test summary required to ship lithium batteries by sea or air."],
        ["MSDS", "Material Safety Data Sheet describing the battery's safety profile."],
      ],
      note: "Battery documents such as UN38.3 and MSDS are confirmed per battery model and configuration.",
    },
    {
      kind: "cards",
      heading: "Tips for first-time importers",
      items: [
        { title: "Check Form E eligibility early", body: "If you import into an ASEAN country, confirm Form E applies before you book — it can significantly reduce duty." },
        { title: "Match battery docs to chemistry", body: "Lithium shipments need UN38.3 and MSDS that match the exact battery configuration ordered." },
        { title: "Reconcile CI and PL", body: "Values and quantities on the invoice and packing list must agree to avoid clearance holds." },
        { title: "Confirm the port of discharge", body: "Lock the delivery port up front so the B/L and routing are correct." },
      ],
    },
  ],
  faq: [
    { q: "Which documents does STARGO provide for an EV shipment?", a: "STARGO prepares CI (Commercial Invoice), PL (Packing List), CO (Certificate of Origin), Form E where applicable, and the B/L (Bill of Lading). Battery shipments also include UN38.3 and MSDS confirmed per configuration." },
    { q: "What is Form E and do I need it?", a: "Form E is the ASEAN–China Free Trade Area Certificate of Origin. If you import into an eligible ASEAN country it can reduce or eliminate import duty." },
    { q: "Do lithium batteries need special documents?", a: "Yes. Lithium batteries require a UN38.3 transport test summary and an MSDS, both confirmed per battery model and configuration." },
    { q: "Can STARGO ship mixed models in one container?", a: "Yes. The MOQ is 10 units and mixed-model containers are accepted, with documentation prepared for the combined shipment." },
  ],
  cta: {
    heading: "Need a documentation checklist for your country?",
    body: "Tell us your destination port and models — we'll confirm the exact documents your import requires.",
    primaryLabel: ctas.requestQuote,
    primaryHref: "/contact",
    secondaryLabel: "WhatsApp sales",
    secondaryHref: contact.whatsappLink,
  },
  article: { datePublished: "2026-01-20", section: "Export" },
};
