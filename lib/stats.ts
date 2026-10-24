export type ABResult = {
  controlRate: number;
  treatmentRate: number;
  absoluteLift: number;
  relativeLift: number;
  zScore: number;
  pValue: number;
  ciLow: number;
  ciHigh: number;
  incrementalConversions: number;
};

// Abramowitz-Stegun approximation; adequate for displayed decision statistics.
export function normalCdf(value: number) {
  const sign = value < 0 ? -1 : 1;
  const x = Math.abs(value) / Math.sqrt(2);
  const t = 1 / (1 + 0.3275911 * x);
  const erf = sign * (1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x));
  return 0.5 * (1 + erf);
}

// Survival function with a continued-fraction tail approximation. Unlike
// 1 - CDF, this retains small p-values for large absolute z-scores.
export function normalSf(value: number) {
  const x = Math.abs(value);
  if (x > 5.5) {
    const phi = Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
    let fraction = 0;
    for (let n = 24; n >= 1; n -= 1) fraction = n / (x + fraction);
    return phi / (x + fraction);
  }
  return 1 - normalCdf(x);
}

export function analyzeAB(controlVisitors: number, controlConversions: number, treatmentVisitors: number, treatmentConversions: number, alpha: number): ABResult {
  const values = [controlVisitors, controlConversions, treatmentVisitors, treatmentConversions];
  if (values.some((value) => !Number.isInteger(value) || value < 0)) throw new Error("Visitors and conversions must be non-negative integers.");
  if (!controlVisitors || !treatmentVisitors) throw new Error("Each variant must have at least one visitor.");
  if (controlConversions > controlVisitors || treatmentConversions > treatmentVisitors) throw new Error("Conversions cannot exceed visitors.");
  const controlRate = controlConversions / controlVisitors;
  const treatmentRate = treatmentConversions / treatmentVisitors;
  const difference = treatmentRate - controlRate;
  const pooled = (controlConversions + treatmentConversions) / (controlVisitors + treatmentVisitors);
  const pooledSe = Math.sqrt(pooled * (1 - pooled) * (1 / controlVisitors + 1 / treatmentVisitors));
  const zScore = pooledSe === 0 ? 0 : difference / pooledSe;
  const pValue = pooledSe === 0 ? 1 : Math.min(1, 2 * normalSf(Math.abs(zScore)));
  const ciSe = Math.sqrt(controlRate * (1 - controlRate) / controlVisitors + treatmentRate * (1 - treatmentRate) / treatmentVisitors);
  const critical = alpha === 0.01 ? 2.5758293035489004 : alpha === 0.10 ? 1.6448536269514722 : 1.959963984540054;
  return {
    controlRate, treatmentRate, absoluteLift: difference,
    relativeLift: controlRate ? difference / controlRate : Infinity,
    zScore, pValue, ciLow: difference - critical * ciSe, ciHigh: difference + critical * ciSe,
    incrementalConversions: difference * treatmentVisitors,
  };
}

export function abDecision(result: ABResult, practicalLift: number, alpha: number) {
  if (result.pValue < alpha && result.ciLow >= practicalLift) return ["Ship treatment", "Statistically significant, and the confidence interval clears the minimum useful lift."];
  if (result.pValue < alpha && result.absoluteLift > practicalLift) return ["Promising, but assess value", "Average lift is useful, but the interval does not fully clear the practical threshold."];
  if (result.ciHigh < practicalLift) return ["Do not ship for this goal", "The confidence interval is below the minimum useful lift set for the experiment."];
  return ["Continue or redesign test", "The evidence is inconclusive; a non-significant result does not prove equivalence."];
}

export function requiredSamplePerArm(baselineRate: number, relativeMde: number, alpha: number, power: number) {
  if (!(baselineRate > 0 && baselineRate < 1)) throw new Error("Baseline conversion must be between 0% and 100%.");
  if (!(relativeMde > 0 && relativeMde < 1)) throw new Error("Relative MDE must be between 0% and 100%.");
  const treatmentRate = baselineRate * (1 + relativeMde);
  if (treatmentRate >= 1) throw new Error("Baseline plus the minimum effect must remain below 100%.");
  const effect = Math.abs(2 * Math.asin(Math.sqrt(treatmentRate)) - 2 * Math.asin(Math.sqrt(baselineRate)));
  const zAlpha = alpha === 0.01 ? 2.5758293035489004 : alpha === 0.10 ? 1.6448536269514722 : 1.959963984540054;
  const powerZ: Record<string, number> = { "0.8": 0.8416212335729143, "0.85": 1.0364333894937898, "0.9": 1.2815515655446004, "0.95": 1.6448536269514722 };
  const zPower = powerZ[String(power)];
  if (!zPower) throw new Error("Unsupported target power.");
  // Equal-arm normal approximation used by statsmodels NormalIndPower.
  return Math.ceil(2 * ((zAlpha + zPower) / effect) ** 2);
}
