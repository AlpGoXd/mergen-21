# Antenna Measurements

S11 measurements of the horn antenna under different conditions, listed in chronological order. Each step builds on the previous one. All measurements use the R&S ZNB8.

## Measurement Log (Chronological Order)

| # | Folder | Calibrated | Location | Notes |
|---|--------|-----------|----------|-------|
| 1 | `1_outside_uncalibrated/` | No | Outdoor | First quick test — VNA was not calibrated |
| 2 | `2_outside_calibrated/` | Yes (TOSM) | Outdoor | Calibrated VNA with cal kit, re-measured outdoors |
| 3 | `3_inside_calibrated/` | Yes (TOSM) | Indoor | Brought antenna inside, measured again (same cal) |
| 4 | `4_inside_aluminum_foil/` | Yes (TOSM) | Indoor | Aluminum foil added at E/H-plane merge point to test sealing (photo included) |
| 5 | `5_inside_cleaned_backshort/` | Yes (TOSM) | Indoor | **FINAL** — Cleaned interior with wipes; backshort pin removed and re-inserted. Showed ~-40 dB — cause unknown |

> **Note:** Measurement #5 is the **definitive measurement** representing the antenna as-built.

## Known Manufacturing Defect

The aluminum sheet used for the horn was obtained for free because it was bent by the manufacturer. As a result, the horn walls are **concave in** (bowed inward along the length of the antenna). See [`antenna_photos/`](antenna_photos/) for photo documentation.

This concavity may affect:
- Aperture efficiency (non-planar phase front)
- Gain reduction compared to the ideal horn simulation
- Slight pattern asymmetry

Compare with simulations:
- [`simulation/cst/ideal_horn/`](../../hardware/simulation/cst/ideal_horn/) — Ideal geometry
- [`simulation/cst/assembly_worstcase/`](../../hardware/simulation/cst/assembly_worstcase/) — Worst-case assembly model
