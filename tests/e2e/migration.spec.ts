import { test, expect } from "@playwright/test";

const routes = [
  ["/", "Seven projects."], ["/customer-churn/", "Customer Churn & Retention"],
  ["/retail-sales-forecast/", "U.S. Retail Sales Forecast"], ["/ab-test-calculator/", "A/B Test Decision Calculator"],
  ["/ecommerce-sql/", "E-commerce SQL Analytics"], ["/customer-segmentation/", "Customer Segmentation"],
  ["/financial-planning/", "Financial Planning & Variance"], ["/healthcare-access/", "Healthcare Access & Readiness"],
] as const;

test("all migrated routes render without browser errors", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  for (const [route, heading] of routes) {
    await page.goto(route);
    await expect(page.getByRole("heading", { level: 1 })).toContainText(heading);
    await expect(page.locator(".site-footer")).toBeVisible();
  }
  expect(errors).toEqual([]);
});

test("A/B calculator matches the Python reference and sample planner", async ({ page }) => {
  await page.goto("/ab-test-calculator/");
  await expect(page.getByTestId("ab-outcome")).toContainText("confidence interval clears");
  await expect(page.getByText("2.01e-18", { exact: false })).toBeVisible();
  await expect(page.getByTestId("ab-sample-size")).toHaveText("14,745");
  await page.getByLabel("Target power").selectOption("0.95");
  await expect(page.getByTestId("ab-sample-size")).toHaveText("24,411");
  await page.getByLabel("Control conversions").fill("10000");
  await expect(page.getByTestId("ab-outcome")).toBeVisible();
});

test("churn scoring and thresholds preserve model behavior", async ({ page }) => {
  await page.goto("/customer-churn/");
  await expect(page.getByTestId("churn-risk")).toHaveText("91.4%");
  await page.getByLabel("Customer contract").selectOption("Two year");
  const changed = await page.getByTestId("churn-risk").textContent();
  expect(changed).not.toBe("91.4%");
  await page.getByLabel("Churn operating threshold").focus();
  await page.keyboard.press("Home");
  await expect(page.getByText("95.3%", { exact: true })).toBeVisible();
  await expect(page.getByText("710", { exact: true })).toBeVisible();
});

test("forecast horizon changes and downloads the selected snapshot", async ({ page }) => {
  await page.goto("/retail-sales-forecast/");
  await expect(page.getByRole("heading", { name: "Explore a 12-month forecast" })).toBeVisible();
  await page.getByRole("button", { name: "24 mo", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Explore a 24-month forecast" })).toBeVisible();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download 24-month CSV" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("us-retail-sales-forecast.csv");
});

test("e-commerce cohort and category controls recompute", async ({ page }) => {
  await page.goto("/ecommerce-sql/");
  const before = await page.getByTestId("cohort-retention").textContent();
  await page.getByLabel("Cohort maturity").focus();
  await page.keyboard.press("Home");
  await expect(page.getByTestId("cohort-retention")).not.toHaveText(before || "");
  await expect(page.getByText("Cohort age:")).toContainText("M3");
  await page.getByLabel("SQL query").selectOption("04_cohort_retention.sql");
  await expect(page.locator(".code-block")).toContainText("cohort");
});

test("segmentation filters reproduce the reviewed segment denominator", async ({ page }) => {
  await page.goto("/customer-segmentation/");
  await page.getByLabel("RFM segment filter").selectOption("At Risk");
  await expect(page.getByTestId("segmentation-count")).toHaveText("908 matching customers");
  await page.getByLabel("Campaign segment").selectOption("Champions");
  await expect(page.getByRole("button", { name: "Download 946 anonymized IDs" })).toBeVisible();
});

test("financial scenarios change EBITDA and reset cleanly", async ({ page }) => {
  await page.goto("/financial-planning/");
  const baseline = await page.getByTestId("finance-ebitda").textContent();
  await page.getByLabel("Revenue adjustment").focus();
  await page.keyboard.press("End");
  await expect(page.getByTestId("finance-ebitda")).not.toHaveText(baseline || "");
  await page.getByRole("button", { name: "Reset scenario" }).click();
  await expect(page.getByTestId("finance-ebitda")).toHaveText(baseline || "");
});

test("healthcare filters preserve the higher-priority denominator", async ({ page }) => {
  await page.goto("/healthcare-access/");
  await page.getByLabel("Review priority band").selectOption("Higher review priority");
  await expect(page.getByTestId("healthcare-count")).toHaveText("Current filter: 10 states/UTs");
  await page.getByLabel("Minimum data completeness").focus();
  await page.keyboard.press("End");
  await expect(page.getByTestId("healthcare-count")).toBeVisible();
});

test("390px layouts avoid horizontal page overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  for (const [route] of routes) {
    await page.goto(route);
    const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth }));
    expect(dimensions.scroll, route).toBeLessThanOrEqual(dimensions.client + 1);
  }
});

test("capture desktop visual evidence", async ({ page }) => {
  await page.goto("/");
  await page.screenshot({ path: "test-results/home-desktop.png", fullPage: true });
  await page.goto("/ab-test-calculator/");
  await page.screenshot({ path: "test-results/ab-desktop.png", fullPage: true });
});
