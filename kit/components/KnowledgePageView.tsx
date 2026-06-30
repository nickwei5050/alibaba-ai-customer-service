/**
 * KnowledgePageView.tsx — OPTIONAL reference renderer.
 *
 * This is a STARTING POINT, not a replacement for your design system. It shows
 * how to turn a `KnowledgePage` data object into a premium page while keeping
 * your animations. Swap the <Reveal> wrapper for your existing GSAP / React
 * Bits scroll-reveal component and restyle with your tokens.
 *
 * Heavy/cinematic blocks should be dynamic-imported (see the `Particles`
 * example) so they never block the hero's LCP.
 */
import dynamic from "next/dynamic";
import type { KnowledgePage, ContentBlock } from "@/lib/content/types";
import { breadcrumbSchema, faqSchema, jsonLd } from "@/lib/schema";

// Heavy decorative layer loaded only on the client, below the fold.
// Replace "@/components/Particles" with your real effect component.
const Particles = dynamic(() => import("@/components/Particles"), {
  ssr: false,
  loading: () => null,
});

/** Replace with your existing animated scroll-reveal wrapper. */
function Reveal({ children }: { children: React.ReactNode }) {
  return <div data-reveal>{children}</div>;
}

function Block({ block }: { block: ContentBlock }) {
  switch (block.kind) {
    case "prose":
      return (
        <section className="kp-prose">
          {block.heading && <h2>{block.heading}</h2>}
          {block.paragraphs.map((p, i) => (
            <p key={i}>{p}</p>
          ))}
        </section>
      );
    case "stats":
      return (
        <section className="kp-stats">
          {block.heading && <h2>{block.heading}</h2>}
          <div className="kp-stats-grid">
            {block.items.map((s, i) => (
              <div key={i} className="kp-stat-card">
                <span className="kp-stat-value">{s.value}</span>
                <span className="kp-stat-label">{s.label}</span>
              </div>
            ))}
          </div>
        </section>
      );
    case "cards":
      return (
        <section className="kp-cards">
          {block.heading && <h2>{block.heading}</h2>}
          <div className="kp-card-grid">
            {block.items.map((c, i) => (
              <article key={i} className="kp-card">
                <h3>{c.title}</h3>
                <p>{c.body}</p>
              </article>
            ))}
          </div>
        </section>
      );
    case "steps":
      return (
        <section className="kp-steps">
          {block.heading && <h2>{block.heading}</h2>}
          <ol>
            {block.steps.map((s, i) => (
              <li key={i}>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </li>
            ))}
          </ol>
        </section>
      );
    case "table":
      return (
        <section className="kp-table">
          {block.heading && <h2>{block.heading}</h2>}
          <div className="kp-table-scroll">
            <table>
              <thead>
                <tr>
                  {block.columns.map((c, i) => (
                    <th key={i} scope="col">
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {block.rows.map((row, i) => (
                  <tr key={i}>
                    {row.map((cell, j) => (
                      <td key={j}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {block.note && <p className="kp-note">{block.note}</p>}
        </section>
      );
  }
}

export default function KnowledgePageView({ page }: { page: KnowledgePage }) {
  return (
    <main className="kp">
      {/* Structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: jsonLd(breadcrumbSchema(page.breadcrumb)) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: jsonLd(faqSchema(page.faq)) }}
      />

      <header className="kp-hero">
        <Particles />
        <p className="kp-eyebrow">{page.hero.eyebrow}</p>
        <h1>{page.hero.h1}</h1>
        <p className="kp-subtitle">{page.hero.subtitle}</p>
      </header>

      {page.blocks.map((block, i) => (
        <Reveal key={i}>
          <Block block={block} />
        </Reveal>
      ))}

      <Reveal>
        <section className="kp-faq">
          <h2>Frequently asked questions</h2>
          <dl>
            {page.faq.map((f, i) => (
              <div key={i} className="kp-faq-item">
                <dt>{f.q}</dt>
                <dd>{f.a}</dd>
              </div>
            ))}
          </dl>
        </section>
      </Reveal>

      <Reveal>
        <section className="kp-cta">
          <h2>{page.cta.heading}</h2>
          <p>{page.cta.body}</p>
          <div className="kp-cta-actions">
            <a className="kp-cta-primary" href={page.cta.primaryHref}>
              {page.cta.primaryLabel}
            </a>
            {page.cta.secondaryLabel && page.cta.secondaryHref && (
              <a className="kp-cta-secondary" href={page.cta.secondaryHref}>
                {page.cta.secondaryLabel}
              </a>
            )}
          </div>
        </section>
      </Reveal>
    </main>
  );
}
