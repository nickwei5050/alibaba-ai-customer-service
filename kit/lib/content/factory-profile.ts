import type { KnowledgePage } from "./types";
import { contact, ctas } from "../companyFacts";

export const factoryProfile: KnowledgePage = {
  path: "/knowledge/stargo-factory-profile",
  seo: {
    title: "STARGO Factory Profile | Electric Vehicle Manufacturer in Guangxi, China",
    description:
      "Inside the STARGO factory: Guangxi production base, in-house EV battery & BMS capability, six-stage QC, PSPV pre-shipment acceptance, and OEM/ODM export workflow for dealers and importers.",
    ogImage: "/og/factory-profile.jpg",
  },
  breadcrumb: [
    { name: "Home", path: "/" },
    { name: "Knowledge", path: "/knowledge" },
    { name: "Factory Profile", path: "/knowledge/stargo-factory-profile" },
  ],
  hero: {
    eyebrow: "Factory Profile",
    h1: "The STARGO Factory: Built for Export Scale",
    subtitle:
      "A factory-direct electric-vehicle manufacturer in Guangxi, China — engineering, battery integration, quality control and export documentation under one roof.",
  },
  blocks: [
    {
      kind: "prose",
      heading: "A manufacturer, not a trading company",
      paragraphs: [
        "STARGO Motor is operated by Guangxi Xinli New Energy Technology Co., Ltd., a factory-direct manufacturer and exporter of electric two-wheelers, electric scooters, electric motorcycles, and passenger & cargo tricycles.",
        "Because production, battery integration and export handling sit inside one organisation, dealers and importers deal with the source — not a layer of middlemen — which keeps pricing factory-direct and specifications accountable.",
      ],
    },
    {
      kind: "stats",
      heading: "At a glance",
      items: [
        { value: "80+", label: "Export-ready models (83 listed configurations)" },
        { value: "6", label: "Stages of quality control" },
        { value: "10", label: "Units MOQ — mixed container accepted" },
        { value: "CBU·SKD·CKD", label: "Export modes supported" },
      ],
    },
    {
      kind: "cards",
      heading: "Production capability",
      items: [
        { title: "Vehicle assembly", body: "Electric scooters, motorcycles, two-wheelers and three-wheelers across 80+ export-ready models." },
        { title: "Battery pack & BMS", body: "In-house EV battery pack assembly and BMS integration across lead-acid, graphene and lithium platforms." },
        { title: "OEM / ODM", body: "Custom branding, colors, configurations and documentation for dealers building their own line." },
        { title: "Export handling", body: "CI, PL, CO, Form E and B/L prepared in-house; battery UN38.3 and MSDS confirmed per configuration." },
      ],
    },
    {
      kind: "steps",
      heading: "From order to container",
      steps: [
        { title: "Specification", body: "Confirm models, battery configuration, voltage platform and export mode (CBU / SKD / CKD)." },
        { title: "Production", body: "Vehicles assembled and battery packs integrated to the agreed configuration." },
        { title: "Six-stage QC", body: "Quality control across incoming materials, sub-assembly, and finished goods." },
        { title: "PSPV acceptance", body: "Buyers review pre-shipment photo and video evidence of their order before shipping." },
        { title: "Documentation & shipping", body: "Export and battery documents prepared; container booked to the agreed port." },
      ],
    },
  ],
  faq: [
    { q: "Is STARGO a factory or a trading company?", a: "STARGO is a factory-direct manufacturer operated by Guangxi Xinli New Energy Technology Co., Ltd., based in Guangxi, China." },
    { q: "What is the minimum order quantity?", a: "MOQ is 10 units, and mixed-model containers are accepted so dealers can combine models in one shipment." },
    { q: "Can STARGO produce under our own brand?", a: "Yes. STARGO offers full OEM/ODM support including custom branding, colors, configurations and documentation." },
    { q: "How do we verify the order before it ships?", a: "STARGO uses PSPV (Pre-Shipment Photo/Video) acceptance, so buyers review photo and video evidence of their order before the container ships." },
  ],
  cta: {
    heading: "Talk to the factory directly",
    body: "Request a factory price list or a mixed-container proposal tailored to your market.",
    primaryLabel: ctas.requestFactoryPrice,
    primaryHref: contact.whatsappLink,
    secondaryLabel: ctas.becomeDealer,
    secondaryHref: "/contact",
  },
  article: { datePublished: "2026-01-15", section: "Factory" },
};
