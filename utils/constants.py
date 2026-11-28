"""
Modeled assumptions for the first-draft dashboard.
ALL VALUES ARE TIER 3 ESTIMATES FROM PUBLIC BENCHMARKS.
"""

MARKETS = ["Hong Kong", "Singapore", "Korea", "China"]

STORE_COUNTS = {"Hong Kong": 8, "Singapore": 3, "Korea": 8, "China": 18}
AVG_GIA_M2 = 600
GRID_FACTORS = {"Hong Kong": 0.79, "Singapore": 0.50, "Korea": 0.52, "China": 0.53}
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

DESIGN_FOR_DISASSEMBLY = {"Hong Kong": 0.35, "Singapore": 0.35, "Korea": 0.30, "China": 0.25}
FIXTURE_REUSE = {"Hong Kong": 0.20, "Singapore": 0.20, "Korea": 0.15, "China": 0.15}
VM_REUSE = {"Hong Kong": 0.40, "Singapore": 0.40, "Korea": 0.40, "China": 0.55}
RECYCLED_CONTENT = {"Hong Kong": 0.15, "Singapore": 0.15, "Korea": 0.12, "China": 0.10}

BASELINE_YEAR = 2021
TARGET_YEAR = 2035
LONG_TERM_YEAR = 2040

# ============================================================
# LCA stages — baseline footprint
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

BASELINE_TOTAL_TCO2E = sum(LCA_STAGES.values())  # 10,000

# ============================================================
# Stage-level reduction profile — share of each stage's baseline
# that is abated by each year. Curves differ per stage so that
# total reduction is NOT flat across stages.
#
# Example reading: "Operations (energy & refrigerants)" is
# 35% abated by 2030 and 65% by 2035; "Raw material extraction"
# is 20% abated by 2030 and 45% by 2035.
# ============================================================
STAGE_REDUCTION_PROFILE = {
    "Raw material extraction": {
        2022: 0.01, 2023: 0.02, 2024: 0.04, 2025: 0.06, 2026: 0.08,
        2027: 0.10, 2028: 0.13, 2029: 0.16, 2030: 0.20, 2031: 0.25,
        2032: 0.30, 2033: 0.35, 2034: 0.40, 2035: 0.45,
    },
    "Manufacturing / production": {
        2022: 0.01, 2023: 0.03, 2024: 0.06, 2025: 0.09, 2026: 0.12,
        2027: 0.16, 2028: 0.21, 2029: 0.26, 2030: 0.31, 2031: 0.37,
        2032: 0.43, 2033: 0.49, 2034: 0.55, 2035: 0.61,
    },
    "Transport & distribution": {
        2022: 0.00, 2023: 0.01, 2024: 0.02, 2025: 0.04, 2026: 0.06,
        2027: 0.10, 2028: 0.14, 2029: 0.19, 2030: 0.24, 2031: 0.30,
        2032: 0.36, 2033: 0.42, 2034: 0.48, 2035: 0.54,
    },
    "Store fit-out & construction": {
        2022: 0.00, 2023: 0.02, 2024: 0.05, 2025: 0.08, 2026: 0.12,
        2027: 0.17, 2028: 0.22, 2029: 0.27, 2030: 0.32, 2031: 0.37,
        2032: 0.42, 2033: 0.47, 2034: 0.52, 2035: 0.57,
    },
    "Operations (energy & refrigerants)": {
        2022: 0.04, 2023: 0.10, 2024: 0.17, 2025: 0.24, 2026: 0.30,
        2027: 0.36, 2028: 0.41, 2029: 0.45, 2030: 0.49, 2031: 0.53,
        2032: 0.57, 2033: 0.60, 2034: 0.63, 2035: 0.65,
    },
    "Seasonal / VM refresh": {
        2022: 0.03, 2023: 0.08, 2024: 0.14, 2025: 0.20, 2026: 0.27,
        2027: 0.34, 2028: 0.40, 2029: 0.45, 2030: 0.50, 2031: 0.54,
        2032: 0.57, 2033: 0.60, 2034: 0.62, 2035: 0.63,
    },
    "Maintenance & repair": {
        2022: 0.02, 2023: 0.05, 2024: 0.08, 2025: 0.12, 2026: 0.16,
        2027: 0.20, 2028: 0.25, 2029: 0.30, 2030: 0.35, 2031: 0.40,
        2032: 0.45, 2033: 0.50, 2034: 0.55, 2035: 0.59,
    },
    "End of life (waste, take-back)": {
        2022: 0.01, 2023: 0.03, 2024: 0.07, 2025: 0.11, 2026: 0.16,
        2027: 0.22, 2028: 0.28, 2029: 0.34, 2030: 0.40, 2031: 0.45,
        2032: 0.49, 2033: 0.52, 2034: 0.55, 2035: 0.57,
    },
}

