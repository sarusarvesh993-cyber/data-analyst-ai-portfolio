import type { CSSProperties, ReactNode } from "react";
import Link from "next/link";
import { number } from "@/lib/format";

export function ProjectHero({ number: projectNumber, kicker, title, description, tags, accent = "#0f8a7b" }: {
  number: string; kicker: string; title: string; description: string; tags: string[]; accent?: string;
}) {
  return <section className="project-hero" style={{ "--accent": accent } as CSSProperties}>
    <div className="project-number-large">{projectNumber}</div>
    <div className="eyebrow light">{kicker}</div>
    <h1>{title}</h1>
    <p>{description}</p>
    <div className="tag-row">{tags.map((tag) => <span className="hero-tag" key={tag}>{tag}</span>)}</div>
  </section>;
}

export function KpiGrid({ items, columns = 4 }: { items: Array<{ label: string; value: string; note?: string }>; columns?: number }) {
  return <div className={`kpi-grid kpi-${columns}`}>{items.map((item) => <div className="kpi-card" key={item.label}>
    <span>{item.label}</span><strong>{item.value}</strong>{item.note && <small>{item.note}</small>}
  </div>)}</div>;
}

export function Notice({ title, children, tone = "navy", icon }: { title: string; children: ReactNode; tone?: "navy" | "teal" | "amber"; icon?: string }) {
  return <aside className={`notice notice-${tone}`}>
    <span className="notice-icon">{icon || (tone === "amber" ? "!" : tone === "teal" ? "✓" : "i")}</span>
    <div><strong>{title}</strong><p>{children}</p></div>
  </aside>;
}

export function Section({ eyebrow, title, copy, children, id }: { eyebrow?: string; title: string; copy?: string; children: ReactNode; id?: string }) {
  return <section className="content-section" id={id}>
    <div className="section-heading">{eyebrow && <span className="eyebrow">{eyebrow}</span>}<h2>{title}</h2>{copy && <p>{copy}</p>}</div>
    {children}
  </section>;
}

export function Panel({ title, copy, children, actions }: { title?: string; copy?: string; children: ReactNode; actions?: ReactNode }) {
  return <div className="panel">
    {(title || actions) && <div className="panel-heading"><div>{title && <h3>{title}</h3>}{copy && <p>{copy}</p>}</div>{actions}</div>}
    {children}
  </div>;
}

export function BarList({ items, valueFormat = (value) => number(value), color = "#0f8a7b" }: {
  items: Array<{ label: string; value: number; note?: string }>;
  valueFormat?: (value: number) => string; color?: string;
}) {
  const maximum = Math.max(...items.map((item) => Math.abs(item.value)), 1);
  return <div className="bar-list">{items.map((item) => <div className="bar-row" key={item.label}>
    <div className="bar-label"><span>{item.label}</span><strong>{valueFormat(item.value)}</strong></div>
    <div className="bar-track"><span style={{ width: `${Math.max(1, Math.abs(item.value) / maximum * 100)}%`, background: color }} /></div>
    {item.note && <small>{item.note}</small>}
  </div>)}</div>;
}

export type LineSeries = { name: string; color: string; points: Array<{ x: string; y: number }> };
export function LineChart({ series, height = 300, valueFormat = (value) => number(value), labelFormat = (value) => value }: {
  series: LineSeries[]; height?: number; valueFormat?: (value: number) => string; labelFormat?: (value: string) => string;
}) {
  const width = 800;
  const padding = { left: 64, right: 20, top: 22, bottom: 42 };
  const all = series.flatMap((item) => item.points);
  const yMin = Math.min(...all.map((point) => point.y));
  const yMax = Math.max(...all.map((point) => point.y));
  const span = yMax - yMin || 1;
  const low = yMin - span * 0.08;
  const high = yMax + span * 0.08;
  const basePoints = series[0]?.points || [];
  const x = (index: number, count: number) => padding.left + (index / Math.max(1, count - 1)) * (width - padding.left - padding.right);
  const y = (value: number) => padding.top + (1 - (value - low) / (high - low)) * (height - padding.top - padding.bottom);
  const path = (points: LineSeries["points"]) => points.map((point, index) => `${index ? "L" : "M"}${x(index, points.length).toFixed(1)},${y(point.y).toFixed(1)}`).join(" ");
  const tickIndices = [...new Set([0, Math.floor((basePoints.length - 1) / 2), basePoints.length - 1])];
  return <div className="chart-wrap">
    <svg className="line-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Line chart: ${series.map((item) => item.name).join(", ")}`}>
      {[0, 0.5, 1].map((ratio) => {
        const value = low + ratio * (high - low);
        return <g key={ratio}><line x1={padding.left} x2={width - padding.right} y1={y(value)} y2={y(value)} className="grid-line" />
          <text x={padding.left - 9} y={y(value) + 4} textAnchor="end" className="axis-text">{valueFormat(value)}</text></g>;
      })}
      {series.map((item) => <path key={item.name} d={path(item.points)} fill="none" stroke={item.color} strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />)}
      {tickIndices.map((index) => basePoints[index] && <text key={index} x={x(index, basePoints.length)} y={height - 12} textAnchor={index === 0 ? "start" : index === basePoints.length - 1 ? "end" : "middle"} className="axis-text">{labelFormat(basePoints[index].x)}</text>)}
    </svg>
    <div className="chart-legend">{series.map((item) => <span key={item.name}><i style={{ background: item.color }} />{item.name}</span>)}</div>
  </div>;
}

export function DataTable<T>({ rows, columns, rowKey, empty = "No rows match the current filters." }: {
  rows: T[];
  columns: Array<{ label: string; render: (row: T) => ReactNode; align?: "right" | "left" }>;
  rowKey: (row: T, index: number) => string;
  empty?: string;
}) {
  if (!rows.length) return <div className="empty-state">{empty}</div>;
  return <div className="table-scroll"><table><thead><tr>{columns.map((column) => <th key={column.label} style={{ textAlign: column.align || "left" }}>{column.label}</th>)}</tr></thead>
    <tbody>{rows.map((row, index) => <tr key={rowKey(row, index)}>{columns.map((column) => <td key={column.label} style={{ textAlign: column.align || "left" }}>{column.render(row)}</td>)}</tr>)}</tbody>
  </table></div>;
}

export function DownloadLinks({ files }: { files: Array<{ href: string; label: string }> }) {
  return <div className="download-grid">{files.map((file) => <a className="download-link" href={file.href} download key={file.href}><span>↓</span>{file.label}</a>)}</div>;
}

export function SourceFooter({ folder, children }: { folder: string; children: ReactNode }) {
  return <div className="source-footer"><div><strong>Source and interpretation boundary</strong><p>{children}</p></div>
    <a href={`https://github.com/sarusarvesh993-cyber/data-analyst-ai-portfolio/tree/main/${folder}`} target="_blank" rel="noreferrer">Review project files ↗</a></div>;
}

export function BackHome() {
  return <Link className="back-home" href="/">← All analytics projects</Link>;
}
