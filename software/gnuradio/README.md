# GNU Radio Flowgraphs

Real-time signal acquisition for the ADALM-PLUTO SDR targeting 1420.405 MHz hydrogen line observations.

## Current Repo State

The `flowgraphs/` directory is currently scaffolding-only in this repo snapshot (placeholder file committed). The flowgraphs listed below are planned/working locally and will be committed after cleanup.

## Flowgraphs Available

| File | Purpose | Input | Output | Status |
|------|---------|-------|--------|--------|
| `acquisition_1ch.grc` | Single-channel HI receiver | PlutoSDR I/Q | C64 file sink | Planned commit |
| `acquisition_1ch_nodc.grc` | Single-channel (DC-blocked) | PlutoSDR I/Q | C64 file sink | Planned commit |
| `[future] acquisition_dual.grc` | Dual-channel (future) | PlutoSDR I/Q | C64 files | Planned |

## Hardware Setup

1. **ADALM-PLUTO SDR**
   - USB connection to host PC
   - No external power required (USB-powered)
   - Typical USB 3.0 bandwidth limit: 110 MSPS

2. **Expected signal path:**
   ```
   Antenna (16.9 dBi) -> LNA (19.7 dB) -> BPF (-0.8 dB) -> Amp (20.8 dB) -> PlutoSDR
   Expected: ~40 dB cascade gain + 0.75 dB NF
   ```

3. **Typical GNU Radio settings**
   - Frequency: 1420.405 MHz
   - Sample rate: 2 MSPS (Nyquist limit -> ~1 MHz baseband BW)
   - Receiver gain (PlutoSDR): 0--73 dB manual (use 0 dB -- cascade already provides 40 dB)
   - RF bandwidth: 20 MHz (capture full HI line + some bandwidth for search)

## Installation & Setup

### Prerequisites

```bash
# Ubuntu 22.04 (or similar)
sudo apt update
sudo apt install -y gnuradio gr-iio python3-pip

# Or use conda (more reliable for GNU Radio)
conda create -n gnuradio -c conda-forge gnuradio=3.10
conda activate gnuradio
```

### Run a Flowgraph

```bash
# Method 1: GUI (interactive)
gnuradio-companion acquisition_1ch.grc

# Method 2: Headless (automated)
grcc -d . acquisition_1ch.grc
python3 acquisition_1ch.py
```

## Typical Observation Workflow

1. **Prep:** Connect antenna, LDO power supply, and PlutoSDR
2. **Verify hardware:** `usb-devices | grep 0456` (should show Analog Devices)
3. **Run flowgraph:**
   ```bash
   gnuradio-companion acquisition_1ch.grc
   ```
4. **Set parameters in GRC (GUI):**
   - Frequency: 1420.405 MHz (or scan range in future multi-frequency version)
   - Duration: Set file sink to close after N samples (e.g., 10 seconds @ 2 MSPS = 20M samples)
   - Output file: `20260401_1430_l030_b00.c64`
5. **Start recording:** Click "Execute" in GRC toolbar
6. **Monitor:** Should see baseband IQ waterfall; HI line appears as bright feature ~+/-0.5 MHz from DC

## File Formats

**C64 format** (PlutoSDR native, GNU Radio File Sink export):
- Complex 32-bit float interleaved (IQIQIQ...)
- File extension: `.c64`
- Read with: `numpy.fromfile('file.c64', dtype=np.complex64)`

Example Python:
```python
import numpy as np

# Load C64 file
iq_data = np.fromfile('observation.c64', dtype=np.complex64)
print(f"Loaded {len(iq_data)} samples")

# Convert to power spectrum
psd = np.abs(iq_data)**2
```

## Directory Structure

```
gnuradio/
├── README.md          # This file
├── flowgraphs/        # GRC flowgraph files (.grc)
└── examples/          # Example scripts and configurations
```

## Troubleshooting

### PlutoSDR not detected
```bash
usb-devices | grep 0456
# If nothing: try sudo, check USB 2.0 vs. 3.0 port, reseat cable
```

### gr-iio not found
```bash
# Rebuild GNU Radio from source or use conda
conda install -c conda-forge gr-iio
```

### Flowgraph freezes during execute
- Reduce sample rate (try 1 MSPS instead of 2)
- Check USB bandwidth saturation (run `dmesg` for errors)
- Increase file sink buffer size

### Noisy or flat spectrum
- Verify RF chain power supply (-5V, -12V present?)
- Check antenna connection (SMA connector contact)
- Try known-good 1 MHz test signal from vector signal generator to verify chain

## See Also

- GNU Radio documentation: https://www.gnuradio.org/
- ADALM-PLUTO quick start: https://wiki.analog.com/university/tools/pluto
- gr-iio blocks: https://github.com/analogdevicesinc/gr-iio

## Next Steps

After acquiring data, proceed to [`../analysis/`](../analysis/) for calibration & spectral analysis.
