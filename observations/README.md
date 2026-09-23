# Observations

First-light hydrogen line (1420.405 MHz) observations from Mergen-21, collected 2026-04-29 from Istanbul, Turkey (~41.0°N, 29.0°E).

## Contents

- `data/` — Raw spectra (`.dat`, NumPy float32) saved by `reciver.grc`
- `plots/` — Waterfall and directional sweep plots (PNG)
- `stellarium_*.png` — Sky reference charts for each pointing direction

## First-Light Session — 2026-04-29

Directional sweeps across the galactic plane.

| File label | Direction |
|------------|-----------|
| `_bati` | West (Batı) |
| `_guney` | South (Güney) |
| `_doggu` / `_Dogu` | East (Doğu) |

## Stellarium Reference Charts

These are sky screenshots taken during the observation session to document where the telescope was pointing.

| File | What it shows |
|------|---------------|
| `stellarium_east.png` | Eastern sky at observation time |
| `stellarium_south.png` | Southern sky |
| `stellarium_west.png` | Western sky |
| `stellarium_high_fov_sweep.png` | Wide FOV showing the full sweep arc |

## Plots

Observation plots are in `plots/`:
- `east.png`, `south.png`, `west.png` — Spectra per direction
- `east_100_integration.png` / `east 100 integration.png` — East direction with 100-sample integration
- `sweeping from east to west.png` — Full sweep waterfall

An earlier plot, `allahyok.png` ("first signal detection attempt"), was removed from the repository in a prior commit and is no longer available.

## Acquisition Settings

Per-file acquisition provenance for the 2026-04-29 session is recorded in [`captures.csv`](captures.csv), derived from the observer's confirmed capture metadata. Summary:

- The west (`_bati`), south (`_guney`), and 05:02:04 east (`_doggu`) pointings, and the sweep (`_180partygirl_500int.dat`), all ran with `integration_time = 1000` on the flowgraph (1.0 s per row).
- Only `..._050450_Dogu_100.dat` used `integration_time = 100` (0.1 s per row); this is the one file whose name correctly states its integration setting.
- The sweep file's name says "500int", but it actually ran with `integration_time = 1000`; the filename is wrong.
- Azimuths were read from two phone compasses at the time of each static pointing. Elevation (roughly 35 degrees) was estimated by the observer and was not logged. The sweep capture has no angle log at all; it moved through pointings manually with pauses and is qualitative only (its azimuth is not recoverable and its effective bandwidth cannot be estimated by row differencing).

In addition to the five captures in `captures.csv`, `data/` contains 21 earlier `.dat` files with no direction suffix (plain `mergen21_spec_20260429_HHMMSS.dat`). These are earlier test and commissioning captures; their acquisition settings were not recorded and they are not included in `captures.csv`.

## Loading the Data

These `.dat` files are the sample SDR recordings distributed with the repository.
A real antenna or SDR is not needed to view them.

```python
import numpy as np

FFT_SIZE = 2048
raw = np.fromfile('data/mergen21_spec_20260429_041703.dat', dtype=np.float32)
spectra = raw[:len(raw) // FFT_SIZE * FFT_SIZE].reshape(-1, FFT_SIZE)
avg_spectrum = spectra.mean(axis=0)   # time-averaged spectrum
```

**Interactive viewer** (run from the repository root):
```bash
python software/analysis/mergen21_waterfall_viewer.py
```

In the viewer: click **Add...**, navigate to `observations/data/`, select one or more `.dat` files, then click **Plot**. Switch the X axis to **Velocity [km/s]** to see the Doppler scale.

See [`docs/lab-manual-04-observe.md`](../docs/lab-manual-04-observe.md) for a step-by-step walkthrough.

## Site

**Location:** Istanbul, Turkey (~41.0°N, 29.0°E)  
**Target:** Galactic plane HI emission (1420.405 MHz)  
**Method:** Tangent-point method for rotation curve extraction
