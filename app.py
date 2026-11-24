"""
Luxury Store CO2 Reduction Dashboard — First Draft
Baseline 2021 · Trajectory through 2035 · Long-term target 2040
ALL FIGURES ARE TIER 3 MODELED ESTIMATES FROM PUBLIC BENCHMARKS.
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
    "bronze": "#8A7044",
    "sage": "#3D5A4A",
    "green": "#2E4A3A",
    "grey": "#8A8A8A",
    "oxblood": "#6B2C2C",
    "grid": "#E8E5E0",
}
CHART_COLORS = [
    "#3D5A4A",  # sage green
    "#B08D57",  # champagne
    "#6B2C2C",  # oxblood
    "#8A7044",  # bronze
    "#A67C3D",  # amber
    "#7A8B6F",  # pale sage
    "#5A4A3A",  # taupe
    "#C7B59A",  # cream
    "#4A6B5A",  # muted green
    "#A5504F",  # muted red
]

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    h1, h2, h3, h4 { font-weight: 400; letter-spacing: 0.01em; color: #1F1F1F; }
    [data-testid="stMetricValue"] { font-size: 1.35rem !important; font-weight: 500 !important; }
    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important; color: #6B6B6B !important;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    [data-testid="stMetricDelta"] { font-size: 0.8rem !important; }
    .exec-summary { font-size: 0.86rem; line-height: 1.55; }
    .exec-summary b { color: #1F1F1F; }
    .exec-summary .variance-neg { color: #2E4A3A; font-weight: 600; }
    .exec-summary .variance-pos { color: #6B2C2C; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Helpers ----------------
def _get_selection(key):
    state = st.session_state.get(key)
    if state and isinstance(state, dict):
        sel = state.get("selection", {})
        if hasattr(sel, "get"):
            return sel.get("points", []) or []
    return []


def _clicked_value(event, key, field="x"):
    pts = _get_selection(key)
    if not pts and event is not None:
        try:
            sel = event.get("selection", {}) if isinstance(event, dict) else event.selection
            pts = sel.get("points", []) if hasattr(sel, "get") else []
        except Exception:
            pts = []
    if not pts:
        return None
    p = pts[0]
    return p.get(field) or p.get("label")


def _safe_plotly(fig, key):
    try:
        return st.plotly_chart(
            fig, key=key, use_container_width=True,
            on_select="rerun", selection_mode="points",
        )
    except TypeError:
        st.plotly_chart(fig, key=key, use_container_width=True)
        return None


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

# ---------------- Executive summary (for sidebar) ----------------
all_em = calc.scaled_annual_emissions(C.MARKETS)
all_plan = calc.plan_trajectory(C.MARKETS)
all_cum = calc.cumulative_by_driver(C.MARKETS)
top_3 = sorted(all_cum.items(), key=lambda x: -x[1])[:3]
base_v = all_em[C.BASELINE_YEAR]
end_v = all_em[C.TARGET_YEAR]
plan_v = all_plan[C.TARGET_YEAR]
var = end_v - plan_v
red_pct = (1 - end_v / base_v) * 100 if base_v else 0.0
var_class = "variance-neg" if var <= 0 else "variance-pos"

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### Executive summary")
    st.markdown(
        f'<div class="exec-summary">'
        f'<b>Baseline ({C.BASELINE_YEAR}):</b> {base_v:,.0f} tCO₂e<br>'
        f'<b>{C.TARGET_YEAR} projected:</b> {end_v:,.0f} tCO₂e<br>'
        f'<b>{C.TARGET_YEAR} plan:</b> {plan_v:,.0f} tCO₂e<br>'
        f'<b>Variance:</b> <span class="{var_class}">{var:+,.0f} tCO₂e</span><br>'
        f'<b>Cumulative reduction:</b> −{red_pct:.1f}%'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("**Top reduction levers to 2035**")
    for i, (drv, val) in enumerate(top_3, start=1):
        scope = C.DRIVER_SCOPES.get(drv, "")
        st.markdown(f"{i}. **{drv}** — {val:,.0f} tCO₂e  \n   <span style='color:#8A8A8A;font-size:0.78rem;'>{scope}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Baseline framework**")
    st.caption(
        f"1.5°C-aligned retail pathway  \n"
        f"Base year {C.BASELINE_YEAR}  \n"
        f"−50% by 2030 · −70% by {C.TARGET_YEAR} · −90% by {C.LONG_TERM_YEAR}"
    )
    st.markdown("---")
    st.markdown("**Data status**")
    st.caption(
        "All figures Tier 3 modeled estimates from public benchmarks. "
        "Not assurance-ready. Not for external reporting."
    )

# ---------------- Header ----------------
st.title("Luxury Store CO₂ Reduction Dashboard")
st.caption(
    "Multi-market retail portfolio · Hong Kong · Singapore · Korea · China · "
    "Baseline 2021 · Trajectory to 2035"
)
st.divider()

# ---------------- Tabs ----------------
tabs = st.tabs([
    "Overview", "LCA Index", "Capital Goods", "Seasonal & VM",
    "Scope 1+2", "Circularity & Waste", "Data Quality", "Method",
])

# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tabs[0]:
    st.subheader("Absolute emissions trajectory, 2021–2035")
    st.caption(
        "Projected store-attributable emissions against plan. "
        "Select a year to drill into monthly detail. Click a bar or slice to select it in place."
    )

    country_filter = st.multiselect(
        "Markets in scope", options=C.MARKETS, default=C.MARKETS, key="countries",
    ) or C.MARKETS

    emissions = calc.scaled_annual_emissions(country_filter)
    plan = calc.plan_trajectory(country_filter)
    years = sorted(emissions.keys())
    years_str = [str(y) for y in years]

    # KPI row
    base_v = emissions[C.BASELINE_YEAR]
    end_v = emissions[C.TARGET_YEAR]
    plan_v = plan[C.TARGET_YEAR]
    var = end_v - plan_v
    pct = (1 - end_v / base_v) * 100 if base_v else 0.0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(f"{C.BASELINE_YEAR} baseline", f"{base_v:,.0f} tCO₂e")
    k2.metric(f"{C.TARGET_YEAR} projected", f"{end_v:,.0f} tCO₂e")
    k3.metric(f"{C.TARGET_YEAR} plan", f"{plan_v:,.0f} tCO₂e")
    k4.metric("Variance vs plan", f"{var:+,.0f} tCO₂e")
    k5.metric("Reduction vs baseline", f"−{pct:.1f}%")

    # Year selector — guaranteed mechanism, syncs with chart click
    if "ov_year" not in st.session_state:
        st.session_state.ov_year = C.TARGET_YEAR
    sel_year = st.radio(
        "Year", years, key="ov_year",
        horizontal=True, label_visibility="collapsed",
    )

    # Main trajectory chart
    fig = go.Figure()
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
        marker_color=P["sage"],
        marker_line_color=P["green"], marker_line_width=0.5,
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
        height=420, yaxis_title="tCO₂e / yr", xaxis_title="Year",
        bargap=0.20,
        legend=dict(orientation="h", y=1.10, x=0),
        margin=dict(t=30, b=30, l=10, r=10),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor=P["grid"]),
    )
    bar_event = _safe_plotly(fig, key="ov_bar")

    clicked_year = _clicked_value(bar_event, "ov_bar", field="x")
    try:
        clicked_year_int = int(clicked_year) if clicked_year is not None else None
    except (ValueError, TypeError):
        clicked_year_int = None
    if clicked_year_int and clicked_year_int in emissions and clicked_year_int != sel_year:
        st.session_state.ov_year = clicked_year_int
        st.rerun()

    # Monthly drill-down
    st.divider()
    st.markdown(f"### Monthly drill-down · {sel_year}")
    if sel_year == C.BASELINE_YEAR:
        st.info(
            f"{sel_year} is the baseline year — no reductions to allocate across months. "
            "See the LCA Index tab for baseline composition."
        )
    else:
        monthly = calc.monthly_driver_breakdown(sel_year, country_filter)
        if not monthly:
            st.info(f"No reductions modeled for {sel_year}. Select another year.")
        else:
            monthly_rows = []
            for drv, vals in monthly.items():
                for i, v in enumerate(vals):
                    monthly_rows.append({
                        "Month": C.MONTH_LABELS[i],
                        "Driver": drv,
                        "Scope": C.DRIVER_SCOPES.get(drv, ""),
                        "tCO2e": v,
                        "Month_idx": i,
                    })
            m_df = pd.DataFrame(monthly_rows)
            order = {m: i for i, m in enumerate(C.MONTH_LABELS)}

            # Stacked bars by driver per month
            fig_m = px.bar(
                m_df,
                x="Month", y="tCO2e", color="Driver",
                color_discrete_sequence=CHART_COLORS,
                category_orders={"Month": C.MONTH_LABELS},
                title=f"{sel_year} — reduction by initiative, month by month",
            )
            # cumulative line
            cum_by_month = m_df.groupby("Month")["tCO2e"].sum().reindex(C.MONTH_LABELS).cumsum()
            fig_m.add_trace(go.Scatter(
                x=C.MONTH_LABELS, y=cum_by_month.values,
                mode="lines+markers", name="Cumulative",
                line=dict(color=P["ink"], width=2, dash="dot"),
                marker=dict(size=5, color=P["ink"]),
                yaxis="y2",
                hovertemplate="Cum %{x}<br>%{y:,.1f} tCO₂e<extra></extra>",
            ))
            fig_m.update_layout(
                height=440,
                yaxis=dict(title="tCO₂e / month", gridcolor=P["grid"]),
                yaxis2=dict(
                    title="Cumulative tCO₂e", overlaying="y", side="right",
                    showgrid=False,
                ),
                legend=dict(orientation="v", x=1.02, y=1, font=dict(size=10)),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=50, b=40, l=10, r=10),
            )
            st.plotly_chart(fig_m, use_container_width=True, key="ov_monthly")

            # Year-total driver summary with scopes
            year_drv = calc.year_drivers(sel_year, country_filter)
            ydf = pd.DataFrame(
                sorted(year_drv.items(), key=lambda x: -x[1]),
                columns=["Driver", "tCO2e"],
            )
            ydf["Scope"] = ydf["Driver"].map(C.DRIVER_SCOPES)
            st.markdown(f"**{sel_year} total: {ydf['tCO2e'].sum():,.1f} tCO₂e**")
            st.dataframe(ydf, use_container_width=True, hide_index=True)

    # Contribution pie chart
    st.divider()
    st.markdown("### Cumulative contribution by initiative, 2021–2035")
    cum = calc.cumulative_by_driver(country_filter)
    c_df = pd.DataFrame(
        sorted(cum.items(), key=lambda x: -x[1]),
        columns=["Driver", "tCO2e"],
    )
    c_df["Scope"] = c_df["Driver"].map(C.DRIVER_SCOPES)

    c_left, c_right = st.columns([2, 1])
    with c_left:
        fig_p = px.pie(
            c_df, names="Driver", values="tCO2e", hole=0.55,
            color_discrete_sequence=CHART_COLORS,
        )
        fig_p.update_traces(
            textinfo="percent", textfont=dict(color="white", size=11),
            marker=dict(line=dict(color="white", width=2)),
            hovertemplate="%{label}<br>%{value:,.0f} tCO₂e (%{percent})<extra></extra>",
        )
        fig_p.update_layout(
            height=380, showlegend=True,
            legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10)),
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        pie_event = _safe_plotly(fig_p, key="ov_pie")

    # Initiative selector — guaranteed mechanism
    initiative_options = ["— Select —"] + list(C.INITIATIVES.keys())
    if "ov_initiative" not in st.session_state:
        st.session_state.ov_initiative = "— Select —"

    with c_right:
        st.markdown("**Drill-down**")
        st.radio(
            "Initiative", initiative_options,
            key="ov_initiative", label_visibility="collapsed",
        )

    clicked_drv = _clicked_value(pie_event, "ov_pie", field="label")
    if clicked_drv in C.INITIATIVES and clicked_drv != st.session_state.ov_initiative:
        st.session_state.ov_initiative = clicked_drv
        st.rerun()

    selected_driver = st.session_state.ov_initiative
    if selected_driver in C.INITIATIVES:
        st.divider()
        scope = C.DRIVER_SCOPES.get(selected_driver, "")
        st.markdown(f"### Drill-down · {selected_driver}")
        st.caption(f"**Scope:** {scope} · Year {sel_year}")

        dd = DD.drill_down(sel_year, selected_driver, country_filter)
        st.caption(
            f"Activity type · {dd['activity_type']} · "
            f"total in {sel_year}: {dd['total']:,.1f} tCO₂e"
        )

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**Country**")
            cdf = pd.DataFrame(
                sorted([(k, v["total"]) for k, v in dd["countries"].items()], key=lambda x: -x[1]),
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
                        "Country": c, "Area of activity": a,
                        "Specific item": item, "tCO₂e": round(iv, 2),
                    })
        idf = pd.DataFrame(rows).sort_values(
            ["Country", "Area of activity", "tCO₂e"],
            ascending=[True, True, False],
        )
        st.dataframe(idf, use_container_width=True, hide_index=True)
    else:
        st.info(
            "Select a year above, then click an initiative slice (or use the radio) "
            "to drill into the five-level breakdown."
        )


# ============================================================
# TAB 2 — LCA INDEX
# ============================================================
with tabs[1]:
    st.subheader("End-to-end lifecycle view")
    st.caption(
        "Full operational footprint from raw material extraction through end of life. "
        "Stages sum to the 2021 baseline. Scale reflects markets selected on the Overview tab."
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
            marker_color=P["sage"],
        )
        fig.update_layout(
            height=520, showlegend=False,
            title=f"LCA stages — total {lca_df['tCO2e'].sum():,.0f} tCO₂e (baseline {C.BASELINE_YEAR})",
            xaxis_title="tCO₂e / yr",
            yaxis=dict(categoryorder="total ascending"),
            plot_bgcolor="rgba(0,0,
