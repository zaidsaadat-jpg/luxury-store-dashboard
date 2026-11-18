"""
Luxury Store CO2 Reduction Dashboard — First Draft
Baseline: Chanel Mission 1.5 / Net-Zero 2040 (2021 base year)
ALL FIGURES ARE TIER 3 MODELED ESTIMATES FROM PUBLIC BENCHMARKS.
Not assurance-ready. Not for external reporting.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import constants as C
from utils import calc

st.set_page_config(
    page_title="Luxury Store CO2 Dashboard (Draft)",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Sidebar ----------------
st.sidebar.title("Filters & Context")
st.sidebar.caption("Draft dashboard · Tier 3 modeled estimates only")
market_filter = st.sidebar.multiselect(
    "Markets in scope", options=C.MARKETS, default=C.MARKETS,
)
st.sidebar.divider()
st.sidebar.markdown(
    "**Baseline:** Chanel Mission 1.5 / Net-Zero 2040\n\n"
    f"- Base year: {C.BASE_YEAR}\n"
    "- Scope 1+2: −50% by 2030\n"
    "- Scope 3: −42% by 2030\n"
    "- All scopes: −90% by 2040"
)
st.sidebar.divider()
st.sidebar.caption(
    "⚠️ All data is modeled from public benchmarks. "
    "Replace with store-level Tier 1–2 data before any external use."
)

# ---------------- Compute ----------------
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
df["Store-attributable Scope 3 (gross)"] = (
    df["Fit-out annualized (tCO2e)"]
    + df["Seasonal/VM (tCO2e)"]
    + df["Category 5 waste (tCO2e)"]
)

# ---------------- Header ----------------
st.title("🌿 Luxury Store CO₂ Reduction Dashboard — First Draft")
st.caption(
    "Sustainability Director view · Markets: Hong Kong · Singapore · Korea · China "
    "· Baseline: Chanel Mission 1.5 (2021 base year)"
)

tab_overview, tab_scope12, tab_fitout, tab_seasonal, tab_circ, tab_quality, tab_about = st.tabs([
    "🏠 Overview", "⚡ Scope 1+2", "🏗️ Capital Goods",
    "🎨 Seasonal & VM", "♻️ Circularity", "🔍 Data Quality", "ℹ️ About & Method",
])

# ---------------- Overview ----------------
with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Scope 1+2 (modeled)", f"{df['Scope 1+2 total'].sum():,.0f} tCO₂e")
    c2.metric("Fit-out (annualized)", f"{df['Fit-out annualized (tCO2e)'].sum():,.0f} tCO₂e")
    c3.metric("Seasonal / VM", f"{df['Seasonal/VM (tCO2e)'].sum():,.0f} tCO₂e")
    c4.metric("Avoided (memo)", f"{df['Avoided emissions (tCO2e)'].sum():,.0f} tCO₂e")

    st.divider()
    col_a, col_b = st.columns([2, 1])

    with col_a:
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Scope 2", x=df["Market"], y=df["Scope 2 (tCO2e)"], marker_color="#636EFA"))
        fig.add_trace(go.Bar(name="Scope 1 refrigerant", x=df["Market"], y=df["Scope 1 refrigerant (tCO2e)"], marker_color="#EF553B"))
        fig.add_trace(go.Bar(name="Fit-out (annualized)", x=df["Market"], y=df["Fit-out annualized (tCO2e)"], marker_color="#00CC96"))
        fig.add_trace(go.Bar(name="Seasonal / VM", x=df["Market"], y=df["Seasonal/VM (tCO2e)"], marker_color="#AB63FA"))
        fig.add_trace(go.Bar(name="Category 5 waste", x=df["Market"], y=df["Category 5 waste (tCO2e)"], marker_color="#FFA15A"))
        fig.update_layout(
            barmode="stack",
            title="Modeled store-attributable emissions by market (tCO₂e/yr)",
            yaxis_title="tCO₂e / yr",
            legend=dict(orientation="h", y=-0.25),
            height=460,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("**Emissions mix**")
        mix = pd.DataFrame({
            "Category": ["Scope 1+2", "Fit-out", "Seasonal/VM", "Waste"],
            "tCO2e": [
                df["Scope 1+2 total"].sum(),
                df["Fit-out annualized (tCO2e)"].sum(),
                df["Seasonal/VM (tCO2e)"].sum(),
                df["Category 5 waste (tCO2e)"].sum(),
            ],
        })
        pie = px.pie(mix, names="Category", values="tCO2e", hole=0.5)
        pie.update_layout(height=460, showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(pie, use_container_width=True)

    st.divider()
    st.subheader("Market breakdown")
    st.dataframe(
        df[["Market", "Boutiques", "Floor area (m²)", "Scope 1+2 total",
            "Store-attributable Scope 3 (gross)", "Avoided emissions (tCO2e)"]],
        use_container_width=True, hide_index=True,
    )
    st.info(
        "**How to read this.** The modeled Scope 3 capital-goods line dominates the "
        "store-attributable footprint. Circularity is the main reduction lever — but the "
        "avoided-emissions memo is still small relative to gross fit-out emissions. "
        "This is a *data-prioritisation* dashboard, not a performance claim."
    )

# ---------------- Scope 1+2 ----------------
with tab_scope12:
    st.subheader("⚡ Scope 1+2 — Operational energy and refrigerants")
    st.caption(
        "Modeled from store count × floor area × energy intensity × grid factor. "
        "Refrigerants at 2.5 kg/store/yr × GWP 1,430."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Modeled electricity", f"{df['Electricity (MWh)'].sum():,.0f} MWh")
    c2.metric("Scope 2 (location-based)", f"{df['Scope 2 (tCO2e)'].sum():,.0f} tCO₂e")
    c3.metric("Scope 1 refrigerant", f"{df['Scope 1 refrigerant (tCO2e)'].sum():,.0f} tCO₂e")

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(df, x="Market", y="Scope 2 (tCO2e)", color="Market", text_auto=".0f",
                     title="Scope 2 (location-based) by market")
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig = px.bar(df, x="Market", y="Scope 1 refrigerant (tCO2e)", color="Market",
                     text_auto=".1f", title="Scope 1 refrigerant by market")
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Grid factors and intensity applied**")
    st.dataframe(pd.DataFrame({
        "Market": C.MARKETS,
        "Grid factor (kgCO₂e/kWh)": [C.GRID_FACTORS[m] for m in C.MARKETS],
        "Energy intensity (kWh/m²/yr)": [C.ENERGY_INTENSITY for _ in C.MARKETS],
    }), use_container_width=True, hide_index=True)

    st.warning(
        "**Market-based Scope 2 will be lower** where renewable procurement covers these markets "
        "(Singapore and Korea VPAs are public; HK and CN coverage is not). This draft reports "
        "location-based only — replace with market-based once RE certificates are available by store."
    )

# ---------------- Fit-out ----------------
with tab_fitout:
    st.subheader("🏗️ Scope 3 Category 2 — Boutique fit-out (capital goods)")
    st.caption(
        "Modeled at 850 kgCO₂e/m² (A1–A5) per renovation, annualized over a 5-year cycle. "
        "This is the largest store-attributable line and the primary lever for circular design."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Full renovation footprint", f"{sum(fitout_full.values()):,.0f} tCO₂e / cycle")
    c2.metric("Annualized", f"{df['Fit-out annualized (tCO2e)'].sum():,.0f} tCO₂e/yr")
    c3.metric("China share", f"{(fitout['China'] / sum(fitout.values()) * 100):.0f}%")

    fig = px.bar(df, x="Market", y="Fit-out annualized (tCO2e)", color="Market",
                 text_auto=".0f", title="Annualized fit-out embodied carbon by market")
    fig.update_layout(showlegend=False, height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(pd.DataFrame({
        "Market": C.MARKETS,
        "Floor area (m²)": [area[m] for m in C.MARKETS],
        "Full renovation (tCO₂e)": [round(fitout_full[m], 0) for m in C.MARKETS],
        "Annualized (tCO₂e/yr)": [round(fitout[m], 0) for m in C.MARKETS],
        "Share of modeled Scope 3": [f"{(fitout[m] / sum(fitout.values()) * 100):.0f}%" for m in C.MARKETS],
    }), use_container_width=True, hide_index=True)

    st.info(
        "**Circular-design levers.** Each year ~20% of the fleet is renovated. "
        "Raising design-for-disassembly and fixture reuse lowers annualized intensity "
        "even without reducing renovation frequency, because reused fixtures displace new production."
    )

# ---------------- Seasonal ----------------
with tab_seasonal:
    st.subheader("🎨 Seasonal builds, visual merchandising and events")
    st.caption(
        "Modeled at 40 kgCO₂e/m² selling area/yr (70% of GIA). "
        "Highest-uncertainty line — replace with VM procurement records first."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Gross seasonal/VM", f"{df['Seasonal/VM (tCO2e)'].sum():,.0f} tCO₂e/yr")
    c2.metric("Avoided (memo)", f"{df['Avoided emissions (tCO2e)'].sum():,.0f} tCO₂e/yr")
    c3.metric("China modeled reuse", f"{C.VM_REUSE['China']*100:.0f}%")

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.bar(df, x="Market", y="Seasonal/VM (tCO2e)", color="Market",
                     text_auto=".0f", title="Gross seasonal / VM by market")
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        reuse_df = pd.DataFrame({
            "Market": C.MARKETS,
            "VM reuse rate": [C.VM_REUSE[m] * 100 for m in C.MARKETS],
        })
        fig = px.bar(reuse_df, x="Market", y="VM reuse rate", color="Market",
                     text_auto=".0f", title="VM / seasonal kit reuse rate (%)")
        fig.update_layout(showlegend=False, height=400, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Bridge: gross → avoided → memo net position**")
    gross = df["Seasonal/VM (tCO2e)"].sum()
    avoid = df["Avoided emissions (tCO2e)"].sum()
    bridge = go.Figure(go.Waterfall(
        x=["Gross seasonal/VM", "Avoided (reuse)", "Memo net"],
        y=[gross, -avoid, 0],
        measure=["absolute", "relative", "total"],
        text=[f"{gross:,.0f}", f"-{avoid:,.0f}", f"{gross - avoid:,.0f}"],
    ))
    bridge.update_layout(height=400, yaxis_title="tCO₂e/yr", showlegend=False)
    st.plotly_chart(bridge, use_container_width=True)

    st.caption(
        "Avoided emissions sit **outside** the Scope 3 inventory boundary (GHG Protocol). "
        "They answer 'what would emissions have been under a linear model?' — not a netting claim."
    )

# ---------------- Circularity ----------------
with tab_circ:
    st.subheader("♻️ Circularity indicators (leading indicators)")
    st.caption(
        "These predict whether the capital-goods line will fall in the next renovation cycle. "
        "Treat as primary metrics, not secondary."
    )
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
                 title="Circularity indicators by market (modeled, %)")
    fig.update_layout(height=460, yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(circ, use_container_width=True, hide_index=True)

    st.warning(
        "**Portfolio read.** Modeled design-for-disassembly (~29%) and fixture reuse (~17%) "
        "are below what a 2040 net-zero trajectory implies. The largest near-term lever is "
        "**boutique fit-out redesign**, not VM reuse — VM reuse is already relatively strong "
        "(especially China, informed by SUBLIMAGE event reuse)."
    )

    st.markdown("**Thresholds to track against**")
    st.markdown(
        "- Design-for-disassembly: **>60%** full credit (WBCSD CTI); 40–60% partial\n"
        "- Fixture reuse/recycling: **75%** of non-hazardous C&D waste (Kering minimum)\n"
        "- Material passport coverage: **>60%** of fixture mass (WBCSD CTI)\n"
        "- VM kit reuse: **≥3–4 uses** per kit (Kering Qeelin benchmark)"
    )

# ---------------- Data Quality ----------------
with tab_quality:
    st.subheader("🔍 Data-quality heat map")
    st.caption(
        "Every cell is Tier 3 (modeled) in this draft. Use this to sequence the first data-collection wave."
    )
    quality = pd.DataFrame(
        {
            "Hong Kong": ["Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Not included"],
            "Singapore": ["Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Not included"],
            "Korea": ["Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Tier 3", "Not included"],
            "China": ["Tier 3", "Tier 3", "Tier 3", "Tier 3 (partial)", "Tier 3", "Tier 3", "Not included"],
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
    st.info(
        "**Sequencing.** Start with Hong Kong and Singapore (stronger landlord data-sharing norms, "
        "Lee Gardens benchmark, Singapore MEI audit backstop). Korea needs a concession-ownership "
        "mapping exercise first. China needs the longest runway due to scale and renewable-procurement complexity."
    )

# ---------------- About ----------------
with tab_about:
    st.subheader("ℹ️ About this draft")
    st.markdown(f"""
