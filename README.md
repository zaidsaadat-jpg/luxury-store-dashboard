# Luxury Store CO₂ Reduction Dashboard — First Draft

A Streamlit dashboard tracking store-attributable CO₂ for luxury boutiques in
Hong Kong, Singapore, Korea, and China. The methodology is anchored to the
**Chanel Mission 1.5 / Net-Zero 2040** framework (2021 base year) as the
baseline reference — reusable for any luxury retail portfolio that reports
against a similar SBTi-validated trajectory.

> ⚠️ **All figures are Tier 3 modeled estimates from public benchmarks.**
> Not assurance-ready. Not for external reporting. This is a *frame* for
> replacing estimates with store-level data.

## Stack (100% free)

- **GitHub** — repo and version control
- **Streamlit Community Cloud** — free hosting for public repos
- **Python + Streamlit + Plotly + Pandas** — all open source

No paid services. No proprietary data in this repo.

## Live dashboard

Deployed via Streamlit Community Cloud from this repo — see the Streamlit
"Deploy" steps below.

## Run locally

```bash
git clone https://github.com/<your-username>/luxury-store-dashboard.git
cd luxury-store-dashboard
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