# Plan trajectory derived from the stage-level reductions above
def _plan_from_stages():
    plan = {}
    for y in range(BASELINE_YEAR, TARGET_YEAR + 1):
        remaining = 0.0
        for stage, baseline in LCA_STAGES.items():
            reduction = STAGE_REDUCTION_PROFILE[stage].get(y, 0.0)
            remaining += baseline * (1 - reduction)
        plan[y] = remaining
    return plan

PLAN_TRAJECTORY = _plan_from_stages()

# ============================================================
# Initiatives — each driver now maps to one LCA stage so the
# driver's annual reductions reconcile with the stage curve.
# ============================================================
DRIVER_TO_STAGE = {
    "Renewable electricity transition": "Operations (energy & refrigerants)",
    "Energy efficiency (LED/HVAC)": "Operations (energy & refrigerants)",
    "Refrigerant management": "Operations (energy & refrigerants)",
    "Circular fit-out redesign": "Store fit-out & construction",
    "VM & seasonal reuse": "Seasonal / VM refresh",
    "Waste diversion": "End of life (waste, take-back)",
    "Logistics optimization": "Transport & distribution",
    "Packaging circularity": "Manufacturing / production",
    "Modular & adaptable design": "Store fit-out & construction",
    "Asset longevity & retention": "Maintenance & repair",
}

# Driver share within stage — used to split each stage's annual
# reduction into drivers.
DRIVER_SHARE_WITHIN_STAGE = {
    "Operations (energy & refrigerants)": {
        "Renewable electricity transition": 0.40,
        "Energy efficiency (LED/HVAC)": 0.40,
        "Refrigerant management": 0.20,
    },
    "Store fit-out & construction": {
        "Circular fit-out redesign": 0.70,
        "Modular & adaptable design": 0.30,
    },
    "Seasonal / VM refresh": {
        "VM & seasonal reuse": 1.00,
    },
    "End of life (waste, take-back)": {
        "Waste diversion": 1.00,
    },
    "Transport & distribution": {
        "Logistics optimization": 1.00,
    },
    "Manufacturing / production": {
        "Packaging circularity": 1.00,
    },
    "Maintenance & repair": {
        "Asset longevity & retention": 1.00,
    },
    "Raw material extraction": {},
}

def _compute_initiatives():
    """Derive each driver's annual reductions from stage curves and shares."""
    out = {d: {} for d in DRIVER_TO_STAGE}
    for y in range(BASELINE_YEAR + 1, TARGET_YEAR + 1):
        for stage, baseline in LCA_STAGES.items():
            r_y = STAGE_REDUCTION_PROFILE[stage].get(y, 0.0)
            r_prev = STAGE_REDUCTION_PROFILE[stage].get(y - 1, 0.0)
            incremental = baseline * (r_y - r_prev)
            if incremental <= 0:
                continue
            for drv, share in DRIVER_SHARE_WITHIN_STAGE.get(stage, {}).items():
                out[drv][y] = out[drv].get(y, 0.0) + incremental * share
    return out

INITIATIVES = _compute_initiatives()

# ============================================================
# Scopes, colors, glossaries
# ============================================================
DRIVER_SCOPES = {
    "Renewable electricity transition": "Scope 2",
    "Energy efficiency (LED/HVAC)": "Scope 1+2",
    "Refrigerant management": "Scope 1",
    "Circular fit-out redesign": "Scope 3 · Cat 2",
    "VM & seasonal reuse": "Scope 3",
    "Waste diversion": "Scope 3 · Cat 5",
    "Logistics optimization": "Scope 3 · Cat 4/9",
    "Packaging circularity": "Scope 3 · Cat 5/12",
    "Modular & adaptable design": "Scope 3 · Cat 2",
    "Asset longevity & retention": "Scope 3 · Cat 2",
}

