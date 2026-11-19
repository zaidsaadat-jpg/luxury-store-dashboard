"""
Five-level drill-down helper.
Level 1: Driver → Level 2: Activity type → Level 3: Country
→ Level 4: Area of activity → Level 5: Specific item
"""
from utils.constants import INITIATIVES, COUNTRY_WEIGHTS, DRIVER_STRUCTURE, MARKETS


def drivers_for_year(year):
    """Return {driver: tco2e_saved} for the selected year."""
    return {d: v[year] for d, v in INITIATIVES.items() if year in v}


def drill_down(year, driver):
    """Return nested breakdown of one driver's reduction in a given year."""
    amount = INITIATIVES[driver][year]
    structure = DRIVER_STRUCTURE[driver]
    weights = COUNTRY_WEIGHTS[driver]
    result = {"total": amount, "activity_type": structure["activity_type"], "countries": {}}
    for country in MARKETS:
        c_amount = amount * weights[country]
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
