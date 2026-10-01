# Lab Manual 3: Measure

**Topic:** VNA characterization of the antenna and RF chain; noise figure and IP3 measurements  
**Estimated time:** 4–5 hours  
**Prerequisites:** Lab 2 complete (assembled hardware); access to a VNA and spectrum analyzer

---

## Learning Objectives

After completing this lab, students will be able to:

1. Calibrate a VNA (SOLT or equivalent) and measure antenna S11.
2. Measure two-port S-parameters (gain and input/output match) of a cascaded RF chain.
3. Measure noise figure using the Y-factor method (the Mergen-21 reference value was obtained with the gain method; see Part C).
4. Measure the third-order intercept point (OIP3) using a two-tone test.
5. Compare measured performance against simulation predictions (Lab 1) and datasheet values.

---

## Equipment Required

| Instrument | Specification | Used in |
|---|---|---|
| Vector network analyzer (VNA) | 1-port or 2-port, 1–2 GHz minimum | S11, S21 |
| Calibration kit | Matched to VNA connector type (SMA or N) | VNA calibration |
| Spectrum analyzer | NF measurement option preferred; 1–2 GHz | NF, IP3 |
| Noise source | Calibrated ENR at 1420 MHz, SMA | NF |
| Signal generator (x2 for IP3) | 1400–1440 MHz, ≥ +10 dBm output | IP3 |
| DC power supply | 5 V, 1 A minimum | RF chain bias |
| Coaxial cables | SMA male-male, low-loss, 30–50 cm | All |
| Attenuators (10–30 dB) | SMA, rated > 0 dBm | IP3 |

---

## Part A: Antenna S11 Measurement

### Files Produced

Compare your measured files against the five sequential measurements in `measurements/antenna/`, which document the evolution from first assembly to final optimized antenna:

| Measurement | File |
|---|---|
| 1: Outdoor, uncalibrated | `measurements/antenna/1_outside_uncalibrated/alp_anten_uncal_0.s1p` |
| 2: Outdoor, VNA-calibrated | `measurements/antenna/2_outside_calibrated/alp_anten_cal_0.s1p` |
| 3: Indoor lab, calibrated | `measurements/antenna/3_inside_calibrated/alp_anten_lab_0.s1p` |
| 4: Indoor, aluminum foil on panels | `measurements/antenna/4_inside_aluminum_foil/alp_anten_lab_0_enhanced.s1p` |
| 5: Indoor, backshort cleaned | `measurements/antenna/5_inside_cleaned_backshort/anten_son_horn.s1p` |

### Procedure

#### A1: VNA calibration

1. Connect the calibration kit to the VNA port that will connect to the antenna.
2. Perform a full 1-port SOLT calibration at the measurement plane (the cable end where the antenna will connect).
3. Set the frequency range to **1.3–1.6 GHz** to capture the full resonance including off-target peaks.
4. Use at least **201 frequency points** (more is better for resolving the resonance shape).
5. Verify calibration: connect a SOLT short and verify |S11| = 0 dB; connect SOLT open and verify |S11| = 0 dB; connect SOLT load and verify |S11| ≤ −40 dB.

#### A2: First measurement (antenna in free space)

1. Connect the antenna N-type port to the VNA via the calibrated cable.
2. Face the antenna aperture away from walls and other metal surfaces (outdoors is ideal; otherwise aim at an RF-absorbing wall or at the ceiling of a large room).
3. Record S11 as a Touchstone .s1p file.
4. Note the frequency of minimum S11 (the resonance) and its depth.

**Expected result:** S11 < −20 dB at or near 1420.405 MHz.

If S11 is only −10 to −15 dB, check:
- Cable and connector quality (especially at the N-type)
- Feed probe dimensions (length and straightness)
- Whether the backshort is making good contact with the waveguide panels

#### A3: Effect of environment

Repeat the measurement in different environments:

1. Outdoors, open field
2. Indoor lab (walls nearby)
3. With and without grounded objects near the aperture

The resonance frequency should not shift by more than a few MHz between environments. Large shifts indicate the antenna is coupling to nearby objects.

#### A4: Final result interpretation

Load your .s1p file and the reference file `5_inside_cleaned_backshort/anten_son_horn.s1p` in the same S-parameter viewer:

```python
import numpy as np
import matplotlib.pyplot as plt

def read_s1p(fname):
    data = np.loadtxt(fname, comments=['!', '#'])
    return data[:, 0], data[:, 1] + 1j * data[:, 2]  # freq, S11 complex

f_ref, s11_ref = read_s1p('measurements/antenna/5_inside_cleaned_backshort/anten_son_horn.s1p')
f_yours, s11_yours = read_s1p('your_measurement.s1p')

plt.figure()
plt.plot(f_ref / 1e9, 20 * np.log10(np.abs(s11_ref)), label='Reference (Mergen-21)')
plt.plot(f_yours / 1e9, 20 * np.log10(np.abs(s11_yours)), label='Your measurement')
plt.xlabel('Frequency (GHz)')
plt.ylabel('S11 (dB)')
plt.axvline(1.420405, color='red', ls='--', label='HI 21 cm')
plt.legend()
plt.grid()
plt.show()
```

---

## Part B: RF Chain S-Parameter Measurement

### Procedure

#### B1: VNA 2-port calibration

1. Perform a full 2-port SOLT calibration over **1.0–2.0 GHz**.
2. Reference planes are at the cable ends that will connect to the chain input (SMA) and output (SMA).

#### B2: Individual component measurement

Measure each component in the chain separately:
- ZX60-P162LN+ (LNA): connect +5 V DC bias before measuring. The LNA requires bias to function.
- ZX75BP-1450-S+ (BPF): passive, no bias needed.
- ZX60-V63+ (Amp): connect +5 V DC bias.