DRIVER_COLORS = {
    "Renewable electricity transition": "#4E79A7",
    "Energy efficiency (LED/HVAC)": "#F28E2B",
    "Refrigerant management": "#76B7B2",
    "Circular fit-out redesign": "#59A14F",
    "VM & seasonal reuse": "#E15759",
    "Waste diversion": "#9C755F",
    "Logistics optimization": "#EDC948",
    "Packaging circularity": "#B07AA1",
    "Modular & adaptable design": "#FF9DA7",
    "Asset longevity & retention": "#BAB0AC",
}

SCOPE_DEFINITIONS = {
    "Scope 1": "Direct emissions from owned or controlled sources — on-site fuel combustion, refrigerant leakage.",
    "Scope 2": "Indirect emissions from purchased electricity, heat, steam, or cooling.",
    "Scope 1+2": "Combined direct (Scope 1) and energy-indirect (Scope 2) emissions.",
    "Scope 3": "All other indirect value-chain emissions (15 categories upstream and downstream).",
    "Scope 3 · Cat 2": "Category 2 — Capital goods. Upstream emissions from goods purchased or acquired for capital use: fixtures, fit-out materials, equipment, furniture.",
    "Scope 3 · Cat 4/9": "Category 4 (upstream transportation & distribution) and Category 9 (downstream transportation & distribution) — freight, logistics, reverse logistics.",
    "Scope 3 · Cat 5": "Category 5 — Waste generated in operations. Emissions from treatment and disposal of waste created by the company's own activities.",
    "Scope 3 · Cat 5/12": "Category 5 (waste generated in operations) combined with Category 12 (end-of-life treatment of sold products) — e.g. packaging sent out with purchases.",
}

DRIVER_DEFINITIONS = {
    "Renewable electricity transition": "Switching boutique electricity from grid power to renewable sources (PPAs, green tariffs, on-site generation) to decarbonise Scope 2.",
    "Energy efficiency (LED/HVAC)": "Reducing electricity consumption per m² through LED retrofit, HVAC optimisation, controls, and trading-hours scheduling.",
    "Refrigerant management": "Preventing leaks of high-GWP refrigerants from HVAC and display fridges, and transitioning to lower-GWP alternatives (R-32, R-290).",
    "Circular fit-out redesign": "Designing boutique interiors for reuse — disassembly, modularity, reclaimed materials — to cut the embodied carbon of each renovation cycle.",
    "VM & seasonal reuse": "Reusing seasonal builds, props, mannequins and display kits across stores and seasons instead of commissioning new assets.",
    "Waste diversion": "Segregating waste streams at store level and diverting fit-out, VM and packaging waste from landfill to reuse or recycling.",
    "Logistics optimization": "Shifting freight modes (air → sea), consolidating shipments, and reducing reverse-logistics emissions from returns and take-back.",
    "Packaging circularity": "Reducing packaging mass, using recycled content, and designing for reuse/recycling (including take-back at point of sale).",
    "Modular & adaptable design": "Designing fixtures as interchangeable modules that can be reconfigured across seasons and stores rather than replaced.",
    "Asset longevity & retention": "Extending the service life of fixtures and VM assets through refurbishment, repair, reupholstery, and cross-store transfers.",
}

