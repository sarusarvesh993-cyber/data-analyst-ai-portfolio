"use client";

import { useMemo, useState } from "react";
import data from "@/public/data/churn.json";
import { BarList, KpiGrid, Notice, Panel, Section, SourceFooter } from "@/components/ui";
import { downloadCsv } from "@/lib/csv";
import { number, percent } from "@/lib/format";

type Contract = "Month-to-month" | "One year" | "Two year";
type Internet = "DSL" | "Fiber optic" | "No";
type YesNo = "Yes" | "No";
type Payment = "Electronic check" | "Mailed check" | "Bank transfer" | "Credit card";

export default function ChurnTool() {
  const [threshold, setThreshold] = useState(0.5);
  const [tenure, setTenure] = useState(8);
  const [monthly, setMonthly] = useState(85);
  const [senior, setSenior] = useState(false);
  const [dependents, setDependents] = useState(false);
  const [contract, setContract] = useState<Contract>("Month-to-month");
  const [internet, setInternet] = useState<Internet>("DSL");
  const [tech, setTech] = useState<YesNo>("No");
  const [security, setSecurity] = useState<YesNo>("No");
  const [payment, setPayment] = useState<Payment>("Electronic check");

  const metrics = data.thresholds[Math.round((threshold - 0.2) / 0.05)];
  const probability = useMemo(() => {
    const model = data.model;
    let logit = model.intercept;
    logit += (tenure - model.numeric.tenure.mean) / model.numeric.tenure.scale * model.numeric.tenure.coefficient;
    logit += (monthly - model.numeric.MonthlyCharges.mean) / model.numeric.MonthlyCharges.scale * model.numeric.MonthlyCharges.coefficient;
    logit += (Number(senior) - model.numeric.SeniorCitizen.mean) / model.numeric.SeniorCitizen.scale * model.numeric.SeniorCitizen.coefficient;
    logit += (Number(dependents) - model.numeric.Dependents.mean) / model.numeric.Dependents.scale * model.numeric.Dependents.coefficient;
    logit += model.categorical.Contract[contract] + model.categorical.InternetService[internet] + model.categorical.TechSupport[tech] + model.categorical.OnlineSecurity[security] + model.categorical.PaymentMethod[payment];
    return 1 / (1 + Math.exp(-logit));
  }, [tenure, monthly, senior, dependents, contract, internet, tech, security, payment]);
  const band = probability >= 0.65 ? "High" : probability >= 0.35 ? "Medium" : "Low";

  return <>
    <Notice title="Demonstration dataset" tone="amber">The 5,000 customer records are generated from a fixed seed. This page demonstrates a reproducible workflow; its findings are not estimates for a real company.</Notice>
    <KpiGrid items={[
      { label: "Customer records", value: number(data.records) },
      { label: "Observed churn", value: percent(data.observedChurn, 1) },
      { label: "Holdout ROC–AUC", value: data.auc.toFixed(3), note: "Logistic regression" },
      { label: "Holdout sample", value: number(data.holdoutRows) },
    ]} />

    <Section eyebrow="Portfolio patterns" title="Where the synthetic model sees risk" copy="Associations in generated data demonstrate analysis and delivery—not real customer causation.">
      <div className="two-column">
        <Panel title="Churn rate by contract"><BarList valueFormat={(value) => percent(value, 1)} items={data.contractRates.map((row) => ({ label: row.Contract, value: row.Churn }))} /></Panel>
        <Panel title="Churn rate by tenure band"><BarList color="#173b63" valueFormat={(value) => percent(value, 1)} items={data.tenureRates.map((row) => ({ label: `${row.tenure_band} months`, value: row.Churn }))} /></Panel>
      </div>
    </Section>

    <Section eyebrow="Customer scenario" title="Score one account with the exported model" copy="The browser applies the original scaler, one-hot coefficients, and logistic intercept. No Python service is called.">
      <div className="split-layout">
        <Panel title="Account profile">
          <div className="stack">
            <label className="field"><span>Tenure: <b className="control-value">{tenure} months</b></span><input aria-label="Customer tenure" type="range" min="1" max="72" value={tenure} onChange={(e) => setTenure(Number(e.target.value))} /></label>
            <label className="field"><span>Monthly charges: <b className="control-value">${monthly}</b></span><input aria-label="Monthly charges" type="range" min="20" max="120" value={monthly} onChange={(e) => setMonthly(Number(e.target.value))} /></label>
            <label className="field"><span>Contract</span><select aria-label="Customer contract" value={contract} onChange={(e) => setContract(e.target.value as Contract)}><option>Month-to-month</option><option>One year</option><option>Two year</option></select></label>
            <label className="field"><span>Internet service</span><select aria-label="Internet service" value={internet} onChange={(e) => setInternet(e.target.value as Internet)}><option>DSL</option><option>Fiber optic</option><option>No</option></select></label>
            <div className="form-grid">
              <label className="field"><span>Tech support</span><select aria-label="Tech support" value={tech} onChange={(e) => setTech(e.target.value as YesNo)}><option>No</option><option>Yes</option></select></label>
              <label className="field"><span>Online security</span><select aria-label="Online security" value={security} onChange={(e) => setSecurity(e.target.value as YesNo)}><option>No</option><option>Yes</option></select></label>
            </div>
            <label className="field"><span>Payment method</span><select aria-label="Payment method" value={payment} onChange={(e) => setPayment(e.target.value as Payment)}><option>Electronic check</option><option>Mailed check</option><option>Bank transfer</option><option>Credit card</option></select></label>
            <label className="field-inline"><input type="checkbox" checked={senior} onChange={(e) => setSenior(e.target.checked)} />Senior citizen</label>
            <label className="field-inline"><input type="checkbox" checked={dependents} onChange={(e) => setDependents(e.target.checked)} />Has dependents</label>
          </div>
        </Panel>
        <div className="stack">
          <div className="result-banner"><div><span>Estimated churn score</span><strong data-testid="churn-risk" className={`score-${band.toLowerCase()}`}>{percent(probability, 1)}</strong></div><p><b>{band} outreach priority.</b> Score bands: High ≥65%, Medium ≥35%. This is a synthetic model score, not a calibrated real-world probability.</p></div>
          <Panel title="Decision guidance"><p className="helper-text">A real retention program should validate the model on production data, estimate contact economics, and measure incremental retention with a randomized holdout.</p><p className="helper-text">Default reference profile reproduces the Python model at <b>{percent(data.reference.probability, 1)}</b>.</p></Panel>
        </div>
      </div>
    </Section>

    <Section eyebrow="Model diagnostics" title="Choose an operating threshold" copy="A lower threshold captures more churners but creates more unnecessary contacts.">
      <Panel title={`Flag customers at or above ${threshold.toFixed(2)}`}>
        <label className="field"><span>Operating threshold</span><input aria-label="Churn operating threshold" type="range" min="0.2" max="0.8" step="0.05" value={threshold} onChange={(e) => setThreshold(Number(e.target.value))} /></label>
        <KpiGrid items={[
          { label: "Precision", value: percent(metrics.precision, 1) }, { label: "Recall", value: percent(metrics.recall, 1) },
          { label: "F1 score", value: metrics.f1.toFixed(3) }, { label: "Customers flagged", value: number(metrics.flagged) },
        ]} />
        <div className="two-column">
          <div><h3 className="subtle">Holdout confusion matrix</h3><div className="confusion"><div className="matrix-label">Actual / predicted</div><div className="matrix-label">Stay</div><div className="matrix-label">Churn</div><div className="matrix-label">Actual stay</div><div className="matrix-value">{metrics.confusionMatrix[0][0]}</div><div className="matrix-value">{metrics.confusionMatrix[0][1]}</div><div className="matrix-label">Actual churn</div><div className="matrix-value">{metrics.confusionMatrix[1][0]}</div><div className="matrix-value">{metrics.confusionMatrix[1][1]}</div></div></div>
          <div><h3 className="subtle">Top coefficient magnitudes</h3><BarList items={data.importance.slice(0, 6).map((row) => ({ label: row.feature, value: row.importance }))} valueFormat={(value) => value.toFixed(3)} /></div>
        </div>
        <div className="form-actions"><button className="button ghost" onClick={() => downloadCsv("churn-threshold-metrics.csv", data.thresholds.map((row) => ({ ...row, confusionMatrix: undefined })))}>Download threshold metrics</button></div>
      </Panel>
    </Section>
    <SourceFooter folder="01-customer-churn">Seeded synthetic customers; 80/20 stratified holdout. Coefficient magnitude is association, not causation. Choose thresholds from campaign capacity and the cost of missed churners.</SourceFooter>
  </>;
}
