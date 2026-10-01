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
Antenna (16.9 dBi) → LNA (19.24 dB) → BPF (−1.73 dB) → Amp (20.24 dB) → PlutoSDR   [VNA, 1420.405 MHz]
Cascade: 39.52 dB gain (VNA), ~1.5 dB NF (cable-corrected)
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

## Simulated HI-Line Injector

`reciver.grc` also contains a simulated hydrogen-line transmit chain (`tx_noise` -> `tx_lpf` -> `tx_rotator` -> `iio_pluto_sink_0`) used to inject a synthetic Gaussian line for pipeline testing. All four blocks are saved with `state: disabled` in the flowgraph. The RX Pluto (`pluto_rx`, `uri: ip:192.168.10.1`) and the TX Pluto (`iio_pluto_sink_0`, `uri: ip:192.168.20.1`) are configured with different device URIs, so this is a loopback/self-test path that requires a second physical PlutoSDR; it is not a path that could inject into a live RX capture through the same device. This does not by itself establish whether the injector was disabled during any particular observing session.

TODO(Alp): confirm injector was disabled during all 2026-04-29 captures

## Known issue: truncated WOLA prototype filter

The flowgraph builds an 8-branch WOLA/PFB channelizer. The prototype filter is designed with:

```
firdes.low_pass(1.0, samp_rate, samp_rate/(4*fft_size), samp_rate/(4*fft_size), window.WIN_KAISER, beta)
```

with `samp_rate = 2048000`, `fft_size = 2048`, `beta = 8.6`. This call returns 32,299 taps in total. However, the 8 channelizer branches (the `blocks_multiply_const_vxx_*` blocks) only consume `kaiser_window[0:8*fft_size]`, i.e. the first 16,384 taps. The effective analysis window used by the channelizer is therefore truncated well before the filter's natural end, cutting it off just past its peak rather than using the full symmetric taper.

A reproducible check for this (32,299 designed vs. 16,384 used) is at `software/analysis/wola_window_check.py`. As of this writing, `software/analysis/wola_taps_firdes.npy` (the committed reference taps needed by that script) had not yet been added to the repository, so verifying the tap counts numerically requires a working GNU Radio 3.10 installation to regenerate the taps; if `wola_taps_firdes.npy` has since been committed, `wola_window_check.py` can be run directly without GNU Radio.

## See Also

- [GNU Radio docs](https://www.gnuradio.org/)
- [ADALM-PLUTO quick start](https://wiki.analog.com/university/tools/pluto)
- [gr-iio](https://github.com/analogdevicesinc/gr-iio)
- Analysis pipeline: [`../analysis/`](../analysis/)
- Waterfall viewer: [`../analysis/mergen21_waterfall_viewer.py`](../analysis/mergen21_waterfall_viewer.py)
- Observation data: [`../../observations/`](../../observations/)
