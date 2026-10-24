import type { Metadata } from "next";
import "./globals.css";
import SiteHeader from "@/components/SiteHeader";
import { repository } from "@/lib/projects";

export const metadata: Metadata = {
  title: { default: "Data Analytics Portfolio | Sarvesh Kommawar", template: "%s | Sarvesh Kommawar" },
  description: "Seven interactive analytics projects spanning classification, forecasting, experimentation, SQL, segmentation, FP&A, and healthcare operations.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>
    <a className="skip-link" href="#main">Skip to content</a>
    <SiteHeader />
    <main id="main">{children}</main>
    <footer className="site-footer"><div><strong>Sarvesh Kommawar · Data Analytics</strong><p>Evidence, validated methods, useful decisions, and visible limitations.</p></div>
      <div><a href={repository} target="_blank" rel="noreferrer">Source repository ↗</a><span>Static Next.js · No runtime secrets</span></div>
    </footer>
  </body></html>;
}
