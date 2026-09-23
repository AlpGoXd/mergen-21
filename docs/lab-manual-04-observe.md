# Lab Manual 4: Observe

**Topic:** Setting up the software receiver, making hydrogen line observations, and analyzing the data  
**Estimated time:** 2 hours (software only with example data) or 4–6 hours (with real hardware)  
**Prerequisites:** Python 3.8+, NumPy, Matplotlib installed; GNU Radio 3.10+ for live acquisition

---

## Learning Objectives

After completing this lab, students will be able to:

1. Install and run the GNU Radio receiver flowgraph.
2. Configure the ADALM-PLUTO SDR for hydrogen line reception.
3. Record spectral data and verify that 21 cm emission is detected.
4. Use the waterfall viewer to display and interpret the recorded spectra.
5. Identify Doppler-shifted hydrogen emission from different galactic longitudes.
6. Qualitatively relate the observed frequency shift to the galactic rotation curve.

---

## Part A: Software Setup (No Hardware Required)

This part uses the example data files already included in the repository. A real antenna or SDR is **not needed** to complete Part A.

### A1: Install Python dependencies

```bash
pip install -r software/requirements.txt
```

This installs: `numpy`, `scipy`, `matplotlib`, `astropy`.

### A2: Explore the example data

Example spectra from the Mergen-21 first-light session (2026-04-29, Istanbul, Turkey) are in `observations/data/`. Each `.dat` file is a sequence of float32 power spectra produced by the receiver flowgraph:

```
observations/data/
├── mergen21_spec_20260429_022811.dat   ← early session, pointing east
├── mergen21_spec_20260429_041703.dat   ← later session, pointing east (100 integrations)
├── mergen21_spec_20260429_045525_bati.dat    ← pointing west  (Batı = West in Turkish)
├── mergen21_spec_20260429_045857_guney.dat   ← pointing south (Güney = South)
├── mergen21_spec_20260429_050204_doggu.dat   ← pointing east  (Doğu = East)
└── ...
```

Load a single spectrum and display it:

```python
import numpy as np
import matplotlib.pyplot as plt

FFT_SIZE  = 2048
SAMP_RATE = 2_048_000   # samples/second
LO_FREQ   = 1_420_405_000  # Hz (hydrogen line)

# Load the file
raw = np.fromfile('observations/data/mergen21_spec_20260429_041703.dat', dtype=np.float32)

# Each FFT_SIZE values is one spectrum; take the average
n_rows = len(raw) // FFT_SIZE
spectra = raw[:n_rows * FFT_SIZE].reshape(n_rows, FFT_SIZE)
avg = spectra.mean(axis=0)

# Frequency axis (baseband, then shifted to RF)
bb_hz = np.fft.fftshift(np.fft.fftfreq(FFT_SIZE, d=1.0 / SAMP_RATE))
rf_mhz = (LO_FREQ + bb_hz) / 1e6

plt.figure(figsize=(10, 4))
plt.plot(rf_mhz, 10 * np.log10(np.maximum(avg, 1e-30)))
plt.axvline(1420.405751768, color='red', ls='--', label='H I rest frequency')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Power (dB, uncalibrated)')
plt.title('Average spectrum: east pointing, 2026-04-29')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
```

**What to look for:** A peak at or near 1420.405 MHz is galactic hydrogen emission. A peak slightly shifted in frequency (by up to ±2 MHz) indicates a Doppler velocity.

### A3: Use the interactive waterfall viewer

The waterfall viewer provides a graphical interface for browsing multiple .dat files:

```bash
python software/analysis/mergen21_waterfall_viewer.py
```

In the viewer:
1. Click **Add...** and select one or more `.dat` files from `observations/data/`.
2. Verify that FFT size = 2048, sample rate = 2048000 Hz, LO = 1420405000 Hz.
3. Click **Plot**. The upper panel shows power vs. time (waterfall); the lower panel shows the time-averaged spectrum.
4. Switch the X axis to **Velocity [km/s]** to see the Doppler velocity scale. The hydrogen line rest frequency appears at 0 km/s.

### A4: Compare east vs. west pointing

