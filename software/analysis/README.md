# Analysis

Python scripts for processing raw spectra into first-light line fits and averaging-noise statistics, plus utilities for the waterfall viewer and S-parameter cleanup. Galactic rotation curve extraction is future work, not implemented here (see "What these scripts do NOT do" below).

## Scripts

| Script | Purpose |
|--------|---------|
| `mergen21_hi_analysis.py` | End-to-end reproduction from the raw GNU Radio captures: `mergen21_hi_measurements.csv` (full parameter set), `mergen21_hi_line_parameters.csv` (S/E/W summary: peak %, FWHM, centroid, galactic l/b), `mergen21_data_manifest.csv` (sha256 of every input), `mergen21_hi_derived.json` (scalar results quoted in the manuscript, including the noise-figure arithmetic), and `mergen21_hi_validation.png`. Run with `--root`/`--outdir`. |
| `first_light_and_averaging.py` | Builds the first-light spectra figure and `averaging_noise.csv` (the tau=1/2/4/8 s averaging-noise table for the E1/E2 captures) from the raw captures. Run with `--root`/`--outdir`. |
| `mergen21_waterfall_viewer.py` | Interactive waterfall / spectrum viewer for `.dat` files |
| `sanitize_sps.py` | S-parameter file cleanup utility |
| `wola_window_check.py` | Reproduces the WOLA prototype-filter truncation check. Runs only with GNU Radio installed: the designed taps (`wola_taps_firdes.npy`) are not committed, so the first run designs them with `firdes` and caches them next to the script |

`outputs/VERIFICATION.md` records an independent re-run of `mergen21_hi_analysis.py` and `first_light_and_averaging.py` against this checkout, verified against `reference_outputs/`. See that file for the full comparison and for the offline-IERS caveat on galactic l/b.

## What these scripts do NOT do (future work)

The full calibration pipeline described in earlier drafts of this README (bandpass-ripple correction, gain calibration to K/Jy, and tangent-point rotation-curve extraction) is not implemented. What is released and verified is: line-profile Gaussian fits at 1420.405 MHz for the south/east/west pointings, and an averaging-noise (radiometer) analysis. Rotation-curve extraction needs frequency-axis verification, oscillator calibration, and pointing records not currently in this repository -- see `docs/analysis/PROVENANCE_ADDENDUM.md` for what was withdrawn from an earlier draft of this analysis and why, and `docs/analysis/MISSING_FROM_RELEASE.md` for what a reader will not find in this release.

## Quick Start

```bash
pip install -r ../requirements.txt

# Reproduce the line fits and derived scalars
python3 mergen21_hi_analysis.py --root ../.. --outdir outputs

# Reproduce the first-light figure and averaging-noise table
python3 first_light_and_averaging.py --root ../.. --outdir outputs

# View a spectrum interactively
python3 mergen21_waterfall_viewer.py ../../observations/data/
```

## Calibration Reference

- **Cascade gain:** 39.5 dB +/- 0.5 dB (measured; the VNA cascade file has ~42.5 MHz point spacing and no sample exactly at 1420.405 MHz)
- **System NF:** about 1.5 dB (1.54 dB, cable-corrected gain-method estimate; see `measurements/rf-chain/nf/README.md`)
- **BPF ripple:** ±0.5 dB across 1400–1500 MHz (not yet corrected for in the released analysis scripts)

```python
import numpy as np

rows = np.fromfile(path, dtype=np.float32).reshape(-1, 2048)  # linear power, one row per saved average; channel k is (k - 1024) kHz from the LO
```

## See Also

- Observation data: [`../../observations/`](../../observations/)
- GNU Radio flowgraphs: [`../gnuradio/`](../gnuradio/)
- Simulation reference: [`../../hardware/simulation/`](../../hardware/simulation/)
