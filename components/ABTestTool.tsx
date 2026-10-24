"use client";

import { useMemo, useState } from "react";
import { BarList, KpiGrid, Notice, Panel, Section, SourceFooter } from "@/components/ui";
import { downloadCsv } from "@/lib/csv";
import { number, percent, signedPercent } from "@/lib/format";
import { abDecision, analyzeAB, requiredSamplePerArm } from "@/lib/stats";

export default function ABTestTool() {
  const [controlVisitors, setControlVisitors] = useState(100_000);
  const [controlConversions, setControlConversions] = useState(11_522);
  const [treatmentVisitors, setTreatmentVisitors] = useState(100_000);
  const [treatmentConversions, setTreatmentConversions] = useState(12_802);
  const [practicalPp, setPracticalPp] = useState(0.5);
  const [alpha, setAlpha] = useState(0.05);
  const [baseline, setBaseline] = useState(10);
  const [mde, setMde] = useState(10);
  const [power, setPower] = useState(0.8);

  const analysis = useMemo(() => {
    try {
      const result = analyzeAB(controlVisitors, controlConversions, treatmentVisitors, treatmentConversions, alpha);
      return { result, decision: abDecision(result, practicalPp / 100, alpha), error: "" };
    } catch (error) { return { result: null, decision: null, error: error instanceof Error ? error.message : "Invalid experiment values." }; }
  }, [controlVisitors, controlConversions, treatmentVisitors, treatmentConversions, practicalPp, alpha]);
  const sample = useMemo(() => {
    try { return { value: requiredSamplePerArm(baseline / 100, mde / 100, 0.05, power), error: "" }; }
    catch (error) { return { value: null, error: error instanceof Error ? error.message : "Invalid planning assumptions." }; }
  }, [baseline, mde, power]);

  return <>
    <Notice title="Decision rule" tone="teal">A small p-value is not enough. The result should also clear a business-defined minimum useful lift and pass experiment-quality checks before rollout.</Notice>
    {analysis.result && <KpiGrid items={[
      { label: "Control rate", value: percent(analysis.result.controlRate, 2) },
      { label: "Treatment rate", value: percent(analysis.result.treatmentRate, 2) },
      { label: "Relative lift", value: signedPercent(analysis.result.relativeLift, 1) },
      { label: "Two-sided p-value", value: analysis.result.pValue.toPrecision(3), note: `z = ${analysis.result.zScore.toFixed(3)}` },
    ]} />}

    <Section eyebrow="Experiment workspace" title="Test the observed result" copy="Uses a two-sided pooled two-proportion z-test and an unpooled confidence interval for treatment minus control.">
      <div className="two-column wide-left">
        <Panel title="Cumulative experiment counts" copy="Edit all four values; results update immediately.">
          <div className="form-grid">
            <label className="field"><span>Control visitors</span><input aria-label="Control visitors" type="number" min="1" step="100" value={controlVisitors} onChange={(e) => setControlVisitors(Number(e.target.value))} /></label>
            <label className="field"><span>Control conversions</span><input aria-label="Control conversions" type="number" min="0" step="10" value={controlConversions} onChange={(e) => setControlConversions(Number(e.target.value))} /></label>
            <label className="field"><span>Treatment visitors</span><input aria-label="Treatment visitors" type="number" min="1" step="100" value={treatmentVisitors} onChange={(e) => setTreatmentVisitors(Number(e.target.value))} /></label>
            <label className="field"><span>Treatment conversions</span><input aria-label="Treatment conversions" type="number" min="0" step="10" value={treatmentConversions} onChange={(e) => setTreatmentConversions(Number(e.target.value))} /></label>
            <label className="field"><span>Minimum useful lift: <b className="control-value">{practicalPp.toFixed(1)} pp</b></span><input aria-label="Minimum useful lift" type="range" min="0" max="5" step="0.1" value={practicalPp} onChange={(e) => setPracticalPp(Number(e.target.value))} /></label>
            <label className="field"><span>Significance level α</span><select aria-label="Significance level" value={alpha} onChange={(e) => setAlpha(Number(e.target.value))}><option value="0.01">0.01 · 99% confidence</option><option value="0.05">0.05 · 95% confidence</option><option value="0.10">0.10 · 90% confidence</option></select></label>
          </div>
          {analysis.error && <p className="negative" role="alert">{analysis.error}</p>}
          {analysis.result && <div className="form-actions"><button className="button dark" onClick={() => downloadCsv("ab-test-result.csv", [{
            control_visitors: controlVisitors, control_conversions: controlConversions, treatment_visitors: treatmentVisitors,
            treatment_conversions: treatmentConversions, control_rate: analysis.result!.controlRate, treatment_rate: analysis.result!.treatmentRate,
            absolute_lift: analysis.result!.absoluteLift, relative_lift: analysis.result!.relativeLift, p_value: analysis.result!.pValue,
            ci_low: analysis.result!.ciLow, ci_high: analysis.result!.ciHigh, decision: analysis.decision![0],
          }])}>Download result CSV</button></div>}
        </Panel>
        <div className="stack">
          {analysis.result && analysis.decision && <>
            <Notice title={analysis.decision[0]} tone={analysis.decision[0] === "Ship treatment" ? "teal" : "amber"} icon="→"><span data-testid="ab-outcome">{analysis.decision[1]}</span></Notice>
            <Panel title="Effect and uncertainty">
              <div className="three-column">
                <div className="mini-stat"><span>Absolute lift</span><strong>{signedPercent(analysis.result.absoluteLift, 2)}</strong></div>
                <div className="mini-stat"><span>{(1 - alpha) * 100}% CI low</span><strong>{signedPercent(analysis.result.ciLow, 2)}</strong></div>
                <div className="mini-stat"><span>Incremental conversions</span><strong>{number(analysis.result.incrementalConversions)}</strong></div>
              </div>
              <p className="helper-text">{percent(1 - alpha, 0)} confidence interval: [{signedPercent(analysis.result.ciLow, 2)}, {signedPercent(analysis.result.ciHigh, 2)}]</p>
            </Panel>
          </>}
        </div>
      </div>
      {analysis.result && <Panel title="Observed conversion rates"><BarList color="#6c59cf" valueFormat={(value) => percent(value, 2)} items={[{ label: "Control", value: analysis.result.controlRate }, { label: "Treatment", value: analysis.result.treatmentRate }]} /></Panel>}
    </Section>

    <Section eyebrow="Pre-registration" title="Plan the next sample before seeing the result" copy="Equal-sized groups, two-sided α = 0.05, normal approximation to the two-proportion test.">
      <div className="two-column">
        <Panel title="Sample-size assumptions">
          <div className="form-grid three">
            <label className="field"><span>Expected baseline %</span><input aria-label="Expected baseline" type="number" min="0.1" max="99" step="0.1" value={baseline} onChange={(e) => setBaseline(Number(e.target.value))} /></label>
            <label className="field"><span>Minimum relative lift %</span><input aria-label="Minimum relative lift" type="number" min="0.1" max="100" step="0.5" value={mde} onChange={(e) => setMde(Number(e.target.value))} /></label>
            <label className="field"><span>Target power</span><select aria-label="Target power" value={power} onChange={(e) => setPower(Number(e.target.value))}><option value="0.8">80%</option><option value="0.85">85%</option><option value="0.9">90%</option><option value="0.95">95%</option></select></label>
          </div>
          {sample.error && <p className="negative" role="alert">{sample.error}</p>}
        </Panel>
        {sample.value !== null && <div className="result-banner"><div><span>Required sample per arm</span><strong data-testid="ab-sample-size">{number(sample.value)}</strong></div><p>Total visitors: <b>{number(sample.value * 2)}</b>. No adjustment for attrition, repeated peeking, unequal allocation, or multiple metrics.</p></div>}
      </div>
    </Section>

    <Section eyebrow="Method" title="What the calculator assumes">
      <div className="two-column"><Panel title="Core assumptions"><ol className="method-list"><li>Independent randomized users</li><li>Concurrent experiment variants</li><li>Pre-specified conversion event and window</li><li>Adequate expected successes and failures</li><li>No unplanned repeated stopping</li></ol></Panel>
      <Panel title="Controlled decision brief"><p className="helper-text">This Vercel edition generates no live LLM prose. The decision label is a deterministic rule applied to the displayed statistics and your practical threshold.</p><p className="helper-text">Confirm guardrail metrics, randomization quality, and experiment duration before rollout.</p></Panel></div>
    </Section>
    <SourceFooter folder="03-ab-test">The included example is synthetic. A non-significant result is not proof of equality; repeated peeking changes the false-positive rate.</SourceFooter>
  </>;
}
