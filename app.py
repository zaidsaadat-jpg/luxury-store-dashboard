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
    page_title="Luxury Store CO₂ Reduction Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Palette ----------------
P = {
    "ink": "#1F1F1F",
    "gold": "#B08D57",
    "grey": "#8A8A8A",
    "green": "#2E4A3A",
    "oxblood": "#6B2C2C",
    "grid": "#E8E5E0",
    "paper": "#FAF8F4",
}
CHART_COLORS = [P["ink"], P["gold"], P["grey"], P["green"], P["oxblood"], "#A67C3D", "#4A4A4A"]

st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }
    h1, h2, h3, h4 { font-weight: 400; letter-spacing: 0.01em; color: #1F1F1F; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Helpers ----------------
def _selected_points(event):
    if event is None:
        return []
    try:
        sel = event["selection"] if "selection" in event else {}
        pts = sel.get("points", []) if hasattr(sel, "get") else sel["points"]
        return list(pts or [])
    except Exception:
        return []


def _clicked(event, fallback=None):
    pts = _selected_points(event)
    if not pts:
        return fallback
    p = pts[0]
    for key in ("label", "x"):
        if key in p and p[key] is not None:
            return p[key]
    return fallback


def _safe_plotly(fig, key):
    try:
        return st.plotly_chart(
            fig, key=key, use_container_width=True,
            on_select="rerun", selection_mode="points",
        )
    except TypeError:
        st.plotly_chart(fig, key=key, use_container_width=True)
        return None


# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### Baseline")
    st.caption("1.5°C-aligned retail pathway")
    st.markdown(
        f"- Base year: **{C.BASELINE_YEAR}**\n"
        f"- −50% by **2030**\n"
        f"- −70% by **{C.TARGET_YEAR}**\n"
        f"- −90% by **{C.LONG_TERM_YEAR}**"
    )
    st.divider()
    st.markdown("### Data status")
    st.caption(
        "All figures are Tier 3 modeled estimates from public benchmarks. "
        "Not assurance-ready. Not for external reporting."
    )


# ---------------- Static footprint ----------------
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
df["Scope 1+2 total"] = df["Scope 2 (tCO2e)"] + df["Scope 1 refrigerant (tCO2e)"]


# ---------------- Header ----------------
st.title("Luxury Store CO₂ Reduction Dashboard")
st.caption(
    "Multi-market retail portfolio · Hong Kong · Singapore · Korea · China · "
    "Baseline 2021 · Trajectory to 2035"
)
st.divider()


# ---------------- Tabs ----------------
tabs = st.tabs([
    "Overview",
    "LCA Index",
    "Capital Goods",
    "Seasonal & VM",
    "Scope 1+2",
    "Circularity & Waste",
    "Data Quality",
    "Method",
])


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tabs[0]:
    st.subheader("Absolute emissions trajectory, 2021–2035")
    st.caption(
        "Projected store-attributable emissions against the planned trajectory. "
        "Click a bar to inspect its drivers. Click a slice in the contribution pie "
        "to drill into the five-level breakdown."
    )

    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        country_filter = st.multiselect(
            "Markets in scope",
            options=C.MARKETS,
            default=C.MARKETS,
            key="countries",
        )
    if not country_filter:
        country_filter = C.MARKETS

    emissions = calc.scaled_annual_emissions(country_filter)
    plan = calc.plan_trajectory(country_filter)
    years = sorted(emissions.keys())
    years_str = [str(y) for y in years]

    base_v = emissions[C.BASELINE_YEAR]
    end_v = emissions[C.TARGET_YEAR]
    plan_v = plan[C.TARGET_YEAR]
    variance = end_v - plan_v
    pct = (1 - end_v / base_v) * 100 if base_v else 0.0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(f"{C.BASELINE_YEAR} baseline", f"{base_v:,.0f} tCO₂e")
    k2.metric(f"{C.TARGET_YEAR} projected", f"{end_v:,.0f} tCO₂e")
    k3.metric(f"{C.TARGET_YEAR} plan", f"{plan_v:,.0f} tCO₂e")
    k4.metric("Variance vs plan", f"{variance:+,.0f} tCO₂e")
    k5.metric("Reduction vs baseline", f"−{pct:.1f}%")

    fig = go.Figure()
    # ±5% plan tolerance band
    fig.add_trace(go.Scatter(
        x=years_str, y=[plan[y] * 1.05 for y in years],
        mode="lines", line=dict(width=0), hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=years_str, y=[plan[y] * 0.95 for y in years],
        mode="lines", line=dict(width=0), fill="tonexty",
        fillcolor="rgba(176,141,87,0.12)",
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Bar(
        x=years_str, y=[emissions[y] for y in years],
        name="Projected emissions",
        marker_color=P["ink"],
        hovertemplate="%{x}<br>%{y:,.0f} tCO₂e<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=years_str, y=[plan[y] for y in years],
        mode="lines+markers", name="Planned trajectory",
        line=dict(color=P["gold"], width=2.5, dash="dash"),
        marker=dict(size=6, color=P["gold"]),
        hovertemplate="Plan %{x}<br>%{y:,.0f} tCO₂e<extra></extra>",
    ))
    fig.update_layout(
        height=480,
        yaxis_title="tCO₂e / yr",
        xaxis_title="Year",
        bargap=0.35,
        legend=dict(orientation="h", y=1.10, x=0),
        margin=dict(t=40, b=40, l=10, r=10),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor=P["grid"]),
    )
    bar_event = _safe_plotly(fig, key="ov_bar")

    sel_year = _clicked(bar_event, fallback=None)
    try:
        sel_year = int(sel_year)
    except Exception:
        sel_year = C.TARGET_YEAR
    if sel_year not in emissions:
        sel_year = C.TARGET_YEAR

    st.caption(
        f"**Selected year:** {sel_year} · modeled {emissions[sel_year]:,.0f} tCO₂e · "
        f"plan {plan[sel_year]:,.0f} tCO₂e · "
        f"variance {emissions[sel_year] - plan[sel_year]:+,.0f} tCO₂e"
    )

    st.divider()

    left, right = st.columns([1, 1])

    with left:
        st.markdown(f"#### Reduction drivers in {sel_year}")
        year_drivers = calc.year_drivers(sel_year, country_filter)
        if year_drivers:
            d_df = pd.DataFrame(
                sorted(year_drivers.items(), key=lambda x: -x[1]),
                columns=["Driver", "tCO2e"],
            )
            fig_d = px.bar(d_df, x="tCO2e", y="Driver", orientation="h", text="tCO2e")
            fig_d.update_traces(
                texttemplate="%{text:,.0f}", textposition="outside",
                marker_color=P["gold"],
            )
            fig_d.update_layout(
                height=340, showlegend=False,
                yaxis=dict(categoryorder="total ascending", title=""),
                xaxis=dict(title="tCO₂e saved", gridcolor=P["grid"]),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig_d, use_container_width=True, key="ov_drivers_year")
        else:
            st.info(f"No reductions modeled for {sel_year}. Click another bar.")

    with right:
        st.markdown("#### Contribution by initiative, cumulative to 2035")
        cum = calc.cumulative_by_driver(country_filter)
        c_df = pd.DataFrame(
            sorted(cum.items(), key=lambda x: -x[1]),
            columns=["Driver", "tCO2e"],
        )
        fig_p = px.pie(
            c_df, names="Driver", values="tCO2e", hole=0.55,
            color_discrete_sequence=CHART_COLORS,
        )
        fig_p.update_traces(
            textinfo="percent",
            textfont=dict(color="white", size=12),
            marker=dict(line=dict(color="white", width=2)),
        )
        fig_p.update_layout(
            height=340, showlegend=True,
            legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=11)),
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        pie_event = _safe_plotly(fig_p, key="ov_pie")
        sel_driver = _clicked(pie_event, fallback=None)
        if sel_driver not in C.INITIATIVES:
            sel_driver = None

    st.divider()
    if sel_driver:
        st.markdown(f"#### Drill-down · {sel_driver} · {sel_year}")
        dd = DD.drill_down(sel_year, sel_driver, country_filter)

        st.caption(
            f"Activity type · {dd['activity_type']} · "
            f"total reduction in {sel_year}: {dd['total']:,.1f} tCO₂e"
        )

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**Country**")
            cdf = pd.DataFrame(
                sorted(
                    [(k, v["total"]) for k, v in dd["countries"].items()],
                    key=lambda x: -x[1],
                ),
                columns=["Country", "tCO2e"],
            )
            fig_c = px.bar(cdf, x="tCO2e", y="Country", orientation="h", text="tCO2e")
            fig_c.update_traces(
                texttemplate="%{text:,.1f}", textposition="outside",
                marker_color=P["ink"],
            )
            fig_c.update_layout(
                height=260, showlegend=False,
                yaxis=dict(categoryorder="total ascending", title=""),
                xaxis=dict(title="tCO₂e", gridcolor=P["grid"]),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig_c, use_container_width=True, key="dd_country")

        with c4:
            st.markdown("**Area of activity**")
            area_totals = {}
            for c, v in dd["countries"].items():
                for a, av in v["areas"].items():
                    area_totals[a] = area_totals.get(a, 0) + av["total"]
            adf = pd.DataFrame(
                sorted(area_totals.items(), key=lambda x: -x[1]),
                columns=["Area", "tCO2e"],
            )
            fig_a = px.bar(adf, x="tCO2e", y="Area", orientation="h", text="tCO2e")
            fig_a.update_traces(
                texttemplate="%{text:,.1f}", textposition="outside",
                marker_color=P["gold"],
            )
            fig_a.update_layout(
                height=260, showlegend=False,
                yaxis=dict(categoryorder="total ascending", title=""),
                xaxis=dict(title="tCO₂e", gridcolor=P["grid"]),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
            )
            st.plotly_chart(fig_a, use_container_width=True, key="dd_area")

        st.markdown("**Specific items**")
        rows = []
        for c, v in dd["countries"].items():
            for a, av in v["areas"].items():
                for item, iv in av["items"].items():
                    rows.append({
                        "Country": c,
                        "Area of activity": a,
                        "Specific item": item,
                        "tCO₂e": round(iv, 2),
                    })
        idf = pd.DataFrame(rows).sort_values(
            ["Country", "Area of activity", "tCO₂e"],
            ascending=[True, True, False],
        )
        st.dataframe(idf, use_container_width=True, hide_index=True)
    else:
        st.info(
            "Click a slice of the contribution pie to drill into the five-level breakdown "
            "(driver → activity type → country → area of activity → specific item)."
        )


