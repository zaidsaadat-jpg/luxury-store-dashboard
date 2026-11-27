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
BASELINE_TOTAL_TCO2E = 10000.0

PLAN_TRAJECTORY = {
    2021: 10000.0,
    2025: 7500.0,
    2030: 4000.0,
    2035: 2000.0,
}

INITIATIVES = {
    "Energy efficiency (LED/HVAC)": {
        2022: 100, 2023: 200, 2024: 250, 2025: 200, 2026: 100, 2027: 50,
    },
    "Renewable electricity transition": {
        2023: 30, 2024: 100, 2025: 200, 2026: 300, 2027: 300, 2028: 200, 2029: 70,
    },
    "Refrigerant management": {
        2022: 20, 2023: 50, 2024: 80, 2025: 120, 2026: 120, 2027: 80, 2028: 30,
    },
    "Circular fit-out redesign": {
        2023: 20, 2024: 70, 2025: 150, 2026: 220, 2027: 280, 2028: 250,
        2029: 200, 2030: 150, 2031: 100, 2032: 80, 2033: 60, 2034: 50, 2035: 40,
    },
    "VM & seasonal reuse": {
        2022: 20, 2023: 40, 2024: 60, 2025: 80, 2026: 100, 2027: 120,
        2028: 120, 2029: 120, 2030: 80, 2031: 60, 2032: 50, 2033: 40, 2034: 30, 2035: 20,
    },
    "Waste diversion": {
        2023: 30, 2024: 50, 2025: 60, 2026: 50, 2027: 30,
    },
    "Logistics optimization": {
        2024: 20, 2025: 40, 2026: 60, 2027: 90, 2028: 100, 2029: 100,
        2030: 90, 2031: 80, 2032: 70, 2033: 60, 2034: 50, 2035: 40,
    },
    "Packaging circularity": {
        2023: 10, 2024: 30, 2025: 50, 2026: 60, 2027: 70, 2028: 60,
        2029: 50, 2030: 40, 2031: 30, 2032: 20, 2033: 15, 2034: 10, 2035: 5,
    },
    "Modular & adaptable design": {
        2024: 10, 2025: 30, 2026: 60, 2027: 90, 2028: 110, 2029: 120,
        2030: 110, 2031: 90, 2032: 70, 2033: 50, 2034: 40, 2035: 30,
    },
    "Asset longevity & retention": {
        2022: 40, 2023: 60, 2024: 60, 2025: 60, 2026: 60, 2027: 60,
        2028: 50, 2029: 50, 2030: 40, 2031: 30, 2032: 25, 2033: 20, 2034: 15, 2035: 10,
    },
}

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

# ============================================================
# Strategy / action plan attribution per driver
# Each driver's total is split across strategic levers by weight.
# Weights are modeled planning assumptions — a strategy can touch
# multiple areas of activity, so this is an attribution, not a
# strict hierarchy split.
# ============================================================
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
        "areas": {
            "Boutique electricity": {
                "items": ["Base lighting", "Display lighting", "HVAC", "AV/POS"],
                "weights": {"Base lighting": 0.30, "Display lighting": 0.35, "HVAC": 0.25, "AV/POS": 0.10},
            },
        },
        "area_weights": {"Boutique electricity": 1.0},
    },
    "Energy efficiency (LED/HVAC)": {
        "activity_type": "Scope 1+2 — Energy efficiency",
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
        "activity_type": "Scope 3 · Cat 2 — Capital goods",
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
        "activity_type": "Scope 3 · Cat 5 — Waste",
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
    "Logistics optimization": {
        "activity_type": "Scope 3 · Cat 4/9 — Transport",
        "areas": {
            "Inbound freight": {
                "items": ["Sea freight", "Air freight", "Road"],
                "weights": {"Sea freight": 0.55, "Air freight": 0.30, "Road": 0.15},
            },
            "Store-to-store transfers": {
                "items": ["Fixtures", "VM props", "Product"],
                "weights": {"Fixtures": 0.40, "VM props": 0.30, "Product": 0.30},
            },
            "Reverse logistics": {
                "items": ["Returns processing", "Take-back haulage"],
                "weights": {"Returns processing": 0.60, "Take-back haulage": 0.40},
            },
        },
        "area_weights": {"Inbound freight": 0.45, "Store-to-store transfers": 0.30, "Reverse logistics": 0.25},
    },
    "Packaging circularity": {
        "activity_type": "Scope 3 · Cat 5/12 — Packaging",
        "areas": {
            "Retail packaging": {
                "items": ["Shopping bags", "Product boxes", "Tissue"],
                "weights": {"Shopping bags": 0.50, "Product boxes": 0.30, "Tissue": 0.20},
            },
            "Delivery packaging": {
                "items": ["E-commerce boxes", "Fillers", "Tape"],
                "weights": {"E-commerce boxes": 0.55, "Fillers": 0.25, "Tape": 0.20},
            },
        },
        "area_weights": {"Retail packaging": 0.60, "Delivery packaging": 0.40},
    },
    "Modular & adaptable design": {
        "activity_type": "Scope 3 · Cat 2 — Capital goods",
        "areas": {
            "Modular fixtures": {
                "items": ["Interchangeable panels", "Standard shelving modules", "Modular display tables"],
                "weights": {"Interchangeable panels": 0.40, "Standard shelving modules": 0.35, "Modular display tables": 0.25},
            },
            "Demountable partitions": {
                "items": ["Demountable walls", "Movable screens", "Flexible columns"],
                "weights": {"Demountable walls": 0.50, "Movable screens": 0.30, "Flexible columns": 0.20},
            },
        },
        "area_weights": {"Modular fixtures": 0.60, "Demountable partitions": 0.40},
    },
    "Asset longevity & retention": {
        "activity_type": "Scope 3 · Cat 2 — Capital goods",
        "areas": {
            "Fixture life extension": {
                "items": ["Refurbishment", "Reupholstery", "Repair"],
                "weights": {"Refurbishment": 0.45, "Reupholstery": 0.30, "Repair": 0.25},
            },
            "Cross-store reuse": {
                "items": ["Fixture transfers", "VM asset transfer"],
                "weights": {"Fixture transfers": 0.60, "VM asset transfer": 0.40},
            },
        },
        "area_weights": {"Fixture life extension": 0.55, "Cross-store reuse": 0.45},
    },
}

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

