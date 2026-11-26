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
    """
    Robustly extract the selected driver from a pie click event.
    Tries, in order: customdata → label → point_number lookup → point_index lookup.
    """
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

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("### Executive summary")
    st.markdown(
        f'<div class="exec-summary">'
        f'<b>Baseline ({C.BASELINE_YEAR}):</b> {base_v:,.0f} tCO₂e<br>'
        f'<b>{C.TARGET_YEAR} projected:</b> {end_v:,.0f} tCO₂e<br>'
        f'<b>{C.TARGET_YEAR} plan:</b> {plan_v:,.0f} tCO₂e<br>'
        f'<b>Variance vs plan:</b> <span class="{var_class}">{var:+,.0f} tCO₂e</span><br>'
        f'<b>Reduction vs baseline ({C.TARGET_YEAR}):</b> −{red_pct:.1f}% '
        f'({base_v - end_v:,.0f} tCO₂e/yr)<br>'
        f'<b>Cumulative CO₂ avoided (2021–{C.TARGET_YEAR}):</b> '
        f'<span class="cum-avoided">{all_cum_avoided:,.0f} tCO₂e</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Two views of the same result: the *annual snapshot* (tCO₂e avoided per year by 2035) "
        "and the *cumulative integrated total* (sum of yearly avoided amounts)."
    )
    st.markdown("---")
    st.markdown("**Top reduction levers to 2035**")
    for i, (drv, val) in enumerate(top_3, start=1):
        scope = C.DRIVER_SCOPES.get(drv, "")
        st.markdown(
            f"{i}. **{drv}** — {val:,.0f} tCO₂e  \n"
            f"&nbsp;&nbsp;<span style='color:#8A8A8A;font-size:0.78rem;'>{scope}</span>",
            unsafe_allow_html=True,
        )
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
    k1.metric(f"{C.BASELINE_YEAR} baseline", f"{base_v:,.0f} tCO₂e")
    k2.metric(f"{C.TARGET_YEAR} projected", f"{end_v:,.0f} tCO₂e")
    k3.metric(f"{C.TARGET_YEAR} plan", f"{plan_v:,.0f} tCO₂e")
    k4.metric("Variance vs plan", f"{var:+,.0f} tCO₂e")
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

    # ---------------- TRAJECTORY VIEW ----------------
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
            hovertemplate="%{x}<br>%{y:,.0f} tCO₂e<br><i>Click to see monthly detail</i><extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=years_str, y=[plan[y] for y in years],
            mode="lines+markers", name="Planned trajectory",
            line=dict(color=P["gold"], width=2.5, dash="dash"),
            marker=dict(size=6, color=P["gold"]),
            hovertemplate="Plan %{x}<br>%{y:,.0f} tCO₂e<extra></extra>",
        ))
        fig.update_layout(
            height=460, yaxis_title="tCO₂e / yr", xaxis_title="Year",
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
        if clicked_year_int and clicked_year_int in emissions:
            st.session_state.detail_year = clicked_year_int
            st.session_state.selected_year = clicked_year_int
            st.session_state.view_mode = "detail"
            st.rerun()

    # ---------------- CUMULATIVE BY DRIVER VIEW ----------------
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
            hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:,.0f} tCO₂e cumulative<extra></extra>",
        )
        fig_cum.update_layout(
            height=540,
            xaxis=dict(title="Year", tickmode="linear", dtick=1, gridcolor=P["grid"]),
            yaxis=dict(title="Cumulative CO₂ avoided (tCO₂e)", gridcolor=P["grid"]),
            showlegend=True,
            legend=dict(orientation="h", y=-0.20, x=0, font=dict(size=10)),
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=130, l=10, r=10),
        )
        _safe_plotly(fig_cum, key="ov_cum", selection=False)

        total_at_2035 = sum(total_per_driver.values())
        st.caption(
            f"Cumulative total 2021–{C.TARGET_YEAR}: **{total_at_2035:,.0f} tCO₂e**. "
            f"Matches the 'Cumulative CO₂ avoided' metric in the sidebar."
        )

    # ---------------- MONTHLY DETAIL VIEW ----------------
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
                    yaxis=dict(title="tCO₂e / month", gridcolor=P["grid"]),
                    yaxis2=dict(
                        title="Cumulative tCO₂e",
                        overlaying="y", side="right", showgrid=False,
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
                st.markdown(f"**{detail_year} total: {ydf['tCO2e'].sum():,.1f} tCO₂e**")
                st.dataframe(ydf, use_container_width=True, hide_index=True)

    # ---------- Pie chart (full width, callout labels, click-to-drill) ----------
    st.divider()
    st.markdown("### Cumulative contribution by initiative, 2021–2035")
    st.caption(
        "Click a slice (or use the selector below) to drill into the country, area, "
        "and specific-item breakdown. The country and area charts split the same "
        "cumulative value shown in the slice."
    )
    cum = calc.cumulative_by_driver(country_filter)
    c_df = pd.DataFrame(
        sorted(cum.items(), key=lambda x: -x[1]),
        columns=["Driver", "tCO2e"],
    ).reset_index(drop=True)

    if "selected_initiative" not in st.session_state:
        st.session_state.selected_initiative = "— Select —"

    # Sync widget state if changed externally (e.g. by a click)
    if st.session_state.get("_last_pie_sync") != st.session_state.selected_initiative:
        st.session_state.pop("pie_select", None)
        st.session_state["_last_pie_sync"] = st.session_state.selected_initiative

    # Explicit go.Pie with customdata so the driver name is ALWAYS in the click event
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
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} tCO₂e (%{percent})<extra></extra>",
        sort=False,
        direction="clockwise",
    )])
    fig_p.update_layout(
        height=640,
        showlegend=False,
        margin=dict(t=40, b=40, l=220, r=220),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    pie_event = _safe_plotly(fig_p, key="ov_pie")

    # Fallback selector — guaranteed drill-down even if click is missed
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

    # Click handler — runs after the widget renders so we can override
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
                f"↳ Matches pie chart slice value ({pie_slice_value:,.0f} tCO₂e). "
                f"The country and area charts below split this total."
            )

        if dd['total'] == 0:
            st.warning(
                f"No reductions modeled for **{selected_driver}** in {horizon_label}. "
                f"Try a later year or switch to the cumulative view."
            )
        else:
            c3, c4 = st.columns(2)
            with c3:
                st.markdown(f"**Country split · {horizon_label}**")
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
                    height=280, showlegend=False,
                    yaxis=dict(categoryorder="total ascending", title=""),
                    xaxis=dict(title="tCO₂e", gridcolor=P["grid"]),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, b=10, l=10, r=10),
                )
                st.plotly_chart(fig_c, use_container_width=True, key="dd_country")
                st.caption(f"Sum: {cdf['tCO2e'].sum():,.1f} tCO₂e")

            with c4:
                st.markdown(f"**Area split · {horizon_label}**")
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
                    height=280, showlegend=False,
                    yaxis=dict(categoryorder="total ascending", title=""),
                    xaxis=dict(title="tCO₂e", gridcolor=P["grid"]),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, b=10, l=10, r=10),
                )
                st.plotly_chart(fig_a, use_container_width=True, key="dd_area")
                st.caption(f"Sum: {adf['tCO2e'].sum():,.1f} tCO₂e")

            st.markdown("**Specific items**")
            rows = []
            for c, v in dd["countries"].items():
                for a, av in v["areas"].items():
                    for item, iv in av["items"].items():
                        rows.append({
                            "Country": c, "Area of activity": a,
                            "Specific item": item, "tCO₂e": round(iv, 2),
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
                    f"Showing {len(filtered)} of {len(idf)} items · "
                    f"click column headers to re-sort"
                )
    else:
        st.info(
            "Click a slice of the pie (or use the selector above) to drill into "
            "the five-level breakdown and see the driver definition."
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
    cov = calc.coverage_factor(
        st.session_state.get("countries", C.MARKETS) or C.MARKETS
    )
    lca_df = pd.DataFrame({
        "Stage": list(C.LCA_STAGES.keys()),
        "tCO2e": [v * cov for v in C.LCA_STAGES.values()],
    })
    lca_df["% of total"] = (lca_df["tCO2e"] / lca_df["tCO2e"].sum() * 100).round(1)

    cA, cB = st.columns([3, 2])
    with cA:
        fig = px.bar(lca_df, x="tCO2e", y="Stage", orientation="h", text="% of total")
        fig.update_traces(
            texttemplate="%{text}%", textposition="outside", marker_color=P["sage"],
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
            color_continuous_scale=[[0, "#EFEAE0"], [1, P["sage"]]],
        )
        fig2.update_layout(
            height=520, title="Share of baseline footprint",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig2, use_container_width=True, key="lca_tree")
    st.dataframe(lca_df, use_container_width=True, hide_index=True)


# ============================================================
# Opportunity-matrix helper
# ============================================================
def render_opportunity_tab(opportunities, scope_area_key, title, intro):
    st.subheader(title)
    st.caption(intro)
    st.markdown("#### 1. Full scope of items assessed")
    scope_rows = []
    for area_name, data in C.DRIVER_STRUCTURE[scope_area_key]["areas"].items():
        for item, w in data["weights"].items():
            scope_rows.append({
                "Area of activity": area_name, "Specific item": item,
                "Relative share": f"{w * 100:.0f}%",
            })
    st.dataframe(pd.DataFrame(scope_rows), use_container_width=True, hide_index=True)

    st.markdown("#### 2. Initiatives matrix — effort vs impact (to 2035)")
    opp_df = pd.DataFrame(
        opportunities,
        columns=["Initiative", "Impact (tCO2e by 2035)", "Effort (1–5)", "Status"],
    )
    status_colors = {"Acted": P["green"], "In progress": P["gold"], "Opportunity": P["oxblood"]}
    c_a, c_b = st.columns([2, 1])
    with c_a:
        fig = px.scatter(
            opp_df, x="Effort (1–5)", y="Impact (tCO2e by 2035)",
            size="Impact (tCO2e by 2035)", color="Status",
            color_discrete_map=status_colors, hover_name="Initiative",
            title="Effort vs impact",
        )
        fig.update_layout(
            height=480, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor=P["grid"]), yaxis=dict(gridcolor=P["grid"]),
        )
        fig.update_xaxes(range=[0, 5.5], tickmode="array", tickvals=[1, 2, 3, 4, 5])
        st.plotly_chart(fig, use_container_width=True, key=f"opp_scatter_{scope_area_key}")
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
        C.FITOUT_OPPORTUNITIES, "Circular fit-out redesign",
        "Capital goods — boutique fit-out",
        "Full scope of assessable items, then initiatives matrix (effort vs impact) to 2035.",
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
        C.SEASONAL_OPPORTUNITIES, "VM & seasonal reuse",
        "Seasonal builds, visual merchandising and events",
        "Highest-velocity carbon source. Full item scope first, then effort/impact matrix.",
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
        increasing={"marker": {"color": P["sage"]}},
        totals={"marker": {"color": P["green"]}},
        connector={"line": {"color": P["grey"]}},
    ))
    bridge.update_layout(
        height=380, yaxis_title="tCO₂e / yr", showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis_gridcolor=P["grid"],
    )
    st.plotly_chart(bridge, use_container_width=True, key="vm_bridge")


