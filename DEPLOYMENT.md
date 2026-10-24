# Vercel deployment

The production app is now the static Next.js application in `app/`, not the legacy Streamlit server. See `MIGRATION_VERCEL.md` for route parity, architecture, and verification evidence.

## 1. Verify locally

```powershell
npm ci
npm run typecheck
npm run build
npx playwright install chromium
npm test
```

Optional original-analysis checks:

```powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest -q
python scripts/export_web_data.py
```

Do not commit `.env`, `.streamlit/secrets.toml`, a Hugging Face token, a Vercel token, `node_modules`, `.next`, `out`, or `.vercel`.

## 2. Push the reviewed migration

```powershell
git status
git add .
git commit -m "Migrate analytics portfolio from Streamlit to Vercel"
git push origin main
```

The existing Vercel project connected to `sarusarvesh993-cyber/data-analyst-ai-portfolio` will build the pushed commit.

## 3. Vercel settings

The supplied `vercel.json` is authoritative:

```json
{
  "framework": null,
  "buildCommand": "npm run build",
  "outputDirectory": "out"
}
```

This selects **Other** and serves the completed static export. No Python entrypoint, environment variable, Function, cron job, persistent storage, or paid API is required.

## 4. Production acceptance

Run against the actual HTTPS production alias:

```powershell
$env:PLAYWRIGHT_BASE_URL="https://YOUR-REAL-DEPLOYMENT.vercel.app"
npm test
```

Also verify in a private browser window:

- All eight routes load directly and on refresh.
- A/B default planner reads 14,745 per arm; 95% power reads 24,411.
- Churn default scenario reads 91.4%; threshold 0.20 reads 95.3% recall and 710 flagged.
- Forecast horizon and CSV, cohort controls, segmentation filters/exports, FP&A scenario/reset, and healthcare filters work.
- No horizontal page overflow appears at 390px; wide data tables scroll internally.
- No live LLM call, runtime secret, or Python server is expected.

## 5. Finish the cutover

1. Record the production URL and deployment commit.
2. Update the pending Vercel link in `README.md` only after tests pass.
3. Update external portfolio links to the Vercel routes.
4. Keep the previous Streamlit app labeled **legacy** until the owner decides to retire it.

Rollback by reverting the migration commit in GitHub/Vercel. The original Streamlit files remain available for a separate legacy deployment.
