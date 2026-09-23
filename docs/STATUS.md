# Repository Status Matrix

High-level status snapshot for major subsystems.

Last updated: 2026-09-23

| Area | Status | Notes |
|------|--------|-------|
| Hardware (antenna, RF chain, LDO, simulations) | Complete | All under `hardware/`; fully characterized and documented. |
| Measurements (VNA, IP3, NF, antenna) | Complete | All under `measurements/`. |
| Build log | Complete | Photos in `docs/build-log/`; assembly notes in `hardware/antenna/ASSEMBLY.md`. |
| GNU Radio software | Complete | `reciver.grc` (main acquisition) + `21cm synth/` test flowgraphs in `software/gnuradio/`. |
| Analysis software | Complete for first-light; K/Jy calibration and rotation-curve extraction not started | `mergen21_hi_analysis.py` and `first_light_and_averaging.py` reproduce the manuscript's line fits, galactic l/b, and averaging-noise tables (see `software/analysis/outputs/VERIFICATION.md`). Waterfall viewer also in `software/analysis/`. |
| First-light observations | Complete for south/east/west pointings; azimuth sweep withdrawn | Raw spectra in `observations/data/`. The manual azimuth sweep's pointing cannot be recovered and is not part of the released results; see `docs/analysis/PROVENANCE_ADDENDUM.md`. |
| Rotation curve (tangent-point method) | Not started | Future work; needs frequency-axis verification, oscillator calibration, and pointing records not yet in place. |
| Open-source release prep | In progress | Final cleanup ongoing. |

## Notes

- This matrix is intentionally simple and is the single source of truth for completion status.
- For subsystem details, follow each folder README.
