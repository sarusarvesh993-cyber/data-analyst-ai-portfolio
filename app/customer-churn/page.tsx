import type { Metadata } from "next";
import ChurnTool from "@/components/ChurnTool";
import { BackHome, ProjectHero } from "@/components/ui";
import { projects } from "@/lib/projects";
const project = projects[0];
export const metadata: Metadata = { title: "Customer Churn & Retention" };
export default function Page() { return <div className="page-shell"><BackHome /><ProjectHero number={project.number} kicker="Project 01 · Retention analytics" title={project.title} description="Identify which customer profiles to prioritize and see how the score threshold changes campaign workload, precision, and recall." tags={project.tags} accent={project.accent} /><ChurnTool /></div>; }
