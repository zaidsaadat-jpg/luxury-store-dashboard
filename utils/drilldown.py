"""
Five-level drill-down helper.
Level 1: Driver → Level 2: Activity type → Level 3: Country
→ Level 4: Area of activity → Level 5: Specific item
"""
from utils.constants import INITIATIVES, MARKETS

try:
    from utils.constants import COUNTRY_WEIGHTS, DRIVER_STRUCTURE
except ImportError:
    # Fallback used when constants.py doesn't define these yet.
    COUNTRY_WEIGHTS = {
        "Renewable electricity transition": {"Hong Kong": 0.15, "Singapore": 0.08, "Korea": 0.20, "China": 0.57},
        "Energy efficiency (LED/HVAC)": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.20, "China": 0.52},
        "Refrigerant management": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.22, "China": 0.50},
        "Circular fit-out redesign": {"Hong Kong": 0.20, "Singapore": 0.10, "Korea": 0.22, "China": 0.48},
        "VM & seasonal reuse": {"Hong Kong": 0.18, "Singapore": 0.08, "Korea": 0.20, "China": 0.54},
        "Waste diversion": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.22, "China": 0.50},
    }
    DRIVER_STRUCTURE = {
        "Renewable electricity transition": {
            "activity_type": "Scope 1+2 — Energy",
            "areas": {"Boutique electricity": {
                "items": ["Base lighting", "Display lighting", "HVAC", "AV/POS"],
                "weights": {"Base lighting": 0.30, "Display lighting": 0.35, "HVAC": 0.25, "AV/POS": 0.10},
            }},
            "area_weights": {"Boutique electricity": 1.0},
        },
        "Energy efficiency (LED/HVAC)": {
            "activity_type": "Scope 1+2 — Energy",
            "areas": {
                "HVAC": {"items": ["Chillers", "AHUs", "Controls"], "weights": {"Chillers": 0.50, "AHUs": 0.30, "Controls": 0.20}},
                "Lighting": {"items": ["Base lighting", "Display lighting", "Track lighting"], "weights": {"Base lighting": 0.40, "Display lighting": 0.35, "Track lighting": 0.25}},
            },
            "area_weights": {"HVAC": 0.55, "Lighting": 0.45},
        },
        "Refrigerant management": {
            "activity_type": "Scope 1 — Refrigerants",
            "areas": {"Refrigeration": {"items": ["HVAC refrigerant", "Display fridges"], "weights": {"HVAC refrigerant": 0.80, "Display fridges": 0.20}}},
            "area_weights": {"Refrigeration": 1.0},
        },
        "Circular fit-out redesign": {
            "activity_type": "Scope 3 Cat 2 — Capital goods",
            "areas": {
                "Millwork & joinery": {"items": ["Wall panels", "Cash wraps", "Built-in shelving"], "weights": {"Wall panels": 0.40, "Cash wraps": 0.25, "Built-in shelving": 0.35}},
                "Loose furniture": {"items": ["Display tables", "Seating", "Wardrobes"], "weights": {"Display tables": 0.40, "Seating": 0.25, "Wardrobes": 0.35}},
                "Flooring": {"items": ["Carpet", "Stone", "Timber"], "weights": {"Carpet": 0.40, "Stone": 0.35, "Timber": 0.25}},
                "Lighting fixtures": {"items": ["Decorative luminaires", "Track systems"], "weights": {"Decorative luminaires": 0.55, "Track systems": 0.45}},
                "Partitions": {"items": ["Feature walls", "Demountable partitions"], "weights": {"Feature walls": 0.55, "Demountable partitions": 0.45}},
            },
            "area_weights": {"Millwork & joinery": 0.30, "Loose furniture": 0.20, "Flooring": 0.15, "Lighting fixtures": 0.15, "Partitions": 0.20},
        },
        "VM & seasonal reuse": {
            "activity_type": "Scope 3 — Seasonal / VM",
            "areas": {
                "Window displays": {"items": ["Prop structures", "Backdrops", "Lighting"], "weights": {"Prop structures": 0.45, "Backdrops": 0.35, "Lighting": 0.20}},
                "Mannequins & forms": {"items": ["Full mannequins", "Bust forms", "Hands/feet"], "weights": {"Full mannequins": 0.55, "Bust forms": 0.30, "Hands/feet": 0.15}},
                "In-store installations": {"items": ["Plinths", "Risers", "Campaign sets"], "weights": {"Plinths": 0.30, "Risers": 0.25, "Campaign sets": 0.45}},
                "Graphics & signage": {"items": ["Printed panels", "Acrylic signs", "Fabric banners"], "weights": {"Printed panels": 0.45, "Acrylic signs": 0.35, "Fabric banners": 0.20}},
            },
            "area_weights": {"Window displays": 0.30, "Mannequins & forms": 0.25, "In-store installations": 0.25, "Graphics & signage": 0.20},
        },
        "Waste diversion": {
            "activity_type": "Scope 3 Cat 5 — Waste",
            "areas": {
                "Fit-out waste": {"items": ["Timber", "Metal", "Acrylic"], "weights": {"Timber": 0.40, "Metal": 0.35, "Acrylic": 0.25}},
                "VM waste": {"items": ["Props", "Mannequins", "Signage"], "weights": {"Props": 0.45, "Mannequins": 0.30, "Signage": 0.25}},
                "Packaging waste": {"items": ["Cardboard", "Tissue", "Bags"], "weights": {"Cardboard": 0.50, "Tissue": 0.30, "Bags": 0.20}},
            },
            "area_weights": {"Fit-out waste": 0.55, "VM waste": 0.25, "Packaging waste": 0.20},
        },
    }


def drill_down(year, driver, countries=None):
    """
    Return nested breakdown of one driver's reduction in a given year,
    scaled to the selected markets only.
    """
    if countries is None:
        countries = MARKETS

    weights_all = COUNTRY_WEIGHTS[driver]
    total_w = sum(weights_all.get(c, 0.0) for c in countries)
    amount = INITIATIVES[driver].get(year, 0) * total_w
    structure = DRIVER_STRUCTURE[driver]

    norm = {
        c: (weights_all.get(c, 0.0) / total_w if total_w else 0.0)
        for c in countries
    }

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
