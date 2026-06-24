import type { KnowledgePage } from "./types";
import { contact, ctas } from "../companyFacts";

export const batteryComparison: KnowledgePage = {
  path: "/compare/lead-acid-vs-graphene-vs-lithium-battery",
  seo: {
    title: "Lead-Acid vs Graphene vs Lithium EV Batteries | Dealer Selection Guide",
    description:
      "Compare lead-acid, graphene and lithium batteries for electric scooters and motorcycles: cost, weight, cycle life, range and best-fit markets — so dealers can spec the right pack for each segment.",
    ogImage: "/og/battery-comparison.jpg",
  },
  breadcrumb: [
    { name: "Home", path: "/" },
    { name: "Compare", path: "/compare" },
    { name: "Battery Types", path: "/compare/lead-acid-vs-graphene-vs-lithium-battery" },
  ],
  hero: {
    eyebrow: "Battery Comparison",
    h1: "Lead-Acid vs Graphene vs Lithium",
    subtitle:
      "Three battery platforms, three price-and-performance profiles. Here's how to choose the right one for your market and price segment.",
  },
  blocks: [
    {
      kind: "prose",
      heading: "There is no single best battery — only the best fit",
      paragraphs: [
        "The right battery depends on your selling price, your customers' daily range needs, local charging habits and after-sales support. STARGO supplies all three platforms so dealers can match chemistry to market.",
      ],
    },
    {
      kind: "table",
      heading: "Side by side",
      columns: ["Factor", "Lead-acid", "Graphene", "Lithium (Li-ion / LiFePO4)"],
      rows: [
        ["Upfront cost", "Lowest", "Low–medium", "Highest"],
        ["Weight", "Heaviest", "Heavy", "Lightest"],
        ["Cycle life", "Shortest", "Longer than standard lead-acid", "Longest"],
        ["Energy density", "Low", "Low–medium", "High"],
        ["Serviceability", "Widely serviceable", "Widely serviceable", "Requires BMS-aware support"],
        ["Best for", "Price-first markets", "Value upgrade over lead-acid", "Range, weight and lifetime-cost markets"],
      ],
      note: "General guidance; exact figures depend on the specific battery model and configuration.",
    },
    {
      kind: "cards",
      heading: "Choose by market signal",
      items: [
        { title: "Lowest landed price wins", body: "Lead-acid keeps the unit price down for the most price-sensitive segments." },
        { title: "Customers want more for a little more", body: "Graphene is the natural step up from lead-acid where buyers will pay slightly more for better cycle life." },
        { title: "Range & weight matter", body: "Lithium suits longer commutes, lighter vehicles and customers who value lifetime cost over upfront price." },
        { title: "Fleet & total cost of ownership", body: "Lithium's cycle life often wins for fleet and delivery operators running high daily mileage." },
      ],
    },
  ],
  faq: [
    { q: "Which battery is cheapest?", a: "Lead-acid has the lowest upfront cost, which makes it strong for the most price-sensitive markets." },
    { q: "Is graphene better than lead-acid?", a: "Graphene is an enhanced lead-acid chemistry that typically offers better cycle life than standard lead-acid, at a modest price increase." },
    { q: "When should I choose lithium?", a: "Choose lithium when range, light weight, and long cycle life matter — for example longer commutes, lighter vehicles, or fleet operators focused on total cost of ownership." },
    { q: "Can STARGO help me pick the right battery for my market?", a: "Yes. Share your selling price, typical daily range and market, and STARGO will recommend a battery configuration to match." },
  ],
  cta: {
    heading: "Not sure which platform fits your price point?",
    body: "Get battery configuration support tailored to your market and target price.",
    primaryLabel: ctas.batterySupport,
    primaryHref: contact.whatsappLink,
    secondaryLabel: ctas.requestFactoryPrice,
    secondaryHref: "/contact",
  },
  article: { datePublished: "2026-01-25", section: "Battery" },
};
