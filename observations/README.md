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
- `allahyok.png` — First signal detection attempt

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
