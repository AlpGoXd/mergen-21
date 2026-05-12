# Observations

First-light hydrogen line (1420.405 MHz) observations from Mergen-21.

## Contents

- `data/` — Raw spectra (`mergen21_spec_YYYYMMDD_HHMMSS[_label].dat`, NumPy float32)
- `plots/` — Waterfall and directional sweep plots (PNG)

## First-Light Session — 2026-04-29

Directional sweeps from Istanbul, Turkey (~41.0°N, 29.0°E).

| File label | Direction |
|------------|-----------|
| `_bati` | West (Batı) |
| `_guney` | South (Güney) |
| `_doggu` / `_Dogu` | East (Doğu) |

## Data Format

`.dat` files are NumPy float32 power spectra saved by `software/gnuradio/reciver.grc`:

```python
import numpy as np
spec = np.fromfile('mergen21_spec_20260429_041703.dat', dtype=np.float32)
```

Visualise with:
```bash
python3 software/analysis/mergen21_waterfall_viewer.py observations/data/
```

## Site

**Location:** Istanbul, Turkey (~41.0°N, 29.0°E)  
**Target:** Galactic plane HI emission (1420.405 MHz)  
**Method:** Tangent-point method for rotation curve extraction