ACTION_PLANS = {
    "Circular fit-out redesign": {
        "Design for disassembly (screws vs glue)": 0.30,
        "Modular & reconfigurable fixtures": 0.25,
        "Recycled / reclaimed materials": 0.20,
        "Low-carbon material substitution": 0.15,
        "Local / regional sourcing": 0.10,
    },
    "VM & seasonal reuse": {
        "Reusable display structures": 0.30,
        "Standardized kits across stores": 0.25,
        "Refurbishment of props & mannequins": 0.20,
        "Digital signage replacing print": 0.15,
        "Cross-season / cross-city reuse": 0.10,
    },
    "Renewable electricity transition": {
        "Corporate power purchase agreements": 0.40,
        "Unbundled RECs / green tariffs": 0.35,
        "On-site solar generation": 0.15,
        "Landlord renewable provision": 0.10,
    },
    "Energy efficiency (LED/HVAC)": {
        "LED base lighting retrofit": 0.30,
        "LED display & track lighting": 0.25,
        "HVAC controls & scheduling": 0.20,
        "Chiller / AHU equipment upgrades": 0.15,
        "Sub-metering & monitoring": 0.10,
    },
    "Refrigerant management": {
        "Leak detection & preventive maintenance": 0.40,
        "Low-GWP refrigerant transition": 0.40,
        "Equipment replacement cycle": 0.20,
    },
    "Waste diversion": {
        "Segregated recycling streams": 0.35,
        "Take-back schemes (fixtures, packaging)": 0.30,
        "Reuse / donation programmes": 0.20,
        "Composting / energy recovery": 0.15,
    },
    "Logistics optimization": {
        "Modal shift air → sea freight": 0.40,
        "Shipment consolidation & load optimization": 0.25,
        "Reverse logistics network redesign": 0.20,
        "Regional / local supplier proximity": 0.15,
    },
    "Packaging circularity": {
        "Reduce packaging mass": 0.30,
        "Recycled / certified content": 0.30,
        "Reusable packaging (bags, boxes)": 0.25,
        "Take-back at point of sale": 0.15,
    },
    "Modular & adaptable design": {
        "Interchangeable wall & display panels": 0.35,
        "Standard shelving modules": 0.30,
        "Demountable partition systems": 0.25,
        "Flexible display tables": 0.10,
    },
    "Asset longevity & retention": {
        "Fixture refurbishment programme": 0.35,
        "Reupholstery & repair": 0.25,
        "Cross-store fixture transfers": 0.25,
        "Long-term maintenance contracts": 0.15,
    },
}

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

DRIVER_STRUCTURE = {
    "Renewable electricity transition": {
        "activity_type": "Scope 2 — Purchased electricity",
        "areas": {"Boutique electricity": {
            "items": ["Base lighting", "Display lighting", "HVAC", "AV/POS"],
            "weights": {"Base lighting": 0.30, "Display lighting": 0.35, "HVAC": 0.25, "AV/POS": 0.10},
        }},
        "area_weights": {"Boutique electricity": 1.0},
    },
    "Energy efficiency (LED/HVAC)": {
        "activity_type": "Scope 1+2 — Energy efficiency",
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
        "activity_type": "Scope 3 · Cat 2 — Capital goods",
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
        "activity_type": "Scope 3 · Cat 5 — Waste",
        "areas": {
            "Fit-out waste": {"items": ["Timber", "Metal", "Acrylic"], "weights": {"Timber": 0.40, "Metal": 0.35, "Acrylic": 0.25}},
            "VM waste": {"items": ["Props", "Mannequins", "Signage"], "weights": {"Props": 0.45, "Mannequins": 0.30, "Signage": 0.25}},
            "Packaging waste": {"items": ["Cardboard", "Tissue", "Bags"], "weights": {"Cardboard": 0.50, "Tissue": 0.30, "Bags": 0.20}},
        },
        "area_weights": {"Fit-out waste": 0.55, "VM waste": 0.25, "Packaging waste": 0.20},
    },
    "Logistics optimization": {
        "activity_type": "Scope 3 · Cat 4/9 — Transport",
        "areas": {
            "Inbound freight": {"items": ["Sea freight", "Air freight", "Road"], "weights": {"Sea freight": 0.55, "Air freight": 0.30, "Road": 0.15}},
            "Store-to-store transfers": {"items": ["Fixtures", "VM props", "Product"], "weights": {"Fixtures": 0.40, "VM props": 0.30, "Product": 0.30}},
            "Reverse logistics": {"items": ["Returns processing", "Take-back haulage"], "weights": {"Returns processing": 0.60, "Take-back haulage": 0.40}},
        },
        "area_weights": {"Inbound freight": 0.45, "Store-to-store transfers": 0.30, "Reverse logistics": 0.25},
    },
    "Packaging circularity": {
        "activity_type": "Scope 3 · Cat 5/12 — Packaging",
        "areas": {
            "Retail packaging": {"items": ["Shopping bags", "Product boxes", "Tissue"], "weights": {"Shopping bags": 0.50, "Product boxes": 0.30, "Tissue": 0.20}},
            "Delivery packaging": {"items": ["E-commerce boxes", "Fillers", "Tape"], "weights": {"E-commerce boxes": 0.55, "Fillers": 0.25, "Tape": 0.20}},
        },
        "area_weights": {"Retail packaging": 0.60, "Delivery packaging": 0.40},
    },
    "Modular & adaptable design": {
        "activity_type": "Scope 3 · Cat 2 — Capital goods",
        "areas": {
            "Modular fixtures": {"items": ["Interchangeable panels", "Standard shelving modules", "Modular display tables"], "weights": {"Interchangeable panels": 0.40, "Standard shelving modules": 0.35, "Modular display tables": 0.25}},
            "Demountable partitions": {"items": ["Demountable walls", "Movable screens", "Flexible columns"], "weights": {"Demountable walls": 0.50, "Movable screens": 0.30, "Flexible columns": 0.20}},
        },
        "area_weights": {"Modular fixtures": 0.60, "Demountable partitions": 0.40},
    },
    "Asset longevity & retention": {
        "activity_type": "Scope 3 · Cat 2 — Capital goods",
        "areas": {
            "Fixture life extension": {"items": ["Refurbishment", "Reupholstery", "Repair"], "weights": {"Refurbishment": 0.45, "Reupholstery": 0.30, "Repair": 0.25}},
            "Cross-store reuse": {"items": ["Fixture transfers", "VM asset transfer"], "weights": {"Fixture transfers": 0.60, "VM asset transfer": 0.40}},
        },
        "area_weights": {"Fixture life extension": 0.55, "Cross-store reuse": 0.45},
    },
}