FITOUT_OPPORTUNITIES = [
    ("Design for disassembly (screws, not glue)", 600.0, 4, "Opportunity"),
    ("Modular millwork design", 450.0, 3, "In progress"),
    ("Reusable modular partitions", 300.0, 3, "Opportunity"),
    ("Take-back scheme for fixtures", 250.0, 4, "Opportunity"),
    ("Reclaimed timber sourcing", 200.0, 2, "Acted"),
    ("Low-carbon concrete / stone alternatives", 180.0, 3, "Opportunity"),
    ("Local supplier sourcing (Asia-based mills)", 150.0, 2, "In progress"),
    ("LED retrofit + controls", 120.0, 1, "Acted"),
    ("Recyclable mannequins (recycled polystyrene)", 80.0, 1, "Acted"),
    ("Material passport for top 20 SKUs", 50.0, 2, "Opportunity"),
]

SEASONAL_OPPORTUNITIES = [
    ("Standardized reusable VM kits", 120.0, 2, "In progress"),
    ("Multi-city event set reuse", 100.0, 2, "Acted"),
    ("Recycled polystyrene mannequins", 60.0, 1, "Acted"),
    ("Digital signage replacing printed graphics", 80.0, 2, "Opportunity"),
    ("Reusable window display structures", 70.0, 3, "Opportunity"),
    ("Return-and-refurbish scheme for props", 50.0, 3, "Opportunity"),
    ("Fabric banner reuse program", 30.0, 1, "In progress"),
]

RENEWABLE_OPPORTUNITIES = [
    ("Corporate power purchase agreements", 200.0, 3, "In progress"),
    ("Unbundled RECs / green tariffs", 180.0, 2, "Acted"),
    ("On-site solar (where viable)", 80.0, 4, "Opportunity"),
    ("Landlord renewable provision (green lease)", 40.0, 3, "Opportunity"),
]

ENERGY_EFFICIENCY_OPPORTUNITIES = [
    ("LED base lighting retrofit", 60.0, 1, "Acted"),
    ("LED display & track lighting", 50.0, 1, "Acted"),
    ("HVAC controls & scheduling", 40.0, 2, "In progress"),
    ("Chiller / AHU equipment upgrades", 30.0, 3, "Opportunity"),
    ("Sub-metering & monitoring", 20.0, 2, "In progress"),
]

REFRIGERANT_OPPORTUNITIES = [
    ("Leak detection & preventive maintenance", 70.0, 2, "In progress"),
    ("Low-GWP refrigerant transition (R-32, R-290)", 70.0, 3, "Opportunity"),
    ("Equipment replacement cycle", 40.0, 3, "Opportunity"),
]

WASTE_OPPORTUNITIES = [
    ("Fixture take-back & reuse programme", 100.0, 3, "Opportunity"),
    ("Segregated waste streams at store level", 60.0, 2, "In progress"),
    ("Mannequin refurbishment scheme", 40.0, 2, "Opportunity"),
    ("Local recycling partner network", 30.0, 2, "In progress"),
]

PACKAGING_OPPORTUNITIES = [
    ("Reduce packaging mass (thinner bags, boxes)", 60.0, 1, "In progress"),
    ("Recycled / FSC-certified content", 50.0, 2, "Acted"),
    ("Reusable shopping bags / boxes", 40.0, 2, "In progress"),
    ("Packaging take-back at point of sale", 30.0, 3, "Opportunity"),
    ("Digital receipts & documentation", 10.0, 1, "Acted"),
]

MODULAR_OPPORTUNITIES = [
    ("Interchangeable wall / display panels", 180.0, 3, "In progress"),
    ("Standard shelving modules (cross-store)", 150.0, 2, "Acted"),
    ("Demountable partition systems", 120.0, 3, "Opportunity"),
    ("Flexible display tables (configurable)", 60.0, 2, "In progress"),
    ("Tool-free assembly fixtures", 40.0, 3, "Opportunity"),
]

LONGEVITY_OPPORTUNITIES = [
    ("Fixture refurbishment programme", 90.0, 2, "In progress"),
    ("Reupholstery & repair (vs replacement)", 60.0, 2, "Acted"),
    ("Cross-store fixture transfers", 60.0, 2, "In progress"),
    ("Long-term maintenance contracts", 40.0, 1, "Acted"),
    ("Take-back at end of first life", 30.0, 3, "Opportunity"),
]

LOGISTICS_OPPORTUNITIES = [
    ("Modal shift air → sea freight", 120.0, 4, "Opportunity"),
    ("Shipment consolidation & load optimization", 80.0, 2, "In progress"),
    ("Regional / local supplier proximity", 60.0, 2, "Acted"),
    ("Reverse logistics network redesign", 50.0, 3, "Opportunity"),
    ("Store-to-store transfer optimization", 40.0, 2, "In progress"),
    ("Low-carbon last-mile (electric vehicles)", 30.0, 4, "Opportunity"),
]

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