# ============================================================
# TAB 2 — LCA INDEX
# ============================================================
with tabs[1]:
    st.subheader("End-to-end lifecycle view")
    st.caption(
        "The full operational footprint from raw material extraction through end of life. "
        "Stages sum to the 2021 baseline. The scale reflects markets selected on the Overview tab."
    )

    cov = calc.coverage_factor(st.session_state.get("countries", C.MARKETS) or C.MARKETS)

    lca_df = pd.DataFrame({
        "Stage": list(C.LCA_STAGES.keys()),
        "tCO2e": [v * cov for v in C.LCA_STAGES.values()],
    })
    lca_df["% of total"] = (lca_df["tCO2e"] / lca_df["tCO2e"].sum() * 100).round(1)

    cA, cB = st.columns([3, 2])
    with cA:
        fig = px.bar(lca_df, x="tCO2e", y="Stage", orientation="h", text="% of total")
        fig.update_traces(
            texttemplate="%{text}%", textposition="outside",
            marker_color=P["ink"],
        )
        fig.update_layout(
            height=520, showlegend=False,
            title=f"LCA stages — total {lca_df['tCO2e'].sum():,.0f} tCO₂e (baseline {C.BASELINE_YEAR})",
            xaxis_title="tCO₂e / yr",
            yaxis=dict(categoryorder="total ascending"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, key="lca_bar")

    with cB:
        fig2 = px.treemap(
            lca_df, path=["Stage"], values="tCO2e", color="tCO2e",
            color_continuous_scale=[[0, "#EFEAE0"], [1, P["ink"]]],
        )
        fig2.update_layout(
            height=520, title="Share of baseline footprint",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig2, use_container_width=True, key="lca_tree")

    st.dataframe(lca_df, use_container_width=True, hide_index=True)
    st.info(
        "The Overview tab shows how this total falls year by year toward 2035. "
        "Each stage then has its own tab: Operations → Scope 1+2; Store fit-out → Capital Goods; "
        "Seasonal/VM → Seasonal & VM; End of life → Circularity & Waste."
    )


# ============================================================
# Helper for opportunity-matrix tabs
# ============================================================
def render_opportunity_tab(opportunities, scope_area_key, title, intro):
    st.subheader(title)
    st.caption(intro)

    st.markdown("#### 1. Full scope of items assessed")
    scope_rows = []
    for area_name, data in C.DRIVER_STRUCTURE[scope_area_key]["areas"].items():
        for item, w in data["weights"].items():
            scope_rows.append({
                "Area of activity": area_name,
                "Specific item": item,
                "Relative share": f"{w * 100:.0f}%",
            })
    st.dataframe(pd.DataFrame(scope_rows), use_container_width=True, hide_index=True)

    st.markdown("#### 2. Initiatives matrix — effort vs impact (to 2035)")
    opp_df = pd.DataFrame(
        opportunities,
        columns=["Initiative", "Impact (tCO2e by 2035)", "Effort (1–5)", "Status"],
    )
    status_colors = {
        "Acted": P["green"],
        "In progress": P["gold"],
        "Opportunity": P["oxblood"],
    }

    c_a, c_b = st.columns([2, 1])
    with c_a:
        fig = px.scatter(
            opp_df, x="Effort (1–5)", y="Impact (tCO2e by 2035)",
            size="Impact (tCO2e by 2035)", color="Status",
            color_discrete_map=status_colors, hover_name="Initiative",
            title="Effort vs impact",
        )
        fig.update_layout(
            height=480,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor=P["grid"]), yaxis=dict(gridcolor=P["grid"]),
        )
        fig.update_xaxes(range=[0, 5.5], tickmode="array", tickvals=[1, 2, 3, 4, 5])
        st.plotly_chart(fig, use_container_width=True, key=f"opp_scatter_{scope_area_key}")
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

    st.markdown("#### 3. Initiative detail")
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
        "Capital goods — boutique fit-out",
        "Full scope of assessable items, then the initiatives matrix (effort vs impact) to 2035. "
        "Items highlighted as 'Acted' or 'In progress' are already in delivery; 'Opportunity' items are unclaimed.",
    )
    st.divider()
    st.subheader("Modeled fit-out footprint by market")
    fig = px.bar(
        df, x="Market", y="Fit-out annualized (tCO2e)", color="Market",
        color_discrete_sequence=CHART_COLORS, text_auto=".0f",
        title="Annualized fit-out embodied carbon",
    )
    fig.update_layout(
        showlegend=False, height=380,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor=P["grid"]),
    )
    st.plotly_chart(fig, use_container_width=True, key="cap_market_bar")


