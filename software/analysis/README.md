# Analysis

Python scripts for processing raw spectra into calibrated plots and galactic rotation curve estimates.

## Scripts

| Script | Purpose |
|--------|---------|
| `mergen21_waterfall_viewer.py` | Interactive waterfall / spectrum viewer for `.dat` files |
| `sanitize_sps.py` | S-parameter file cleanup utility |

## Planned Pipeline

```
Raw spectra (*.dat)
    │
[1] Spectral estimation (Welch PSD)
    │
[2] Bandpass correction (remove BPF ripple)
    │
[3] Gain calibration (convert to K or Jy)
    │
[4] Line profile extraction (Gaussian fit @ 1420.405 MHz)
    │
[5] Rotation curve analysis (tangent-point method)
    │
Output: v_LSR, T_B, plots
```

## Quick Start

```bash
pip install -r ../requirements.txt

# View a spectrum
python3 mergen21_waterfall_viewer.py ../../observations/data/
```

## Calibration Reference

- **Cascade gain:** 39.7 dB (measured @ 1.42 GHz)
- **System NF:** 0.75 dB → T_sys ≈ 30–40 K near zenith
- **BPF ripple:** ±0.5 dB across 1400–1500 MHz (correct via S21 polynomial fit)

```python
import numpy as np
from scipy import signal

iq = np.fromfile('obs.dat', dtype=np.float32)
f, pxx = signal.welch(iq, fs=2e6, nperseg=1024)
pxx_db = 10 * np.log10(pxx)
```

## See Also

- Observation data: [`../../observations/`](../../observations/)
- GNU Radio flowgraphs: [`../gnuradio/`](../gnuradio/)
- Simulation reference: [`../../hardware/simulation/`](../../hardware/simulation/)
