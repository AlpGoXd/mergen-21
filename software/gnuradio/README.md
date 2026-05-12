# GNU Radio Flowgraphs

Real-time signal acquisition and synthesis flowgraphs for the ADALM-PLUTO SDR, targeting 1420.405 MHz hydrogen line observations.

## Flowgraphs

### Receiver

| File | Purpose | Input | Output |
|------|---------|-------|--------|
| `reciver.grc` / `reciver.py` | Main HI line receiver | PlutoSDR I/Q | Spectrum data (`.dat`) |

### Synthesis / Test (`21cm synth/`)

Test flowgraphs used to validate the analysis pipeline without live RF hardware:

| File | Purpose |
|------|---------|
| `topo1_cw_tone.grc` | Single CW tone at 1420.405 MHz |
| `topo2_single_gaussian.grc` | Gaussian spectral line (simulated HI) |
| `topo3_galaxy_rotation.grc` | Multi-component Gaussian (simulated galactic HI spectrum) |
| `topo3_required_constants.grc` | Physical constants block used by topo3 |
| `fftdemo.grc` | Basic FFT display demo |
| `testingit.grc` | Scratch/test flowgraph |

## Hardware Setup

**Expected signal path:**
```
Antenna (16.9 dBi) → LNA (19.7 dB) → BPF (−0.8 dB) → Amp (20.8 dB) → PlutoSDR
Cascade: ~40 dB gain, 0.75 dB NF
```

**PlutoSDR settings (receiver):**
- Center frequency: 1420.405 MHz
- Sample rate: 2 MSPS (~1 MHz baseband BW)
- RF bandwidth: 20 MHz
- PlutoSDR gain: 0 dB (cascade already provides ~40 dB)

## Installation

```bash
# Ubuntu 22.04
sudo apt install -y gnuradio gr-iio

# Or conda (more reliable)
conda create -n gnuradio -c conda-forge gnuradio=3.10 gr-iio
conda activate gnuradio
```

## Running

```bash
# GUI
gnuradio-companion reciver.grc

# Headless
python3 reciver.py
```

## Observation Workflow

1. Connect antenna → LNA power supply → PlutoSDR → PC
2. Verify PlutoSDR: `usb-devices | grep 0456`
3. Launch `reciver.grc` in GRC
4. Set center frequency to 1420.405 MHz, confirm sample rate 2 MSPS
5. Run; output written to `logs/`

## Output Format

The receiver saves NumPy float32 power spectra (not raw I/Q). Recorded files go to `observations/data/`:

```python
import numpy as np
spec = np.fromfile('../../observations/data/mergen21_spec_20260429_041703.dat', dtype=np.float32)
```

## Troubleshooting

**PlutoSDR not detected:**
```bash
usb-devices | grep 0456
# Try: sudo, USB 2.0 port, reseat cable
```

**gr-iio not found:**
```bash
conda install -c conda-forge gr-iio
```

**Flowgraph freezes:**
- Reduce sample rate to 1 MSPS
- Check USB bandwidth (`dmesg`)

**Flat / noisy spectrum:**
- Verify LDO power supply (±5 V, ±12 V)
- Check SMA connections

## See Also

- [GNU Radio docs](https://www.gnuradio.org/)
- [ADALM-PLUTO quick start](https://wiki.analog.com/university/tools/pluto)
- [gr-iio](https://github.com/analogdevicesinc/gr-iio)
- Analysis pipeline: [`../analysis/`](../analysis/)
- Waterfall viewer: [`../analysis/mergen21_waterfall_viewer.py`](../analysis/mergen21_waterfall_viewer.py)
- Observation data: [`../../observations/`](../../observations/)