# ============================================================
# TAB 4 — SEASONAL & VM
# ============================================================
with tabs[3]:
    render_opportunity_tab(
        C.SEASONAL_OPPORTUNITIES,
        "VM & seasonal reuse",
        "Seasonal builds, visual merchandising and events",
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
        decreasing={"marker": {"color": P["gold"]}},
        increasing={"marker": {"color": P["ink"]}},
        totals={"marker": {"color": P["green"]}},
        connector={"line": {"color": P["grey"]}},
    ))
    bridge.update_layout(
        height=380, yaxis_title="tCO₂e / yr", showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis_gridcolor=P["grid"],
    )
    st.plotly_chart(bridge, use_container_width=True, key="vm_bridge")
    st.caption(
        "Avoided emissions sit outside the Scope 3 inventory boundary. "
        "They are a memo item, not a netting claim."
    )


# ============================================================
# TAB 5 — SCOPE 1+2
# ============================================================
with tabs[4]:
    render_opportunity_tab(
        C.ENERGY_OPPORTUNITIES,
        "Renewable electricity transition",
        "Scope 1+2 — Operational energy and refrigerants",
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
        fig = px.bar(
            df, x="Market", y="Scope 2 (tCO2e)", color="Market",
            color_discrete_sequence=CHART_COLORS, text_auto=".0f",
            title="Scope 2 (location-based)",
        )
        fig.update_layout(
            showlegend=False, height=380,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor=P["grid"]),
        )
        st.plotly_chart(fig, use_container_width=True, key="scope2_bar")
    with c_b:
        fig = px.bar(
            df, x="Market", y="Scope 1 refrigerant (tCO2e)", color="Market",
            color_discrete_sequence=CHART_COLORS, text_auto=".1f",
            title="Scope 1 refrigerant",
        )
        fig.update_layout(
            showlegend=False, height=380,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor=P["grid"]),
        )
        st.plotly_chart(fig, use_container_width=True, key="scope1_bar")

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
        "Circularity and end-of-life management",
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
    fig = px.bar(
        melted, x="Indicator", y="%", color="Market", barmode="group",
        color_discrete_sequence=CHART_COLORS,
        title="Circularity indicators (%)",
    )
    fig.update_layout(
        height=440, yaxis_range=[0, 100],
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor=P["grid"]),
    )
    st.plotly_chart(fig, use_container_width=True, key="circ_bars")
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
    st.subheader("Data-quality heat map")
    st.caption(
        "Every cell is Tier 3 (modeled) in this draft. Use this to sequence the first data-collection wave."
    )
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
# TAB 8 — METHOD
# ============================================================
with tabs[7]:
    st.subheader("About this draft")
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
circularity standards, WBCSD CTI thresholds). The dashboard is a frame for replacing
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
