# OpenDART API Key and GitHub Pages Setup

## 1. Register the API key in GitHub Secrets

1. Obtain an OpenDART key from https://opendart.fss.or.kr/.
2. Open this repository's **Settings → Secrets and variables → Actions**.
3. Select **New repository secret**.
4. Set the name to **DART_API_KEY** exactly.
5. Paste the issued key into Secret and save.
6. Do not put the key into Python files, JSON, CSV, README, issues, or public logs.

The workflow checks that the secret is present and has the expected 40-character format before sending requests. It never prints the key. If OpenDART returns an invalid-key response, replace the repository secret with a valid key and run the workflow again.

## 2. Enable GitHub Pages

1. Open **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Run **Actions → Samsung Electronics DART Financial Data Update & Deploy → Run workflow**.
4. Follow the latest run at https://github.com/HSC-Class02/hy_samsung-electronics/actions.
5. The dashboard URL is https://hsc-class02.github.io/hy_samsung-electronics/.

The deployment job is separate from data collection, so a failed API refresh does not block deployment of the most recently committed dashboard.

## 3. Run locally (optional)

Python 3.11+ is recommended:

    python -m pip install -r requirements.txt

Windows PowerShell:

    $env:DART_API_KEY = "paste-your-key-in-your-local-terminal-only"
    python scripts/fetch_dart.py --self-test
    python scripts/fetch_dart.py
    python scripts/analyze.py
    python scripts/build_dashboard.py
    python scripts/validate_project.py

macOS/Linux:

    export DART_API_KEY="paste-your-key-in-your-local-terminal-only"
    python scripts/fetch_dart.py --self-test
    python scripts/fetch_dart.py
    python scripts/analyze.py
    python scripts/build_dashboard.py
    python scripts/validate_project.py

Never commit terminal history, .env files, or any local file that contains the API key.
