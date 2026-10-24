import type { Metadata } from "next";
import SegmentationTool from "@/components/SegmentationTool";
import { BackHome, ProjectHero } from "@/components/ui";
import { projects } from "@/lib/projects";
const project = projects[4];
export const metadata: Metadata = { title: "Customer Segmentation & Marketing Dashboard" };
export default function Page() { return <div className="page-shell"><BackHome /><ProjectHero number={project.number} kicker="Project 05 · RFM, clustering & campaign design" title={project.title} description="Build transparent RFM audiences, validate a clustering challenger, and turn segments into measurable campaign tests." tags={project.tags} accent={project.accent} /><SegmentationTool /></div>; }