Load the east-pointing file (`_doggu` or `_Dogu`) and the west-pointing file (`_bati`) in the same viewer session (use Ctrl+click to select multiple files).

**Discussion questions:**
1. Is the HI emission peak at the same frequency for east and west pointings?
2. If not, which direction has higher velocity, and what does that imply about galactic rotation?
3. Look at the Stellarium sky charts in `observations/stellarium_*.png`. What galactic longitude was the antenna pointing at for each file?

---

## Part B: GNU Radio Receiver Setup (Hardware Required)

This part requires:
- Assembled antenna, LDO board, and RF chain (from Lab 2)
- ADALM-PLUTO SDR connected via USB
- Computer with GNU Radio 3.10+ and the gr-iio / PlutoSDR plugin

### B1: Install GNU Radio

**Ubuntu 22.04 (recommended):**
```bash
sudo apt update
sudo apt install -y gnuradio python3-gi
# Install gr-iio (PlutoSDR driver)
sudo apt install -y gr-iio
```

**Conda (more reliable across distributions):**
```bash
conda create -n gnuradio310 -c conda-forge gnuradio=3.10 gr-iio python=3.11
conda activate gnuradio310
```

Verify installation:
```bash
python3 -c "from gnuradio import gr; print(gr.version())"
gnuradio-companion --version
```

### B2: Connect the hardware

1. Power on the LDO board and verify +5 V on both outputs.
2. Connect the RF chain: Antenna N-type → SMA cable → LNA input. LNA output → BPF. BPF output → Amp. Amp output → PlutoSDR RX1.
3. Connect the PlutoSDR USB port to the computer.
4. Verify PlutoSDR is detected:
   ```bash
   # Linux
   usb-devices | grep 0456
   # Should show: Vendor=0456 ProdID=b673 (or similar ADALM-PLUTO ID)
   
   # Windows
   iio_info -s
   ```

### B3: Configure the log directory

Before running the flowgraph, set the output directory to a location of your choice. Open `software/gnuradio/reciver.py` and change the `log_dir` variable on approximately line 73:

```python
self.log_dir = log_dir = "logs"   # relative to the directory where you run the script
```

Or provide an absolute path to a directory that already exists on your system.

### B4: Launch the receiver

```bash
cd software/gnuradio
python3 reciver.py
```

Or open the flowgraph in GNU Radio Companion:
```bash
gnuradio-companion reciver.grc
```

The GUI shows three panels:
- **RX Quick-Look FFT** (bottom): raw spectrum directly from the PlutoSDR; it confirms RF reception
- **Integrated Power Spectrum** (middle): time-averaged spectrum, updated every ~second
- **Waterfall** (top): historical spectrogram

### B5: Verify reception

With the antenna connected and pointed at the sky:

1. Confirm that noise floor is visible in the Quick-Look FFT panel (flat noise power around −100 to −120 dBm/bin is expected).
2. Confirm that the PlutoSDR is not receiving at its full digital range (saturation appears as a perfectly flat spectrum; if you see this, reduce the SDR gain from 30 dB to 0 dB in the GUI).
3. After 1–2 minutes of integration, a broad emission feature should become visible near 1420.405 MHz in the integrated spectrum. The galactic disk is always above the horizon and produces detectable emission when the beam overlaps it.

### B6: Record an observation

The flowgraph saves data automatically to `logs/` (or whichever directory you configured). File naming: `mergen21_spec_YYYYMMDD_HHMMSS.dat`.

For a useful observation:
1. Note the antenna pointing direction (azimuth and elevation) and current UTC time.
2. Run for at least **5 minutes** per pointing direction to accumulate signal. More integration = better SNR.
3. Move the antenna to a new pointing direction and repeat.

---

## Part C: Analysis: Galactic Rotation Curve (future work)

This part describes a method for a future exercise. It has not been carried out on the released Mergen-21 dataset: rotation-curve extraction needs frequency-axis verification, oscillator calibration, and pointing records that are not yet in place. See `docs/analysis/PROVENANCE_ADDENDUM.md` for what the April 2026 session's data currently supports (pointing-dependent line detections; not a rotation curve).

