import type { Metadata } from "next";
import EcommerceTool from "@/components/EcommerceTool";
import { BackHome, ProjectHero } from "@/components/ui";
import { projects } from "@/lib/projects";
const project = projects[3];
export const metadata: Metadata = { title: "E-commerce SQL Analytics" };
export default function Page() { return <div className="page-shell"><BackHome /><ProjectHero number={project.number} kicker="Project 04 · SQL, cohorts & marketplace operations" title={project.title} description="Analyze marketplace orders with safe SQL grains, cohort retention, delivery KPIs, and category performance." tags={project.tags} accent={project.accent} /><EcommerceTool /></div>; }
