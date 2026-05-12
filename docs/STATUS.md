# Repository Status Matrix

High-level status snapshot for major subsystems.

Last updated: 2026-05-12

| Area | Status | Notes |
|------|--------|-------|
| Hardware (antenna, RF chain, LDO, simulations) | Complete | All under `hardware/`; fully characterized and documented. |
| Measurements (VNA, IP3, NF, antenna) | Complete | All under `measurements/`. |
| Build log | Complete | Photos in `docs/build-log/`; assembly notes in `hardware/antenna/ASSEMBLY.md`. |
| GNU Radio software | Complete | `reciver.grc` (main acquisition) + `21cm synth/` test flowgraphs in `software/gnuradio/`. |
| Analysis software | In progress | Waterfall viewer in `software/python-scripts/`; full calibration pipeline in development. |
| First-light observations | Complete | Raw spectra + directional sweeps from 2026-04-29 in `software/gnuradio/logs/`. |
| Observations (science-grade) | In progress | Calibrated data population pending; folder structure in `observations/`. |
| Open-source release prep | In progress | Final cleanup ongoing. |

## Notes

- This matrix is intentionally simple and is the single source of truth for completion status.
- For subsystem details, follow each folder README.