# Opportunity matrices — realistic durations and statuses
# Format: (name, cumulative_impact_to_2035, effort_1to5, status, start_year, end_year)
FITOUT_OPPORTUNITIES = [
    ("Design for disassembly (screws, not glue)", 600.0, 4, "Opportunity", 2026, 2035),
    ("Modular millwork design", 450.0, 3, "In progress", 2024, 2032),
    ("Reusable modular partitions", 300.0, 3, "Opportunity", 2026, 2033),
    ("Take-back scheme for fixtures", 250.0, 4, "Opportunity", 2027, 2035),
    ("Reclaimed timber sourcing", 200.0, 2, "Acted", 2022, 2030),
    ("Low-carbon concrete / stone alternatives", 180.0, 3, "Opportunity", 2027, 2034),
    ("Local supplier sourcing (Asia-based mills)", 150.0, 2, "In progress", 2024, 2035),
    ("LED retrofit + controls", 120.0, 1, "Acted", 2022, 2026),
    ("Recyclable mannequins (recycled polystyrene)", 80.0, 1, "Acted", 2023, 2027),
    ("Material passport for top 20 SKUs", 50.0, 2, "Opportunity", 2026, 2029),
]

SEASONAL_OPPORTUNITIES = [
    ("Standardized reusable VM kits", 120.0, 2, "In progress", 2024, 2030),
    ("Multi-city event set reuse", 100.0, 2, "Acted", 2022, 2028),
    ("Recycled polystyrene mannequins", 60.0, 1, "Acted", 2022, 2025),
    ("Digital signage replacing printed graphics", 80.0, 2, "Opportunity", 2026, 2032),
    ("Reusable window display structures", 70.0, 3, "Opportunity", 2027, 2033),
    ("Return-and-refurbish scheme for props", 50.0, 3, "Opportunity", 2027, 2034),
    ("Fabric banner reuse program", 30.0, 1, "In progress", 2024, 2030),
]

RENEWABLE_OPPORTUNITIES = [
    ("Corporate power purchase agreements", 200.0, 3, "In progress", 2024, 2035),
    ("Unbundled RECs / green tariffs", 180.0, 2, "Acted", 2022, 2030),
    ("On-site solar (where viable)", 80.0, 4, "Opportunity", 2027, 2035),
    ("Landlord renewable provision (green lease)", 40.0, 3, "Opportunity", 2026, 2035),
]

ENERGY_EFFICIENCY_OPPORTUNITIES = [
    ("LED base lighting retrofit", 60.0, 1, "Acted", 2022, 2024),
    ("LED display & track lighting", 50.0, 1, "Acted", 2023, 2025),
    ("HVAC controls & scheduling", 40.0, 2, "In progress", 2024, 2028),
    ("Chiller / AHU equipment upgrades", 30.0, 3, "Opportunity", 2026, 2032),
    ("Sub-metering & monitoring", 20.0, 2, "In progress", 2024, 2027),
]

REFRIGERANT_OPPORTUNITIES = [
    ("Leak detection & preventive maintenance", 70.0, 2, "In progress", 2024, 2032),
    ("Low-GWP refrigerant transition (R-32, R-290)", 70.0, 3, "Opportunity", 2026, 2035),
    ("Equipment replacement cycle", 40.0, 3, "Opportunity", 2028, 2035),
]

