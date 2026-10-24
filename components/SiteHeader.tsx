"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { projects, repository } from "@/lib/projects";

export default function SiteHeader() {
  const pathname = usePathname();
  return <header className="site-header">
    <div className="header-main">
      <Link href="/" className="brand" aria-label="Sarvesh analytics portfolio home">
        <span className="brand-mark">SK</span><span><strong>Sarvesh Kommawar</strong><small>Data analytics portfolio</small></span>
      </Link>
      <div className="header-actions"><span className="edition-badge"><i /> Vercel edition</span><a href={repository} target="_blank" rel="noreferrer">GitHub ↗</a></div>
    </div>
    <nav className="project-nav" aria-label="Analytics projects">
      <Link href="/" className={pathname === "/" ? "active" : ""}>Overview</Link>
      {projects.map((project) => <Link key={project.slug} href={project.slug} className={pathname === project.slug.slice(0, -1) ? "active" : ""}><span>{project.number}</span>{project.shortTitle}</Link>)}
    </nav>
  </header>;
}
