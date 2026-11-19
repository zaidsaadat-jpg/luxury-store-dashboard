from utils.constants import (
    MARKETS, STORE_COUNTS, AVG_GIA_M2, GRID_FACTORS, ENERGY_INTENSITY,
    REFRIGERANT_KG_PER_STORE, REFRIGERANT_GWP, FITOUT_INTENSITY,
    RENOVATION_CYCLE, SEASONAL_INTENSITY, SELLING_AREA_RATIO,
    FITOUT_WASTE_INTENSITY, MIXED_WASTE_EF_T_PER_TONNE, VM_REUSE,
    INITIATIVES, BASELINE_YEAR, TARGET_YEAR, BASELINE_TOTAL_TCO2E,
)


def calc_floor_area():
    return {m: STORE_COUNTS[m] * AVG_GIA_M2 for m in MARKETS}


def calc_electricity_mwh():
    a = calc_floor_area()
    return {m: (a[m] * ENERGY_INTENSITY) / 1000 for m in MARKETS}


def calc_scope2_location():
    e = calc_electricity_mwh()
    return {m: (e[m] * 1000 * GRID_FACTORS[m]) / 1000 for m in MARKETS}


def calc_scope1_refrigerant():
    return {m: (STORE_COUNTS[m] * REFRIGERANT_KG_PER_STORE * REFRIGERANT_GWP) / 1000 for m in MARKETS}


def calc_fitout_full_renovation():
    a = calc_floor_area()
    return {m: (a[m] * FITOUT_INTENSITY) / 1000 for m in MARKETS}


def calc_fitout_annualized():
    f = calc_fitout_full_renovation()
    return {m: f[m] / RENOVATION_CYCLE for m in MARKETS}


def calc_seasonal():
    a = calc_floor_area()
    return {m: (a[m] * SELLING_AREA_RATIO * SEASONAL_INTENSITY) / 1000 for m in MARKETS}


def calc_avoided_emissions():
    s = calc_seasonal()
    return {m: s[m] * VM_REUSE[m] for m in MARKETS}


def calc_waste_category5():
    a = calc_floor_area()
    w = {m: (a[m] * FITOUT_WASTE_INTENSITY) / RENOVATION_CYCLE for m in MARKETS}
    return {m: (w[m] / 1000) * MIXED_WASTE_EF_T_PER_TONNE for m in MARKETS}


# ============================================================
# Trajectory calculations
# ============================================================
def annual_reductions():
    """Return {year: {driver: tco2e_saved}}."""
    years = {}
    for driver, amounts in INITIATIVES.items():
        for year, amount in amounts.items():
            years.setdefault(year, {})[driver] = amount
    return years


def annual_emissions():
    """Return {year: absolute tco2e} from baseline through target year."""
    reductions = annual_reductions()
    emissions = {BASELINE_YEAR: BASELINE_TOTAL_TCO2E}
    current = BASELINE_TOTAL_TCO2E
    for year in range(BASELINE_YEAR + 1, TARGET_YEAR + 1):
        current -= sum(reductions.get(year, {}).values())
        emissions[year] = current
    return emissions


def waterfall_data():
    """Return (labels, values, measures) for plotly waterfall chart."""
    emissions = annual_emissions()
    years = sorted(emissions.keys())
    labels = [str(y) for y in years]
    values = [emissions[years[0]]]
    for i in range(1, len(years)):
        values.append(emissions[years[i]] - emissions[years[i - 1]])
    measures = ["absolute"] + ["relative"] * (len(years) - 1)
    return labels, values, measures
