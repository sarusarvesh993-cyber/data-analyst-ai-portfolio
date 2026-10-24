export type Project = {
  number: string;
  slug: string;
  title: string;
  shortTitle: string;
  description: string;
  tags: string[];
  accent: string;
  soft: string;
  sourceFolder: string;
};

export const projects: Project[] = [
  {
    number: "01", slug: "/customer-churn/", title: "Customer Churn & Retention", shortTitle: "Churn",
    description: "Prioritize retention outreach with a reproducible classifier, adjustable threshold, and customer-level risk scenario.",
    tags: ["Classification", "ROC–AUC 0.886", "Thresholds"], accent: "#0f8a7b", soft: "#ddf7f1", sourceFolder: "01-customer-churn",
  },
  {
    number: "02", slug: "/retail-sales-forecast/", title: "U.S. Retail Sales Forecast", shortTitle: "Forecast",
    description: "Backtest a seasonal forecast against a year-ago baseline and examine uncertainty over the planning horizon.",
    tags: ["Time series", "36.4% MAE gain", "Backtesting"], accent: "#b66d11", soft: "#fff0d9", sourceFolder: "02-sales-forecasting",
  },
  {
    number: "03", slug: "/ab-test-calculator/", title: "A/B Test Decision Calculator", shortTitle: "A/B testing",
    description: "Evaluate conversion lift, confidence intervals, practical significance, expected impact, and required sample size.",
    tags: ["Experimentation", "Confidence intervals", "Power"], accent: "#6c59cf", soft: "#ece9ff", sourceFolder: "03-ab-test",
  },
  {
    number: "04", slug: "/ecommerce-sql/", title: "E-commerce SQL Analytics", shortTitle: "E-commerce SQL",
    description: "Analyze marketplace orders with safe SQL grains, cohort retention, delivery KPIs, and category performance.",
    tags: ["DuckDB SQL", "Cohorts", "Data quality"], accent: "#c55745", soft: "#fde8e3", sourceFolder: "04-ecommerce-sql",
  },
  {
    number: "05", slug: "/customer-segmentation/", title: "Customer Segmentation", shortTitle: "Segmentation",
    description: "Build transparent RFM audiences, validate a clustering challenger, and turn segments into measurable campaign tests.",
    tags: ["RFM", "K-means", "Power BI"], accent: "#246585", soft: "#e4f1f8", sourceFolder: "05-customer-segmentation",
  },
  {
    number: "06", slug: "/financial-planning/", title: "Financial Planning & Variance", shortTitle: "FP&A",
    description: "Reconcile a real operating budget, investigate Q3 pacing, and test revenue, cost, and hiring scenarios.",
    tags: ["FP&A", "Excel", "Budget vs actual"], accent: "#327149", soft: "#e6f3ea", sourceFolder: "06-financial-planning",
  },
  {
    number: "07", slug: "/healthcare-access/", title: "Healthcare Access & Readiness", shortTitle: "Healthcare",
    description: "Model state access and staffing in DuckDB, then screen review priorities with visible data completeness.",
    tags: ["Healthcare", "DuckDB", "Public data"], accent: "#a43e5a", soft: "#f9e7ec", sourceFolder: "07-healthcare-access",
  },
];

export const repository = "https://github.com/sarusarvesh993-cyber/data-analyst-ai-portfolio";
