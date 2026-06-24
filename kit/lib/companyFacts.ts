/**
 * companyFacts.ts — Single source of truth for STARGO Motor.
 *
 * Import this everywhere instead of hard-coding brand strings, model counts,
 * MOQ, contact details, OBSIDIAN specs, etc. This is what fixes the
 * "60+ / 80+ / 83 models" inconsistency and the conflicting OBSIDIAN values.
 *
 * RULE: Never invent certifications, prices, awards, customer cases, or
 * factory output numbers that are not present in this file.
 */

export const SITE_URL = "https://www.stargomoto.com" as const;

export const company = {
  brand: "STARGO",
  brandFull: "STARGO Motor",
  legalEntity: "Guangxi Xinli New Energy Technology Co., Ltd.",
  domain: SITE_URL,
  foundedRegion: "Guangxi, China",

  /** One-line positioning used in hero subtitles / meta descriptions. */
  positioning:
    "Factory-direct manufacturer and exporter of electric two-wheelers, electric scooters, electric motorcycles, and passenger & cargo tricycles, with in-house EV battery, BMS and OEM/ODM capability.",

  business:
    "STARGO is a factory-direct manufacturer and exporter of electric two-wheelers, electric scooters, electric motorcycles, passenger tricycles, cargo tricycles, EV batteries, accessories, and OEM/ODM solutions.",
} as const;

/** Normalised buyer personas — use for "who is this for" blocks and copy. */
export const targetBuyers = [
  "Dealers",
  "Distributors",
  "Importers",
  "Fleet operators",
  "E-commerce sellers",
  "Local mobility operators",
] as const;

/** Primary export regions. */
export const markets = [
  "Southeast Asia",
  "Middle East",
  "Africa",
  "Latin America",
  "Europe",
] as const;

export const exportModes = {
  list: ["CBU", "SKD", "CKD"] as const,
  cbu: "CBU — Completely Built Up: fully assembled, ready to sell on arrival.",
  skd: "SKD — Semi Knocked Down: partial assembly, balances duty and local labour.",
  ckd: "CKD — Completely Knocked Down: full local assembly, lowest import duty, supports local-content programs.",
} as const;

/** Commercial terms — the ONLY place these numbers should live. */
export const commercialTerms = {
  moqUnits: 10,
  moqStatement: "MOQ 10 units; mixed-model container accepted.",
  mixedContainer: true,
  // Keep wording generic and truthful — do not invent specific day counts
  // or warranty years that have not been confirmed by the owner.
  leadTime: "Lead time confirmed per order, model and configuration.",
  paymentTerms: "Payment terms confirmed per order (deposit + balance).",
  warranty: "Warranty confirmed per model and battery configuration.",
} as const;

/**
 * THE canonical model-range statement. Use `modelRange.statement` in copy.
 * Replaces all of: "60+ models", "80+ models", "83 export models".
 */
export const modelRange = {
  listedConfigurations: 83,
  statement:
    "80+ export-ready electric two-wheel and three-wheel models, including 83 listed configurations.",
  short: "80+ export-ready models",
} as const;

/** Product categories — normalised taxonomy for nav, schema and copy. */
export const productCategories = [
  { slug: "electric-scooters", name: "Electric Scooters" },
  { slug: "electric-motorcycles", name: "Electric Motorcycles" },
  { slug: "electric-two-wheelers", name: "Electric Two-Wheelers" },
  { slug: "passenger-tricycles", name: "Passenger Tricycles" },
  { slug: "cargo-tricycles", name: "Cargo Tricycles" },
  { slug: "ev-batteries", name: "EV Batteries" },
  { slug: "accessories", name: "Accessories & Spare Parts" },
] as const;

/**
 * OBSIDIAN flagship — the ONLY approved spec wording. Every page that mentions
 * OBSIDIAN must use `obsidian.statement` (or these fields) to avoid the
 * conflicting voltage/power/range values currently scattered across the site.
 */
export const obsidian = {
  name: "OBSIDIAN",
  voltageRange: "72V–120V",
  peakPowerMaxW: 8600,
  rangeMaxKm: 230,
  statement:
    "OBSIDIAN supports high-voltage 72V–120V configurations. Depending on configuration, peak power can reach up to 8600W, with long-range versions reaching up to 230 km under test conditions.",
} as const;

/** Battery platforms STARGO works with. */
export const batteryPlatforms = [
  { type: "Lead-acid", note: "Lowest upfront cost; widely serviceable." },
  { type: "Graphene", note: "Enhanced lead-acid chemistry; better cycle life vs standard lead-acid." },
  { type: "Lithium (Li-ion / LiFePO4)", note: "Lightest weight, longest cycle life, highest energy density." },
] as const;

export const voltagePlatforms = ["48V", "60V", "72V"] as const;

/** Export & battery documentation. Battery docs are confirmed PER battery model. */
export const documents = {
  shipping: [
    { code: "CI", name: "Commercial Invoice" },
    { code: "PL", name: "Packing List" },
    { code: "CO", name: "Certificate of Origin" },
    { code: "Form E", name: "ASEAN–China FTA Certificate of Origin" },
    { code: "B/L", name: "Bill of Lading" },
  ],
  battery: [
    { code: "UN38.3", name: "UN 38.3 lithium battery transport test summary" },
    { code: "MSDS", name: "Material Safety Data Sheet" },
  ],
  batteryNote:
    "Battery documents such as UN38.3 and MSDS are confirmed per battery model and configuration.",
} as const;

/** Quality control & pre-shipment process. */
export const quality = {
  qcStages: 6,
  qcStatement: "Six-stage quality control across incoming materials, assembly and finished goods.",
  pspv: "PSPV — Pre-Shipment Photo/Video acceptance: buyers review photo and video evidence of their order before the container ships.",
} as const;

export const oemOdm = {
  statement:
    "Full OEM/ODM support: custom branding, color schemes, configurations and documentation for dealers and importers building their own line.",
} as const;

/** Contact — the ONLY place these values should live. */
export const contact = {
  salesEmail: "sales@stargomoto.com",
  whatsapp: "+86 187 7512 7878",
  whatsappE164: "+8618775127878",
  whatsappLink: "https://wa.me/8618775127878",
} as const;

/** Reusable CTA copy. */
export const ctas = {
  becomeDealer: "Become a Dealer",
  requestFactoryPrice: "Request Factory Price",
  mixedContainer: "Ask for a Mixed-Container Proposal",
  batterySupport: "Get Battery Configuration Support",
  requestQuote: "Request Quote",
  downloadCatalog: "Download Dealer Catalog",
} as const;

export type CompanyFacts = {
  company: typeof company;
  modelRange: typeof modelRange;
  obsidian: typeof obsidian;
  contact: typeof contact;
};
