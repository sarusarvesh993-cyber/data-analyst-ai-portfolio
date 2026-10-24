"use client";

import { useMemo, useState } from "react";
import data from "@/public/data/ecommerce.json";
import { BarList, DataTable, KpiGrid, LineChart, Notice, Panel, Section, SourceFooter } from "@/components/ui";
import { downloadCsv } from "@/lib/csv";
import { compact, monthLabel, number, percent } from "@/lib/format";

export default function EcommerceTool() {
  const kpis = data.kpis[0];
  const [maturity, setMaturity] = useState(12);
  const [topN, setTopN] = useState(15);
  const sqlFiles = Object.keys(data.sql);
  const [query, setQuery] = useState(sqlFiles[0]);
  const selectedCohorts = data.cohorts.filter((row) => row.month_number === maturity);
  const denominator = selectedCohorts.reduce((sum, row) => sum + row.cohort_size, 0);
  const retention = denominator ? 100 * selectedCohorts.reduce((sum, row) => sum + row.active_customers, 0) / denominator : 0;
  const categories = useMemo(() => [...data.categories].sort((a, b) => b.item_gmv_brl - a.item_gmv_brl).slice(0, topN), [topN]);
  const cohortMonths = [...new Set(data.cohorts.map((row) => row.cohort_month))].sort();
  const ages = Array.from({ length: 13 }, (_, index) => index);
  const qualityPass = data.quality.filter((row) => row.check_status === "PASS").length;
  const topStates = [...data.states].sort((a, b) => b.delivered_orders - a.delivered_orders).slice(0, 12);

  return <>
    <Notice title="Revenue and cohort boundaries" tone="amber">Item GMV is not accounting revenue. Repeat behavior is measured within the available Olist marketplace history; delivery-review relationships are descriptive, not causal.</Notice>
    <KpiGrid columns={5} items={[
      { label: "Delivered orders", value: number(kpis.delivered_orders) }, { label: "Item GMV", value: compact(kpis.item_gmv_brl, "R$") },
      { label: "Repeat customer rate", value: percent(kpis.repeat_customer_rate_pct, 1, true) },
      { label: "On-time delivery", value: percent(kpis.on_time_delivery_rate_pct, 1, true) }, { label: "Average review", value: `${kpis.average_review_score.toFixed(2)} / 5` },
    ]} />
    <Section eyebrow="Executive view" title="Marketplace growth and operating quality" copy={`${monthLabel(kpis.first_order_date)} to ${monthLabel(kpis.last_order_date)} · reviewed DuckDB aggregates`}>
      <Panel title="Monthly item GMV"><LineChart valueFormat={(value) => compact(value, "R$")} labelFormat={monthLabel} series={[{ name: "Item GMV (BRL)", color: "#c55745", points: data.monthly.map((row) => ({ x: row.purchase_month, y: row.item_gmv_brl })) }]} /></Panel>
      <div className="two-column">
        <Panel title="Delivery experience"><DataTable rows={data.delivery} rowKey={(row) => row.delivery_status} columns={[
          { label: "Status", render: (row) => row.delivery_status }, { label: "Orders", render: (row) => number(row.delivered_orders), align: "right" },
          { label: "Avg days", render: (row) => row.average_delivery_days.toFixed(1), align: "right" }, { label: "Review", render: (row) => row.average_review_score.toFixed(2), align: "right" },
          { label: "Low review", render: (row) => percent(row.low_review_rate_pct, 1, true), align: "right" },
        ]} /></Panel>
        <Panel title="Data quality" copy={`${qualityPass} of ${data.quality.length} checks marked PASS`}><DataTable rows={data.quality} rowKey={(row) => row.check_name} columns={[
          { label: "Check", render: (row) => row.check_name }, { label: "Issues", render: (row) => number(row.issue_count), align: "right" },
          { label: "Status", render: (row) => <span className={`status status-${row.check_status.toLowerCase()}`}>{row.check_status}</span> },
        ]} /></Panel>
      </div>
    </Section>
    <Section eyebrow="Cohort analysis" title="Retention by months after first purchase">
      <div className="two-column wide-right">
        <Panel title="Weighted retention"><label className="field"><span>Cohort age: <b className="control-value">M{maturity}</b></span><input aria-label="Cohort maturity" type="range" min="3" max="18" value={maturity} onChange={(e) => setMaturity(Number(e.target.value))} /></label><div className="big-number" data-testid="cohort-retention">{percent(retention, 2, true)}</div><p className="helper-text">{number(denominator)} customers in eligible cohorts. Size-weighted active customers ÷ cohort size.</p></Panel>
        <Panel title="Cohort retention matrix" copy="M0–M12; color intensity follows retention rate."><div className="table-scroll"><table><thead><tr><th>Cohort</th>{ages.map((age) => <th key={age}>M{age}</th>)}</tr></thead><tbody>{cohortMonths.map((month) => <tr key={month}><td>{month.slice(0, 7)}</td>{ages.map((age) => {
          const row = data.cohorts.find((item) => item.cohort_month === month && item.month_number === age);
          const rate = row?.retention_rate_pct;
          return <td key={age} style={{ background: rate === undefined ? "#f5f7f6" : `rgba(15,138,123,${Math.min(.72, .06 + rate / 25)})`, color: rate !== undefined && rate > 12 ? "#fff" : "#234943" }}>{row ? `${rate!.toFixed(1)}%` : "—"}</td>;
        })}</tr>)}</tbody></table></div></Panel>
      </div>
      <div className="form-actions"><button className="button ghost" onClick={() => downloadCsv("ecommerce-cohort-retention.csv", data.cohorts.map((row) => ({ ...row })))}>Download cohort CSV</button></div>
    </Section>
    <Section eyebrow="Category and delivery" title="Where GMV and customer experience differ">
      <Panel title={`Top ${topN} categories by item GMV`} actions={<label className="field-inline"><span className="subtle">Categories</span><input aria-label="Number of categories" type="range" min="8" max="25" value={topN} onChange={(e) => setTopN(Number(e.target.value))} /><b>{topN}</b></label>}>
        <BarList color="#c55745" valueFormat={(value) => compact(value, "R$")} items={categories.map((row) => ({ label: row.category.replaceAll("_", " "), value: row.item_gmv_brl, note: `${number(row.delivered_orders)} orders · ${row.average_review_score.toFixed(2)} review` }))} />
      </Panel>
      <Panel title="Largest states by delivered orders"><DataTable rows={topStates} rowKey={(row) => row.customer_state} columns={[
        { label: "State", render: (row) => row.customer_state }, { label: "Orders", render: (row) => number(row.delivered_orders), align: "right" },
        { label: "GMV", render: (row) => compact(row.item_gmv_brl, "R$"), align: "right" }, { label: "On time", render: (row) => percent(row.on_time_delivery_rate_pct, 1, true), align: "right" },
        { label: "Review", render: (row) => row.average_review_score.toFixed(2), align: "right" },
      ]} /></Panel>
    </Section>
    <Section eyebrow="SQL review" title="Inspect the versioned analytical queries">
      <Panel actions={<select aria-label="SQL query" value={query} onChange={(e) => setQuery(e.target.value)}>{sqlFiles.map((name) => <option key={name}>{name}</option>)}</select>} title={query}><pre className="code-block">{data.sql[query as keyof typeof data.sql]}</pre></Panel>
    </Section>
    <SourceFooter folder="04-ecommerce-sql">Real anonymized Olist marketplace data from 2016–2018 under CC BY-NC-SA 4.0. SQL owns joins and grains; the Vercel app consumes reviewed aggregates rather than exposing a database.</SourceFooter>
  </>;
}
