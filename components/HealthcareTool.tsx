"use client";

import { useMemo, useState } from "react";
import data from "@/public/data/healthcare.json";
import { BarList, DataTable, DownloadLinks, KpiGrid, Notice, Panel, Section, SourceFooter } from "@/components/ui";
import { downloadCsv } from "@/lib/csv";
import { median, number, percent } from "@/lib/format";

const numeric = (value: number | null) => value === null ? null : value;
const display = (value: number | null, decimals = 1) => value === null ? "—" : number(value, decimals);

function AccessScatter() {
  const rows = data.states.filter((row) => row.facilities_24x7_per_100k !== null && row.imr !== null && row.population_lakh !== null);
  const width = 780, height = 350, left = 65, right = 25, top = 22, bottom = 48;
  const xMax = Math.max(...rows.map((row) => row.facilities_24x7_per_100k!)) * 1.08;
  const yMax = Math.max(...rows.map((row) => row.imr!)) * 1.1;
  const populationMax = Math.max(...rows.map((row) => row.population_lakh!));
  const x = (value: number) => left + value / xMax * (width - left - right);
  const y = (value: number) => top + (1 - value / yMax) * (height - top - bottom);
  return <div className="chart-wrap"><svg className="line-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Reported 24x7 access density and infant mortality by state">
    {[0, .5, 1].map((ratio) => <g key={ratio}><line className="grid-line" x1={left} x2={width - right} y1={y(yMax * ratio)} y2={y(yMax * ratio)} /><text className="axis-text" x={left - 8} y={y(yMax * ratio) + 4} textAnchor="end">{number(yMax * ratio)}</text><text className="axis-text" x={x(xMax * ratio)} y={height - 15} textAnchor="middle">{number(xMax * ratio)}</text></g>)}
    <text className="axis-text" x={left} y={height - 2}>24x7 facilities per 100K Census-2011 population</text>
    {rows.map((row) => <circle key={row.state} aria-label={`${row.state}: ${display(row.facilities_24x7_per_100k, 2)} facilities per 100K; IMR ${display(row.imr)}`} cx={x(row.facilities_24x7_per_100k!)} cy={y(row.imr!)} r={5 + 12 * Math.sqrt(row.population_lakh! / populationMax)} fill="rgba(164,62,90,.52)" stroke="#a43e5a" strokeWidth="1"><title>{`${row.state}: ${display(row.facilities_24x7_per_100k, 2)} facilities per 100K; IMR ${display(row.imr)}`}</title></circle>)}
  </svg><div className="chart-legend"><span>Circle size represents reported population · hover for state values</span></div></div>;
}

