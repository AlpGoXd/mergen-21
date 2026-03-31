# Observation Analysis Pipeline

Python scripts for processing raw I/Q data from the ADALM-PLUTO SDR into calibrated spectra and galactic rotation curve estimates.

## Current Repo State

The `scripts/` and `notebooks/` directories are currently scaffolding-only in this repo snapshot (placeholder files committed). The pipeline layout below reflects the intended software structure and active development plan.

## Data Flow

```
Raw I/Q (*.c64)
    |
[1] Spectral estimation (Welch PSD)
    |
[2] Bandpass correction (remove filter ripple)
    |
[3] Gain calibration (absolute power in K or Jy)
    |
[4] Line profile extraction (Gaussian fit around 1420.405 MHz)
    |
[5] Rotation curve analysis
    |
Output: v_LSR, T_B, plots
```

## Scripts

Planned script set (to be committed):

| Script | Input | Output | Purpose |
|--------|-------|--------|---------|
| `load_c64.py` | `*.c64` file | NumPy array (I/Q) | C64 file loader (utility) |
| `estimate_psd.py` | I/Q array | PSD (dB) | Welch's method spectrogram |
| `calibrate_gain.py` | PSD (dB) | PSD (K or Jy) | Convert to brightness temperature |
| `extract_line_profile.py` | Calibrated PSD | Line width, peak, center | HI 21 cm line fitting |
| `rotation_curve.py` | Multiple observations (different l, b) | Rotation curve (v, R) | Galactic dynamics analysis |

## Directory Structure

```
analysis/
├── README.md          # This file
├── scripts/           # Analysis scripts
├── notebooks/         # Jupyter notebooks (future)
└── utils/             # Shared utility modules
```

## Quick Start

```bash
# Prerequisites
pip install -r ../requirements.txt

# Process a single observation
python3 scripts/estimate_psd.py ../../observations/data/20260401_1430_l030_b00.c64
python3 scripts/calibrate_gain.py psd_output.npy --reference-temperature 35  # K
python3 scripts/extract_line_profile.py psd_calibrated.npy --plot
```

## Calibration Details

### Gain Calibration

Converting measured power (dB) to brightness temperature (K):

```
T_B (K) = T_sys * (P_measured - P_reference) / (G_cascade)
```

where:
- `T_sys` ~ 30--40 K (cascade NF 0.75 dB + atmosphere + ground)
- `G_cascade` ~ 39.7 dB (measured @ 1.42 GHz)
- `P_reference` ~ -150 dBm (system noise floor under good conditions)

### Bandpass Correction

The BPF (ZX75BP-1450-S+) has ripple +/-0.5 dB across 1400--1500 MHz.
Correct by dividing measured PSD by the filter's S21 response (polynomial fit).

## Example: Full Processing

```python
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# 1. Load data
iq = np.fromfile('observation.c64', dtype=np.complex64)

# 2. Compute PSD (Welch)
f, pxx = signal.welch(iq, fs=2e6, nperseg=1024, nfft=2048)

# 3. Convert to dB
pxx_db = 10 * np.log10(pxx)

# 4. Shift to center at 1420.405 MHz (accounting for LO offset)
f_shifted = f - 1e6  # Assume 1 MHz DC offset in baseband

# 5. Find HI line (should be bright feature near 0 Hz)
hi_idx = np.where((f_shifted > -0.5e6) & (f_shifted < 0.5e6))[0]

# 6. Fit Gaussian to line profile
from scipy.optimize import curve_fit

def gauss(x, mu, sigma, amp, offset):
    return amp * np.exp(-(x - mu)**2 / (2 * sigma**2)) + offset

popt, _ = curve_fit(gauss, f[hi_idx], pxx_db[hi_idx],
                     p0=[0, 50e3, 10, np.min(pxx_db[hi_idx])])
mu, sigma, amp, offset = popt

print(f"Line center: {mu:.2e} Hz")
print(f"Line width (sigma): {sigma:.2e} Hz ({sigma / 1420.405e6 * 3e5:.1f} km/s)")

# 7. Plot
plt.figure(figsize=(12, 6))
plt.semilogy(f_shifted / 1e3, np.sqrt(pxx), 'b-', label='Measured')
plt.semilogy(f_shifted[hi_idx] / 1e3, gauss(f[hi_idx], *popt), 'r--', label='Gaussian fit')
plt.xlabel('Frequency offset (kHz)')
plt.ylabel('Power (sqrt(PSD))')
plt.title('HI 21 cm Line Profile')
plt.legend()
plt.grid(True)
plt.savefig('hi_line_profile.png', dpi=150)
plt.show()
```

## Rotation Curve Extraction

After collecting observations at multiple galactic longitudes (l = 30 deg, 60 deg, 90 deg, 120 deg, etc.):

1. Extract line center velocity & brightness for each (l, b) position
2. Apply galactic coordinates transformation (galactocentric distance vs. velocity)
3. Fit circular + spiral density wave rotation curve model
4. Compare with published models (e.g., APOGEE, Gaia + Hipparcos)

See `scripts/rotation_curve.py` for full implementation.

## Assumptions & Limitations

- **Gain calibration:** Assumes 39.7 dB cascade gain is stable (verify periodically with known source)
- **Temperature:** T_sys estimated from cascade NF; will vary with sky position (zenith 25 K; horizon 60+ K)
- **RFI:** Istanbul urban environment -> significant interference expected (need flagging)
- **Beam:** 22--25 deg beamwidth limits spatial resolution (~1.5 deg at equator)

## Future Improvements

- [ ] Real-time RFI flagging (spectral kurtosis)
- [ ] Multiple observations co-addition (improve S/N)
- [ ] Dual-pol calibration (Faraday rotation studies)
- [ ] Automated frequency-domain normalization

## See Also

- Observations data: [`../../observations/`](../../observations/)
- GNU Radio flowgraphs: [`../gnuradio/`](../gnuradio/)
- Simulation & calibration reference: [`../../hardware/simulation/`](../../hardware/simulation/)
