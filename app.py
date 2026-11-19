"""
Luxury Store CO2 Reduction Dashboard — First Draft
Baseline 2021 · Trajectory through 2035 · Long-term target 2040
ALL FIGURES ARE TIER 3 MODELED ESTIMATES FROM PUBLIC BENCHMARKS.
Not assurance-ready. Not for external reporting.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import constants as C
from utils import calc
from utils import drilldown as DD

st.set_page_config(
    page_title="Luxury Store CO2 Dashboard (Draft)",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Sidebar ----------------
st.sidebar.title("Filters & Context")
st.sidebar.caption("Draft dashboard · Tier 3 modeled estimates only")
market_filter = st.sidebar.multiselect("Markets in scope", options=C.MARKETS, default=C.MARKETS)
st.sidebar.divider()
st.sidebar.markdown(
    f"**Baseline framework:** 1.5°C-aligned retail pathway\n\n"
    f"- Base year: {C.BASELINE_YEAR}\n"
    f"- −50% by 2030\n"
    f"- −70% by {C.TARGET_YEAR}\n"
    f"- −90% by {C.LONG_TERM_YEAR}"
)
st.sidebar.divider()
st.sidebar.caption(
    "⚠️ All data is modeled from public benchmarks. "
    "Replace with store-level Tier 1–2 data before any external use."
)

# ---------------- Static current-year data ----------------
area = calc.calc_floor_area()
elec = calc.calc_electricity_mwh()
scope2 = calc.calc_scope2_location()
scope1 = calc.calc_scope1_refrigerant()
fitout = calc.calc_fitout_annualized()
fitout_full = calc.calc_fitout_full_renovation()
seasonal = calc.calc_seasonal()
avoided = calc.calc_avoided_emissions()
waste = calc.calc_waste_category5()

df = pd.DataFrame({
    "Market": C.MARKETS,
    "Boutiques": [C.STORE_COUNTS[m] for m in C.MARKETS],
    "Floor area (m²)": [area[m] for m in C.MARKETS],
    "Electricity (MWh)": [elec[m] for m in C.MARKETS],
    "Scope 2 (tCO2e)": [scope2[m] for m in C.MARKETS],
    "Scope 1 refrigerant (tCO2e)": [scope1[m] for m in C.MARKETS],
    "Fit-out annualized (tCO2e)": [fitout[m] for m in C.MARKETS],
    "Seasonal/VM (tCO2e)": [seasonal[m] for m in C.MARKETS],
    "Category 5 waste (tCO2e)": [waste[m] for m in C.MARKETS],
    "Avoided emissions (tCO2e)": [avoided[m] for m in C.MARKETS],
})
df = df[df["Market"].isin(market_filter)].reset_index(drop=True)
df["Scope 1+2 total"] = df["Scope 2 (tCO2e)"] + df["Scope 1 refrigerant (tCO2e)"]

# ---------------- Header ----------------
st.title("🌿 Luxury Store CO₂ Reduction Dashboard — First Draft")
st.caption(
    "Multi-market retail portfolio · Markets: Hong Kong · Singapore · Korea · China "
    "· Baseline 2021 · Trajectory through 2035"
)

tabs = st.tabs([
    "🌍 LCA Index",
    "📉 Overview & Trajectory",
    "🏗️ Capital Goods",
    "🎨 Seasonal & VM",
    "⚡ Scope 1+2",
    "♻️ Circularity & Waste",
    "🔍 Data Quality",
    "ℹ️ About & Method",
])


# ============================================================
# TAB 1 — LCA INDEX
# ============================================================
with tabs[0]:
    st.subheader("🌍 End-to-end lifecycle view — the index")
    st.caption(
        "The entire operational footprint from raw material extraction through end of life. "
        "The sum of all stages equals the 2021 baseline. Every other tab drills into a stage."
    )

    lca_df = pd.DataFrame({
        "Stage": list(C.LCA_STAGES.keys()),
        "tCO2e": list(C.LCA_STAGES.values()),
    })
    lca_df["% of total"] = (lca_df["tCO2e"] / lca_df["tCO2e"].sum() * 100).round(1)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = px.bar(
            lca_df, x="tCO2e", y="Stage", orientation="h",
            text="% of total", color="Stage",
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(
            height=540, showlegend=False,
            title=f"LCA stages — total {C.BASELINE_TOTAL_TCO2E:,.0f} tCO₂e (baseline {C.BASELINE_YEAR})",
            xaxis_title="tCO₂e / yr",
            yaxis=dict(categoryorder="total ascending"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = px.treemap(
            lca_df, path=["Stage"], values="tCO2e", color="tCO2e",
            color_continuous_scale="Greens",
        )
        fig2.update_layout(height=540, title="Share of baseline footprint")
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(lca_df, use_container_width=True, hide_index=True)
    st.info(
        "**How to use this page.** The Overview tab shows how this total falls year by year toward 2035. "
        "Each stage then has its own tab: Operations → Scope 1+2; Store fit-out → Capital Goods; "
        "Seasonal/VM → Seasonal & VM; End of life → Circularity & Waste."
    )


# ============================================================
# TAB 2 — OVERVIEW & TRAJECTORY (WATERFALL + DRILL-DOWN)
# ============================================================
with tabs[1]:
    st.subheader("📉 Absolute emissions trajectory: 2021 baseline → 2035")
    st.caption(
        "Modeled yearly reductions, aggregated across the four markets. The starting bar is the 2021 "
        "baseline; each following bar is that year's reduction; the final bar is the 2035 total."
    )

    labels, values, measures = calc.waterfall_data()
    emissions = calc.annual_emissions()

    fig = go.Figure(go.Waterfall(
        name="Trajectory", orientation="v",
        measure=measures, x=labels, y=values,
        text=[f"{v:,.0f}" if m == "absolute" else f"−{abs(v):,.0f}" for v, m in zip(values, measures)],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#EF553B"}},
        increasing={"marker": {"color": "#636EFA"}},
        totals={"marker": {"color": "#00CC96"}},
    ))
    fig.update_layout(
        title=(
            f"Absolute emissions waterfall — "
            f"{C.BASELINE_TOTAL_TCO2E:,.0f} tCO₂e in {C.BASELINE_YEAR} → "
            f"{emissions[C.TARGET_YEAR]:,.0f} tCO₂e in {C.TARGET_YEAR}"
        ),
        yaxis_title="tCO₂e / yr",
        height=540, showlegend=False,
        margin=dict(t=60, b=60),
    )
    st.plotly_chart(fig, use_container_width=True)

    reduction_pct = (1 - emissions[C.TARGET_YEAR] / C.BASELINE_TOTAL_TCO2E) * 100
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{C.BASELINE_YEAR} baseline", f"{C.BASELINE_TOTAL_TCO2E:,.0f} tCO₂e")
    c2.metric(f"{C.TARGET_YEAR} projected", f"{emissions[C.TARGET_YEAR]:,.0f} tCO₂e")
    c3.metric("Total reduction", f"−{reduction_pct:.1f}%")
    c4.metric("Cumulative avoided", f"{C.BASELINE_TOTAL_TCO2E - emissions[C.TARGET_YEAR]:,.0f} tCO₂e")

    st.divider()
    st.subheader("🔎 Drill down into a year's reductions")
    st.caption(
        "Five levels of granularity: driver → activity type → country → area of activity → specific item. "
        "Choose a year, then narrow down through the selectors."
    )

    active_years = sorted([
        y for y in range(C.BASELINE_YEAR + 1, C.TARGET_YEAR + 1)
        if y in calc.annual_reductions()
    ])
    sel_year = st.selectbox("1️⃣ Year", active_years, index=len(active_years) - 1, key="dd_year")

    drivers_this_year = DD.drivers_for_year(sel_year)
    if not drivers_this_year:
        st.warning("No reductions modeled for this year.")
    else:
        driver_labels = [
            f"{d} — {v:,.0f} tCO₂e"
            for d, v in sorted(drivers_this_year.items(), key=lambda x: -x[1])
        ]
        sel_driver_label = st.selectbox("2️⃣ Level 1 — Driver (initiative)", driver_labels, key="dd_driver")
        sel_driver = sel_driver_label.split(" — ")[0]

        dd = DD.drill_down(sel_year, sel_driver)
        st.caption(f"**Level 2 — Activity type:** {dd['activity_type']}")

        countries_sorted = sorted(dd["countries"].items(), key=lambda x: -x[1]["total"])
        sel_country_label = st.selectbox(
            "3️⃣ Level 3 — Country",
            [f"{c} — {v['total']:,.1f} tCO₂e" for c, v in countries_sorted],
            key="dd_country",
        )
        sel_country = sel_country_label.split(" — ")[0]

        areas = dd["countries"][sel_country]["areas"]
        areas_sorted = sorted(areas.items(), key=lambda x: -x[1]["total"])
        sel_area_label = st.selectbox(
            "4️⃣ Level 4 — Area of activity",
            [f"{a} — {v['total']:,.1f} tCO₂e" for a, v in areas_sorted],
            key="dd_area",
        )
        sel_area = sel_area_label.split(" — ")[0]

        items = areas[sel_area]["items"]
        items_sorted = sorted(items.items(), key=lambda x: -x[1])
        sel_item_label = st.selectbox(
            "5️⃣ Level 5 — Specific item",
            [f"{i} — {v:,.2f} tCO₂e" for i, v in items_sorted],
            key="dd_item",
        )
        sel_item = sel_item_label.split(" — ")[0]

        st.success(
            f"**{sel_year} · {sel_driver} · {sel_country} · {sel_area} · {sel_item}** "
            f"— modeled reduction: **{items[sel_item]:,.2f} tCO₂e**"
        )

        st.divider()
        c_a, c_b = st.columns(2)
        with c_a:
            fig = px.bar(
                x=[c for c, _ in countries_sorted],
                y=[v["total"] for _, v in countries_sorted],
                labels={"x": "Country", "y": "tCO₂e reduction"},
                title=f"{sel_driver} — by country ({sel_year})",
                color=[c for c, _ in countries_sorted],
            )
            fig.update_layout(showlegend=False, height=360)
            st.plotly_chart(fig, use_container_width=True)
        with c_b:
            fig = px.bar(
                x=[a for a, _ in areas_sorted],
                y=[v["total"] for _, v in areas_sorted],
                labels={"x": "Area of activity", "y": "tCO₂e reduction"},
                title=f"{sel_driver} — by area ({sel_country}, {sel_year})",
                color=[a for a, _ in areas_sorted],
            )
            fig.update_layout(showlegend=False, height=360)
            st.plotly_chart(fig, use_container_width=True)


# ============================================================
# Generic helper for opportunity-matrix tabs
# ============================================================
def render_opportunity_tab(
    opportunities, scope_area_key, title, intro,
):
    st.subheader(title)
    st.caption(intro)

    st.markdown("### 1. Full scope of items assessed")
    scope_rows = []
    for area_name, data in C.DRIVER_STRUCTURE[scope_area_key]["areas"].items():
        for item, w in data["weights"].items():
            scope_rows.append({
                "Area of activity": area_name,
                "Specific item": item,
                "Relative share": f"{w*100:.0f}%",
            })
    st.dataframe(pd.DataFrame(scope_rows), use_container_width=True, hide_index=True)

    st.markdown("### 2. Initiatives matrix — effort vs impact (to 2035)")
    opp_df = pd.DataFrame(
        opportunities,
        columns=["Initiative", "Impact (tCO2e by 2035)", "Effort (1–5)", "Status"],
    )
    status_colors = {"Acted": "#00CC96", "In progress": "#FFA15A", "Opportunity": "#EF553B"}

    c_a, c_b = st.columns([2, 1])
    with c_a:
        fig = px.scatter(
            opp_df, x="Effort (1–5)", y="Impact (tCO2e by 2035)",
            size="Impact (tCO2e by 2035)", color="Status",
            color_discrete_map=status_colors, hover_name="Initiative",
            title="Effort vs impact",
        )
        fig.update_layout(height=480)
        fig.update_xaxes(range=[0, 5.5], tickmode="array", tickvals=[1, 2, 3, 4, 5])
        st.plotly_chart(fig, use_container_width=True)
    with c_b:
        st.markdown("**Reading the matrix**")
        st.markdown(
            "- **Top-left** (low effort, high impact) — do first\n"
            "- **Top-right** (high effort, high impact) — strategic bets\n"
            "- **Bottom-left** — quick wins\n"
            "- **Bottom-right** — deprioritize\n"
        )
        for status in ["Acted", "In progress", "Opportunity"]:
            sub = opp_df[opp_df["Status"] == status]
            st.metric(status, f"{sub['Impact (tCO2e by 2035)'].sum():,.0f} tCO₂e")

    st.markdown("### 3. Initiative detail")
    st.dataframe(
        opp_df.sort_values(["Status", "Impact (tCO2e by 2035)"], ascending=[True, False]),
        use_container_width=True, hide_index=True,
    )


# ============================================================
# TAB 3 — CAPITAL GOODS
# ============================================================
with tabs[2]:
    render_opportunity_tab(
        C.FITOUT_OPPORTUNITIES,
        "Circular fit-out redesign",
        "🏗️ Capital goods — boutique fit-out",
        "Full scope of assessable items, then the initiatives matrix (effort vs impact) to 2035. "
        "Items highlighted as 'Acted' or 'In progress' are already in delivery; 'Opportunity' items are unclaimed.",
    )

    st.divider()
    st.subheader("Modeled fit-out footprint by market")
    fig = px.bar(
        df, x="Market", y="Fit-out annualized (tCO2e)", color="Market",
        text_auto=".0f", title="Annualized fit-out embodied carbon",
    )
    fig.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 4 — SEASONAL & VM
# ============================================================
with tabs[3]:
    render_opportunity_tab(
        C.SEASONAL_OPPORTUNITIES,
        "VM & seasonal reuse",
        "🎨 Seasonal builds, visual merchandising and events",
        "Highest-velocity carbon source. Full item scope first, then the effort/impact matrix.",
    )

    st.divider()
    st.subheader("Gross → avoided → memo net position")
    gross = df["Seasonal/VM (tCO2e)"].sum()
    avoid = df["Avoided emissions (tCO2e)"].sum()
    bridge = go.Figure(go.Waterfall(
        x=["Gross seasonal/VM", "Avoided (reuse)", "Memo net"],
        y=[gross, -avoid, 0],
        measure=["absolute", "relative", "total"],
        text=[f"{gross:,.0f}", f"-{avoid:,.0f}", f"{gross - avoid:,.0f}"],
    ))
    bridge.update_layout(height=380, yaxis_title="tCO₂e / yr", showlegend=False)
    st.plotly_chart(bridge, use_container_width=True)
    st.caption(
        "Avoided emissions sit **outside** the Scope 3 inventory boundary. "
        "They are a memo item, not a netting claim."
    )


# ============================================================
# TAB 5 — SCOPE 1+2
# ============================================================
with tabs[4]:
    render_opportunity_tab(
        C.ENERGY_OPPORTUNITIES,
        "Renewable electricity transition",
        "⚡ Scope 1+2 — Operational energy and refrigerants",
        "Full item scope first (energy end-uses, refrigerants), then the effort/impact matrix.",
    )

    st.divider()
    st.subheader("Modeled Scope 1+2 by market")
    c1, c2, c3 = st.columns(3)
    c1.metric("Modeled electricity", f"{df['Electricity (MWh)'].sum():,.0f} MWh")
    c2.metric("Scope 2 (location-based)", f"{df['Scope 2 (tCO2e)'].sum():,.0f} tCO₂e")
    c3.metric("Scope 1 refrigerant", f"{df['Scope 1 refrigerant (tCO2e)'].sum():,.0f} tCO₂e")

    c_a, c_b = st.columns(2)
    with c_a:
        fig = px.bar(df, x="Market", y="Scope 2 (tCO2e)", color="Market",
                     text_auto=".0f", title="Scope 2 (location-based)")
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)
    with c_b:
        fig = px.bar(df, x="Market", y="Scope 1 refrigerant (tCO2e)", color="Market",
                     text_auto=".1f", title="Scope 1 refrigerant")
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.warning(
        "Market-based Scope 2 will be lower where renewable procurement covers these markets. "
        "This draft reports location-based only — replace with market-based when RE certificates "
        "are available by store."
    )


# ============================================================
# TAB 6 — CIRCULARITY & WASTE
# ============================================================
with tabs[5]:
    render_opportunity_tab(
        C.WASTE_OPPORTUNITIES,
        "Waste diversion",
        "♻️ Circularity and end-of-life management",
        "Full scope of waste streams, then circularity indicators, then the effort/impact matrix.",
    )

    st.divider()
    st.subheader("Circularity indicators by market (modeled)")
    circ = pd.DataFrame({
        "Market": C.MARKETS,
        "Design-for-disassembly": [C.DESIGN_FOR_DISASSEMBLY[m] * 100 for m in C.MARKETS],
        "Fixture reuse": [C.FIXTURE_REUSE[m] * 100 for m in C.MARKETS],
        "VM reuse": [C.VM_REUSE[m] * 100 for m in C.MARKETS],
        "Recycled content": [C.RECYCLED_CONTENT[m] * 100 for m in C.MARKETS],
        "Waste diversion": [C.DIVERSION_RATE * 100 for _ in C.MARKETS],
    })
    melted = circ.melt(id_vars="Market", var_name="Indicator", value_name="%")
    fig = px.bar(melted, x="Indicator", y="%", color="Market", barmode="group",
                 title="Circularity indicators (%)")
    fig.update_layout(height=440, yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(circ, use_container_width=True, hide_index=True)

    st.markdown("**Thresholds to track against**")
    st.markdown(
        "- Design-for-disassembly: **>60%** full credit (WBCSD CTI); 40–60% partial\n"
        "- Fixture reuse/recycling: **75%** of non-hazardous C&D waste\n"
        "- Material passport coverage: **>60%** of fixture mass\n"
        "- VM kit reuse: **≥3–4 uses** per kit"
    )


# ============================================================
# TAB 7 — DATA QUALITY
# ============================================================
with tabs[6]:
    st.subheader("🔍 Data-quality heat map")
    st.caption("Every cell is Tier 3 (modeled) in this draft. Use this to sequence the first data-collection wave.")
    quality = pd.DataFrame(
        {
            "Hong Kong": ["Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Not included"],
            "Singapore": ["Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Not included"],
            "Korea":     ["Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Not included"],
            "China":     ["Tier 3", "Tier 3", "Tier 3", "Tier 3 (partial)", "Tier 3", "Tier 3", "Not included"],
        },
        index=[
            "Store electricity", "Refrigerants", "Fit-out embodied carbon",
            "Seasonal builds / VM", "Waste", "Category 12 packaging EoL",
            "Landlord-supplied energy",
        ],
    )
    st.dataframe(quality, use_container_width=True)

    st.markdown("**Data tier definitions**")
    st.markdown(
        "- **Tier 1** — Physical, project-specific (BoQ + EPDs, utility invoices, refrigerant logs)\n"
        "- **Tier 2** — Spend-based with physical overlays (capex records, floor-area allocation)\n"
        "- **Tier 3** — Typology/benchmark modeled estimate (this draft)"
    )


# ============================================================
# TAB 8 — ABOUT & METHOD
# ============================================================
with tabs[7]:
    st.subheader("ℹ️ About this draft")
    st.markdown(f"""