### Background

The hydrogen 21 cm emission line is produced by cold neutral hydrogen clouds throughout the Milky Way disk. Clouds moving toward or away from Earth produce Doppler-shifted emission. By observing along different galactic longitudes, you can reconstruct the rotation speed of the Galaxy at different distances from the center.

### C1: Velocity calculation

The Doppler formula:

$$v = c \cdot \frac{f_{\rm rest} - f_{\rm obs}}{f_{\rm rest}}$$

where:
- c = 299 792.458 km/s
- f_rest = 1 420 405 751.768 Hz (HI rest frequency)
- f_obs = observed frequency of the emission peak

A positive velocity means the cloud is receding (redshift); negative means approaching.

### C2: Tangent-point method

For a galactic longitude l (between 0° and 90°, northern galactic disk), the highest-velocity emission component comes from the tangent point, the point along the line of sight where the observer, the galactic center, and the cloud are aligned. At this point, all of the cloud's velocity is radial.

Rotation speed at the tangent point:

$$v_{\rm rot}(R_{\rm tan}) = v_{\rm max}(l) + v_\odot \sin(l)$$

where v_max is the maximum observed Doppler velocity at longitude l, and v_⊙ ≈ 220 km/s is the Sun's rotation speed. The tangent point radius is R_tan = R_⊙ sin(l) (R_⊙ ≈ 8.5 kpc).

### C3: Comparing east and west observations

At the latitude of Istanbul (41°N), the galactic plane passes through a range of azimuth angles during the night. The Stellarium screenshots in `observations/` document the galactic longitudes observed during the 2026-04-29 session.

Load the directional files (east/west/south) in the viewer and measure the velocity of the most redshifted or blueshifted peak in each spectrum. Plot rotation speed vs. galactocentric radius.

---

## Synthesizer Flowgraphs (Hardware-Free GNU Radio Test)

If you have GNU Radio installed but no PlutoSDR, the `21cm synth/` flowgraphs generate synthetic HI data through the full signal-processing chain:

| Flowgraph | What it generates |
|---|---|
| `topo1_cw_tone.grc` | Single continuous-wave tone at 1420.405 MHz |
| `topo2_single_gaussian.grc` | Single Gaussian spectral line (one HI cloud) |
| `topo3_galaxy_rotation.grc` | Multiple Gaussian components (realistic galactic spectrum) |

To run:
```bash
cd software/gnuradio
gnuradio-companion "21cm synth/topo3_galaxy_rotation.grc"
```

These flowgraphs use a signal source block instead of a PlutoSDR source, so they run entirely in software. They verify that GNU Radio, the FFT integrator, and the display blocks work correctly before connecting real hardware.

---

## Expected Observation Results

From the Istanbul site (41.0°N, 29.0°E), galactic HI emission is detectable in most pointing directions. The following results were achieved in the 2026-04-29 session:

| Direction | File | Peak velocity (km/s) | Notes |
|---|---|---|---|
| East | `_doggu.dat` | ~+40 to +80 | Spiral arm components |
| West | `_bati.dat` | ~+20 to +60 | Different arm crossing |
| South | `_guney.dat` | ~0 to +40 | Near galactic center |

Plots in `observations/plots/` show the spectra from this session.

---

## Troubleshooting

**No signal visible in Quick-Look FFT:** Verify USB cable, try a different USB port, and confirm `iio_info -s` detects the PlutoSDR.

**Flat spectrum (saturation):** Reduce SDR gain to 0 dB, then increase slowly while monitoring the noise floor.

**No HI emission visible after long integration:** Confirm the antenna is pointing at the sky (not a nearby wall or the ground). The galactic plane transits the meridian at LST equal to the right ascension of the target; check a planetarium app.

**Viewer crashes or freezes:** Each .dat file can be several hundred MB. The viewer uses memory-mapping and will decimate to at most 2500 display rows. If problems persist, try loading a single small file first.

**gr-iio not found:** On Ubuntu/conda, ensure the PlutoSDR plugin is installed (package `gr-iio`). On Windows, the PlutoSDR driver and libiio must be installed separately from the Analog Devices website.
