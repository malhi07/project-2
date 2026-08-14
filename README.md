# Project Two — Writing Practice (Streamlit)

Free, open-source English writing practice with AI feedback, scored against
CLB (Canadian Language Benchmark) descriptors. Built to run entirely from
GitHub + Streamlit Cloud — no local install required.

## What's included
- `app.py` — the full Streamlit app (task selection, timed writing box, AI scoring, detailed feedback)
- `data/clb-descriptors.json` — editable scoring rubric (four dimensions, CLB scale 1-12)
- `data/writing-tasks.json` — writing task prompts
- `requirements.txt` — Python dependencies for Streamlit Cloud to install automatically
- `PROJECT_TWO_SPEC.md` — full build spec for the remaining modules (Listening, Reading, Speaking, Vocabulary, Dashboard, Study Plan)

## Deploy with zero local setup

### 1. Get this code onto GitHub (via browser only)
1. Go to https://github.com/new and create a repo named `project-two` (public or private, your choice). Don't add a README — you already have one.
2. On the new empty repo page, click **"uploading an existing file"**.
3. Drag in every file from this folder (`app.py`, `requirements.txt`, `README.md`, `PROJECT_TWO_SPEC.md`, `secrets.toml.example`, and the whole `data/` folder).
4. Click **Commit changes**.

### 2. Deploy on Streamlit Cloud (also browser only)
1. Go to https://share.streamlit.io and sign in with your GitHub account.
2. Click **"Create app"** → choose **"From existing repo"**.
3. Select your `project-two` repo, branch `main`, and set the main file path to `app.py`.
4. Before or after deploying, go to **App settings → Secrets** and paste:
   ```
   ANTHROPIC_API_KEY = "your-real-api-key-here"
   ```
   (Get a key at https://console.anthropic.com if you don't have one.)
5. Click **Deploy**. Streamlit Cloud will install `requirements.txt` and launch the app automatically. You'll get a public URL like `https://your-app-name.streamlit.app`.

That's it — no terminal, no local Node/Python installs. Any time you edit files on GitHub, Streamlit Cloud automatically redeploys.

## Continuing development
Open this repo in Claude Code (it can work directly against a cloned GitHub repo) and ask it to
build the next module from `PROJECT_TWO_SPEC.md` — e.g. "add the Vocabulary practice module as a
new page in this Streamlit app." Keep the same pattern: config-driven data files + a Streamlit view.
