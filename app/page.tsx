import Link from "next/link";
import { KpiGrid, Notice, Section } from "@/components/ui";
import { projects } from "@/lib/projects";

export default function Home() {
  return <div className="page-shell">
    <section className="home-hero">
      <div className="eyebrow light">Analytics that ends in a decision</div>
      <h1>Seven projects. One <em>reviewable</em> analytical workflow.</h1>
      <p>Classification, forecasting, experimentation, SQL, segmentation, financial planning, and healthcare operations—now delivered as a fast, credential-free Vercel experience.</p>
      <div className="hero-actions"><Link className="button primary" href="/customer-churn/">Explore the projects →</Link><Link className="button secondary" href="/ab-test-calculator/">Try the A/B calculator</Link></div>
      <div className="hero-proof"><span>Python-derived snapshots</span><span>Interactive browser tools</span><span>Source limitations visible</span></div>
    </section>

    <KpiGrid items={[
      { label: "Analytics projects", value: "07", note: "Distinct business workflows" },
      { label: "Static routes", value: "08", note: "Direct links and refreshes" },
      { label: "Runtime API keys", value: "0", note: "No browser secrets" },
      { label: "Hosting runtime", value: "Static", note: "No Streamlit server required" },
    ]} />

    <Section eyebrow="Featured work" title="Choose a business problem to explore" copy="Each project connects the analytical method to a decision, exposes its assumptions, and preserves useful interaction in the browser.">
      <div className="project-grid">{projects.map((project) => <article className="project-card" key={project.slug} style={{ borderTopColor: project.accent }}>
        <div className="project-card-top"><span className="project-index" style={{ color: project.accent, background: project.soft }}>{project.number}</span><span className="project-type">Interactive case study</span></div>
        <h3>{project.title}</h3><p>{project.description}</p>
        <div className="tag-row">{project.tags.map((tag) => <span className="tag" key={tag}>{tag}</span>)}</div>
        <Link href={project.slug}>Open project <span>→</span></Link>
      </article>)}</div>
    </Section>

    <Section eyebrow="Migration architecture" title="The analytics stays reviewable. The delivery gets simpler.">
      <div className="architecture-grid">
        {[
          ["01", "Python analysis", "Original notebooks, models, SQL, and validation code remain in the repository for reproducibility."],
          ["02", "Reviewed snapshots", "An explicit exporter transforms model results and reviewed aggregates into deterministic JSON."],
          ["03", "Interactive Next.js", "Browser tools handle thresholds, filters, scenarios, statistical tests, and safe CSV downloads."],
          ["04", "Static Vercel hosting", "No long-running Streamlit process, runtime database, persistent storage, or client-side secret is required."],
        ].map(([step, title, copy]) => <div className="architecture-card" key={step}><span>{step}</span><h3>{title}</h3><p>{copy}</p></div>)}
      </div>
    </Section>

    <Notice title="AI assistance is bounded" tone="navy" icon="AI">The quantitative analysis is deterministic. This Vercel edition uses authored decision briefs and does not call a live LLM or expose a Hugging Face token in the browser.</Notice>
  </div>;
}
