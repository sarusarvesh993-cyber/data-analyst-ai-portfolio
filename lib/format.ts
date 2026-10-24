export const number = (value: number, decimals = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: decimals, minimumFractionDigits: decimals }).format(value);

export const percent = (value: number, decimals = 1, inputIsPercent = false) =>
  `${number(inputIsPercent ? value : value * 100, decimals)}%`;

export const signedPercent = (value: number, decimals = 1, inputIsPercent = false) => {
  const normalized = inputIsPercent ? value : value * 100;
  return `${normalized >= 0 ? "+" : ""}${number(normalized, decimals)}%`;
};

export const compact = (value: number, currency = "", decimals = 1) => {
  const absolute = Math.abs(value);
  if (absolute >= 1_000_000_000) return `${currency}${number(value / 1_000_000_000, decimals)}B`;
  if (absolute >= 1_000_000) return `${currency}${number(value / 1_000_000, decimals)}M`;
  if (absolute >= 1_000) return `${currency}${number(value / 1_000, decimals)}K`;
  return `${currency}${number(value, 2)}`;
};

export const monthLabel = (value: string) => {
  const date = new Date(`${value.slice(0, 10)}T00:00:00Z`);
  return new Intl.DateTimeFormat("en", { month: "short", year: "numeric", timeZone: "UTC" }).format(date);
};

export const finite = (value: unknown, fallback = 0) => {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

export const median = (values: number[]) => {
  const valid = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!valid.length) return null;
  const middle = Math.floor(valid.length / 2);
  return valid.length % 2 ? valid[middle] : (valid[middle - 1] + valid[middle]) / 2;
};
