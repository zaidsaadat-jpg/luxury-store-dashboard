"""
Modeled assumptions for the first-draft dashboard.
ALL VALUES ARE TIER 3 ESTIMATES FROM PUBLIC BENCHMARKS.
Replace this module with CSV loaders when store-level data is available.
"""

MARKETS = ["Hong Kong", "Singapore", "Korea", "China"]

STORE_COUNTS = {
    "Hong Kong": 8, "Singapore": 3, "Korea": 8, "China": 18,
}

AVG_GIA_M2 = 600

GRID_FACTORS = {
    "Hong Kong": 0.79, "Singapore": 0.50, "Korea": 0.52, "China": 0.53,
}

ENERGY_INTENSITY = 250
REFRIGERANT_KG_PER_STORE = 2.5
REFRIGERANT_GWP = 1430

FITOUT_INTENSITY = 850
RENOVATION_CYCLE = 5

SEASONAL_INTENSITY = 40
SELLING_AREA_RATIO = 0.70

FITOUT_WASTE_INTENSITY = 35
MIXED_WASTE_EF_T_PER_TONNE = 0.35
DIVERSION_RATE = 0.60

DESIGN_FOR_DISASSEMBLY = {
    "Hong Kong": 0.35, "Singapore": 0.35, "Korea": 0.30, "China": 0.25,
}
FIXTURE_REUSE = {
    "Hong Kong": 0.20, "Singapore": 0.20, "Korea": 0.15, "China": 0.15,
}
VM_REUSE = {
    "Hong Kong": 0.40, "Singapore": 0.40, "Korea": 0.40, "China": 0.55,
}
RECYCLED_CONTENT = {
    "Hong Kong": 0.15, "Singapore": 0.15, "Korea": 0.12, "China": 0.10,
}

# ============================================================
# Trajectory — baseline 2021, target 2035, long-term 2040
# ============================================================
BASELINE_YEAR = 2021
TARGET_YEAR = 2035
LONG_TERM_YEAR = 2040
BASELINE_TOTAL_TCO2E = 10000.0

# ============================================================
# Annual reductions by initiative (tCO2e saved in that year)
# ============================================================
INITIATIVES = {
    "Renewable electricity transition": {
        2023: 250, 2024: 350, 2025: 450, 2026: 500, 2027: 500,
    },
    "Energy efficiency (LED/HVAC)": {
        2022: 120, 2023: 130, 2024: 130, 2025: 130, 2026: 120,
        2027: 100, 2028: 80, 2029: 60, 2030: 50,
    },
    "Refrigerant management": {
        2022: 60, 2023: 60, 2024: 60, 2025: 50, 2026: 50, 2027: 40,
        2028: 40, 2029: 30, 2030: 30, 2031: 20, 2032: 20,
    },
    "Circular fit-out redesign": {
        2023: 50, 2024: 100, 2025: 150, 2026: 180, 2027: 200,
        2028: 220, 2029: 240, 2030: 250, 2031: 250, 2032: 250,
        2033: 230, 2034: 230, 2035: 220,
    },
    "VM & seasonal reuse": {
        2022: 30, 2023: 40, 2024: 50, 2025: 55, 2026: 60, 2027: 60,
        2028: 60, 2029: 55, 2030: 55, 2031: 50, 2032: 50, 2033: 45,
        2034: 45, 2035: 45,
    },
    "Waste diversion": {
        2023: 15, 2024: 20, 2025: 25, 2026: 25, 2027: 25, 2028: 20,
        2029: 20, 2030: 15,
    },
}

# ============================================================
# Plan trajectory — planned absolute emissions by anchor year.
# Separate from the initiative-driven trajectory so variance
# against plan can be computed. Missing years are interpolated
# linearly in calc.py.
# ============================================================
PLAN_TRAJECTORY = {
    2021: 10000.0,
    2025: 8600.0,
    2030: 5000.0,
    2035: 3000.0,
}

