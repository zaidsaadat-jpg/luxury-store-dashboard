from utils.constants import (
    MARKETS, STORE_COUNTS, AVG_GIA_M2, GRID_FACTORS, ENERGY_INTENSITY,
    REFRIGERANT_KG_PER_STORE, REFRIGERANT_GWP, FITOUT_INTENSITY,
    RENOVATION_CYCLE, SEASONAL_INTENSITY, SELLING_AREA_RATIO,
    FITOUT_WASTE_INTENSITY, MIXED_WASTE_EF_T_PER_TONNE, VM_REUSE,
    INITIATIVES, COUNTRY_WEIGHTS, PLAN_TRAJECTORY, MONTHLY_PATTERNS,
    BASELINE_YEAR, TARGET_YEAR, BASELINE_TOTAL_TCO2E,
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


def country_factor(driver, countries):
    return sum(COUNTRY_WEIGHTS[driver].get(c, 0.0) for c in countries)


def coverage_factor(countries):
    total = 0.0
    covered = 0.0
    for driver, yearly in INITIATIVES.items():
        s = sum(yearly.values())
        total += s
        covered += s * country_factor(driver, countries)
    return (covered / total) if total else 0.0


def year_drivers(year, countries):
    return {
        d: yearly[year] * country_factor(d, countries)
        for d, yearly in INITIATIVES.items()
        if year in yearly
    }


def cumulative_by_driver(countries):
    return {
        d: sum(yearly.values()) * country_factor(d, countries)
        for d, yearly in INITIATIVES.items()
    }


def scaled_annual_emissions(countries):
    cov = coverage_factor(countries)
    base = BASELINE_TOTAL_TCO2E * cov
    emissions = {BASELINE_YEAR: base}
    current = base
    for y in range(BASELINE_YEAR + 1, TARGET_YEAR + 1):
        current -= sum(
            yearly[y] * country_factor(d, countries)
            for d, yearly in INITIATIVES.items()
            if y in yearly
        )
        emissions[y] = current
    return emissions


def plan_trajectory(countries):
    cov = coverage_factor(countries)
    anchors = sorted(PLAN_TRAJECTORY.items())
    out = {}
    for y in range(BASELINE_YEAR, TARGET_YEAR + 1):
        seg_lo, seg_hi = anchors[0], anchors[-1]
        for i in range(len(anchors) - 1):
            if anchors[i][0] <= y <= anchors[i + 1][0]:
                seg_lo, seg_hi = anchors[i], anchors[i + 1]
                break
        if seg_hi[0] == seg_lo[0]:
            v = seg_lo[1]
        else:
            t = (y - seg_lo[0]) / (seg_hi[0] - seg_lo[0])
            v = seg_lo[1] + t * (seg_hi[1] - seg_lo[1])
        out[y] = v * cov
    return out


def monthly_driver_breakdown(year, countries):
    """Return {driver: [tco2e per month]} — seasonality-weighted."""
    result = {}
    for driver, yearly in INITIATIVES.items():
        if year not in yearly:
            continue
        annual = yearly[year] * country_factor(driver, countries)
        if annual <= 0:
            continue
        pattern = MONTHLY_PATTERNS.get(driver, [1.0] * 12)
        total = sum(pattern) or 12.0
        result[driver] = [annual * p / total for p in pattern]
    return result


def cumulative_avoided(countries):
    """Sum of (baseline - emissions[y]) across all years — the integrated
    area between the baseline line and the projected trajectory."""
    emissions = scaled_annual_emissions(countries)
    base = emissions[BASELINE_YEAR]
    return sum(base - emissions[y] for y in emissions.keys())