For each component, record S11, S21, S12, S22 as a .s2p file.

Compare against the reference files in `measurements/rf-chain/vna/`.

#### B3: Cascaded chain measurement

Connect all three stages in series: LNA → BPF → Amp. Apply DC bias to the two amplifiers.

Measure the cascade S-parameters. Expected results:

| Parameter | Expected value at 1420 MHz |
|---|---|
| S21 (cascade gain) | ≈ +39.5 dB +/- 0.5 dB (VNA has no sample exactly at 1420.405 MHz) |
| S11 (input reflection) | Depends on LNA, typically < −10 dB |

Compare against `measurements/rf-chain/vna/cascade/cascaded chain.s2p`.

---

## Part C: Noise Figure Measurement (Y-Factor Method)

### Background

The noise figure (NF) of a receiver is the degradation in signal-to-noise ratio caused by the receiver itself. For a low-noise radio astronomy receiver, NF should be as low as possible. The cascaded NF is dominated by the first stage (LNA), as predicted by the Friis formula (Lab 1).

The Y-factor method uses a calibrated noise source with known excess noise ratio (ENR) to measure NF directly with a spectrum analyzer.

### Equipment

- Calibrated noise source with known ENR at 1420 MHz (typical ENR: 15–30 dB)
- Spectrum analyzer with noise figure measurement mode (or use power meter and calculate)

### Procedure

#### C1: Cable loss correction

Before measuring the receiver, measure the insertion loss of the cable between the noise source and the DUT:

1. Connect: noise source → cable → spectrum analyzer
2. Measure the analyzer's own NF (with noise source directly connected; no DUT).
3. Insert the cable and measure again. The difference is the cable loss at 1420 MHz.

Use this loss value to correct the DUT noise figure measurement.

Compare against `measurements/rf-chain/nf/cable_loss.DAT`.

#### C2: LNA noise figure

1. Connect: noise source → LNA (biased at +5 V) → spectrum analyzer
2. Set up the spectrum analyzer noise figure measurement at **1420 MHz**, 1 MHz bandwidth.
3. Enter the noise source ENR values.
4. Record the measured NF.

Expected LNA NF: **0.7 dB** (datasheet spec).

#### C3: Cascade noise figure

Connect: noise source → LNA → BPF → Amp → spectrum analyzer

Measure NF as above. Expected: **about 1.5 dB, cable-corrected** (Mergen-21 measured result, obtained with the gain method rather than Y-factor: output noise density of the chain with its input terminated in 50 Ω, minus the 39.5 dB chain gain; see `measurements/rf-chain/nf/README.md` for the cable-loss correction arithmetic).

Compare against files in `measurements/rf-chain/nf/`.

---

## Part D: IP3 Measurement

### Background

The third-order intercept point (IP3) characterizes the linearity of the receiver. A high OIP3 means the receiver tolerates strong interferers without generating intermodulation products that could obscure weak signals.

### Procedure

#### D1: Setup

```
Two-tone source (f1 = 1420.355 MHz, f2 = 1420.455 MHz) ── Attenuator ── DUT ── Spectrum analyzer
```

Mergen-21 used two tones 100 kHz apart around 1420.405 MHz (f1 = 1420.355 MHz, f2 = 1420.455 MHz), which places the IMD3 products at 1420.255 and 1420.555 MHz. A vector signal generator in two-tone mode is the simplest source. If you use two separate generators with a power combiner instead, put 20–30 dB attenuators on the generator outputs to prevent the generators from intermodulating each other.

#### D2: Measurement

1. Set the two-tone input to −12 dBm total (the sum of both tones, i.e. about −15 dBm per tone) at the DUT input. Record the DUT output power at f1 and f2 (fundamental) and at 2f1-f2 and 2f2-f1 (IMD3 products) on the spectrum analyzer.
2. Repeat at −15 dBm and −18 dBm total input.
3. Calculate OIP3:
   - OIP3 = Pout (fundamental) + ΔP / 2
   - where ΔP = Pout(fundamental) − Pout(IMD3) in dB

Expected OIP3 for the cascade: **+29.5 dBm** (output-referred) at −12 dBm total two-tone input (−15 dBm per tone).

Compare raw data against files in `measurements/rf-chain/ip3/`.

---

## Results Summary

When all measurements are complete, fill in this table and compare to the reference:

| Parameter | Simulated | Mergen-21 measured | Your result |
|---|---|---|---|
| Antenna S11 at 1420 MHz (dB) | −19.7 (ideal), −21.8 (worst case) | −41.8 (1420.000 MHz sample, 10 MHz grid) | |
| Antenna resonance frequency (MHz) | 1396 (ideal minimum) | 1420 (10 MHz grid) | |
| Cascade gain (dB) | ~40 | 39.5 +/- 0.5 | |
| Cascade NF (dB) | 0.77 (Friis) | about 1.5 (cable-corrected) | |
| Cascade OIP3 (dBm) | — | +29.5 | |

---

## Data Files Reference

All reference measurement files from the Mergen-21 build are in `measurements/`. Open them with any S-parameter viewer (Qucs, scikit-rf, MATLAB RF Toolbox, or the Python snippet in Part A).

```python
# Load and plot a .s2p file with scikit-rf (pip install scikit-rf)
import skrf as rf
import matplotlib.pyplot as plt

ntwk = rf.Network('measurements/rf-chain/vna/cascade/cascaded chain.s2p')
ntwk.plot_s_db(m=1, n=0)  # S21 in dB
plt.title('Cascaded RF chain gain')
plt.show()
```
