import type { Metadata } from "next";
import ABTestTool from "@/components/ABTestTool";
import { BackHome, ProjectHero } from "@/components/ui";
import { projects } from "@/lib/projects";
const project = projects[2];
export const metadata: Metadata = { title: "A/B Test Decision Calculator" };
export default function Page() { return <div className="page-shell"><BackHome /><ProjectHero number={project.number} kicker="Project 03 · Experimentation" title={project.title} description="Decide whether an observed conversion lift is statistically reliable, commercially useful, and supported by an adequately planned sample." tags={[...project.tags, "Practical significance"]} accent={project.accent} /><ABTestTool /></div>; }
