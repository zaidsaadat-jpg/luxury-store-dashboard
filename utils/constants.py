"""
Modeled assumptions for the first-draft dashboard.
ALL VALUES ARE TIER 3 ESTIMATES FROM PUBLIC BENCHMARKS.
Replace this module with CSV loaders when store-level data is available.
"""

MARKETS = ["Hong Kong", "Singapore", "Korea", "China"]

# Store counts (modeled from public boutique listings)
STORE_COUNTS = {
    "Hong Kong": 8,
    "Singapore": 3,
    "Korea": 8,
    "China": 18,
}

# Average boutique GIA (m²)
AVG_GIA_M2 = 600

# Grid emission factors (kgCO2e/kWh, location-based, 2025 public)
GRID_FACTORS = {
    "Hong Kong": 0.79,
    "Singapore": 0.50,
    "Korea": 0.52,
    "China": 0.53,
}

# Energy intensity (kWh/m²/yr)
ENERGY_INTENSITY = 250

# Refrigerant top-up (kg HFC per store per year) and GWP (R-410A equivalent)
REFRIGERANT_KG_PER_STORE = 2.5
REFRIGERANT_GWP = 1430

# Fit-out embodied carbon (kgCO2e/m², A1–A5) and renovation cycle (years)
FITOUT_INTENSITY = 850
RENOVATION_CYCLE = 5

# Seasonal / VM intensity (kgCO2e/m² selling area/yr)
SEASONAL_INTENSITY = 40
SELLING_AREA_RATIO = 0.70

# Fit-out waste (kg/m² per renovation) and mixed-waste emission factor (tCO2e/tonne)
FITOUT_WASTE_INTENSITY = 35
MIXED_WASTE_EF_T_PER_TONNE = 0.35

# Waste diversion baseline
DIVERSION_RATE = 0.60

# Circularity baselines (0–1)
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

# Chanel Mission 1.5 / Net-Zero 2040 targets (baseline framework)
BASE_YEAR = 2021
TARGET_2030_SCOPE12 = -0.50
TARGET_2030_SCOPE3 = -0.42
TARGET_2040_ALL = -0.90