export default function HealthcareTool() {
  const kpis = data.kpis[0];
  const metadata = data.metadata[0];
  const [focus, setFocus] = useState("All");
  const [band, setBand] = useState("All");
  const [completeness, setCompleteness] = useState(0);
  const focusOptions = [...new Set(data.states.map((row) => row.focus_group))].sort();
  const bandOptions = ["Higher review priority", "Moderate review priority", "Lower review priority", "Insufficient data"];
  const filtered = useMemo(() => data.states.filter((row) =>
    (focus === "All" || row.focus_group === focus) && (band === "All" || row.review_priority_band === band) && row.data_completeness_pct >= completeness
  ).sort((a, b) => (b.review_priority_score ?? -1) - (a.review_priority_score ?? -1)), [focus, band, completeness]);
  const readiness = median(filtered.map((row) => numeric(row.phc_three_nurse_readiness_pct)).filter((value): value is number => value !== null));
  const complete = median(filtered.map((row) => row.data_completeness_pct));
  const scatterRows = data.states.filter((row) => row.facilities_24x7_per_100k !== null && row.imr !== null && row.population_lakh !== null);
  const correlation = useMemo(() => {
    const pairs = scatterRows.map((row) => [row.facilities_24x7_per_100k!, row.imr!]);
    const meanX = pairs.reduce((sum, pair) => sum + pair[0], 0) / pairs.length;
    const meanY = pairs.reduce((sum, pair) => sum + pair[1], 0) / pairs.length;
    let numerator = 0, xx = 0, yy = 0;
    pairs.forEach(([x, y]) => { numerator += (x - meanX) * (y - meanY); xx += (x - meanX) ** 2; yy += (y - meanY) ** 2; });
    return numerator / Math.sqrt(xx * yy);
  }, [scatterRows]);
  const priority = data.states.filter((row) => row.review_priority_score !== null).sort((a, b) => b.review_priority_score! - a.review_priority_score!).slice(0, 20).reverse();

  return <>
    <Notice title="Official reports with mixed reference periods">Facility status is reported for 2025-26, population is Census 2011, and health outcomes use SRS reference periods. Rates and scores are review screens—not current capacity estimates or funding formulas.</Notice>
    <KpiGrid columns={6} items={[
      { label: "States & UTs", value: number(kpis.states_and_uts) }, { label: "Sub-centres", value: number(kpis.sub_centres) },
      { label: "PHCs", value: number(kpis.phcs) }, { label: "CHCs", value: number(kpis.chcs) },
      { label: "District hospitals", value: number(kpis.district_hospitals) }, { label: "Reported 24x7", value: number(kpis.facilities_24x7) },
    ]} />
    <Section eyebrow="National overview" title="Separate access signals from source limitations">
      <div className="two-column"><Panel title="Reported facility footprint"><BarList color="#a43e5a" items={[
        { label: "Sub-centres", value: kpis.sub_centres }, { label: "PHCs", value: kpis.phcs }, { label: "CHCs", value: kpis.chcs },
        { label: "District hospitals", value: kpis.district_hospitals }, { label: "Reported 24x7 facilities", value: kpis.facilities_24x7 },
      ]} /></Panel><Panel title="NHM focus groups"><DataTable rows={data.regions} rowKey={(row) => row.focus_group} columns={[
        { label: "Focus group", render: (row) => row.focus_group }, { label: "States/UTs", render: (row) => row.states_and_uts, align: "right" },
        { label: "PHCs", render: (row) => number(row.phcs), align: "right" }, { label: "Median IMR", render: (row) => display(row.median_imr), align: "right" },
        { label: "Median priority", render: (row) => display(row.median_review_priority_score), align: "right" },
      ]} /></Panel></div>
      <KpiGrid items={[
        { label: "Median urban mapping", value: percent(kpis.median_urban_mapping_pct, 1, true) },
        { label: "Median PHC readiness", value: percent(kpis.median_phc_three_nurse_readiness_pct, 1, true) },
        { label: "Median reported IMR", value: number(kpis.median_imr_reporting_states, 1) }, { label: "Higher-priority states/UTs", value: number(kpis.higher_priority_states) },
      ]} />
    </Section>
    <Section eyebrow="State explorer" title="Filter states while keeping completeness visible">
      <Panel title="Review filters"><div className="form-grid three">
        <label className="field"><span>NHM focus group</span><select aria-label="NHM focus group" value={focus} onChange={(e) => setFocus(e.target.value)}><option>All</option>{focusOptions.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label className="field"><span>Review-priority band</span><select aria-label="Review priority band" value={band} onChange={(e) => setBand(e.target.value)}><option>All</option>{bandOptions.map((value) => <option key={value}>{value}</option>)}</select></label>
        <label className="field"><span>Minimum completeness: <b className="control-value">{completeness}%</b></span><input aria-label="Minimum data completeness" type="range" min="0" max="100" step="5" value={completeness} onChange={(e) => setCompleteness(Number(e.target.value))} /></label>
      </div></Panel>
      <KpiGrid columns={5} items={[
        { label: "Selected states/UTs", value: number(filtered.length) }, { label: "Selected PHCs", value: number(filtered.reduce((sum, row) => sum + row.phcs, 0)) },
        { label: "Selected CHCs", value: number(filtered.reduce((sum, row) => sum + row.chcs, 0)) },
        { label: "Median readiness", value: readiness === null ? "—" : percent(readiness, 1, true) }, { label: "Median completeness", value: complete === null ? "—" : percent(complete, 1, true) },
      ]} />
      <Panel title={`${number(filtered.length)} selected states/UTs`} actions={<button className="button dark" onClick={() => downloadCsv("filtered-healthcare-access.csv", filtered.map((row) => ({ ...row })))}>Download filtered data</button>}><div data-testid="healthcare-count" className="subtle">Current filter: {number(filtered.length)} states/UTs</div>
        <DataTable rows={filtered} rowKey={(row) => row.state} columns={[
          { label: "State / UT", render: (row) => row.state }, { label: "Focus", render: (row) => row.focus_group },
          { label: "PHCs", render: (row) => number(row.phcs), align: "right" }, { label: "24x7 / 100K", render: (row) => display(row.facilities_24x7_per_100k, 2), align: "right" },
          { label: "PHC readiness", render: (row) => row.phc_three_nurse_readiness_pct === null ? "—" : percent(row.phc_three_nurse_readiness_pct, 1, true), align: "right" },
          { label: "IMR", render: (row) => display(row.imr), align: "right" }, { label: "Priority", render: (row) => display(row.review_priority_score), align: "right" },
          { label: "Band", render: (row) => <span className={`status status-${row.review_priority_band.split(" ")[0].toLowerCase()}`}>{row.review_priority_band}</span> },
          { label: "Complete", render: (row) => percent(row.data_completeness_pct, 0, true), align: "right" },
        ]} />
      </Panel>
    </Section>
    <Section eyebrow="Access and outcomes" title="Describe the relationship without claiming causation">
      <div className="two-column wide-left"><Panel title="24x7 access density and infant mortality"><AccessScatter /></Panel><div className="stack"><KpiGrid columns={3} items={[{ label: "States in scatter", value: number(scatterRows.length) }, { label: "Correlation", value: correlation.toFixed(2) }, { label: "Rate exclusions", value: number(kpis.population_missing_or_zero_states) }]} /><Notice title="Association is not causation" tone="amber" icon="≠">Facility count does not measure beds, staffing quality, travel time, private capacity, utilization, or case mix.</Notice></div></div>
    </Section>
    <Section eyebrow="Review planner" title="Composite, completeness-aware priority screen">
      <Panel title="Top 20 review-priority scores"><BarList color="#a43e5a" valueFormat={(value) => value.toFixed(1)} items={priority.map((row) => ({ label: row.state, value: row.review_priority_score!, note: `${row.review_priority_band} · ${percent(row.data_completeness_pct, 0, true)} complete` }))} /></Panel>
      <Notice title="Transparent and completeness-aware" tone="teal" icon="4">The score averages percentiles for low 24x7 density, low PHC three-nurse readiness, low urban mapping, and high IMR. It requires at least three components and must be validated locally.</Notice>
    </Section>
    <Section eyebrow="Methods and Power BI" title="Quality checks, metric definitions, and companion files">
      <div className="two-column"><Panel title="Data quality"><DataTable rows={data.quality} rowKey={(row) => row.check_name} columns={[{ label: "Check", render: (row) => row.check_name }, { label: "Issues", render: (row) => row.issue_count, align: "right" }, { label: "Status", render: (row) => <span className={`status status-${row.check_status.toLowerCase()}`}>{row.check_status}</span> }]} /></Panel>
      <Panel title="Metric dictionary"><DataTable rows={data.dictionary} rowKey={(row) => row.metric} columns={[{ label: "Metric", render: (row) => row.metric }, { label: "Unit", render: (row) => row.unit }, { label: "Boundary", render: (row) => row.interpretation_boundary }]} /></Panel></div>
      <div className="two-column"><figure className="image-frame"><img src="/assets/healthcare-power-bi.png" alt="Healthcare access Power BI companion layout target" /><figcaption>Power BI companion layout target; not a hosted report.</figcaption></figure><DownloadLinks files={[{ href: "/downloads/healthcare-access-mart.sql", label: "DuckDB mart SQL" }, { href: "/downloads/healthcare-access-measures.dax", label: "DAX measures" }, { href: "/downloads/healthcare-access-theme.json", label: "Power BI theme" }, { href: "/downloads/healthcare-access-power-bi.md", label: "Desktop build guide" }]} /></div>
    </Section>
    <SourceFooter folder="07-healthcare-access">{metadata.source_name}, status {metadata.status_date}. Population: {metadata.population_basis}. Outcomes: {metadata.health_indicator_basis}. <a href={metadata.source_page} target="_blank" rel="noreferrer">Official NHM source ↗</a></SourceFooter>
  </>;
}