WASTE_OPPORTUNITIES = [
    ("Fixture take-back & reuse programme", 100.0, 3, "Opportunity", 2026, 2035),
    ("Segregated waste streams at store level", 60.0, 2, "In progress", 2024, 2030),
    ("Mannequin refurbishment scheme", 40.0, 2, "Opportunity", 2027, 2033),
    ("Local recycling partner network", 30.0, 2, "In progress", 2024, 2032),
]

PACKAGING_OPPORTUNITIES = [
    ("Reduce packaging mass (thinner bags, boxes)", 60.0, 1, "In progress", 2024, 2028),
    ("Recycled / FSC-certified content", 50.0, 2, "Acted", 2023, 2027),
    ("Reusable shopping bags / boxes", 40.0, 2, "In progress", 2024, 2030),
    ("Packaging take-back at point of sale", 30.0, 3, "Opportunity", 2026, 2033),
    ("Digital receipts & documentation", 10.0, 1, "Acted", 2022, 2024),
]

MODULAR_OPPORTUNITIES = [
    ("Interchangeable wall / display panels", 180.0, 3, "In progress", 2024, 2032),
    ("Standard shelving modules (cross-store)", 150.0, 2, "Acted", 2023, 2030),
    ("Demountable partition systems", 120.0, 3, "Opportunity", 2026, 2035),
    ("Flexible display tables (configurable)", 60.0, 2, "In progress", 2024, 2030),
    ("Tool-free assembly fixtures", 40.0, 3, "Opportunity", 2027, 2034),
]

LONGEVITY_OPPORTUNITIES = [
    ("Fixture refurbishment programme", 90.0, 2, "In progress", 2024, 2032),
    ("Reupholstery & repair (vs replacement)", 60.0, 2, "Acted", 2022, 2030),
    ("Cross-store fixture transfers", 60.0, 2, "In progress", 2024, 2032),
    ("Long-term maintenance contracts", 40.0, 1, "Acted", 2022, 2028),
    ("Take-back at end of first life", 30.0, 3, "Opportunity", 2027, 2034),
]

LOGISTICS_OPPORTUNITIES = [
    ("Modal shift air → sea freight", 120.0, 4, "Opportunity", 2027, 2035),
    ("Shipment consolidation & load optimization", 80.0, 2, "In progress", 2024, 2030),
    ("Regional / local supplier proximity", 60.0, 2, "Acted", 2022, 2028),
    ("Reverse logistics network redesign", 50.0, 3, "Opportunity", 2026, 2035),
    ("Store-to-store transfer optimization", 40.0, 2, "In progress", 2024, 2030),
    ("Low-carbon last-mile (electric vehicles)", 30.0, 4, "Opportunity", 2028, 2035),
]

# Country rollout lag (years) — positive means later than plan anchor,
# negative means earlier. Applied to initiative start/end.
COUNTRY_ROLLOUT_LAG = {
    "China": -1,
    "Korea": 0,
    "Hong Kong": 1,
    "Singapore": 1,
}

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MONTHLY_PATTERNS = {
    "Energy efficiency (LED/HVAC)": [0.7, 0.7, 0.9, 1.1, 1.3, 1.5, 1.6, 1.5, 1.3, 1.0, 0.8, 0.6],
    "Renewable electricity transition": [0.9, 0.9, 1.0, 1.0, 1.1, 1.2, 1.2, 1.2, 1.1, 1.0, 1.0, 0.9],
    "Refrigerant management": [0.8, 0.8, 0.9, 1.0, 1.2, 1.4, 1.5, 1.4, 1.1, 0.9, 0.8, 0.7],
    "Circular fit-out redesign": [1.0, 0.9, 1.1, 1.2, 1.2, 1.1, 0.9, 1.0, 1.1, 1.2, 1.2, 1.1],
    "VM & seasonal reuse": [1.3, 1.2, 1.4, 1.2, 1.0, 0.9, 0.9, 1.0, 1.2, 1.3, 1.5, 1.3],
    "Waste diversion": [1.1, 1.0, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1, 1.2],
    "Logistics optimization": [0.7, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.1, 1.2, 1.3, 1.5, 1.7],
    "Packaging circularity": [1.0, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.2],
    "Modular & adaptable design": [1.0] * 12,
    "Asset longevity & retention": [1.0] * 12,
}
