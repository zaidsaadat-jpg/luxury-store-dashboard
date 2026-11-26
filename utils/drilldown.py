"""
Five-level drill-down helper.
Level 1: Driver → Level 2: Activity type → Level 3: Country
→ Level 4: Area of activity → Level 5: Specific item
"""
from utils.constants import INITIATIVES, MARKETS

try:
    from utils.constants import COUNTRY_WEIGHTS, DRIVER_STRUCTURE
except ImportError:
    COUNTRY_WEIGHTS = {
        "Renewable electricity transition": {"Hong Kong": 0.15, "Singapore": 0.08, "Korea": 0.20, "China": 0.57},
        "Energy efficiency (LED/HVAC)": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.20, "China": 0.52},
        "Refrigerant management": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.22, "China": 0.50},
        "Circular fit-out redesign": {"Hong Kong": 0.20, "Singapore": 0.10, "Korea": 0.22, "China": 0.48},
        "VM & seasonal reuse": {"Hong Kong": 0.18, "Singapore": 0.08, "Korea": 0.20, "China": 0.54},
        "Waste diversion": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.22, "China": 0.50},
        "Logistics optimization": {"Hong Kong": 0.18, "Singapore": 0.10, "Korea": 0.22, "China": 0.50},
        "Packaging circularity": {"Hong Kong": 0.20, "Singapore": 0.10, "Korea": 0.22, "China": 0.48},
        "Modular & adaptable design": {"Hong Kong": 0.20, "Singapore": 0.10, "Korea": 0.22, "China": 0.48},
        "Asset longevity & retention": {"Hong Kong": 0.20, "Singapore": 0.10, "Korea": 0.22, "China": 0.48},
    }
    DRIVER_STRUCTURE = {}


def _normalize_weights(driver, countries):
    w = COUNTRY_WEIGHTS[driver]
    total = sum(w.get(c, 0.0) for c in countries)
    return total, {c: (w.get(c, 0.0) / total if total else 0.0) for c in countries}


def _build_result(driver, amount, norm, countries):
    structure = DRIVER_STRUCTURE[driver]
    result = {
        "total": amount,
        "activity_type": structure["activity_type"],
        "countries": {},
    }
    for country in countries:
        c_amount = amount * norm[country]
        areas = {}
        for area, area_w in structure["area_weights"].items():
            a_amount = c_amount * area_w
            items = {
                item: a_amount * item_w
                for item, item_w in structure["areas"][area]["weights"].items()
            }
            areas[area] = {"total": a_amount, "items": items}
        result["countries"][country] = {"total": c_amount, "areas": areas}
    return result


def drill_down(year, driver, countries=None):
    """Single-year breakdown, scaled to selected markets."""
    if countries is None:
        countries = MARKETS
    if driver not in DRIVER_STRUCTURE:
        return {"total": 0, "activity_type": "", "countries": {}}
    total_w, norm = _normalize_weights(driver, countries)
    amount = INITIATIVES[driver].get(year, 0) * total_w
    return _build_result(driver, amount, norm, countries)


def cumulative_drill_down(driver, countries=None):
    """Cumulative 2021-2035 breakdown — matches pie chart slice value."""
    if countries is None:
        countries = MARKETS
    if driver not in DRIVER_STRUCTURE:
        return {"total": 0, "activity_type": "", "countries": {}}
    total_w, norm = _normalize_weights(driver, countries)
    amount = sum(INITIATIVES[driver].values()) * total_w
    return _build_result(driver, amount, norm, countries)
