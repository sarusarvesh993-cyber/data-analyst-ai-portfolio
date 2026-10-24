const protectText = (value: string) => /^[=+\-@\t\r]/.test(value) ? `'${value}` : value;

const cell = (value: unknown) => {
  if (value === null || value === undefined) return "";
  // Keep numeric values numeric, including legitimate negative numbers.
  if (typeof value === "number" && Number.isFinite(value)) return String(value);
  const text = protectText(String(value)).replace(/"/g, '""');
  return `"${text}"`;
};

export function downloadCsv(filename: string, rows: Array<Record<string, unknown>>) {
  if (!rows.length) return;
  const columns = [...new Set(rows.flatMap((row) => Object.keys(row)))];
  const content = [columns.map(cell).join(","), ...rows.map((row) => columns.map((key) => cell(row[key])).join(","))].join("\r\n");
  downloadText(filename, `\uFEFF${content}`, "text/csv;charset=utf-8");
}

export function downloadText(filename: string, content: string, type = "text/plain;charset=utf-8") {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
