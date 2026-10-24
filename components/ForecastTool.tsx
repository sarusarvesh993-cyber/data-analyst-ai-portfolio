"use client";

import { useState } from "react";
import data from "@/public/data/forecast.json";
import { BarList, KpiGrid, LineChart, Notice, Panel, Section, SourceFooter } from "@/components/ui";
import { downloadCsv } from "@/lib/csv";
import { monthLabel, number, percent } from "@/lib/format";

const billionsFromMillions = (value: number) => `$${number(value / 1000, 1)}B`;

function ForecastChart({ horizon }: { horizon: number }) {
  const history = data.history.slice(-12).map((row) => ({ date: row.date, observed: row.value as number }));
  const future = data.future.slice(0, horizon).map((row) => ({ date: row.date, forecast: row.forecast, lower: row.lower, upper: row.upper }));
  const last = history[history.length - 1];
  const points = [...history, ...future];
  const width = 850, height = 340, left = 65, right = 20, top = 20, bottom = 43;
  const values = [...history.map((row) => row.observed), ...future.flatMap((row) => [row.lower, row.upper])];
  const minimum = Math.min(...values), maximum = Math.max(...values), span = maximum - minimum || 1;
  const low = minimum - span * 0.08, high = maximum + span * 0.08;
  const x = (index: number) => left + index / Math.max(1, points.length - 1) * (width - left - right);
  const y = (value: number) => top + (1 - (value - low) / (high - low)) * (height - top - bottom);
  const observedPath = history.map((row, index) => `${index ? "L" : "M"}${x(index)},${y(row.observed)}`).join(" ");
  const forecastPoints = [{ date: last.date, forecast: last.observed }, ...future];
  const forecastPath = forecastPoints.map((row, index) => `${index ? "L" : "M"}${x(index + history.length - 1)},${y(row.forecast)}`).join(" ");
  const band = [...future.map((row, index) => `${index ? "L" : "M"}${x(index + history.length)},${y(row.upper)}`).join(" "), ...future.slice().reverse().map((row) => `L${x(history.length + future.indexOf(row))},${y(row.lower)}`).join(" ")].join(" ") + " Z";
  const tickIndices = [...new Set([0, Math.floor((points.length - 1) / 2), points.length - 1])];
  return <div className="chart-wrap"><svg className="line-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Observed retail sales and ${horizon}-month forecast with approximate interval`}>
    {[0, .5, 1].map((ratio) => { const value = low + ratio * (high - low); return <g key={ratio}><line className="grid-line" x1={left} x2={width - right} y1={y(value)} y2={y(value)} /><text className="axis-text" x={left - 8} y={y(value) + 4} textAnchor="end">{billionsFromMillions(value)}</text></g>; })}
    <path d={band} fill="rgba(15,138,123,.14)" stroke="none" />
    <path d={observedPath} fill="none" stroke="#173b63" strokeWidth="3" strokeLinecap="round" />
    <path d={forecastPath} fill="none" stroke="#0f8a7b" strokeWidth="3.5" strokeLinecap="round" strokeDasharray="7 4" />
    {tickIndices.map((index) => <text key={index} className="axis-text" x={x(index)} y={height - 12} textAnchor={index === 0 ? "start" : index === points.length - 1 ? "end" : "middle"}>{monthLabel(points[index].date)}</text>)}
  </svg><div className="chart-legend"><span><i style={{ background: "#173b63" }} />Observed</span><span><i style={{ background: "#0f8a7b" }} />Holt–Winters forecast</span><span><i style={{ background: "#a8ded3" }} />Approx. 80% band</span></div></div>;
}

export default function ForecastTool() {
  const [horizon, setHorizon] = useState(12);
  const future = data.future.slice(0, horizon);
  const peak = future.reduce((best, row) => row.forecast > best.forecast ? row : best, future[0]);
  return <>
    <Notice title="Macro planning indicator">FRED series <b>RSAFSNA</b> covers national retail trade and food-services sales, not seasonally adjusted. It is not store, category, or SKU demand.</Notice>
    <KpiGrid items={[
      { label: "Latest observation", value: monthLabel(data.latestDate), note: "Committed snapshot" },
      { label: "Latest sales", value: billionsFromMillions(data.latestSales), note: "Millions USD converted to billions" },
      { label: "Backtest MAE", value: billionsFromMillions(data.metrics.mae), note: "Latest 24-month holdout" },
      { label: "Gain vs baseline", value: percent(data.metrics.improvementPct, 1, true), note: "Lower MAE than year-ago" },
    ]} />
    <Section eyebrow="Planning workspace" title={`Explore a ${horizon}-month forecast`} copy="The backtest remains fixed while the selected future horizon changes, keeping comparisons honest.">
      <Panel title="Forecast horizon" actions={<div className="pill-select">{[3, 6, 9, 12, 15, 18, 21, 24].map((months) => <button key={months} className={horizon === months ? "active" : ""} onClick={() => setHorizon(months)}>{months} mo</button>)}</div>}>
        <ForecastChart horizon={horizon} />
        <div className="form-actions"><button className="button dark" onClick={() => downloadCsv("us-retail-sales-forecast.csv", future.map((row) => ({ observation_date: row.date, forecast_millions_usd: row.forecast, approximate_lower_80: row.lower, approximate_upper_80: row.upper })))}>Download {horizon}-month CSV</button></div>
      </Panel>
      <Notice title="Read the band carefully" tone="amber" icon="±">The shaded range is an empirical approximation from 24-month backtest residuals. It is not a formal prediction interval and may understate a structural shock. Highest selected point: <b>{monthLabel(peak.date)}</b>.</Notice>
    </Section>
    <Section eyebrow="Validation" title="Compare against a credible seasonal baseline">
      <Panel title="Latest 24-month holdout">
        <LineChart valueFormat={billionsFromMillions} labelFormat={monthLabel} series={[
          { name: "Actual", color: "#173b63", points: data.backtest.map((row) => ({ x: row.date, y: row.actual })) },
          { name: "Holt–Winters", color: "#0f8a7b", points: data.backtest.map((row) => ({ x: row.date, y: row.forecast })) },
          { name: "Year-ago baseline", color: "#f4a340", points: data.backtest.map((row) => ({ x: row.date, y: row.naive })) },
        ]} />
      </Panel>
      <KpiGrid columns={3} items={[{ label: "Model MAE", value: `$${number(data.metrics.mae)}M` }, { label: "Model RMSE", value: `$${number(data.metrics.rmse)}M` }, { label: "Seasonal-naive MAE", value: `$${number(data.metrics.naiveMae)}M` }]} />
    </Section>
    <Section eyebrow="Seasonality" title="Recurring calendar pattern retained" copy="Average monthly sales index over the latest 10 years; each year's average is 1.00.">
      <Panel><BarList color="#b66d11" valueFormat={(value) => value.toFixed(2)} items={data.seasonality.map((row) => ({ label: row.month, value: row.index }))} /></Panel>
    </Section>
    <SourceFooter folder="02-sales-forecasting">U.S. Census Bureau via FRED RSAFSNA. Snapshot latest observation: {monthLabel(data.latestDate)}. Refresh intentionally and combine with company-level category data before inventory decisions. <a href="https://fred.stlouisfed.org/series/RSAFSNA" target="_blank" rel="noreferrer">Open FRED ↗</a></SourceFooter>
  </>;
}
