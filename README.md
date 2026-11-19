# Luxury Store CO₂ Reduction Dashboard — First Draft

A Streamlit dashboard tracking store-attributable CO₂ for luxury boutiques in
Hong Kong, Singapore, Korea, and China. Baseline 2021, trajectory through 2035,
aligned to a 1.5°C retail pathway with a long-term −90% by 2040 horizon.

> ⚠️ **All figures are Tier 3 modeled estimates from public benchmarks.**
> Not assurance-ready. Not for external reporting. This is a *frame* for
> replacing estimates with store-level data.

## Stack (100% free)

- **GitHub** — repo and version control
- **Streamlit Community Cloud** — free hosting for public repos
- **Python + Streamlit + Plotly + Pandas** — all open source

## Dashboard tabs

1. **LCA Index** — end-to-end lifecycle view; sums to 10,000 tCO₂e baseline
2. **Overview & Trajectory** — waterfall from 2021 baseline through 2035, with a 5-level drill-down (driver → activity type → country → area → item)
3. **Capital Goods** — boutique fit-out item scope + effort/impact matrix
4. **Seasonal & VM** — full VM/prop/mannequin scope + effort/impact matrix
5. **Scope 1+2** — energy and refrigerant scope + effort/impact matrix
6. **Circularity & Waste** — waste streams, circularity indicators, effort/impact matrix
7. **Data Quality** — Tier 1/2/3 heat map to sequence data collection
8. **About & Method** — baseline, boundary rules, next steps

## Update the modeled assumptions

All estimates live in `utils/constants.py`:
- `BASELINE_TOTAL_TCO2E` and `INITIATIVES` for the trajectory
- `DRIVER_STRUCTURE` for the 5-level drill-down
- `LCA_STAGES` for the LCA index
- `*_OPPORTUNITIES` for each tab's effort/impact matrix

Edit and commit — Streamlit Cloud rebuilds automatically.

## Repo structure
