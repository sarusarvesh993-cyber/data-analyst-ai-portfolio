# Free Streamlit Deployment

The repository is prepared as one multi-page app. The entry file is `streamlit_app.py`; the pages are discovered from `pages/`.

## 1. Verify locally in Windows PowerShell

First, open PowerShell in the folder that actually contains the repository. Do not type `path\to\...` literally. For the usual GitHub Desktop location, use:

```powershell
Set-Location "$HOME\Documents\GitHub\data-analyst-ai-portfolio"
```

Then create the environment and run the checks:

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run streamlit_app.py
```

`requirements-dev.txt` includes the runtime packages plus pytest and the notebook tools.

Check the home page and all three project pages before pushing.

## 2. Push the reviewed files

```powershell
git status
git add .
git commit -m "Add tested multi-page analytics app"
git push origin main
```

Never commit `.env`, a GitHub token, or a Hugging Face token. `.gitignore` already excludes `.env`.

## 3. Create the free cloud app

1. Go to <https://share.streamlit.io/> and sign in with the GitHub account that owns the repository.
2. Select **Create app**.
3. Choose:
   - Repository: `sarusarvesh993-cyber/data-analyst-ai-portfolio`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. Choose an available app URL.
5. Deploy and wait for the dependency installation to finish.

The public repository produces a public app. Streamlit reads `requirements.txt` and `runtime.txt` from the repository.

## 4. Optional AI token

The app works without any token. To enable the optional live Hugging Face call:

1. Open the deployed app's settings.
2. Open **Secrets**.
3. Add:

```toml
HF_TOKEN = "your_hugging_face_token"
```

Do not place this token in a tracked file. If the inference service is unavailable, the authored fallback brief is returned.

## 5. Finish the release

After deployment:

1. Copy the final `https://...streamlit.app` URL.
2. Replace the pending-live text in `README.md` with the URL.
3. Add the same URL to each project README.
4. Add a screenshot under `assets/` and verify every GitHub link.
5. Reboot the app once from Streamlit settings after changing dependencies.

## Common failures

- **ModuleNotFoundError:** verify the missing direct dependency is pinned in `requirements.txt`.
- **File not found:** use paths derived from `Path(__file__)`, not the terminal's current directory.
- **App sleeps or starts slowly:** normal on free hosting; model and forecast functions are cached.
- **Forecast data unavailable:** the app uses a committed FRED snapshot, so it does not require a network call at startup.
- **Token failure:** remove the optional secret and confirm the deterministic fallback works.
