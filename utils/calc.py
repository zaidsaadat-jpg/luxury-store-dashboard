from utils.constants import (
    MARKETS, STORE_COUNTS, AVG_GIA_M2, GRID_FACTORS, ENERGY_INTENSITY,
    REFRIGERANT_KG_PER_STORE, REFRIGERANT_GWP, FITOUT_INTENSITY,
    RENOVATION_CYCLE, SEASONAL_INTENSITY, SELLING_AREA_RATIO,
    FITOUT_WASTE_INTENSITY, MIXED_WASTE_EF_T_PER_TONNE, VM_REUSE,
)


def calc_floor_area():
    return {m: STORE_COUNTS[m] * AVG_GIA_M2 for m in MARKETS}


def calc_electricity_mwh():
    area = calc_floor_area()
    return {m: (area[m] * ENERGY_INTENSITY) / 1000 for m in MARKETS}


def calc_scope2_location():
    elec = calc_electricity_mwh()
    return {m: (elec[m] * 1000 * GRID_FACTORS[m]) / 1000 for m in MARKETS}


def calc_scope1_refrigerant():
    return {
        m: (STORE_COUNTS[m] * REFRIGERANT_KG_PER_STORE * REFRIGERANT_GWP) / 1000
        for m in MARKETS
    }


def calc_fitout_full_renovation():
    area = calc_floor_area()
    return {m: (area[m] * FITOUT_INTENSITY) / 1000 for m in MARKETS}


def calc_fitout_annualized():
    full = calc_fitout_full_renovation()
    return {m: full[m] / RENOVATION_CYCLE for m in MARKETS}


def calc_seasonal():
    area = calc_floor_area()
    return {
        m: (area[m] * SELLING_AREA_RATIO * SEASONAL_INTENSITY) / 1000
        for m in MARKETS
    }


def calc_avoided_emissions():
    seasonal = calc_seasonal()
    return {m: seasonal[m] * VM_REUSE[m] for m in MARKETS}


def calc_waste_category5():
    area = calc_floor_area()
    waste_kg = {m: (area[m] * FITOUT_WASTE_INTENSITY) / RENOVATION_CYCLE for m in MARKETS}
    return {m: (waste_kg[m] / 1000) * MIXED_WASTE_EF_T_PER_TONNE for m in MARKETS}
