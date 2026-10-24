import type { Metadata } from "next";
import ForecastTool from "@/components/ForecastTool";
import { BackHome, ProjectHero } from "@/components/ui";
import { projects } from "@/lib/projects";
const project = projects[1];
export const metadata: Metadata = { title: "U.S. Retail Sales Forecast" };
export default function Page() { return <div className="page-shell"><BackHome /><ProjectHero number={project.number} kicker="Project 02 · Time-series planning" title={project.title} description="Estimate a plausible national retail-sales range, validate it against recent holdout data, and compare it with a simple year-ago baseline." tags={project.tags} accent={project.accent} /><ForecastTool /></div>; }