**Baseline framework:** 1.5°C-aligned retail pathway, {C.BASELINE_YEAR} base year.

**Targets applied:**
- −50% by 2030
- −70% by {C.TARGET_YEAR}
- −90% by {C.LONG_TERM_YEAR}

**Boundary rules applied:**
- Scope 1+2: operational control
- Scope 3 Cat 2 (capital goods): capex ownership test (brand-funded fit-out enters inventory)
- Landlord-owned fixtures: influence-gap memo, not Category 2
- Avoided emissions: memo item, outside inventory boundary
- Category 5 (store waste) and Category 12 (sold-product EoL) kept separate

**Drill-down hierarchy (5 levels):**
1. Driver / initiative
2. Activity type (Scope 1+2, Capital goods, Seasonal/VM, Waste)
3. Country
4. Area of activity
5. Specific item

**Data status:** All figures are Tier 3 modeled estimates built from public benchmarks
(retail embodied carbon, apparel/fashion energy intensity, public 2025 grid factors,
circularity standards, WBCSD CTI thresholds). The dashboard is a *frame* for replacing
estimates with store-level data — not a performance claim.

**Next steps:**
1. Replace `utils/constants.py` with CSV loaders from `data/`
2. Move Hong Kong + Singapore to Tier 1–2 first (6-month sprint)
3. Add green-lease coverage tracker
4. Add internal-carbon-price overlay to the capital-pipeline view
5. Wire to a carbon accounting platform for Category 2 + purchased goods
""")

st.caption(
    "Built with Streamlit + Plotly. Free stack, public repo. "
    "All figures modeled — replace before external use."
)
