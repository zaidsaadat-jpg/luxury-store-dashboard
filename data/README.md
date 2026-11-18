# Data folder — target schema for real data

Replace `utils/constants.py` with loaders for these CSVs when store-level data is available.

| File | One row per | Columns |
|---|---|---|
| `stores.csv` | Store | store_id, market, format, gia_m2, ownership_tag (Chanel-capex / landlord-capex / shared), lease_green_clause (Y/N) |
| `energy.csv` | Store × month | store_id, month, kwh_tenant, kwh_landlord_disclosed, refrigerant_kg_topup, data_tier |
| `fitout.csv` | Fit-out project | project_id, store_id, completion_year, boq_material_mass_kg, epd_coverage_pct, embodied_kgco2e, data_tier |
| `seasonal.csv` | Store × season | store_id, season, material_mass_kg, reuse_count, avoided_kgco2e, data_tier |
| `waste.csv` | Store × month | store_id, month, waste_kg_by_route (landfill/recycle/reuse), data_tier |
| `circularity.csv` | Store × year | store_id, year, design_for_disassembly_pct, fixture_reuse_pct, recycled_content_pct, material_passport_coverage_pct |

**Data tier rules:** Tier 1 = physical/primary; Tier 2 = spend-based with physical overlay; Tier 3 = modeled benchmark. Never blend tiers in a single unlabeled figure.
