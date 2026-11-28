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
    layout="wide", initial_sidebar_state="expanded",
)

P = {
    "ink": "#1F1F1F", "gold": "#B08D57", "bronze": "#8A7044",
    "sage": "#3D5A4A", "green": "#2E4A3A", "grey": "#8A8A8A",
    "oxblood": "#6B2C2C", "grid": "#E8E5E0",
}
CHART_COLORS = [
    "#3D5A4A", "#B08D57", "#6B2C2C", "#8A7044", "#A67C3D",
    "#7A8B6F", "#5A4A3A", "#C7B59A", "#4A6B5A", "#A5504F",
]

st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }
    h1, h2, h3, h4 { font-weight: 400; letter-spacing: 0.01em; color: #1F1F1F; }
    [data-testid="stMetricValue"] { font-size: 1.35rem !important; font-weight: 500 !important; }
    [data-testid="stMetricLabel"] {
        font-size: 0.72rem !important; color: #6B6B6B !important;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    [data-testid="stMetricDelta"] { font-size: 0.8rem !important; }
    .exec-summary, .exec-summary * {
        color: #1F1F1F !important; font-size: 0.86rem; line-height: 1.6;
    }
    .exec-summary b { font-weight: 600; }
    .exec-summary .variance-neg { color: #2E4A3A !important; font-weight: 700; }
    .exec-summary .variance-pos { color: #6B2C2C !important; font-weight: 700; }
    .exec-summary .cum-avoided { color: #1F5673 !important; font-weight: 700; }
    .vc-stage {
        border: 1px solid #E8E5E0; padding: 14px 14px;
        background: #FAF8F4; border-left: 4px solid #3D5A4A;
        height: 100%;
    }
    .vc-stage .title { font-size: 0.95rem; font-weight: 600; color: #1F1F1F; margin-bottom: 6px; }
    .vc-stage .desc { font-size: 0.78rem; color: #5A4A3A; margin-bottom: 8px; }
    .vc-stage .metric { font-size: 1.05rem; color: #1F1F1F; font-weight: 600; }
    .vc-stage .sub { font-size: 0.72rem; color: #6B6B6B; }
    .vc-stage .driver { font-size: 0.75rem; color: #6B6B6B; margin-top: 8px; font-style: italic; }
    </style>
    """,
    unsafe_allow_html=True,
)


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


def _clicked_pie_driver(event, key, c_df):
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
    cd = p.get("customdata")
    if isinstance(cd, (list, tuple)) and cd:
        cd = cd[0]
    if cd in C.INITIATIVES:
        return cd
    lbl = p.get("label")
    if lbl in C.INITIATIVES:
        return lbl
    for idx_key in ("point_number", "point_index"):
        idx = p.get(idx_key)
        if isinstance(idx, int) and 0 <= idx < len(c_df):
            try:
                lbl2 = c_df.iloc[idx]["Driver"]
                if lbl2 in C.INITIATIVES:
                    return lbl2
            except Exception:
                pass
    return None


def _safe_plotly(fig, key, selection=True):
    try:
        if selection:
            return st.plotly_chart(
                fig, key=key, use_container_width=True,
                on_select="rerun", selection_mode="points",
            )
        st.plotly_chart(fig, key=key, use_container_width=True)
        return None
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

# ---------------- Value-chain stage mapping ----------------
# Maps LCA stage → value-chain broad category → drivers relevant to that stage.
VALUE_CHAIN = [
    {
        "id": "design",
        "title": "Design & specification",
        "desc": "Store concept, fixture specification, material selection, and design-for-disassembly decisions made before procurement.",
        "lca_stages": ["Raw material extraction"],
        "drivers": ["Circular fit-out redesign", "Modular & adaptable design",
                    "Asset longevity & retention", "Packaging circularity"],
    },
    {
        "id": "production",
        "title": "Materials & production",
        "desc": "Upstream manufacturing of fixtures, furniture, mannequins, and packaging; the cradle-to-gate footprint of goods purchased.",
        "lca_stages": ["Manufacturing / production"],
        "drivers": ["Circular fit-out redesign", "Modular & adaptable design",
                    "Asset longevity & retention", "Packaging circularity",
                    "VM & seasonal reuse"],
    },
    {
        "id": "logistics",
        "title": "Logistics & installation",
        "desc": "Inbound freight, store installation, store-to-store transfers, and reverse logistics.",
        "lca_stages": ["Transport & distribution"],
        "drivers": ["Logistics optimization"],
    },
    {
        "id": "operations",
        "title": "Store operations",
        "desc": "Electricity use, refrigerant leakage, and seasonal VM refreshes while the store is trading.",
        "lca_stages": ["Operations (energy & refrigerants)", "Seasonal / VM refresh",
                       "Maintenance & repair"],
        "drivers": ["Renewable electricity transition", "Energy efficiency (LED/HVAC)",
                    "Refrigerant management", "VM & seasonal reuse"],
    },
    {
        "id": "eol",
        "title": "End of life",
        "desc": "Waste diversion, take-back schemes, recycling, and end-of-life treatment of sold products and packaging.",
        "lca_stages": ["Store fit-out & construction", "End of life (waste, take-back)"],
        "drivers": ["Waste diversion", "Packaging circularity", "Asset longevity & retention"],
    },
]

# ---------------- Exec summary data ----------------
all_em = calc.scaled_annual_emissions(C.MARKETS)
all_plan = calc.plan_trajectory(C.MARKETS)
all_cum = calc.cumulative_by_driver(C.MARKETS)
all_cum_avoided = calc.cumulative_avoided(C.MARKETS)
top_3 = sorted(all_cum.items(), key=lambda x: -x[1])[:3]
base_v = all_em[C.BASELINE_YEAR]
end_v = all_em[C.TARGET_YEAR]
plan_v = all_plan[C.TARGET_YEAR]
var = end_v - plan_v
red_pct = (1 - end_v / base_v) * 100 if base_v else 0.0
var_class = "variance-neg" if var <= 0 else "variance-pos"

# ---------------- Header ----------------
st.title("Luxury Store CO₂ Reduction Dashboard")
st.caption(
    "Multi-market retail portfolio · Hong Kong · Singapore · Korea · China · "
    "Baseline 2021 · Trajectory to 2035"
)
st.divider()

tabs = st.tabs([
    "Overview",
    "LCA Index",
    "Circular fit-out redesign",
    "VM & seasonal reuse",
    "Energy & refrigerants",
    "Waste & packaging",
    "Logistics optimization",
    "Data Quality",
    "Method",
])

# Determine active tab via query param (fallback for exec summary)
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Overview"

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### Executive summary")
    st.caption(f"Viewing: **{st.session_state.active_tab}**")

    if st.session_state.active_tab == "Overview":
        st.markdown(
            f'<div class="exec-summary">'
            f'<b>Baseline ({C.BASELINE_YEAR}):</b> {base_v:,.1f} tCO₂e<br>'
            f'<b>{C.TARGET_YEAR} projected:</b> {end_v:,.1f} tCO₂e<br>'
            f'<b>{C.TARGET_YEAR} plan:</b> {plan_v:,.1f} tCO₂e<br>'
            f'<b>Variance vs plan:</b> <span class="{var_class}">{var:+,.1f} tCO₂e</span><br>'
            f'<b>Reduction vs baseline:</b> −{red_pct:.1f}%<br>'
            f'<b>Cumulative CO₂ avoided:</b> '
            f'<span class="cum-avoided">{all_cum_avoided:,.1f} tCO₂e</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("**Top 3 levers to 2035**")
        for i, (drv, val) in enumerate(top_3, start=1):
            scope = C.DRIVER_SCOPES.get(drv, "")
            st.markdown(
                f"{i}. **{drv}** — {val:,.1f} tCO₂e  \n"
                f"&nbsp;&nbsp;<span style='color:#8A8A8A;font-size:0.78rem;'>{scope}</span>",
                unsafe_allow_html=True,
            )

    elif st.session_state.active_tab == "LCA Index":
        total_stage = sum(C.LCA_STAGES.values())
        biggest = max(C.LCA_STAGES.items(), key=lambda x: x[1])
        smallest = min(C.LCA_STAGES.items(), key=lambda x: x[1])
        st.markdown(
            f'<div class="exec-summary">'
            f'<b>Mapped baseline:</b> {total_stage:,.1f} tCO₂e<br>'
            f'<b>Value-chain stages:</b> {len(C.LCA_STAGES)} LCA · {len(VALUE_CHAIN)} broad<br>'
            f'<b>Largest stage:</b> {biggest[0]} ({biggest[1]:,.1f})<br>'
            f'<b>Smallest stage:</b> {smallest[0]} ({smallest[1]:,.1f})<br>'
            f'<b>{C.TARGET_YEAR} plan:</b> {plan_v:,.1f} tCO₂e '
            f'({plan_v / total_stage * 100:.1f}% of baseline)'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "This tab maps the full value chain and shows how each broad stage is expected "
            "to contract by 2035. Stage footprints reconcile to the Overview baseline."
        )

    elif st.session_state.active_tab in (
        "Circular fit-out redesign", "VM & seasonal reuse", "Energy & refrigerants",
        "Waste & packaging", "Logistics optimization",
    ):
        # Category-level exec summary
        cat_driver_map = {
            "Circular fit-out redesign": ["Circular fit-out redesign", "Modular & adaptable design", "Asset longevity & retention"],
            "VM & seasonal reuse": ["VM & seasonal reuse"],
            "Energy & refrigerants": ["Renewable electricity transition", "Energy efficiency (LED/HVAC)", "Refrigerant management"],
            "Waste & packaging": ["Waste diversion", "Packaging circularity"],
            "Logistics optimization": ["Logistics optimization"],
        }
        drivers_here = cat_driver_map[st.session_state.active_tab]
        cat_total_cum = sum(all_cum.get(d, 0.0) for d in drivers_here)
        cat_share = cat_total_cum / all_cum_avoided * 100 if all_cum_avoided else 0.0
        top_drv_here = max(
            ((d, all_cum.get(d, 0.0)) for d in drivers_here),
            key=lambda x: x[1],
        )
        st.markdown(
            f'<div class="exec-summary">'
            f'<b>Category cumulative to 2035:</b> {cat_total_cum:,.1f} tCO₂e<br>'
            f'<b>Share of total avoided:</b> {cat_share:.1f}%<br>'
            f'<b>Top driver in category:</b> {top_drv_here[0]} ({top_drv_here[1]:,.1f})<br>'
            f'<b>Drivers covered:</b> {len(drivers_here)}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Category totals reconcile to the Overview pie chart. "
            "Use the driver selector on the tab to see each driver's opportunity matrix."
        )

    else:
        st.caption("See the tab for detail on data quality and methodology.")

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

# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tabs[0]:
    st.session_state.active_tab = "Overview"
    st.subheader("Absolute emissions trajectory, 2021–2035")
    st.caption(
        "Switch between three views. Click a bar in the Trajectory view "
        "to jump to monthly detail for that year."
    )

    country_filter = st.multiselect(
        "Markets in scope", options=C.MARKETS, default=C.MARKETS, key="countries",
    ) or C.MARKETS

    emissions = calc.scaled_annual_emissions(country_filter)
    plan = calc.plan_trajectory(country_filter)
    years = sorted(emissions.keys())
    years_str = [str(y) for y in years]

    base_v = emissions[C.BASELINE_YEAR]
    end_v = emissions[C.TARGET_YEAR]
    plan_v = plan[C.TARGET_YEAR]
    var = end_v - plan_v
    pct = (1 - end_v / base_v) * 100 if base_v else 0.0
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(f"{C.BASELINE_YEAR} baseline", f"{base_v:,.1f} tCO₂e")
    k2.metric(f"{C.TARGET_YEAR} projected", f"{end_v:,.1f} tCO₂e")
    k3.metric(f"{C.TARGET_YEAR} plan", f"{plan_v:,.1f} tCO₂e")
    k4.metric("Variance vs plan", f"{var:+,.1f} tCO₂e")
    k5.metric("Reduction vs baseline", f"−{pct:.1f}%")

    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "trajectory"
    if "detail_year" not in st.session_state:
        st.session_state.detail_year = C.TARGET_YEAR
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = C.TARGET_YEAR

    mode_labels = ["Trajectory", "Cumulative by driver", "Monthly detail"]
    mode_keys = ["trajectory", "cumulative", "detail"]

    if st.session_state.get("_view_sync") != st.session_state.view_mode:
        st.session_state.pop("view_widget", None)
        st.session_state["_view_sync"] = st.session_state.view_mode

    current_idx = (
        mode_keys.index(st.session_state.view_mode)
        if st.session_state.view_mode in mode_keys else 0
    )

    st.radio(
        "Chart view", mode_labels,
        index=current_idx, horizontal=True,
        key="view_widget", label_visibility="collapsed",
        on_change=lambda: st.session_state.update(
            view_mode=mode_keys[mode_labels.index(st.session_state.view_widget)],
            _view_sync=mode_keys[mode_labels.index(st.session_state.view_widget)],
        ),
    )

    if st.session_state.view_mode == "trajectory":
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years_str, y=[plan[y] * 1.05 for y in years],
            mode="lines", line=dict(width=0), hoverinfo="skip", showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=years_str, y=[plan[y] * 0.95 for y in years],
            mode="lines", line=dict(width=0), fill="tonexty",
            fillcolor="rgba(176,141,87,0.12)", hoverinfo="skip", showlegend=False,
        ))
        fig.add_trace(go.Bar(
            x=years_str, y=[emissions[y] for y in years],
            name="Projected annual emissions",
            marker_color=P["sage"],
            marker_line_color=P["green"], marker_line_width=0.5,
            hovertemplate="%{x}<br>%{y:,.1f} tCO₂e<br><i>Click to see monthly detail</i><extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=years_str, y=[plan[y] for y in years],
            mode="lines+markers", name="Planned trajectory",
            line=dict(color=P["gold"], width=2.5, dash="dash"),
            marker=dict(size=6, color=P["gold"]),
            hovertemplate="Plan %{x}<br>%{y:,.1f} tCO₂e<extra></extra>",
        ))
        fig.update_layout(
            height=460, yaxis_title="tCO₂e / yr", xaxis_title="Year",
            bargap=0.20,
            legend=dict(orientation="h", y=1.10, x=0),
            margin=dict(t=30, b=30, l=10, r=10),
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor=P["grid"], tickformat=".1f"),
        )
        bar_event = _safe_plotly(fig, key="ov_bar")
        clicked_year = _clicked_value(bar_event, "ov_bar", field="x")
        try:
            clicked_year_int = int(clicked_year) if clicked_year is not None else None
        except (ValueError, TypeError):
            clicked_year_int = None
        if clicked_year_int and clicked_year_int in emissions:
            st.session_state.detail_year = clicked_year_int
            st.session_state.selected_year = clicked_year_int
            st.session_state.view_mode = "detail"
            st.rerun()

    elif st.session_state.view_mode == "cumulative":
        st.markdown("### Cumulative CO₂ avoided by driver, 2021–2035")
        st.caption(
            "Each band shows how much a driver has accumulated toward the cumulative total. "
            "**Phasing:** energy-efficiency retrofit dominates early years (2022–2025); "
            "circular fit-out and renewable electricity build through the middle (2025–2029); "
            "logistics and modular design take over late (2030–2035)."
        )

        cum_by_driver_year = {}
        for drv, yearly in C.INITIATIVES.items():
            cf = calc.country_factor(drv, country_filter)
            cum = {}
            running = 0.0
            for y in range(C.BASELINE_YEAR, C.TARGET_YEAR + 1):
                running += yearly.get(y, 0) * cf
                cum[y] = running
            cum_by_driver_year[drv] = cum

        total_per_driver = {d: cum_by_driver_year[d][C.TARGET_YEAR] for d in cum_by_driver_year}
        sorted_drivers_asc = sorted(total_per_driver, key=total_per_driver.get)

        long_rows = []
        for drv in sorted_drivers_asc:
            for y in years:
                long_rows.append({
                    "Year": y, "Driver": drv,
                    "Cumulative": cum_by_driver_year[drv][y],
                })
        long_df = pd.DataFrame(long_rows)

        fig_cum = px.area(
            long_df, x="Year", y="Cumulative", color="Driver",
            color_discrete_map=C.DRIVER_COLORS,
            category_orders={"Driver": sorted_drivers_asc},
        )
        fig_cum.update_traces(
            line=dict(width=0.5),
            hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:,.1f} tCO₂e cumulative<extra></extra>",
        )
        fig_cum.update_layout(
            height=540,
            xaxis=dict(title="Year", tickmode="linear", dtick=1, gridcolor=P["grid"]),
            yaxis=dict(
                title="Cumulative CO₂ avoided (tCO₂e)",
                gridcolor=P["grid"], tickformat=".1f",
            ),
            showlegend=True,
            legend=dict(orientation="h", y=-0.20, x=0, font=dict(size=10)),
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=130, l=10, r=10),
        )
        _safe_plotly(fig_cum, key="ov_cum", selection=False)

        total_at_2035 = sum(total_per_driver.values())
        st.caption(
            f"Cumulative total 2021–{C.TARGET_YEAR}: **{total_at_2035:,.1f} tCO₂e**. "
            f"Matches the 'Cumulative CO₂ avoided' metric in the sidebar."
        )

    else:
        if st.session_state.get("_last_year_sync") != st.session_state.detail_year:
            st.session_state.pop("year_widget", None)
            st.session_state["_last_year_sync"] = st.session_state.detail_year

        st.radio(
            "Year", years,
            index=years.index(st.session_state.detail_year)
            if st.session_state.detail_year in years else 0,
            key="year_widget",
            on_change=lambda: st.session_state.update(
                detail_year=st.session_state.year_widget,
                selected_year=st.session_state.year_widget,
                _last_year_sync=st.session_state.year_widget,
            ),
            horizontal=True, label_visibility="collapsed",
        )

        detail_year = st.session_state.detail_year
        st.markdown(f"#### {detail_year} — monthly reduction by initiative")

        if detail_year == C.BASELINE_YEAR:
            st.info(f"{detail_year} is the baseline year — no reductions across months.")
        else:
            monthly = calc.monthly_driver_breakdown(detail_year, country_filter)
            if not monthly:
                st.info(f"No reductions modeled for {detail_year}. Select another year.")
            else:
                rows = []
                for drv, vals in monthly.items():
                    for m_idx, v in enumerate(vals):
                        rows.append({"Month": C.MONTH_LABELS[m_idx], "Driver": drv, "tCO2e": v})
                m_df = pd.DataFrame(rows)

                fig_m = px.bar(
                    m_df, x="Month", y="tCO2e", color="Driver",
                    color_discrete_map=C.DRIVER_COLORS,
                    category_orders={"Month": C.MONTH_LABELS},
                )
                cum_by_month = (
                    m_df.groupby("Month")["tCO2e"].sum()
                    .reindex(C.MONTH_LABELS).cumsum()
                )
                fig_m.add_trace(go.Scatter(
                    x=C.MONTH_LABELS, y=cum_by_month.values,
                    mode="lines+markers", name="Cumulative",
                    line=dict(color=P["ink"], width=2, dash="dot"),
                    marker=dict(size=5, color=P["ink"]),
                    yaxis="y2",
                    hovertemplate="Cumulative %{x}<br>%{y:,.1f} tCO₂e<extra></extra>",
                ))
                fig_m.update_layout(
                    height=480, showlegend=True,
                    legend=dict(orientation="h", y=-0.15, x=0, font=dict(size=10)),
                    xaxis=dict(title=""),
                    yaxis=dict(title="tCO₂e / month", gridcolor=P["grid"], tickformat=".1f"),
                    yaxis2=dict(
                        title="Cumulative tCO₂e",
                        overlaying="y", side="right", showgrid=False, tickformat=".1f",
                    ),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=100, l=10, r=10), bargap=0.20,
                )
                _safe_plotly(fig_m, key="ov_monthly", selection=False)
                st.caption(
                    "Legend below the chart · Dotted line (right axis) = cumulative reduction across the year."
                )

                year_drv = calc.year_drivers(detail_year, country_filter)
                ydf = pd.DataFrame(
                    sorted(year_drv.items(), key=lambda x: -x[1]),
                    columns=["Driver", "tCO2e"],
                )
                ydf["Scope"] = ydf["Driver"].map(C.DRIVER_SCOPES)
                ydf["tCO2e"] = ydf["tCO2e"].round(1)
                st.markdown(f"**{detail_year} total: {ydf['tCO2e'].sum():,.1f} tCO₂e**")
                st.dataframe(ydf, use_container_width=True, hide_index=True)

    # ---------- Pie chart ----------
    st.divider()
    st.markdown("### Cumulative contribution by initiative, 2021–2035")
    st.caption(
        "Click a slice (or use the selector below) to drill into strategy attribution, "
        "country, area, and specific-item breakdown."
    )
    cum = calc.cumulative_by_driver(country_filter)
    c_df = pd.DataFrame(
        sorted(cum.items(), key=lambda x: -x[1]),
        columns=["Driver", "tCO2e"],
    ).reset_index(drop=True)

    if "selected_initiative" not in st.session_state:
        st.session_state.selected_initiative = "— Select —"

    if st.session_state.get("_last_pie_sync") != st.session_state.selected_initiative:
        st.session_state.pop("pie_select", None)
        st.session_state["_last_pie_sync"] = st.session_state.selected_initiative

    fig_p = go.Figure(data=[go.Pie(
        labels=c_df["Driver"].tolist(),
        values=c_df["tCO2e"].tolist(),
        hole=0.45,
        marker=dict(
            colors=[C.DRIVER_COLORS[d] for d in c_df["Driver"]],
            line=dict(color="white", width=2),
        ),
        customdata=c_df["Driver"].tolist(),
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(size=11, color=P["ink"]),
        hovertemplate="<b>%{label}</b><br>%{value:,.1f} tCO₂e (%{percent})<extra></extra>",
        sort=False,
        direction="clockwise",
    )])
    fig_p.update_layout(
        height=640, showlegend=False,
        margin=dict(t=40, b=40, l=220, r=220),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    pie_event = _safe_plotly(fig_p, key="ov_pie")

    pie_selector_options = ["— Select —"] + c_df["Driver"].tolist()
    default_idx = (
        pie_selector_options.index(st.session_state.selected_initiative)
        if st.session_state.selected_initiative in pie_selector_options else 0
    )
    st.selectbox(
        "Or select a driver to drill down",
        pie_selector_options,
        index=default_idx,
        key="pie_select",
        on_change=lambda: st.session_state.update(
            selected_initiative=st.session_state.pie_select,
            _last_pie_sync=st.session_state.pie_select,
        ),
    )

    clicked_drv = _clicked_pie_driver(pie_event, "ov_pie", c_df)
    if clicked_drv in C.INITIATIVES and clicked_drv != st.session_state.selected_initiative:
        st.session_state.selected_initiative = clicked_drv
        st.rerun()

    selected_driver = st.session_state.selected_initiative

    if selected_driver in C.INITIATIVES:
        st.divider()
        scope = C.DRIVER_SCOPES.get(selected_driver, "")
        definition = C.DRIVER_DEFINITIONS.get(selected_driver, "")
        scope_def = C.SCOPE_DEFINITIONS.get(scope, "")

        title_col, btn_col = st.columns([6, 1])
        with title_col:
            st.markdown(f"### Drill-down · {selected_driver}")
        with btn_col:
            if st.button("Clear", key="clear_drill"):
                st.session_state.selected_initiative = "— Select —"
                st.session_state["_last_pie_sync"] = "— Select —"
                st.rerun()

        st.markdown(
            f"**Definition:** {definition}  \n"
            f"**Scope:** {scope} — {scope_def}"
        )

        drill_horizon = st.radio(
            "Drill-down horizon",
            ["Cumulative 2021–2035", "Single year"],
            horizontal=True, key="drill_horizon",
        )

        if drill_horizon == "Single year":
            default_yr = st.session_state.get("selected_year", C.TARGET_YEAR)
            default_idx_y = years.index(default_yr) if default_yr in years else 0
            drill_year = st.selectbox("Year", years, index=default_idx_y, key="drill_year")
            dd = DD.drill_down(drill_year, selected_driver, country_filter)
            horizon_label = f"Year {drill_year}"
        else:
            dd = DD.cumulative_drill_down(selected_driver, country_filter)
            horizon_label = f"Cumulative 2021–{C.TARGET_YEAR}"

        st.caption(
            f"**{horizon_label}** · Activity type: {dd['activity_type']} · "
            f"Total: **{dd['total']:,.1f} tCO₂e**"
        )

        if drill_horizon == "Cumulative 2021–2035":
            pie_slice_value = cum.get(selected_driver, 0)
            st.caption(
                f"↳ Matches pie chart slice value ({pie_slice_value:,.1f} tCO₂e)."
            )

        if dd['total'] == 0:
            st.warning(
                f"No reductions modeled for **{selected_driver}** in {horizon_label}."
            )
        else:
            ap_weights = C.ACTION_PLANS.get(selected_driver, {})
            if ap_weights:
                st.markdown(f"#### Strategy attribution · {horizon_label}")
                ap_df = pd.DataFrame([
                    {"Strategy": s, "tCO2e": dd["total"] * w, "Share %": w * 100.0}
                    for s, w in ap_weights.items()
                ]).sort_values("tCO2e", ascending=True).reset_index(drop=True)

                fig_ap = px.bar(ap_df, x="tCO2e", y="Strategy", orientation="h")
                fig_ap.update_traces(
                    text=ap_df["tCO2e"].round(1),
                    texttemplate="%{text:,.1f}",
                    textposition="outside",
                    marker_color=C.DRIVER_COLORS.get(selected_driver, P["oxblood"]),
                    hovertemplate="<b>%{y}</b><br>%{x:,.1f} tCO₂e<br>%{customdata:.1f}% of driver<extra></extra>",
                    customdata=ap_df["Share %"].round(1).tolist(),
                )
                fig_ap.update_layout(
                    height=max(240, 60 + 45 * len(ap_df)),
                    showlegend=False,
                    xaxis=dict(title="tCO₂e attributed", gridcolor=P["grid"], tickformat=".1f"),
                    yaxis=dict(categoryorder="total ascending", title=""),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, b=10, l=10, r=10),
                )
                st.plotly_chart(fig_ap, use_container_width=True, key="dd_action_plan")

            st.markdown(f"#### Geographic and area splits · {horizon_label}")
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
                fig_c = px.bar(cdf, x="tCO2e", y="Country", orientation="h", text_auto=".1f")
                fig_c.update_traces(textposition="outside", marker_color=P["ink"])
                fig_c.update_layout(
                    height=280, showlegend=False,
                    yaxis=dict(categoryorder="total ascending", title=""),
                    xaxis=dict(title="tCO₂e", gridcolor=P["grid"], tickformat=".1f"),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, b=10, l=10, r=10),
                )
                st.plotly_chart(fig_c, use_container_width=True, key="dd_country")
                st.caption(f"Sum: {cdf['tCO2e'].sum():,.1f} tCO₂e")

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
                fig_a = px.bar(adf, x="tCO2e", y="Area", orientation="h", text_auto=".1f")
                fig_a.update_traces(textposition="outside", marker_color=P["gold"])
                fig_a.update_layout(
                    height=280, showlegend=False,
                    yaxis=dict(categoryorder="total ascending", title=""),
                    xaxis=dict(title="tCO₂e", gridcolor=P["grid"], tickformat=".1f"),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, b=10, l=10, r=10),
                )
                st.plotly_chart(fig_a, use_container_width=True, key="dd_area")
                st.caption(f"Sum: {adf['tCO2e'].sum():,.1f} tCO₂e")

            st.markdown("#### Specific items")
            rows = []
            for c, v in dd["countries"].items():
                for a, av in v["areas"].items():
                    for item, iv in av["items"].items():
                        rows.append({
                            "Country": c, "Area of activity": a,
                            "Specific item": item, "tCO₂e": round(iv, 1),
                        })
            idf = pd.DataFrame(rows)
            if not idf.empty:
                f1, f2 = st.columns(2)
                with f1:
                    cf = st.selectbox(
                        "Filter by country",
                        ["All"] + sorted(idf["Country"].unique().tolist()),
                        key="item_cf",
                    )
                with f2:
                    af = st.selectbox(
                        "Filter by area of activity",
                        ["All"] + sorted(idf["Area of activity"].unique().tolist()),
                        key="item_af",
                    )
                filtered = idf.copy()
                if cf != "All":
                    filtered = filtered[filtered["Country"] == cf]
                if af != "All":
                    filtered = filtered[filtered["Area of activity"] == af]
                filtered = filtered.sort_values("tCO₂e", ascending=False).reset_index(drop=True)
                st.dataframe(filtered, use_container_width=True, hide_index=True)
                st.caption(
                    f"Showing {len(filtered)} of {len(idf)} items · click column headers to re-sort"
                )
    else:
        st.info(
            "Click a slice of the pie (or use the selector above) to drill into "
            "strategy attribution, country, area, and item-level breakdown."
        )


# ============================================================
# TAB 2 — LCA INDEX (value-chain mapped)
# ============================================================
with tabs[1]:
    st.session_state.active_tab = "LCA Index"
    st.subheader("End-to-end lifecycle and value chain")
    st.caption(
        "The full operational value chain, mapped from design through end of life. "
        "Each stage shows baseline footprint and planned reduction by 2035, reconciled "
        "to the Overview baseline and plan."
    )

    lca_country_filter = st.multiselect(
        "Markets in scope (LCA view)",
        options=C.MARKETS, default=C.MARKETS,
        key="lca_countries",
    ) or C.MARKETS
    cov = calc.coverage_factor(lca_country_filter)

    # Compute stage baselines at current coverage
    stage_base = {k: v * cov for k, v in C.LCA_STAGES.items()}
    total_base = sum(stage_base.values())

    # Compute the 2035 plan at coverage to determine total contraction
    plan_local = calc.plan_trajectory(lca_country_filter)
    plan_2035 = plan_local[C.TARGET_YEAR]
    contraction_ratio = plan_2035 / total_base if total_base else 0.0

    # Allocate plan contraction to stages proportional to stage baseline
    stage_plan_2035 = {k: v * contraction_ratio for k, v in stage_base.items()}

    # ---------------- Value-chain ribbon ----------------
    st.markdown("### Value-chain stages")
    ribbon_cols = st.columns(len(VALUE_CHAIN))
    for i, stage in enumerate(VALUE_CHAIN):
        stage_em = sum(stage_base.get(s, 0.0) for s in stage["lca_stages"])
        stage_plan = sum(stage_plan_2035.get(s, 0.0) for s in stage["lca_stages"])
        reduction_pct_stage = (
            (1 - stage_plan / stage_em) * 100 if stage_em else 0.0
        )
        stage_drivers = ", ".join(stage["drivers"][:2]) + (
            " + others" if len(stage["drivers"]) > 2 else ""
        )
        with ribbon_cols[i]:
            st.markdown(
                f'<div class="vc-stage">'
                f'<div class="title">{stage["title"]}</div>'
                f'<div class="desc">{stage["desc"]}</div>'
                f'<div class="metric">{stage_em:,.1f} tCO₂e</div>'
                f'<div class="sub">baseline · planned 2035: {stage_plan:,.1f} '
                f'(−{reduction_pct_stage:.1f}%)</div>'
                f'<div class="driver">Drivers: {stage_drivers}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.caption(
        f"Stage baselines sum to **{total_base:,.1f} tCO₂e**, matching the "
        f"{C.TARGET_YEAR} baseline on the Overview tab. Planned 2035 stage totals "
        f"sum to **{sum(stage_plan_2035.values()):,.1f} tCO₂e**, matching the plan "
        f"anchor on the Overview tab."
    )

    # ---------------- Baseline vs plan by stage ----------------
    st.markdown("### Baseline → 2035 plan by LCA stage")
    vc_rows = []
    for stage in VALUE_CHAIN:
        for lca in stage["lca_stages"]:
            vc_rows.append({
                "Value chain": stage["title"],
                "LCA stage": lca,
                "Baseline (tCO₂e)": stage_base[lca],
                "2035 plan (tCO₂e)": stage_plan_2035[lca],
                "Reduction (tCO₂e)": stage_base[lca] - stage_plan_2035[lca],
            })
    vc_df = pd.DataFrame(vc_rows)

    fig_vc = go.Figure()
    fig_vc.add_trace(go.Bar(
        name="Baseline", x=vc_df["LCA stage"], y=vc_df["Baseline (tCO₂e)"],
        marker_color=P["sage"],
        hovertemplate="<b>%{x}</b><br>Baseline: %{y:,.1f} tCO₂e<extra></extra>",
    ))
    fig_vc.add_trace(go.Bar(
        name="2035 plan", x=vc_df["LCA stage"], y=vc_df["2035 plan (tCO₂e)"],
        marker_color=P["gold"],
        hovertemplate="<b>%{x}</b><br>2035: %{y:,.1f} tCO₂e<extra></extra>",
    ))
    fig_vc.update_layout(
        height=460, barmode="group",
        xaxis=dict(title="", tickangle=-20),
        yaxis=dict(title="tCO₂e / yr", gridcolor=P["grid"], tickformat=".1f"),
        legend=dict(orientation="h", y=1.10, x=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=120, l=10, r=10),
    )
    st.plotly_chart(fig_vc, use_container_width=True, key="lca_stage_bars")

    # ---------------- Methodology ----------------
    st.markdown("### Methodology — how each LCA stage is calculated")
    methodology = {
        "Raw material extraction": (
            "Cradle-to-gate extraction emissions for materials entering the store: "
            "timber, metal, stone, glass, acrylic, textiles. Sourced from supplier EPDs "
            "where available (Tier 1), spend-based estimates from procurement otherwise (Tier 2), "
            "and industry-average material intensities as fallback (Tier 3). "
            "This stage anchors the design-side lever: material choice and design-for-disassembly "
            "determine the extraction footprint of every renovation cycle."
        ),
        "Manufacturing / production": (
            "Cradle-to-gate manufacturing emissions for fixtures, furniture, mannequins, and "
            "packaging. BoQ mass × material-specific emission factors, annualized over the "
            "renovation cycle. Attributed across drivers: circular fit-out (material substitution, "
            "recycled content), modular design (fewer bespoke components), asset longevity "
            "(refurbishment instead of replacement), packaging (mass reduction), and VM reuse "
            "(fewer new assets)."
        ),
        "Transport & distribution": (
            "Upstream freight of fixtures, materials, and products to stores plus store-to-store "
            "transfers and reverse logistics. Calculated as tonne-km × mode-specific emission factors "
            "(sea, road, air). Driver: logistics optimization — modal shift, consolidation, "
            "and reverse-logistics network redesign."
        ),
        "Store fit-out & construction": (
            "Site-stage emissions from installation and renovation activities: "
            "construction waste, on-site energy, packaging disposal. Scope 3 Cat 5 waste "
            "at installation. Attributed to waste diversion (segregation at source), "
            "asset longevity (installation with retention in mind)."
        ),
        "Operations (energy & refrigerants)": (
            "Scope 1+2 emissions while the store is trading: purchased electricity × grid "
            "factor (location-based for this draft), plus refrigerant top-up × GWP. "
            "Drivers: renewable electricity transition (PPAs, RECs), energy efficiency "
            "(LED, HVAC), and refrigerant management (leak reduction, low-GWP). "
            "Location-based only in this draft; market-based will replace when RE certificates are tracked."
        ),
        "Seasonal / VM refresh": (
            "Emissions from seasonal builds, props, mannequins, display kits, and graphics. "
            "Calculated as kgCO₂e per m² of selling area per year, split across window displays, "
            "mannequins, in-store installations, and signage. Attributed to VM & seasonal reuse."
        ),
        "Maintenance & repair": (
            "Emissions from refurbishment and repair of fixtures and VM assets — "
            "reupholstery, refinishing, spare parts. Attributed to asset longevity & retention. "
            "Lower footprint than replacement, but not zero; captured here rather than as avoided."
        ),
        "End of life (waste, take-back)": (
            "Waste generated in operations (Scope 3 Cat 5) plus end-of-life treatment of sold "
            "products and packaging (Category 12). Mass × treatment-specific emission factors "
            "(landfill, incineration, recycling, reuse). Attributed to waste diversion and "
            "packaging circularity."
        ),
    }
    methodology_df = pd.DataFrame([
        {"LCA stage": k, "Calculation basis": v}
        for k, v in methodology.items()
    ])
    st.dataframe(methodology_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("LCA stages — detailed footprint")
    lca_df = pd.DataFrame({
        "Stage": list(stage_base.keys()),
        "Baseline (tCO₂e)": [round(v, 1) for v in stage_base.values()],
        "2035 plan (tCO₂e)": [round(stage_plan_2035[k], 1) for k in stage_base.keys()],
    })
    lca_df["Reduction %"] = (
        (1 - lca_df["2035 plan (tCO₂e)"] / lca_df["Baseline (tCO₂e)"]) * 100
    ).round(1)
    st.dataframe(lca_df, use_container_width=True, hide_index=True)

    colA, colB = st.columns(2)
    with colA:
        fig_t = px.treemap(
            lca_df, path=["Stage"], values="Baseline (tCO₂e)",
            color="Baseline (tCO₂e)",
            color_continuous_scale=[[0, "#EFEAE0"], [1, P["sage"]]],
        )
        fig_t.update_layout(
            height=420, title="Baseline footprint share",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_t, use_container_width=True, key="lca_tree")
    with colB:
        fig_r = px.bar(
            lca_df, x="Stage", y="Reduction %",
            color="Reduction %",
            color_continuous_scale=[[0, "#EFEAE0"], [1, P["sage"]]],
        )
        fig_r.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
        fig_r.update_layout(
            height=420, title="Reduction % by stage (baseline → 2035 plan)",
            xaxis=dict(title="", tickangle=-20),
            yaxis=dict(title="%", gridcolor=P["grid"], tickformat=".1f"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False, margin=dict(b=120),
        )
        st.plotly_chart(fig_r, use_container_width=True, key="lca_reduction")


# ============================================================
# Opportunity + Gantt helper
# ============================================================
def _initiative_gantt(opportunities, key_suffix):
    """Renders a Gantt-style view of initiatives over 2021-2035."""
    # Assign realistic start years based on status
    opp_rows = []
    for name, impact, effort, status in opportunities:
        if status == "Acted":
            start, end = 2022, 2030
        elif status == "In progress":
            start, end = 2024, 2032
        else:
            start, end = 2026, 2035
        years_active = end - start + 1
        annual = impact / years_active if years_active else 0.0
        opp_rows.append({
            "Initiative": name,
            "Status": status,
            "Effort": effort,
            "Start": start,
            "End": end,
            "Duration (yrs)": years_active,
            "Total impact (tCO₂e)": impact,
            "Annual impact (tCO₂e/yr)": annual,
        })
    gdf = pd.DataFrame(opp_rows).sort_values(
        ["Status", "Total impact (tCO₂e)"], ascending=[True, False]
    ).reset_index(drop=True)

    status_colors = {"Acted": P["green"], "In progress": P["gold"], "Opportunity": P["oxblood"]}

    fig = go.Figure()
    for _, row in gdf.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Duration (yrs)"]],
            y=[row["Initiative"]],
            base=[row["Start"] - 2021],
            orientation="h",
            marker=dict(
                color=status_colors[row["Status"]],
                line=dict(color="white", width=1),
            ),
            text=f"{int(row['Start'])}–{int(row['End'])} · {row['Annual impact (tCO₂e/yr)']:.1f}/yr",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=10),
            hovertemplate=(
                f"<b>{row['Initiative']}</b><br>"
                f"Status: {row['Status']}<br>"
                f"Effort: {row['Effort']}/5<br>"
                f"Active: {int(row['Start'])}–{int(row['End'])} "
                f"({int(row['Duration (yrs)'])} yrs)<br>"
                f"Total impact: {row['Total impact (tCO₂e)']:,.1f} tCO₂e<br>"
                f"Annual impact: {row['Annual impact (tCO₂e/yr)']:,.1f} tCO₂e/yr"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        height=max(340, 60 + 42 * len(gdf)),
        barmode="stack",
        xaxis=dict(
            title="Year",
            range=[0, 15],
            tickmode="array",
            tickvals=[i for i in range(0, 15, 1)],
            ticktext=[str(2021 + i) for i in range(0, 15, 1)],
            gridcolor=P["grid"],
        ),
        yaxis=dict(title="", categoryorder="array",
                   categoryarray=list(reversed(gdf["Initiative"].tolist()))),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=40, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"gantt_{key_suffix}")

    # Status legend as chips
    chips = " ".join(
        f'<span style="background:{status_colors[s]};color:white;'
        f'padding:3px 10px;border-radius:2px;font-size:0.78rem;margin-right:6px;">'
        f'{s}</span>'
        for s in ["Acted", "In progress", "Opportunity"]
    )
    st.markdown(chips, unsafe_allow_html=True)
    st.caption(
        "Bars show each initiative's active window; label reads start–end · annualised "
        "reduction impact. Timing is modeled from status: **Acted** — deployed from 2022 and "
        "maintained; **In progress** — from 2024; **Opportunity** — from 2026. "
        "Impact values are cumulative reduction to 2035."
    )
    st.dataframe(
        gdf[["Initiative", "Status", "Effort", "Start", "End", "Duration (yrs)",
             "Total impact (tCO₂e)", "Annual impact (tCO₂e/yr)"]].round(1),
        use_container_width=True, hide_index=True,
    )
    return gdf


def render_opportunity_tab(opportunities, scope_area_key, title, intro, country_filter, key_suffix):
    st.subheader(title)
    st.caption(intro)

    # ---------- Table 1 — Full scope of items, sortable + filterable ----------
    st.markdown("#### Full scope of items assessed")
    scope_rows = []
    driver_total_emissions = 0.0
    if scope_area_key in C.DRIVER_STRUCTURE:
        # Estimate this driver's total cumulative emissions from the drill-down
        dd_cum = DD.cumulative_drill_down(scope_area_key, country_filter)
        driver_total_emissions = dd_cum["total"]
        for area_name, data in C.DRIVER_STRUCTURE[scope_area_key]["areas"].items():
            for item, w in data["weights"].items():
                scope_rows.append({
                    "Area of activity": area_name,
                    "Specific item": item,
                    "tCO₂e": round(driver_total_emissions * w, 1),
                    "Share %": round(w * 100.0, 1),
                })
    scope_df = pd.DataFrame(scope_rows)

    if not scope_df.empty:
        filter_col, sort_col = st.columns([2, 2])
        with filter_col:
            area_filter = st.selectbox(
                "Filter by area of activity",
                ["All"] + sorted(scope_df["Area of activity"].unique().tolist()),
                key=f"area_filter_{key_suffix}",
            )
        with sort_col:
            sort_by = st.selectbox(
                "Sort by",
                ["tCO₂e (desc)", "tCO₂e (asc)", "Share % (desc)",
                 "Area of activity (A→Z)", "Specific item (A→Z)"],
                key=f"sort_{key_suffix}",
            )

        filtered = scope_df.copy()
        if area_filter != "All":
            filtered = filtered[filtered["Area of activity"] == area_filter]

        sort_map = {
            "tCO₂e (desc)": ("tCO₂e", False),
            "tCO₂e (asc)": ("tCO₂e", True),
            "Share % (desc)": ("Share %", False),
            "Area of activity (A→Z)": ("Area of activity", True),
            "Specific item (A→Z)": ("Specific item", True),
        }
        sort_col_name, asc = sort_map[sort_by]
        filtered = filtered.sort_values(sort_col_name, ascending=asc).reset_index(drop=True)

        st.dataframe(filtered, use_container_width=True, hide_index=True)

        # Subtotal row
        subtotal_em = filtered["tCO₂e"].sum()
        subtotal_share = filtered["Share %"].sum()
        st.markdown(
            f"**Subtotal — {area_filter if area_filter != 'All' else 'all areas'}:** "
            f"{subtotal_em:,.1f} tCO₂e · {subtotal_share:.1f}% of driver total "
            f"({driver_total_emissions:,.1f} tCO₂e)"
        )

        # By-area subtotal table
        area_sub = scope_df.groupby("Area of activity").agg(
            tCO₂e=("tCO₂e", "sum"), **{"Share %": ("Share %", "sum")}
        ).reset_index().sort_values("tCO₂e", ascending=False)
        st.markdown("**Subtotals by area of activity**")
        st.dataframe(area_sub.round(1), use_container_width=True, hide_index=True)

    # ---------- Table 2 — Gantt of initiatives ----------
    st.markdown("#### Initiative phasing — Gantt view")
    _initiative_gantt(opportunities, key_suffix)

    # ---------- Table 3 — Effort vs impact scatter ----------
    st.markdown("#### Initiatives matrix — effort vs impact")
    opp_df = pd.DataFrame(
        opportunities,
        columns=["Initiative", "Impact (tCO₂e by 2035)", "Effort (1–5)", "Status"],
    )
    opp_df["Impact (tCO₂e by 2035)"] = opp_df["Impact (tCO₂e by 2035)"].astype(float)

    status_colors = {"Acted": P["green"], "In progress": P["gold"], "Opportunity": P["oxblood"]}
    c_a, c_b = st.columns([2, 1])
    with c_a:
        fig = px.scatter(
            opp_df, x="Effort (1–5)", y="Impact (tCO₂e by 2035)",
            size="Impact (tCO₂e by 2035)", color="Status",
            color_discrete_map=status_colors, hover_name="Initiative",
            title="Effort vs impact",
        )
        fig.update_layout(
            height=480, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor=P["grid"]),
            yaxis=dict(gridcolor=P["grid"], tickformat=".1f"),
        )
        fig.update_xaxes(range=[0, 5.5], tickmode="array", tickvals=[1, 2, 3, 4, 5])
        st.plotly_chart(fig, use_container_width=True, key=f"opp_scatter_{key_suffix}")
    with c_b:
        st.markdown("**Reading the matrix**")
        st.markdown(
            "- **Top-left** — do first\n"
            "- **Top-right** — strategic bets\n"
            "- **Bottom-left** — quick wins\n"
            "- **Bottom-right** — deprioritize"
        )
        for status in ["Acted", "In progress", "Opportunity"]:
            sub = opp_df[opp_df["Status"] == status]
            st.metric(status, f"{sub['Impact (tCO₂e by 2035)'].sum():,.1f} tCO₂e")


# ============================================================
# TAB 3 — CIRCULAR FIT-OUT REDESIGN
# ============================================================
with tabs[2]:
    st.session_state.active_tab = "Circular fit-out redesign"
    country_filter = st.multiselect(
        "Markets in scope", options=C.MARKETS, default=C.MARKETS,
        key="fitout_countries",
    ) or C.MARKETS
    driver_pick = st.selectbox(
        "Driver in this category",
        ["Circular fit-out redesign", "Modular & adaptable design", "Asset longevity & retention"],
        key="fitout_driver_pick",
    )
    opp_map = {
        "Circular fit-out redesign": C.FITOUT_OPPORTUNITIES,
        "Modular & adaptable design": C.MODULAR_OPPORTUNITIES,
        "Asset longevity & retention": C.LONGEVITY_OPPORTUNITIES,
    }
    render_opportunity_tab(
        opp_map[driver_pick], driver_pick,
        f"Capital goods — {driver_pick}",
        "Full scope of assessable items, then initiative phasing, then the effort/impact matrix.",
        country_filter, f"cap_{driver_pick[:6]}",
    )
    st.divider()
    st.subheader("Modeled fit-out footprint by market")
    fig = px.bar(
        df[df["Market"].isin(country_filter)],
        x="Market", y="Fit-out annualized (tCO2e)", color="Market",
        color_discrete_sequence=CHART_COLORS, text_auto=".1f",
        title="Annualized fit-out embodied carbon",
    )
    fig.update_layout(
        showlegend=False, height=380,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor=P["grid"], tickformat=".1f"),
    )
    st.plotly_chart(fig, use_container_width=True, key="cap_market_bar")


# ============================================================
# TAB 4 — VM & SEASONAL REUSE
# ============================================================
with tabs[3]:
    st.session_state.active_tab = "VM & seasonal reuse"
    country_filter = st.multiselect(
        "Markets in scope", options=C.MARKETS, default=C.MARKETS,
        key="vm_countries",
    ) or C.MARKETS
    render_opportunity_tab(
        C.SEASONAL_OPPORTUNITIES, "VM & seasonal reuse",
        "VM & seasonal reuse",
        "Highest-velocity carbon source. Full item scope, phasing, then effort/impact matrix.",
        country_filter, "vm",
    )
    st.divider()
    st.subheader("Gross → avoided → memo net position")
    sub = df[df["Market"].isin(country_filter)]
    gross = sub["Seasonal/VM (tCO2e)"].sum()
    avoid = sub["Avoided emissions (tCO2e)"].sum()
    bridge = go.Figure(go.Waterfall(
        x=["Gross seasonal/VM", "Avoided (reuse)", "Memo net"],
        y=[gross, -avoid, 0],
        measure=["absolute", "relative", "total"],
        text=[f"{gross:,.1f}", f"-{avoid:,.1f}", f"{gross - avoid:,.1f}"],
        decreasing={"marker": {"color": P["gold"]}},
        increasing={"marker": {"color": P["sage"]}},
        totals={"marker": {"color": P["green"]}},
        connector={"line": {"color": P["grey"]}},
    ))
    bridge.update_layout(
        height=380, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="tCO₂e / yr", gridcolor=P["grid"], tickformat=".1f"),
    )
    st.plotly_chart(bridge, use_container_width=True, key="vm_bridge")


# ============================================================
# TAB 5 — ENERGY & REFRIGERANTS
# ============================================================
with tabs[4]:
    st.session_state.active_tab = "Energy & refrigerants"
    country_filter = st.multiselect(
        "Markets in scope", options=C.MARKETS, default=C.MARKETS,
        key="energy_countries",
    ) or C.MARKETS
    driver_pick = st.selectbox(
        "Driver in this category",
        ["Renewable electricity transition", "Energy efficiency (LED/HVAC)", "Refrigerant management"],
        key="energy_driver_pick",
    )
    opp_map = {
        "Renewable electricity transition": C.RENEWABLE_OPPORTUNITIES,
        "Energy efficiency (LED/HVAC)": C.ENERGY_EFFICIENCY_OPPORTUNITIES,
        "Refrigerant management": C.REFRIGERANT_OPPORTUNITIES,
    }
    render_opportunity_tab(
        opp_map[driver_pick], driver_pick,
        f"Scope 1+2 — {driver_pick}",
        "Full item scope, phasing, then effort/impact matrix.",
        country_filter, f"energy_{driver_pick[:6]}",
    )
    st.divider()
    st.subheader("Modeled Scope 1+2 by market")
    sub = df[df["Market"].isin(country_filter)]
    c1, c2, c3 = st.columns(3)
    c1.metric("Electricity", f"{sub['Electricity (MWh)'].sum():,.1f} MWh")
    c2.metric("Scope 2 (location-based)", f"{sub['Scope 2 (tCO2e)'].sum():,.1f} tCO₂e")
    c3.metric("Scope 1 refrigerant", f"{sub['Scope 1 refrigerant (tCO2e)'].sum():,.1f} tCO₂e")
    c_a, c_b = st.columns(2)
    with c_a:
        fig = px.bar(
            sub, x="Market", y="Scope 2 (tCO2e)", color="Market",
            color_discrete_sequence=CHART_COLORS, text_auto=".1f",
            title="Scope 2 (location-based)",
        )
        fig.update_layout(
            showlegend=False, height=380,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor=P["grid"], tickformat=".1f"),
        )
        st.plotly_chart(fig, use_container_width=True, key="scope2_bar")
    with c_b:
        fig = px.bar(
            sub, x="Market", y="Scope 1 refrigerant (tCO2e)", color="Market",
            color_discrete_sequence=CHART_COLORS, text_auto=".1f",
            title="Scope 1 refrigerant",
        )
        fig.update_layout(
            showlegend=False, height=380,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor=P["grid"], tickformat=".1f"),
        )
        st.plotly_chart(fig, use_container_width=True, key="scope1_bar")


# ============================================================
# TAB 6 — WASTE & PACKAGING
# ============================================================
with tabs[5]:
    st.session_state.active_tab = "Waste & packaging"
    country_filter = st.multiselect(
        "Markets in scope", options=C.MARKETS, default=C.MARKETS,
        key="waste_countries",
    ) or C.MARKETS
    driver_pick = st.selectbox(
        "Driver in this category",
        ["Waste diversion", "Packaging circularity"],
        key="waste_driver_pick",
    )
    opp_map = {
        "Waste diversion": C.WASTE_OPPORTUNITIES,
        "Packaging circularity": C.PACKAGING_OPPORTUNITIES,
    }
    render_opportunity_tab(
        opp_map[driver_pick], driver_pick,
        driver_pick,
        "Full waste stream scope, phasing, then effort/impact matrix.",
        country_filter, f"waste_{driver_pick[:6]}",
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
    circ = circ[circ["Market"].isin(country_filter)]
    melted = circ.melt(id_vars="Market", var_name="Indicator", value_name="%")
    fig = px.bar(
        melted, x="Indicator", y="%", color="Market", barmode="group",
        color_discrete_sequence=CHART_COLORS,
        title="Circularity indicators (%)",
    )
    fig.update_layout(
        height=440, yaxis_range=[0, 100],
        yaxis=dict(gridcolor=P["grid"], tickformat=".1f"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True, key="circ_bars")
    st.dataframe(circ.round(1), use_container_width=True, hide_index=True)


# ============================================================
# TAB 7 — LOGISTICS OPTIMIZATION
# ============================================================
with tabs[6]:
    st.session_state.active_tab = "Logistics optimization"
    country_filter = st.multiselect(
        "Markets in scope", options=C.MARKETS, default=C.MARKETS,
        key="log_countries",
    ) or C.MARKETS
    render_opportunity_tab(
        C.LOGISTICS_OPPORTUNITIES, "Logistics optimization",
        "Logistics optimization",
        "Full freight and reverse-logistics scope, phasing, then effort/impact matrix.",
        country_filter, "log",
    )


# ============================================================
# TAB 8 — DATA QUALITY
# ============================================================
with tabs[7]:
    st.session_state.active_tab = "Data Quality"
    st.subheader("Data-quality heat map")
    st.caption(
        "Every cell is Tier 3 (modeled). Use this to sequence the first data-collection wave."
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
    st.markdown(
        "- **Tier 1** — Physical, project-specific (BoQ + EPDs, utility invoices)\n"
        "- **Tier 2** — Spend-based with physical overlays\n"
        "- **Tier 3** — Typology/benchmark modeled estimate (this draft)"
    )


# ============================================================
# TAB 9 — METHOD
# ============================================================
with tabs[8]:
    st.session_state.active_tab = "Method"
    st.subheader("About this draft")
    st.markdown(f"""
**Baseline framework:** 1.5°C-aligned retail pathway, {C.BASELINE_YEAR} base year.

**Targets applied:** −50% by 2030 · −70% by {C.TARGET_YEAR} · −90% by {C.LONG_TERM_YEAR}

**Boundary rules applied:**
- Scope 1+2: operational control
- Scope 3 Cat 2 (capital goods): capex ownership test
- Landlord-owned fixtures: influence-gap memo, not Category 2
- Avoided emissions: memo item, outside inventory boundary
- Category 5 (store waste) and Category 12 (sold-product EoL) kept separate

**Drill-down hierarchy (5 levels):** driver → activity type → country → area → item
**Additional view:** strategy attribution (within each driver's drill-down)

**Metric definitions:**
- **Reduction vs baseline (2035)** — annual snapshot vs 2021 baseline.
- **Cumulative CO₂ avoided (2021–2035)** — integrated total of yearly avoided amounts.
- **Impact (tCO₂e by 2035)** — cumulative reduction contribution of a specific initiative.

**LCA methodology summary:** see the LCA Index tab for stage-by-stage calculation basis.
""")
    st.markdown("### Scope glossary")
    for scope, definition in C.SCOPE_DEFINITIONS.items():
        st.markdown(f"**{scope}** — {definition}")

    st.markdown("### Driver glossary")
    for driver, definition in C.DRIVER_DEFINITIONS.items():
        scope = C.DRIVER_SCOPES.get(driver, "")
        st.markdown(f"**{driver}** *({scope})* — {definition}")

st.caption(
    "Built with Streamlit + Plotly. Free stack, public repo. "
    "All figures modeled — replace before external use."
)
