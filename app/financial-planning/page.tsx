import type { Metadata } from "next";
import FinanceTool from "@/components/FinanceTool";
import { BackHome, ProjectHero } from "@/components/ui";
import { projects } from "@/lib/projects";
const project = projects[5];
export const metadata: Metadata = { title: "Financial Planning & Variance Command Center" };
export default function Page() { return <div className="page-shell"><BackHome /><ProjectHero number={project.number} kicker="Project 06 · FP&A, variance & scenario planning" title={project.title} description="Reconcile a real operating budget, investigate Q3 pacing, and test revenue, cost, and hiring scenarios." tags={project.tags} accent={project.accent} /><FinanceTool /></div>; }
