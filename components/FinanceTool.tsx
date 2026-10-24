"use client";

import { useMemo, useState } from "react";
import data from "@/public/data/finance.json";
import { BarList, DataTable, DownloadLinks, KpiGrid, LineChart, Notice, Panel, Section, SourceFooter } from "@/components/ui";
import { downloadCsv } from "@/lib/csv";
import { compact, monthLabel, number, percent } from "@/lib/format";

type PlanRow = (typeof data.corporatePlan)[number] & { scenarioAmount?: number };
const pnl = (rows: PlanRow[], column: "base_forecast_amount" | "scenarioAmount") => {
  const revenue = rows.filter((row) => row.statement_group === "Revenue").reduce((sum, row) => sum + Number(row[column] || 0), 0);
  const cost = rows.filter((row) => row.statement_group !== "Revenue").reduce((sum, row) => sum + Number(row[column] || 0), 0);
  return { revenue, cost, ebitda: revenue - cost, margin: revenue ? 100 * (revenue - cost) / revenue : 0 };
};

export default function FinanceTool() {
  const kpis = data.kpis[0];
  const metadata = data.metadata[0];
  const [department, setDepartment] = useState("All");
  const [fund, setFund] = useState("All");
  const [direction, setDirection] = useState<"above" | "below">("above");
  const [revenueAdjustment, setRevenueAdjustment] = useState(0);
  const [costInflation, setCostInflation] = useState(0);
  const [hiringSavings, setHiringSavings] = useState(0);

  const filtered = useMemo(() => data.mart.filter((row) =>
    (department === "All" || row.dept_rollup_name === department) && (fund === "All" || row.fund_name === fund)
  ), [department, fund]);
  const budget = filtered.reduce((sum, row) => sum + row.budget, 0);
  const expenditures = filtered.reduce((sum, row) => sum + row.expenditures, 0);
  const expected = filtered.reduce((sum, row) => sum + row.expected_spend_to_date, 0);
  const visible = [...filtered].sort((a, b) => Math.abs(b.pace_variance) - Math.abs(a.pace_variance)).slice(0, 100);
  const drivers = data.drivers.filter((row) => direction === "above" ? row.pace_variance > 0 : row.pace_variance < 0).sort((a, b) => b.absolute_pace_variance - a.absolute_pace_variance).slice(0, 10);

  const scenario = useMemo(() => data.corporatePlan.map((row) => {
    let scenarioAmount = row.base_forecast_amount;
    if (row.period_status === "Forecast") {
      scenarioAmount *= 1 + (row.statement_group === "Revenue" ? revenueAdjustment : costInflation) / 100;
      if (["Product & engineering", "General & administrative"].includes(row.line_item)) scenarioAmount *= 1 - hiringSavings / 100;
    }
    return { ...row, scenarioAmount };
  }), [revenueAdjustment, costInflation, hiringSavings]);
  const base = pnl(data.corporatePlan, "base_forecast_amount");
  const scenarioPnl = pnl(scenario, "scenarioAmount");
  const monthlyScenario = data.corporateMonthly.map((month) => {
    const rows = scenario.filter((row) => row.month === month.month);
    return { x: month.month, y: pnl(rows, "scenarioAmount").ebitda };
  });

  return <>
    <Notice title="Two distinct models, clearly separated" tone="amber">The public-finance view uses City of Austin FY2026 Q3 budget-versus-expenditure data. The corporate scenario is a <b>seeded synthetic model</b>; its revenue, COGS, EBITDA, and hiring assumptions are not Austin data.</Notice>
    <KpiGrid columns={5} items={[
      { label: "Annual budget", value: compact(kpis.annual_budget, "$") }, { label: "Expenditures to date", value: compact(kpis.expenditures_to_date, "$") },
      { label: "Utilization", value: percent(kpis.utilization_pct, 1, true), note: `Through Q${kpis.through_quarter} · ${kpis.elapsed_pct}% elapsed` },
      { label: "Pace variance", value: compact(kpis.pace_variance, "$"), note: "Actual minus straight-line expectation" },
      { label: "Above-pace departments", value: number(kpis.above_pace_departments), note: `${kpis.departments} departments reviewed` },
    ]} />
    <Section eyebrow="Public-finance explorer" title="Filter the reviewed planning mart" copy="The 75% Q3 benchmark is a pacing reference, not an accounting forecast.">
      <Panel title="Department and fund filters"><div className="form-grid">
        <label className="field"><span>Department</span><select aria-label="Department filter" value={department} onChange={(e) => { setDepartment(e.target.value); setFund("All"); }}><option>All</option>{data.departments.map((row) => <option key={row.dept_rollup_name}>{row.dept_rollup_name}</option>)}</select></label>
        <label className="field"><span>Fund</span><select aria-label="Fund filter" value={fund} onChange={(e) => setFund(e.target.value)}><option>All</option>{[...new Set(data.funds.filter((row) => department === "All" || row.dept_rollup_name === department).map((row) => row.fund_name))].sort().map((name) => <option key={name}>{name}</option>)}</select></label>
      </div></Panel>
      <KpiGrid items={[
        { label: "Filtered budget", value: compact(budget, "$") }, { label: "Expenditures", value: compact(expenditures, "$") },
        { label: "Utilization", value: budget ? percent(100 * expenditures / budget, 1, true) : "—" }, { label: "Pace variance", value: compact(expenditures - expected, "$") },
      ]} />
      <Panel title={`Largest absolute pace variances · ${number(visible.length)} of ${number(filtered.length)} shown`} actions={<button className="button ghost" onClick={() => downloadCsv("filtered-financial-planning-mart.csv", filtered.map((row) => ({ ...row })))}>Download filtered rows</button>}>
        <DataTable rows={visible} rowKey={(row, index) => `${row.dept_rollup_name}-${row.fund_name}-${row.program_name}-${index}`} columns={[
          { label: "Department", render: (row) => row.dept_rollup_name }, { label: "Fund", render: (row) => row.fund_name }, { label: "Program", render: (row) => row.program_name },
          { label: "Budget", render: (row) => compact(row.budget, "$"), align: "right" }, { label: "Spent", render: (row) => compact(row.expenditures, "$"), align: "right" },
          { label: "Utilization", render: (row) => percent(row.utilization_pct, 1, true), align: "right" },
          { label: "Pace", render: (row) => <span className={`status ${row.pace_variance > 0 ? "status-warn" : "status-pass"}`}>{row.pace_status}</span> },
        ]} />
      </Panel>
    </Section>
    <Section eyebrow="Variance drivers" title="Sequence investigation by materiality">
      <Panel actions={<div className="pill-select"><button className={direction === "above" ? "active" : ""} onClick={() => setDirection("above")}>Above pace</button><button className={direction === "below" ? "active" : ""} onClick={() => setDirection("below")}>Below pace</button></div>} title={`${direction === "above" ? "Above" : "Below"} straight-line pace`}>
        <BarList color={direction === "above" ? "#c55745" : "#327149"} valueFormat={(value) => compact(value, "$")} items={drivers.map((row) => ({ label: row.program_name, value: row.absolute_pace_variance, note: `${row.dept_rollup_name} · signed ${compact(row.pace_variance, "$")}` }))} />
      </Panel>
    </Section>
    <Section eyebrow="Synthetic corporate scenario" title="Test revenue, cost inflation, and hiring-delay assumptions" copy="Only future-period rows change. Actual periods and the reviewed public-finance data stay untouched.">
      <div className="split-layout"><Panel title="Future-period assumptions">
        <div className="stack">
          <label className="field"><span>Revenue adjustment: <b className="control-value">{revenueAdjustment > 0 ? "+" : ""}{revenueAdjustment}%</b></span><input aria-label="Revenue adjustment" type="range" min="-30" max="30" value={revenueAdjustment} onChange={(e) => setRevenueAdjustment(Number(e.target.value))} /></label>
          <label className="field"><span>Cost inflation: <b className="control-value">{costInflation > 0 ? "+" : ""}{costInflation}%</b></span><input aria-label="Cost inflation" type="range" min="-10" max="20" value={costInflation} onChange={(e) => setCostInflation(Number(e.target.value))} /></label>
          <label className="field"><span>Hiring-delay savings: <b className="control-value">{hiringSavings}%</b></span><input aria-label="Hiring delay savings" type="range" min="0" max="20" value={hiringSavings} onChange={(e) => setHiringSavings(Number(e.target.value))} /></label>
          <button className="button ghost" onClick={() => { setRevenueAdjustment(0); setCostInflation(0); setHiringSavings(0); }}>Reset scenario</button>
        </div>
      </Panel><div className="stack"><div className="result-banner"><div><span>Scenario EBITDA</span><strong data-testid="finance-ebitda">{compact(scenarioPnl.ebitda, "$")}</strong></div><p>Base forecast EBITDA: <b>{compact(base.ebitda, "$")}</b><br />Change: <b>{compact(scenarioPnl.ebitda - base.ebitda, "$")}</b></p></div>
        <KpiGrid columns={3} items={[{ label: "Revenue", value: compact(scenarioPnl.revenue, "$") }, { label: "Cost", value: compact(scenarioPnl.cost, "$") }, { label: "EBITDA margin", value: percent(scenarioPnl.margin, 1, true) }]} /></div></div>
      <Panel title="Monthly EBITDA: base forecast versus scenario"><LineChart valueFormat={(value) => compact(value, "$")} labelFormat={monthLabel} series={[
        { name: "Base forecast", color: "#173b63", points: data.corporateMonthly.map((row) => ({ x: row.month, y: row.base_forecast_ebitda })) },
        { name: "Scenario", color: "#327149", points: monthlyScenario },
      ]} /></Panel>
      <div className="form-actions"><button className="button dark" onClick={() => downloadCsv("corporate-scenario.csv", scenario.map((row) => ({ ...row })))}>Download scenario line items</button></div>
    </Section>
    <Section eyebrow="Excel and Power BI" title="Companion deliverables for desktop review">
      <div className="two-column"><figure className="image-frame"><img src="/assets/finance-power-bi.png" alt="Financial planning Power BI companion layout target" /><figcaption>Power BI companion layout target; not a hosted report.</figcaption></figure><div><DownloadLinks files={[{ href: "/downloads/financial-planning-model.xlsx", label: "Formula-driven Excel model" }, { href: "/downloads/financial-planning-measures.dax", label: "DAX measures" }, { href: "/downloads/financial-planning-theme.json", label: "Power BI theme" }, { href: "/downloads/financial-planning-power-bi.md", label: "Desktop build guide" }]} /></div></div>
    </Section>
    <SourceFooter folder="06-financial-planning">{metadata.source_name}; FY{metadata.snapshot_fiscal_year} Q{metadata.snapshot_through_quarter}, {number(metadata.source_rows)} source rows. <a href={metadata.source_url} target="_blank" rel="noreferrer">Open City of Austin dataset ↗</a>. Corporate model status: {metadata.corporate_model_status}.</SourceFooter>
  </>;
}