# Country allocation weights per driver
COUNTRY_WEIGHTS = {
    "Renewable electricity transition": {"Hong Kong": 0.15, "Singapore": 0.08, "Korea": 0.20, "China": 0.57},
    "Energy efficiency (LED/HVAC)": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.20, "China": 0.52},
    "Refrigerant management": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.22, "China": 0.50},
    "Circular fit-out redesign": {"Hong Kong": 0.20, "Singapore": 0.10, "Korea": 0.22, "China": 0.48},
    "VM & seasonal reuse": {"Hong Kong": 0.18, "Singapore": 0.08, "Korea": 0.20, "China": 0.54},
    "Waste diversion": {"Hong Kong": 0.20, "Singapore": 0.08, "Korea": 0.22, "China": 0.50},
}

# ============================================================
# Five-level drill-down structure per driver
# ============================================================
DRIVER_STRUCTURE = {
    "Renewable electricity transition": {
        "activity_type": "Scope 1+2 — Energy",
        "areas": {
            "Boutique electricity": {
                "items": ["Base lighting", "Display lighting", "HVAC", "AV/POS"],
                "weights": {"Base lighting": 0.30, "Display lighting": 0.35, "HVAC": 0.25, "AV/POS": 0.10},
            },
        },
        "area_weights": {"Boutique electricity": 1.0},
    },
    "Energy efficiency (LED/HVAC)": {
        "activity_type": "Scope 1+2 — Energy",
        "areas": {
            "HVAC": {
                "items": ["Chillers", "AHUs", "Controls"],
                "weights": {"Chillers": 0.50, "AHUs": 0.30, "Controls": 0.20},
            },
            "Lighting": {
                "items": ["Base lighting", "Display lighting", "Track lighting"],
                "weights": {"Base lighting": 0.40, "Display lighting": 0.35, "Track lighting": 0.25},
            },
        },
        "area_weights": {"HVAC": 0.55, "Lighting": 0.45},
    },
    "Refrigerant management": {
        "activity_type": "Scope 1 — Refrigerants",
        "areas": {
            "Refrigeration": {
                "items": ["HVAC refrigerant", "Display fridges"],
                "weights": {"HVAC refrigerant": 0.80, "Display fridges": 0.20},
            },
        },
        "area_weights": {"Refrigeration": 1.0},
    },
    "Circular fit-out redesign": {
        "activity_type": "Scope 3 Cat 2 — Capital goods",
        "areas": {
            "Millwork & joinery": {
                "items": ["Wall panels", "Cash wraps", "Built-in shelving"],
                "weights": {"Wall panels": 0.40, "Cash wraps": 0.25, "Built-in shelving": 0.35},
            },
            "Loose furniture": {
                "items": ["Display tables", "Seating", "Wardrobes"],
                "weights": {"Display tables": 0.40, "Seating": 0.25, "Wardrobes": 0.35},
            },
            "Flooring": {
                "items": ["Carpet", "Stone", "Timber"],
                "weights": {"Carpet": 0.40, "Stone": 0.35, "Timber": 0.25},
            },
            "Lighting fixtures": {
                "items": ["Decorative luminaires", "Track systems"],
                "weights": {"Decorative luminaires": 0.55, "Track systems": 0.45},
            },
            "Partitions": {
                "items": ["Feature walls", "Demountable partitions"],
                "weights": {"Feature walls": 0.55, "Demountable partitions": 0.45},
            },
        },
        "area_weights": {
            "Millwork & joinery": 0.30, "Loose furniture": 0.20, "Flooring": 0.15,
            "Lighting fixtures": 0.15, "Partitions": 0.20,
        },
    },
    "VM & seasonal reuse": {
        "activity_type": "Scope 3 — Seasonal / VM",
        "areas": {
            "Window displays": {
                "items": ["Prop structures", "Backdrops", "Lighting"],
                "weights": {"Prop structures": 0.45, "Backdrops": 0.35, "Lighting": 0.20},
            },
            "Mannequins & forms": {
                "items": ["Full mannequins", "Bust forms", "Hands/feet"],
                "weights": {"Full mannequins": 0.55, "Bust forms": 0.30, "Hands/feet": 0.15},
            },
            "In-store installations": {
                "items": ["Plinths", "Risers", "Campaign sets"],
                "weights": {"Plinths": 0.30, "Risers": 0.25, "Campaign sets": 0.45},
            },
            "Graphics & signage": {
                "items": ["Printed panels", "Acrylic signs", "Fabric banners"],
                "weights": {"Printed panels": 0.45, "Acrylic signs": 0.35, "Fabric banners": 0.20},
            },
        },
        "area_weights": {
            "Window displays": 0.30, "Mannequins & forms": 0.25,
            "In-store installations": 0.25, "Graphics & signage": 0.20,
        },
    },
    "Waste diversion": {
        "activity_type": "Scope 3 Cat 5 — Waste",
        "areas": {
            "Fit-out waste": {
                "items": ["Timber", "Metal", "Acrylic"],
                "weights": {"Timber": 0.40, "Metal": 0.35, "Acrylic": 0.25},
            },
            "VM waste": {
                "items": ["Props", "Mannequins", "Signage"],
                "weights": {"Props": 0.45, "Mannequins": 0.30, "Signage": 0.25},
            },
            "Packaging waste": {
                "items": ["Cardboard", "Tissue", "Bags"],
                "weights": {"Cardboard": 0.50, "Tissue": 0.30, "Bags": 0.20},
            },
        },
        "area_weights": {"Fit-out waste": 0.55, "VM waste": 0.25, "Packaging waste": 0.20},
    },
}