**Baseline framework:** Chanel Mission 1.5 / Net-Zero 2040 (SBTi-validated, {C.BASE_YEAR} base year).

**Targets applied:**
- Scope 1+2: **−50% by 2030** vs {C.BASE_YEAR}
- Scope 3: **−42% by 2030** vs {C.BASE_YEAR}
- All scopes: **−90% by 2040** vs {C.BASE_YEAR}
- 100% renewable electricity in own operations (2025 target)

**Boundary rules applied:**
- Scope 1+2: operational control
- Scope 3 Cat 2 (capital goods): capex ownership test (brand-funded fit-out enters inventory)
- Landlord-owned fixtures: influence-gap memo, not Category 2
- Avoided emissions: memo item, outside inventory boundary
- Category 5 (store waste) and Category 12 (sold-product EoL) kept separate

**Data status:** All figures are Tier 3 modeled estimates built from public benchmarks
(GLA retail embodied carbon, LVMH/Dior energy intensity, public grid factors,
Kering circularity standards, WBCSD CTI thresholds). None of these figures are
company-reported data. The dashboard is a *frame* for replacing estimates with store-level data —
not a performance claim.

**Next steps:**
1. Replace `utils/constants.py` with CSV loaders from `data/`
2. Move Hong Kong + Singapore to Tier 1–2 first (6-month sprint)
3. Add landlord data-sharing tracker (green lease coverage %)
4. Add internal-carbon-price overlay to the capital-pipeline view
5. Wire to a carbon accounting platform for Category 2 + purchased goods
""")

st.caption(
    "Built with Streamlit + Plotly. Free stack, public repo. "
    "All figures modeled — replace before external use."
)
