# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Mergen-21: a low-cost 21 cm (1420.405 MHz) hydrogen-line radio telescope, built as an EE graduation project (Ozyegin University). This is primarily a **hardware/RF documentation repo** — CAD, S-parameters, datasheets, measurement data, lab manuals — with a thin Python/GNU Radio software layer for acquisition and analysis. Most files are not code; treat READMEs under each top-level folder as authoritative for that subsystem before assuming structure.

## Commands

```bash
# Install analysis/software dependencies
pip install -r software/requirements.txt

# View recorded spectra (no SDR/hardware needed)
python software/analysis/mergen21_waterfall_viewer.py
# then in the GUI: Add... -> pick a .dat from observations/data/ -> X axis = Velocity [km/s] -> Plot

# GNU Radio (only for live acquisition; requires gnuradio 3.10+ and gr-iio for PlutoSDR)
gnuradio-companion software/gnuradio/receiver.grc     # GUI edit
python3 software/gnuradio/receiver.py                 # headless run
```

There is no build/lint/test suite — this is a small collection of standalone scripts and `.grc` flowgraphs, not a package.

## Architecture / data flow

Signal path: **Horn antenna → LNA (ZX60-P162LN+) → bandpass filter (ZX75BP-1450-S+) → 2nd amp (ZX60-V63+) → ADALM-PLUTO SDR → GNU Radio → `.dat` files → Python analysis**. Cascade is 39.5 dB +/- 0.5 dB gain, about 1.5 dB NF (cable-corrected; measured, see `measurements/rf-chain/nf/README.md`).

- `software/gnuradio/receiver.grc` / `receiver.py` — the real acquisition flowgraph (PlutoSDR I/Q in, power-spectrum `.dat` out via NumPy float32). `receiver.py` is *generated from* the `.grc` file by GNU Radio Companion — edit the `.grc`, not the `.py`, unless doing a quick headless tweak, and regenerate to keep them in sync.
- `software/gnuradio/21cm synth/` — synthetic test flowgraphs (CW tone, Gaussian line, multi-component galaxy rotation) used to validate the analysis pipeline without live RF hardware. Same generated-`.py`-from-`.grc` relationship applies (e.g. `topo2_single_gaussian.grc` / `.py`).
- `software/analysis/mergen21_waterfall_viewer.py` — standalone Tkinter+matplotlib GUI. Auto-detects acquisition parameters (LO freq, sample rate, FFT size, integration time) by parsing tokens out of `.dat` filenames (see `parse_filename_params`); defaults match the flowgraph (`DEFAULT_LO_FREQ = 1420405000`, `DEFAULT_SAMP_RATE = 2048000`, `DEFAULT_FFT_SIZE = 2048`). Files are memory-mapped and decimated for large waterfalls (`MAX_WATERFALL_ROWS = 2500`).
- `software/analysis/sanitize_sps.py` — S-parameter file cleanup utility for VNA exports.
- `software/analysis/mergen21_hi_analysis.py` and `software/analysis/first_light_and_averaging.py` reproduce the manuscript's line fits, averaging-noise tables, and derived scalars from the raw captures (see `software/analysis/outputs/VERIFICATION.md`). Gain calibration to K/Jy and tangent-point rotation-curve extraction are future work, not yet implemented — see `software/analysis/README.md` and `docs/analysis/PROVENANCE_ADDENDUM.md`.
- `observations/data/*.dat` — raw recorded power spectra, NumPy float32, read with `np.fromfile(path, dtype=np.float32)`. Filenames encode timestamp and sometimes direction (e.g. `..._050450_Dogu_100.dat`, `Dogu` = east in Turkish).
- `hardware/`, `measurements/` — CAD (Inventor, STEP), EM sim exports (CST, AWR), Altium/Gerbers for the LDO board, and lab measurement data (VNA/NF/IP3). These are reference artifacts, not something Claude will typically edit; consult the relevant subfolder README for what each file is before touching it.
- `docs/lab-manual-0{1..4}-*.md` — the four-phase project curriculum (simulate → build → measure → observe); useful context for *why* a hardware choice was made.
- `docs/STATUS.md` — single source of truth for what's done vs. in progress per subsystem.

## Conventions

- Commit message categories used in this repo: `[docs]`, `[software]`, `[hardware]`, `[measurement]`, `[fix]`.
- Licensing differs by content type — hardware is CERN-OHL-S v2, software is GPL-3.0, docs/photos are CC BY-SA 4.0. Keep new files consistent with whichever license covers their directory (see README "Licensing" section).
