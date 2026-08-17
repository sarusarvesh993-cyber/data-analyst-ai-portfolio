# Deploy the Plotly Dash command center

The production entry point is `ecommerce_dash_app.py`. It exposes both `app`
and the Flask `server` object expected by managed hosts.

## 1. Validate locally

From the repository root in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python ecommerce_dash_app.py
```

Open `http://127.0.0.1:8050` and review all five navigation sections, the
filters, SQL selector, table sorting, and executive-brief download.

## 2. Publish on the Plotly Cloud free plan

Plotly's official Dash documentation states that getting started with Plotly
Cloud is free. It supports publishing from local Dash developer tools or by
uploading files at `https://cloud.plotly.com/`.

1. Create or sign in to an account at `https://cloud.plotly.com/`.
2. Stop the local app with `Ctrl+C`.
3. Install the optional Cloud publishing extension:

   ```powershell
   python -m pip install "dash[cloud]"
   ```

4. Start this app in debug mode:

   ```powershell
   $env:DASH_DEBUG = "1"
   python ecommerce_dash_app.py
   ```

5. Open `http://127.0.0.1:8050`.
6. Open the Dash developer-tools panel and select **Plotly Cloud**.
7. Sign in through the browser window, return to the app, and use the app name
   `olist-commerce-command-center`.
8. Select the free personal team and choose **Publish App**.
9. When the build reports **App is live**, open it and set sharing to public.
10. Copy the exact public URL.

The repository remains comfortably below Plotly Cloud's documented file-size
limits because raw Olist CSVs, the local DuckDB file, and the virtual
environment are ignored.

## 3. Link the Streamlit portfolio to Dash

The Streamlit summary checks `ECOMMERCE_DASH_URL`. In Streamlit Community
Cloud, open the portfolio app's **Settings → Secrets** and add:

```toml
ECOMMERCE_DASH_URL = "https://your-plotly-cloud-url"
```

Save and reboot the Streamlit app. The Project 04 page will then show a
**Launch the full Plotly Dash command center** button.

## 4. Production checklist

- The Dash home page loads without a callback error.
- All five navigation views render.
- Date, state, and category controls update their supported grains.
- The SQL selector displays the committed query files.
- The quality table shows seven `PASS` checks and one documented `REVIEW`.
- The executive brief downloads as a text file.
- The app is publicly accessible in a private/incognito browser window.
- The Streamlit portfolio's Project 04 launch button opens the Dash URL.

No API token, database credential, or paid service is required at runtime.
