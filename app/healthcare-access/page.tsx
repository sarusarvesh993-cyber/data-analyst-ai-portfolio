import type { Metadata } from "next";
import HealthcareTool from "@/components/HealthcareTool";
import { BackHome, ProjectHero } from "@/components/ui";
import { projects } from "@/lib/projects";
const project = projects[6];
export const metadata: Metadata = { title: "India Healthcare Access & Readiness" };
export default function Page() { return <div className="page-shell"><BackHome /><ProjectHero number={project.number} kicker="Project 07 · Public-health operations & DuckDB" title={project.title} description="Turn official NHM quarterly MIS reports into transparent state-level access, staffing, mapping, outcome, and data-quality review signals." tags={[...project.tags, "36 states & UTs"]} accent={project.accent} /><HealthcareTool /></div>; }