# ============================================================
# LCA stages — sum equals BASELINE_TOTAL_TCO2E (10,000)
# ============================================================
LCA_STAGES = {
    "Raw material extraction": 1200.0,
    "Manufacturing / production": 2500.0,
    "Transport & distribution": 800.0,
    "Store fit-out & construction": 2800.0,
    "Operations (energy & refrigerants)": 1700.0,
    "Seasonal / VM refresh": 400.0,
    "Maintenance & repair": 300.0,
    "End of life (waste, take-back)": 300.0,
}

# ============================================================
# Opportunity matrices — (name, impact_tCO2e_by_2035, effort_1to5, status)
# ============================================================
FITOUT_OPPORTUNITIES = [
    ("Design for disassembly (screws, not glue)", 600, 4, "Opportunity"),
    ("Modular millwork design", 450, 3, "In progress"),
    ("Reusable modular partitions", 300, 3, "Opportunity"),
    ("Take-back scheme for fixtures", 250, 4, "Opportunity"),
    ("Reclaimed timber sourcing", 200, 2, "Acted"),
    ("Low-carbon concrete / stone alternatives", 180, 3, "Opportunity"),
    ("Local supplier sourcing (Asia-based mills)", 150, 2, "In progress"),
    ("LED retrofit + controls", 120, 1, "Acted"),
    ("Recyclable mannequins (recycled polystyrene)", 80, 1, "Acted"),
    ("Material passport for top 20 SKUs", 50, 2, "Opportunity"),
]

SEASONAL_OPPORTUNITIES = [
    ("Standardized reusable VM kits", 120, 2, "In progress"),
    ("Multi-city event set reuse", 100, 2, "Acted"),
    ("Recycled polystyrene mannequins", 60, 1, "Acted"),
    ("Digital signage replacing printed graphics", 80, 2, "Opportunity"),
    ("Reusable window display structures", 70, 3, "Opportunity"),
    ("Return-and-refurbish scheme for props", 50, 3, "Opportunity"),
    ("Fabric banner reuse program", 30, 1, "In progress"),
]

ENERGY_OPPORTUNITIES = [
    ("Renewable electricity (RE100 trajectory)", 500, 3, "In progress"),
    ("Refrigerant transition to low-GWP (R-32, R-290)", 180, 3, "Opportunity"),
    ("HVAC controls optimization", 120, 2, "In progress"),
    ("LED display lighting retrofit", 90, 1, "Acted"),
    ("Sub-metering for landlord-supplied energy", 60, 2, "Opportunity"),
    ("Trading-hours-based HVAC scheduling", 70, 1, "Acted"),
    ("Predictive maintenance for chillers", 40, 2, "Opportunity"),
]

WASTE_OPPORTUNITIES = [
    ("Fixture take-back & reuse program", 100, 3, "Opportunity"),
    ("Segregated waste streams at store level", 60, 2, "In progress"),
    ("Packaging take-back at point of sale", 50, 3, "Opportunity"),
    ("Mannequin refurbishment scheme", 40, 2, "Opportunity"),
    ("Local recycling partner network", 30, 2, "In progress"),
]
