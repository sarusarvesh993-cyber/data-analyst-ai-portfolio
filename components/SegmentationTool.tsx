"use client";

import { useMemo, useState } from "react";
import data from "@/public/data/segmentation.json";
import { BarList, DataTable, DownloadLinks, KpiGrid, LineChart, Notice, Panel, Section, SourceFooter } from "@/components/ui";
import { downloadCsv } from "@/lib/csv";
import { compact, median, monthLabel, number, percent } from "@/lib/format";

export default function SegmentationTool() {
  const kpis = data.kpis[0];
  const [segment, setSegment] = useState("All");
  const [country, setCountry] = useState("All");
  const [minimumValue, setMinimumValue] = useState(0);
  const [chosenSegment, setChosenSegment] = useState("At Risk");
  const filtered = useMemo(() => data.customers.filter((row) =>
    (segment === "All" || row.rfm_segment === segment) && (country === "All" || row.country === country) && row.monetary_value >= minimumValue
  ), [segment, country, minimumValue]);
  const filteredRevenue = filtered.reduce((sum, row) => sum + row.monetary_value, 0);
  const recency = median(filtered.map((row) => row.recency_days));
  const monetary = median(filtered.map((row) => row.monetary_value));
  const visible = [...filtered].sort((a, b) => b.monetary_value - a.monetary_value).slice(0, 100);
  const campaign = data.segments.find((row) => row.rfm_segment === chosenSegment)!;
  const audience = data.customers.filter((row) => row.rfm_segment === chosenSegment);

  return <>
    <Notice title="Historical customer-level analysis" tone="amber">UCI Online Retail transactions from 2010–2011. Completed-purchase value is not profit, unidentified purchases are outside customer coverage, and segments do not establish campaign treatment effects.</Notice>
    <KpiGrid columns={5} items={[
      { label: "Identified customers", value: number(kpis.customers) }, { label: "Gross revenue", value: compact(kpis.gross_revenue, "£") },
      { label: "Repeat customer rate", value: percent(kpis.repeat_customer_rate_pct, 1, true) },
      { label: "Selected silhouette", value: kpis.selected_silhouette_score.toFixed(3), note: `${kpis.selected_cluster_count} clusters` },
      { label: "Sales value coverage", value: percent(kpis.identified_sales_value_coverage_pct, 1, true) },
    ]} />
    <Section eyebrow="Executive view" title="Transparent RFM audiences with a clustering challenger">
      <Panel title="Monthly identified-customer revenue"><LineChart valueFormat={(value) => compact(value, "£")} labelFormat={monthLabel} series={[{ name: "Revenue (GBP)", color: "#246585", points: data.monthly.map((row) => ({ x: row.purchase_month, y: row.revenue })) }]} /></Panel>
      <Panel title="RFM segment summary"><DataTable rows={data.segments} rowKey={(row) => row.rfm_segment} columns={[
        { label: "Segment", render: (row) => row.rfm_segment }, { label: "Customers", render: (row) => number(row.customers), align: "right" },
        { label: "Revenue", render: (row) => compact(row.revenue, "£"), align: "right" }, { label: "Median recency", render: (row) => `${number(row.median_recency_days)} days`, align: "right" },
        { label: "Revenue share", render: (row) => percent(row.revenue_share_pct, 1, true), align: "right" }, { label: "Objective", render: (row) => row.objective },
      ]} /></Panel>
    </Section>
    <Section eyebrow="Audience explorer" title="Filter anonymized customers and export the result" copy="Filters run entirely in your browser. The table previews the 100 highest-value matches; CSV includes every match.">
      <Panel title="Audience filters">
        <div className="form-grid three">
          <label className="field"><span>RFM segment</span><select aria-label="RFM segment filter" value={segment} onChange={(e) => setSegment(e.target.value)}><option>All</option>{data.segments.map((row) => <option key={row.rfm_segment}>{row.rfm_segment}</option>)}</select></label>
          <label className="field"><span>Country</span><select aria-label="Country filter" value={country} onChange={(e) => setCountry(e.target.value)}><option>All</option>{data.countries.map((row) => <option key={row.country}>{row.country}</option>)}</select></label>
          <label className="field"><span>Minimum historical value £</span><input aria-label="Minimum customer value" type="number" min="0" step="250" value={minimumValue} onChange={(e) => setMinimumValue(Number(e.target.value))} /></label>
        </div>
      </Panel>
      <KpiGrid items={[
        { label: "Matching customers", value: number(filtered.length), note: "Current filter denominator" },
        { label: "Historical value", value: compact(filteredRevenue, "£") }, { label: "Median recency", value: recency === null ? "—" : `${number(recency)} days` },
        { label: "Median customer value", value: monetary === null ? "—" : compact(monetary, "£") },
      ]} />
      <Panel title={`Customer preview · ${number(visible.length)} shown`} actions={<button className="button dark" onClick={() => downloadCsv("filtered-customer-segments.csv", filtered.map((row) => ({ ...row })))}>Download all {number(filtered.length)}</button>}>
        <div data-testid="segmentation-count" className="subtle">{number(filtered.length)} matching customers</div>
        <DataTable rows={visible} rowKey={(row) => String(row.customer_id)} columns={[
          { label: "Customer", render: (row) => row.customer_id }, { label: "Country", render: (row) => row.country }, { label: "Segment", render: (row) => row.rfm_segment },
          { label: "Recency", render: (row) => number(row.recency_days), align: "right" }, { label: "Frequency", render: (row) => number(row.frequency), align: "right" },
          { label: "Value", render: (row) => compact(row.monetary_value, "£"), align: "right" }, { label: "Cluster", render: (row) => row.cluster_name },
        ]} />
      </Panel>
    </Section>
    <Section eyebrow="Model validation" title="Evaluate the clustering challenger, not just its labels">
      <div className="two-column"><Panel title="Silhouette by cluster count"><BarList color="#246585" valueFormat={(value) => value.toFixed(3)} items={data.validation.map((row) => ({ label: `${row.n_clusters} clusters${String(row.selected_model).toLowerCase() === "true" ? " · selected" : ""}`, value: row.silhouette_score, note: `Seed stability ARI ${row.seed_stability_ari.toFixed(3)}` }))} /></Panel>
      <Panel title="Top countries by revenue"><BarList valueFormat={(value) => compact(value, "£")} items={[...data.countries].sort((a, b) => b.revenue - a.revenue).slice(0, 8).map((row) => ({ label: row.country, value: row.revenue }))} /></Panel></div>
    </Section>
    <Section eyebrow="Campaign design" title="Turn a segment into a measurable test">
      <Panel actions={<select aria-label="Campaign segment" value={chosenSegment} onChange={(e) => setChosenSegment(e.target.value)}>{data.segments.map((row) => <option key={row.rfm_segment}>{row.rfm_segment}</option>)}</select>} title={`${campaign.rfm_segment} · ${number(campaign.customers)} customers`}>
        <div className="three-column"><div className="mini-stat"><span>Objective</span><strong>{campaign.objective}</strong></div><div className="mini-stat"><span>Primary KPI</span><strong>{campaign.primary_kpi}</strong></div><div className="mini-stat"><span>Channel</span><strong>{campaign.channel}</strong></div></div>
        <Notice title="Treatment and guardrail" tone="teal">{campaign.treatment}. Guardrail: {campaign.guardrail}.</Notice>
        <p className="helper-text"><b>Experiment:</b> {campaign.experiment}</p>
        <button className="button dark" onClick={() => downloadCsv(`${chosenSegment.toLowerCase().replaceAll(" ", "-")}-audience.csv`, audience.map((row) => ({ ...row })))}>Download {number(audience.length)} anonymized IDs</button>
      </Panel>
    </Section>
    <Section eyebrow="Power BI companion" title="Desktop-ready model, DAX, theme, and validation guide">
      <div className="two-column"><figure className="image-frame"><img src="/assets/segmentation-power-bi.png" alt="Customer segmentation Power BI executive page layout target" /><figcaption>Power BI companion layout target; not a claim of a hosted report.</figcaption></figure><div><DownloadLinks files={[{ href: "/downloads/customer-segmentation-measures.dax", label: "DAX measures" }, { href: "/downloads/customer-segmentation-theme.json", label: "Power BI theme" }, { href: "/downloads/customer-segmentation-power-bi.md", label: "Desktop build guide" }]} /><p className="helper-text">The PBIX authoring and Service refresh remain separate manual steps.</p></div></div>
    </Section>
    <SourceFooter folder="05-customer-segmentation">Real anonymized UCI Online Retail data under CC BY 4.0. Snapshot {kpis.snapshot_date}; analysis {monthLabel(kpis.analysis_start_date)}–{monthLabel(kpis.analysis_end_date)}. Exports contain anonymized IDs and approved analytical fields only.</SourceFooter>
  </>;
}
