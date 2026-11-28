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
    .vc-stage .driver { font-size: 0.72rem; color: #5A4A3A; margin-top: 8px; }
    .vc-stage .driver b { color: #1F1F1F; }
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
VALUE_CHAIN = [
    {
        "id": "design",
        "title": "Design & specification",
        "desc": "Concept, fixture specification, material selection, design-for-disassembly decisions before procurement.",
        "lca_stages": ["Raw material extraction"],
    },
    {
        "id": "production",
        "title": "Materials & production",
        "desc": "Upstream manufacturing of fixtures, furniture, mannequins, and packaging.",
        "lca_stages": ["Manufacturing / production"],
    },
    {
        "id": "logistics",
        "title": "Logistics & installation",
        "desc": "Inbound freight, installation, store-to-store transfers, and reverse logistics.",
        "lca_stages": ["Transport & distribution"],
    },
    {
        "id": "operations",
        "title": "Store operations",
        "desc": "Electricity, refrigerant leakage, seasonal refreshes, and maintenance.",
        "lca_stages": ["Operations (energy & refrigerants)", "Seasonal / VM refresh",
                       "Maintenance & repair", "Store fit-out & construction"],
    },
    {
        "id": "eol",
        "title": "End of life",
        "desc": "Waste diversion, take-back, recycling, end-of-life of sold products and packaging.",
        "lca_stages": ["End of life (waste, take-back)"],
    },
]

# ---------------- Header ----------------
st.title("Luxury Store CO₂ Reduction Dashboard")
st.caption(
    "Multi-market retail portfolio · Hong Kong · Singapore · Korea · China · "
    "Baseline 2021 · Trajectory to 2035"
)
st.divider()

tabs = st.tabs([
    "Overview", "LCA Index", "Circular fit-out redesign", "VM & seasonal reuse",
    "Energy & refrigerants", "Waste & packaging", "Logistics optimization",
    "Data Quality", "Method",
])

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Overview"


# ---------------- Exec summary ----------------
def render_exec_summary():
    tab = st.session_state.active_tab
    with st.sidebar:
        st.markdown("### Executive summary")
        st.caption(f"Viewing: **{tab}**")

        if tab == "Overview":
            countries = st.session_state.get("countries", C.MARKETS) or C.MARKETS
            em = calc.scaled_annual_emissions(countries)
            pl = calc.plan_trajectory(countries)
            cum_av = calc.cumulative_avoided(countries)
            b = em[C.BASELINE_YEAR]
            e = em[C.TARGET_YEAR]
            p = pl[C.TARGET_YEAR]
            v = e - p
            pct = (1 - e / b) * 100 if b else 0
            vcls = "variance-neg" if v <= 0 else "variance-pos"
            st.markdown(
                f'<div class="exec-summary">'
                f'<b>Baseline ({C.BASELINE_YEAR}):</b> {b:,.1f} tCO₂e<br>'
                f'<b>{C.TARGET_YEAR} projected:</b> {e:,.1f} tCO₂e<br>'
                f'<b>{C.TARGET_YEAR} plan:</b> {p:,.1f} tCO₂e<br>'
                f'<b>Variance vs plan:</b> <span class="{vcls}">{v:+,.1f} tCO₂e</span><br>'
                f'<b>Reduction vs baseline:</b> −{pct:.1f}%<br>'
                f'<b>Cumulative CO₂ avoided:</b> '
                f'<span class="cum-avoided">{cum_av:,.1f} tCO₂e</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("---")
            top = sorted(
                ((d, calc.cumulative_by_driver(countries).get(d, 0))
                 for d in C.INITIATIVES), key=lambda x: -x[1]
            )[:3]
            st.markdown("**Top 3 levers to 2035**")
            for i, (d, v2) in enumerate(top, start=1):
                scope = C.DRIVER_SCOPES.get(d, "")
                st.markdown(
                    f"{i}. **{d}** — {v2:,.1f} tCO₂e  \n"
                    f"&nbsp;&nbsp;<span style='color:#8A8A8A;font-size:0.78rem;'>{scope}</span>",
                    unsafe_allow_html=True,
                )

        elif tab == "LCA Index":
            countries = st.session_state.get("lca_countries", C.MARKETS) or C.MARKETS
            cov = calc.coverage_factor(countries)
            stage_base = {k: v * cov for k, v in C.LCA_STAGES.items()}
            total = sum(stage_base.values())
            biggest = max(stage_base.items(), key=lambda x: x[1])
            smallest = min(stage_base.items(), key=lambda x: x[1])
            plan_c = calc.plan_trajectory(countries)[C.TARGET_YEAR]
            # Compute reduced stage totals for the exec summary
            reduced_totals = {}
            for stage, base in stage_base.items():
                r35 = C.STAGE_REDUCTION_PROFILE[stage].get(C.TARGET_YEAR, 0)
                reduced_totals[stage] = base * (1 - r35)
            big_red = max(
                ((k, (1 - reduced_totals[k] / stage_base[k]) * 100)
                 for k in stage_base), key=lambda x: x[1],
            )
            small_red = min(
                ((k, (1 - reduced_totals[k] / stage_base[k]) * 100)
                 for k in stage_base), key=lambda x: x[1],
            )
            st.markdown(
                f'<div class="exec-summary">'
                f'<b>Mapped baseline:</b> {total:,.1f} tCO₂e<br>'
                f'<b>{C.TARGET_YEAR} plan:</b> {plan_c:,.1f} tCO₂e '
                f'({plan_c/total*100:.1f}% of baseline)<br>'
                f'<b>Largest stage:</b> {biggest[0]}<br>'
                f'&nbsp;&nbsp;{biggest[1]:,.1f} tCO₂e baseline<br>'
                f'<b>Deepest reduction:</b> {big_red[0]}<br>'
                f'&nbsp;&nbsp;−{big_red[1]:.1f}% by {C.TARGET_YEAR}<br>'
                f'<b>Shallowest reduction:</b> {small_red[0]}<br>'
                f'&nbsp;&nbsp;−{small_red[1]:.1f}% by {C.TARGET_YEAR}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Stages reduce at different rates by design: energy-related stages "
                "move faster, material and logistics stages slower."
            )

        elif tab in ("Circular fit-out redesign", "VM & seasonal reuse",
                     "Energy & refrigerants", "Waste & packaging", "Logistics optimization"):
            key_map = {
                "Circular fit-out redesign": ("fitout_countries", "fitout_driver_pick",
                    ["Circular fit-out redesign", "Modular & adaptable design", "Asset longevity & retention"]),
                "VM & seasonal reuse": ("vm_countries", None, ["VM & seasonal reuse"]),
                "Energy & refrigerants": ("energy_countries", "energy_driver_pick",
                    ["Renewable electricity transition", "Energy efficiency (LED/HVAC)", "Refrigerant management"]),
                "Waste & packaging": ("waste_countries", "waste_driver_pick",
                    ["Waste diversion", "Packaging circularity"]),
                "Logistics optimization": ("log_countries", None, ["Logistics optimization"]),
            }
            ck, dk, drivers_here = key_map[tab]
            countries = st.session_state.get(ck, C.MARKETS) or C.MARKETS
            active_driver = (
                st.session_state.get(dk, drivers_here[0]) if dk else drivers_here[0]
            )
            cum_all = calc.cumulative_by_driver(countries)
            cat_total = sum(cum_all.get(d, 0) for d in drivers_here)
            total_avoided = calc.cumulative_avoided(countries)
            cat_share = (cat_total / total_avoided * 100) if total_avoided else 0
            drv_total = cum_all.get(active_driver, 0)
            drv_share = (drv_total / cat_total * 100) if cat_total else 0

            st.markdown(
                f'<div class="exec-summary">'
                f'<b>Active driver:</b> {active_driver}<br>'
                f'<b>Driver cumulative:</b> {drv_total:,.1f} tCO₂e<br>'
                f'<b>Driver share of category:</b> {drv_share:.1f}%<br>'
                f'<b>Category cumulative:</b> {cat_total:,.1f} tCO₂e<br>'
                f'<b>Category share of portfolio avoided:</b> {cat_share:.1f}%<br>'
                f'<b>Drivers in category:</b> {len(drivers_here)}'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Category totals reconcile to the Overview pie chart. "
                "Switching driver or market updates these figures."
            )

        elif tab == "Data Quality":
            st.markdown(
                '<div class="exec-summary">'
                '<b>Current data tier:</b> Tier 3 (modeled)<br>'
                '<b>Categories tracked:</b> 7<br>'
                '<b>Markets covered:</b> 4<br>'
                '<b>Landlord-supplied energy:</b> not included yet'
                '</div>',
                unsafe_allow_html=True,
            )

        elif tab == "Method":
            st.caption(
                "Method tab documents boundary rules, definitions, glossaries, "
                "and LCA methodology."
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


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tabs[0]:
    st.session_state.active_tab = "Overview"
    st.subheader("Absolute emissions trajectory, 2021–2035")
    st.caption(
        "Switch between three views. Click a bar in the Trajectory view to drill into "
        "monthly detail. All views respect the country filter."
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
            "The phase changes tell the story: energy retrofit early, circular fit-out mid, "
            "logistics and modular late."
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
            yaxis=dict(title="Cumulative CO₂ avoided (tCO₂e)",
                       gridcolor=P["grid"], tickformat=".1f"),
            showlegend=True,
            legend=dict(orientation="h", y=-0.20, x=0, font=dict(size=10)),
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=130, l=10, r=10),
        )
        _safe_plotly(fig_cum, key="ov_cum", selection=False)

        st.caption(
            f"Cumulative total 2021–{C.TARGET_YEAR}: "
            f"**{sum(total_per_driver.values()):,.1f} tCO₂e**. "
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
                        title="Cumulative tCO₂e", overlaying="y", side="right",
                        showgrid=False, tickformat=".1f",
                    ),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=100, l=10, r=10), bargap=0.20,
                )
                _safe_plotly(fig_m, key="ov_monthly", selection=False)

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
        sort=False, direction="clockwise",
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
            "Drill-down horizon", ["Cumulative 2021–2035", "Single year"],
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

        if dd['total'] == 0:
            st.warning(f"No reductions modeled for **{selected_driver}** in {horizon_label}.")
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
                    texttemplate="%{text:,.1f}", textposition="outside",
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
                cdf = pd.DataFrame(
                    sorted([(k, v["total"]) for k, v in dd["countries"].items()],
                           key=lambda x: -x[1]),
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
                st.caption(f"Country split · sum: {cdf['tCO2e'].sum():,.1f} tCO₂e")

            with c4:
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
                st.caption(f"Area split · sum: {adf['tCO2e'].sum():,.1f} tCO₂e")
    else:
        st.info(
            "Click a slice of the pie (or use the selector above) to drill into "
            "strategy attribution, country, area, and item-level breakdown."
        )


# ============================================================
# TAB 2 — LCA INDEX
# ============================================================
with tabs[1]:
    st.session_state.active_tab = "LCA Index"
    st.subheader("End-to-end lifecycle and value chain")
    st.caption(
        "The full value chain from design through end of life. Each stage shows baseline, "
        "planned reduction by 2035, and the drivers that act on it."
    )

    lca_countries = st.multiselect(
        "Markets in scope (LCA view)", options=C.MARKETS, default=C.MARKETS,
        key="lca_countries",
    ) or C.MARKETS
    cov = calc.coverage_factor(lca_countries)

    stage_base = {k: v * cov for k, v in C.LCA_STAGES.items()}
    total_base = sum(stage_base.values())

    # Compute reduced stage at 2035 from stage profile
    stage_2035 = {}
    for stage, base in stage_base.items():
        r35 = C.STAGE_REDUCTION_PROFILE[stage].get(C.TARGET_YEAR, 0.0)
        stage_2035[stage] = base * (1 - r35)
    total_2035 = sum(stage_2035.values())

    st.markdown("### Value-chain stages")
    ribbon_cols = st.columns(len(VALUE_CHAIN))
    for i, stage in enumerate(VALUE_CHAIN):
        stage_em = sum(stage_base.get(s, 0.0) for s in stage["lca_stages"])
        stage_pl = sum(stage_2035.get(s, 0.0) for s in stage["lca_stages"])
        reduction_pct_stage = (1 - stage_pl / stage_em) * 100 if stage_em else 0.0
        # Which drivers touch this stage, with their tCO2e baseline component
        stage_drivers = []
        for lca in stage["lca_stages"]:
            for drv, share in C.DRIVER_SHARE_WITHIN_STAGE.get(lca, {}).items():
                contribution = stage_base[lca] * share
                stage_drivers.append((drv, contribution))
        stage_drivers.sort(key=lambda x: -x[1])
        driver_html = "<br>".join(
            f"· <b>{d}</b> — {v:,.1f} tCO₂e" for d, v in stage_drivers[:3]
        )
        with ribbon_cols[i]:
            st.markdown(
                f'<div class="vc-stage">'
                f'<div class="title">{stage["title"]}</div>'
                f'<div class="desc">{stage["desc"]}</div>'
                f'<div class="metric">{stage_em:,.1f} tCO₂e</div>'
                f'<div class="sub">baseline · planned 2035: {stage_pl:,.1f} '
                f'(−{reduction_pct_stage:.1f}%)</div>'
                f'<div class="driver">Drivers acting here:<br>{driver_html}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.caption(
        f"Stage baselines sum to **{total_base:,.1f} tCO₂e** — the "
        f"{C.BASELINE_YEAR} baseline on the Overview tab. Planned 2035 stage totals "
        f"sum to **{total_2035:,.1f} tCO₂e** — the plan anchor on the Overview tab. "
        f"Reductions differ per stage (e.g. energy fast, materials slower), which is "
        f"why the combined reduction is not uniformly 80%."
    )

    # ---------------- Baseline vs 2035 by LCA stage ----------------
    st.markdown("### Baseline → 2035 by LCA stage")
    vc_rows = []
    for lca, base in stage_base.items():
        vc_rows.append({
            "LCA stage": lca,
            "Baseline (tCO₂e)": round(base, 1),
            "2035 (tCO₂e)": round(stage_2035[lca], 1),
            "Reduction %": round((1 - stage_2035[lca] / base) * 100, 1) if base else 0,
        })
    vc_df = pd.DataFrame(vc_rows)

    fig_vc = go.Figure()
    fig_vc.add_trace(go.Bar(
        name="Baseline", x=vc_df["LCA stage"], y=vc_df["Baseline (tCO₂e)"],
        marker_color=P["sage"],
        hovertemplate="<b>%{x}</b><br>Baseline: %{y:,.1f}<extra></extra>",
    ))
    fig_vc.add_trace(go.Bar(
        name="2035 plan", x=vc_df["LCA stage"], y=vc_df["2035 (tCO₂e)"],
        marker_color=P["gold"],
        hovertemplate="<b>%{x}</b><br>2035: %{y:,.1f}<extra></extra>",
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

    # ---------------- Stage-driver linkage chart ----------------
    st.markdown("### Driver contribution inside each LCA stage (baseline)")
    link_rows = []
    for lca, base in stage_base.items():
        for drv, share in C.DRIVER_SHARE_WITHIN_STAGE.get(lca, {}).items():
            link_rows.append({
                "LCA stage": lca,
                "Driver": drv,
                "Baseline share (tCO₂e)": round(base * share, 1),
            })
    link_df = pd.DataFrame(link_rows)
    fig_link = px.bar(
        link_df, x="Baseline share (tCO₂e)", y="LCA stage", color="Driver",
        orientation="h", color_discrete_map=C.DRIVER_COLORS,
        text_auto=".1f",
    )
    fig_link.update_layout(
        height=460,
        xaxis=dict(title="tCO₂e at baseline", gridcolor=P["grid"], tickformat=".1f"),
        yaxis=dict(title="", categoryorder="total ascending"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=10)),
        margin=dict(t=20, b=40, l=10, r=160),
    )
    st.plotly_chart(fig_link, use_container_width=True, key="lca_stage_driver_link")

    # ---------------- Methodology (expanders) ----------------
    st.markdown("### Methodology — how each LCA stage is calculated")
    methodology = {
        "Raw material extraction": (
            "**Data:** Supplier EPDs where available (Tier 1); spend-based procurement "
            "estimates otherwise (Tier 2); industry-average material intensities as "
            "fallback (Tier 3). **Calculation:** Mass of each material (timber, metal, "
            "stone, glass, acrylic, textile) × material-specific cradle-to-gate emission "
            "factor. **Drivers:** design-for-disassembly and material choice in "
            "Circular fit-out redesign determine the extraction footprint of every renovation."
        ),
        "Manufacturing / production": (
            "**Data:** BoQ mass × material-specific emission factors; annualized over the "
            "renovation cycle. **Calculation:** Σ (component mass × fabrication factor) "
            "for fixtures, furniture, mannequins, and packaging. **Drivers:** Circular "
            "fit-out (material substitution, recycled content), modular design (fewer "
            "bespoke components), asset longevity (refurbishment vs replacement), "
            "packaging (mass reduction), VM reuse (fewer new assets)."
        ),
        "Transport & distribution": (
            "**Data:** Freight logs or logistics partner data (Tier 1); spend-based "
            "estimates on logistics cost (Tier 2). **Calculation:** Tonne-km × mode-specific "
            "emission factor (sea, road, air). **Driver:** logistics optimization — modal "
            "shift, consolidation, reverse-logistics network redesign."
        ),
        "Store fit-out & construction": (
            "**Data:** Bill of Quantities with material masses (Tier 1); capex by project "
            "type (Tier 2); per-m² benchmark (Tier 3). **Calculation:** Σ (material mass × "
            "cradle-to-gate EF) + construction waste (Scope 3 Cat 5). **Drivers:** circular "
            "fit-out redesign and modular & adaptable design — the two determinant levers."
        ),
        "Operations (energy & refrigerants)": (
            "**Data:** Utility invoices (Tier 1); floor-area allocation from landlord data "
            "(Tier 2); kWh/m² benchmark × grid factor (Tier 3). **Calculation:** "
            "kWh × grid emission factor (location-based) + refrigerant top-up (kg) × GWP. "
            "**Drivers:** renewable electricity transition, energy efficiency, refrigerant management."
        ),
        "Seasonal / VM refresh": (
            "**Data:** VM procurement records (Tier 1); estimated kgCO₂e per m² of selling "
            "area (Tier 3). **Calculation:** selling area (70% of GIA) × VM intensity, split "
            "across window displays, mannequins, in-store installations, signage. "
            "**Driver:** VM & seasonal reuse."
        ),
        "Maintenance & repair": (
            "**Data:** Maintenance log (Tier 1); estimated from refurbishment frequency "
            "(Tier 3). **Calculation:** Σ (refurb/repair events × avg embodied carbon avoided "
            "vs replacement). **Driver:** asset longevity & retention."
        ),
        "End of life (waste, take-back)": (
            "**Data:** Waste contractor manifests (Tier 1); estimated waste mass by area "
            "(Tier 3). **Calculation:** Mass × treatment-specific EF (landfill, incineration, "
            "recycling, reuse) for Scope 3 Cat 5 (own waste) and Cat 12 (sold products). "
            "**Driver:** waste diversion."
        ),
    }
    for stage, text in methodology.items():
        with st.expander(f"{stage} — calculation basis"):
            st.markdown(text)

    st.divider()
    st.subheader("LCA stages — detailed footprint")
    st.dataframe(vc_df, use_container_width=True, hide_index=True)

    colA, colB = st.columns(2)
    with colA:
        fig_t = px.treemap(
            vc_df, path=["LCA stage"], values="Baseline (tCO₂e)",
            color="Baseline (tCO₂e)",
            color_continuous_scale=[[0, "#EFEAE0"], [1, P["sage"]]],
        )
        fig_t.update_layout(height=420, title="Baseline footprint share",
                            paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_t, use_container_width=True, key="lca_tree")
    with colB:
        fig_r = px.bar(
            vc_df, x="LCA stage", y="Reduction %",
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
def _initiative_gantt(opportunities, country_filter, key_suffix):
    """Gantt of initiatives with per-country timing offsets."""
    # Use the earliest offset among selected markets (China is -1, HK/SG +1)
    offsets = [C.COUNTRY_ROLLOUT_LAG.get(c, 0) for c in country_filter]
    chosen_offset = min(offsets) if offsets else 0
    offset_label = ", ".join(
        f"{c}: {C.COUNTRY_ROLLOUT_LAG.get(c, 0):+d}y" for c in country_filter
    )

    opp_rows = []
    for name, impact, effort, status, start, end in opportunities:
        start_c = max(C.BASELINE_YEAR, start + chosen_offset)
        end_c = min(C.TARGET_YEAR, end + chosen_offset)
        if end_c < start_c:
            end_c = start_c
        duration = end_c - start_c + 1
        annual = impact / duration if duration else 0.0
        opp_rows.append({
            "Initiative": name,
            "Status": status,
            "Effort": effort,
            "Start": start_c,
            "End": end_c,
            "Duration (yrs)": duration,
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
            base=[row["Start"] - C.BASELINE_YEAR],
            orientation="h",
            marker=dict(color=status_colors[row["Status"]],
                        line=dict(color="white", width=1)),
            text=f"{int(row['Start'])}–{int(row['End'])} · {row['Annual impact (tCO₂e/yr)']:.1f}/yr",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=9),
            hovertemplate=(
                f"<b>{row['Initiative']}</b><br>"
                f"Status: {row['Status']}<br>"
                f"Effort: {row['Effort']}/5<br>"
                f"Active: {int(row['Start'])}–{int(row['End'])} "
                f"({int(row['Duration (yrs)'])} yrs)<br>"
                f"Total impact: {row['Total impact (tCO₂e)']:,.1f} tCO₂e<br>"
                f"Annual: {row['Annual impact (tCO₂e/yr)']:,.1f} tCO₂e/yr<extra></extra>"
            ),
            showlegend=False,
        ))
    fig.update_layout(
        height=max(340, 60 + 42 * len(gdf)),
        barmode="stack",
        xaxis=dict(
            title="Year",
            range=[0, C.TARGET_YEAR - C.BASELINE_YEAR],
            tickmode="array",
            tickvals=[i for i in range(0, C.TARGET_YEAR - C.BASELINE_YEAR + 1)],
            ticktext=[str(C.BASELINE_YEAR + i) for i in range(0, C.TARGET_YEAR - C.BASELINE_YEAR + 1)],
            gridcolor=P["grid"],
        ),
        yaxis=dict(title="", categoryorder="array",
                   categoryarray=list(reversed(gdf["Initiative"].tolist()))),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=40, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"gantt_{key_suffix}")

    chips = " ".join(
        f'<span style="background:{status_colors[s]};color:white;'
        f'padding:3px 10px;border-radius:2px;font-size:0.78rem;margin-right:6px;">'
        f'{s}</span>'
        for s in ["Acted", "In progress", "Opportunity"]
    )
    st.markdown(chips, unsafe_allow_html=True)
    st.caption(
        f"Timing shown for markets in scope (offset vs plan anchor: {offset_label}). "
        f"Bars show each initiative's active window in the earliest-offset market in scope; "
        f"label reads start–end · annualised reduction. Durations reflect a realistic "
        f"ramp (retrofits quick, material substitutions slow)."
    )
    st.dataframe(gdf.round(1), use_container_width=True, hide_index=True)


def render_opportunity_tab(opportunities, scope_area_key, title, intro, country_filter, key_suffix):
    st.subheader(title)
    st.caption(intro)

    # ---------- Table 1 — merged scope + subtotals, sortable + filterable ----------
    st.markdown("#### Full scope of items assessed")
    dd_cum = DD.cumulative_drill_down(scope_area_key, country_filter)
    driver_total = dd_cum["total"]

    scope_rows = []
    if scope_area_key in C.DRIVER_STRUCTURE:
        for area_name, data in C.DRIVER_STRUCTURE[scope_area_key]["areas"].items():
            for item, w in data["weights"].items():
                scope_rows.append({
                    "Area of activity": area_name,
                    "Specific item": item,
                    "tCO₂e": round(driver_total * w, 1),
                })
    scope_df = pd.DataFrame(scope_rows)

    if not scope_df.empty:
        area_filter = st.selectbox(
            "Filter by area of activity",
            ["All"] + sorted(scope_df["Area of activity"].unique().tolist()),
            key=f"area_filter_{key_suffix}",
        )
        sort_by = st.selectbox(
            "Sort by",
            ["tCO₂e (desc)", "tCO₂e (asc)", "Area of activity (A→Z)", "Specific item (A→Z)"],
            key=f"sort_{key_suffix}",
        )

        filtered = scope_df.copy()
        if area_filter != "All":
            filtered = filtered[filtered["Area of activity"] == area_filter]

        sort_map = {
            "tCO₂e (desc)": ("tCO₂e", False),
            "tCO₂e (asc)": ("tCO₂e", True),
            "Area of activity (A→Z)": ("Area of activity", True),
            "Specific item (A→Z)": ("Specific item", True),
        }
        col, asc = sort_map[sort_by]
        filtered = filtered.sort_values(col, ascending=asc).reset_index(drop=True)

        # Share % within the current view (i.e. All = 100%)
        view_total = filtered["tCO₂e"].sum()
        filtered["Share %"] = (filtered["tCO₂e"] / view_total * 100).round(1) if view_total else 0.0
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(
            f"View total: {view_total:,.1f} tCO₂e · Share % is relative to this view "
            f"({'all items' if area_filter == 'All' else f'items in {area_filter}'})."
        )

        # Area subtotals table (share % vs ALL driver total)
        area_sub = scope_df.groupby("Area of activity", as_index=False)["tCO₂e"].sum()
        area_sub["Share of driver total %"] = (
            area_sub["tCO₂e"] / driver_total * 100
        ).round(1) if driver_total else 0.0
        area_sub = area_sub.sort_values("tCO₂e", ascending=False).reset_index(drop=True)
        st.markdown("**Subtotals by area of activity**")
        st.dataframe(area_sub.round(1), use_container_width=True, hide_index=True)
        st.caption(
            f"Driver total across all areas: {driver_total:,.1f} tCO₂e "
            f"({C.DRIVER_SCOPES.get(scope_area_key, '')}). "
            f"Shares sum to 100%."
        )

    # ---------- Table 2 — Effort vs impact (moved before Gantt) ----------
    st.markdown("#### Initiatives overview — effort vs impact")
    opp_df = pd.DataFrame(
        opportunities,
        columns=["Initiative", "Impact (tCO₂e by 2035)", "Effort (1–5)",
                 "Status", "Start", "End"],
    )
    opp_df["Impact (tCO₂e by 2035)"] = opp_df["Impact (tCO₂e by 2035)"].astype(float)

    status_colors = {"Acted": P["green"], "In progress": P["gold"], "Opportunity": P["oxblood"]}
    c_a, c_b = st.columns([2, 1])
    with c_a:
        fig = px.scatter(
            opp_df, x="Effort (1–5)", y="Impact (tCO₂e by 2035)",
            size="Impact (tCO₂e by 2035)", color="Status",
            color_discrete_map=status_colors, hover_name="Initiative",
            title="Effort vs reduction impact",
        )
        fig.update_layout(
            height=460, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
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
        st.metric("Total impact to 2035",
                  f"{opp_df['Impact (tCO₂e by 2035)'].sum():,.1f} tCO₂e")

    # ---------- Table 3 — Gantt phasing ----------
    st.markdown("#### Initiative phasing — Gantt view")
    _initiative_gantt(opportunities, country_filter, key_suffix)


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
        "Item scope, initiatives overview, then phasing Gantt.",
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
        "Highest-velocity carbon source. Item scope, initiatives, then Gantt.",
        country_filter, "vm",
    )


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
        "Item scope, initiatives overview, then Gantt phasing.",
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
        fig.update_layout(showlegend=False, height=380,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          yaxis=dict(gridcolor=P["grid"], tickformat=".1f"))
        st.plotly_chart(fig, use_container_width=True, key="scope2_bar")
    with c_b:
        fig = px.bar(
            sub, x="Market", y="Scope 1 refrigerant (tCO2e)", color="Market",
            color_discrete_sequence=CHART_COLORS, text_auto=".1f",
            title="Scope 1 refrigerant",
        )
        fig.update_layout(showlegend=False, height=380,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          yaxis=dict(gridcolor=P["grid"], tickformat=".1f"))
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
        "Item scope, initiatives overview, then Gantt phasing.",
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
        "Freight and reverse-logistics scope, initiatives, then Gantt phasing.",
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

**How reductions are modelled:** each LCA stage has its own reduction curve from 2021 to 2035. 
Driver-level reductions are derived from stage reductions × driver share within stage. 
This ensures the driver pie, the LCA view, and the Overview trajectory all reconcile.

**Metric definitions:**
- **Reduction vs baseline (2035)** — annual snapshot vs 2021 baseline.
- **Cumulative CO₂ avoided (2021–2035)** — integrated total of yearly avoided amounts.
- **Impact (tCO₂e by 2035)** — cumulative reduction contribution of a specific initiative.
- **Share % (filtered view)** — relative to the currently filtered table total.
- **Share of driver total %** — relative to the driver's full unfiltered total.

**LCA methodology summary:** see LCA Index tab for stage-by-stage calculation basis.
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

# Render sidebar last so active_tab reflects current view
render_exec_summary()