# ============================================================
# TAB 5 — SCOPE 1+2
# ============================================================
with tabs[4]:
    render_opportunity_tab(
        C.ENERGY_OPPORTUNITIES, "Renewable electricity transition",
        "Scope 1+2 — Operational energy and refrigerants",
        "Full item scope first (energy end-uses, refrigerants), then effort/impact matrix.",
    )
    st.divider()
    st.subheader("Modeled Scope 1+2 by market")
    c1, c2, c3 = st.columns(3)
    c1.metric("Electricity", f"{df['Electricity (MWh)'].sum():,.0f} MWh")
    c2.metric("Scope 2", f"{df['Scope 2 (tCO2e)'].sum():,.0f} tCO₂e")
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


# ============================================================
# TAB 6 — CIRCULARITY & WASTE
# ============================================================
with tabs[5]:
    render_opportunity_tab(
        C.WASTE_OPPORTUNITIES, "Waste diversion",
        "Circularity and end-of-life management",
        "Full waste stream scope, circularity indicators, then effort/impact matrix.",
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


# ============================================================
# TAB 7 — DATA QUALITY
# ============================================================
with tabs[6]:
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
# TAB 8 — METHOD
# ============================================================
with tabs[7]:
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

**Drill-down hierarchy (5 levels):**
1. Driver / initiative
2. Activity type (Scope 1+2, Capital goods, Seasonal/VM, Waste, Transport, Packaging)
3. Country
4. Area of activity
5. Specific item

**Metric definitions:**
- **Reduction vs baseline (2035)** — annual snapshot: how much lower the 2035 footprint is vs 2021 baseline.
- **Cumulative CO₂ avoided (2021–2035)** — integrated total: sum across all years of (baseline − projected).

**Chart views (Overview tab):**
- **Trajectory** — annual emissions bars + plan line. Click any bar for monthly detail.
- **Cumulative by driver** — stacked area of cumulative avoided emissions; shows which drivers dominate early vs late.
- **Monthly detail** — stacked bars by initiative for a single year, with cumulative line.
""")
    st.markdown("### Scope glossary")
    for scope, definition in C.SCOPE_DEFINITIONS.items():
        st.markdown(f"**{scope}** — {definition}")

    st.markdown("### Driver glossary")
    for driver, definition in C.DRIVER_DEFINITIONS.items():
        scope = C.DRIVER_SCOPES.get(driver, "")
        st.markdown(f"**{driver}** *({scope})* — {definition}")

    st.markdown("**Data status:** All figures are Tier 3 modeled estimates built from public benchmarks.")

st.caption(
    "Built with Streamlit + Plotly. Free stack, public repo. "
    "All figures modeled — replace before external use."
)
