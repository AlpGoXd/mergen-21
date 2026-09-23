# Lab Manual 1 — Simulate

**Topic:** Electromagnetic simulation of the horn antenna and RF cascade analysis  
**Estimated time:** 3–4 hours  
**Prerequisites:** Basic knowledge of electromagnetic simulation concepts; familiarity with S-parameters

---

## Learning Objectives

After completing this lab, students will be able to:

1. Build a parametric pyramidal horn antenna model in CST Studio Suite using a provided VBA macro.
2. Interpret S11, far-field directivity, and beamwidth simulation results.
3. Understand the effect of manufacturing tolerances on antenna performance (ideal vs. worst-case).
4. Analyse a cascaded RF chain using S-parameter files and Friis noise-figure formulas.
5. Predict the system noise figure of a multi-stage receiver using AWR or Python.

---

## Part A — Horn Antenna Simulation (CST Studio Suite)

### Required Software

- CST Studio Suite 2023 or later (frequency-domain tetrahedral solver)
- Any version that supports VBA macros and frequency-domain simulation

### Files Needed (from this repository)

| File | Location |
|---|---|
| VBA macro (rebuilds full model) | `hardware/simulation/cst/ideal_horn/ideal_hornfrfr_creator.mcs.bas` |
| Design parameters | `hardware/simulation/cst/ideal_horn/ideal_hornfrfr_all_parameters.txt` |
| Expected S11 result | `hardware/simulation/cst/ideal_horn/ideal_hornfrfr.s1p` |
| Expected far-field (E-plane) | `hardware/simulation/cst/ideal_horn/ideal_hornfrfr_farfield_phi0.txt` |
| Expected far-field (H-plane) | `hardware/simulation/cst/ideal_horn/ideal_hornfrfr_farfield_phi90.txt` |

### Procedure

#### A1 — Create the parametric model

1. Open CST Studio Suite. Create a new **Microwave & RF** project.
2. In the VBA Macro editor (menu: **Macros → Edit/Run VBA Macros**), open and run `ideal_hornfrfr_creator.mcs.bas`. This macro creates the complete 3D geometry, assigns materials, defines the coaxial port, and sets solver parameters. No manual geometry entry is required.
3. After the macro finishes, verify that the model contains the following components:
   - Horn body (four aluminium panels forming the pyramidal section)
   - Rectangular waveguide section (WR-650 equivalent)
   - Backshort (short-circuit termination at the rear of the waveguide)
   - N-type coaxial feed probe (copper wire)

#### A2 — Review design parameters

Open `ideal_hornfrfr_all_parameters.txt` and note the key geometric values. The design is optimised for 1420.405 MHz (the neutral hydrogen 21 cm line). Important parameters include:

- Aperture dimensions (E-plane height, H-plane width)
- Flare length
- Probe depth and diameter
- Backshort distance (distance from probe to waveguide end wall)

These values can be changed in the CST parameter editor to explore sensitivity.

#### A3 — Run the simulation

1. Set the frequency range to **1–2 GHz** in the solver settings.
2. Select the **Frequency-Domain (FD) tetrahedral** solver with adaptive mesh refinement.
3. Run the simulation. Expected runtime: 30–90 minutes depending on workstation.

#### A4 — Analyse results

After the simulation completes, open the results navigator and extract:

| Result | How to access | Expected value |
|---|---|---|
| S11 (reflection coefficient) | Results → S-Parameters → S1,1 | −30 dB or better at 1420 MHz |
| Peak directivity | Farfield → Farfield Plots | ≈ 16.9 dBi at 1420 MHz |
| E-plane 3 dB beamwidth | Farfield, Phi=0 cut | ≈ 26° |
| H-plane 3 dB beamwidth | Farfield, Phi=90 cut | ≈ 22° |

Compare your S11 curve against `ideal_hornfrfr.s1p`. They should match exactly (the `.s1p` was exported from the same model).

#### A5 — Manufacturing tolerance study (optional, 1 extra hour)

The `assembly_worstcase/` folder contains simulation results for a model that includes assembly imperfections: gaps at panel seams, added bridging blocks, and individually modelled screws. This represents the realistic worst case after fabrication.

1. Open `assembly_worstcase/hornffrfr_assembly_worstcase.stp` in CST as an imported geometry. Add the same materials and port as the ideal model.
2. Compare the simulated S11 against `hornffrfr_assembly_worstcase.s1p`.

**Discussion question:** What is the degradation in S11 depth and frequency shift caused by realistic assembly tolerances? Is the antenna still well-matched at 1420 MHz?

---

## Part B — RF Cascade Analysis

### Files Needed

| File | Location |
|---|---|
| S2P files for each stage | `hardware/rf-chain/datasheet-s-parameters/` |
| AWR noise figure data | `hardware/simulation/awr/ZX60_P162LN_NF.txt`, `ZX60_V63_NF.txt` |
| Simulated cascade S2P | `hardware/simulation/awr/rf_chain_cascaded.s2p` |
| Cascade gain plot | `hardware/simulation/awr/rf_chain_gain.png` |

### Background

The receiver RF chain consists of three stages in series:

```
Antenna → [ZX60-P162LN+] → [ZX75BP-1450-S+] → [ZX60-V63+] → SDR
           LNA: G=19.7 dB    BPF: IL=0.8 dB      Amp: G=20.8 dB
           NF=0.7 dB         NF=0.8 dB             NF=3.7 dB
```

### Procedure

#### B1 — Manual Friis calculation

Using the Friis formula for cascaded noise figure:

$$F_{sys} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2}$$

where F is the noise factor (linear), G is the available gain (linear).

Given the datasheet values:

| Stage | Gain G (dB) | NF F (dB) |
|---|---|---|
| ZX60-P162LN+ (LNA) | 19.7 | 0.7 |
| ZX75BP-1450-S+ (BPF) | −0.8 | 0.8 |
| ZX60-V63+ (Amp) | 20.8 | 3.7 |

Calculate the cascaded noise figure and compare it to the measured value of **about 1.5 dB (cable-corrected)** (see `measurements/rf-chain/nf/`).

#### B2 — S-parameter cascade in Python

The following Python code loads the stage S-parameter files and computes the cascade using a simple S21 chain multiplication (for gain/loss only):

```python
import numpy as np

def read_s2p(filename):
    """Read a 2-port Touchstone .s2p file, return (freq_hz, S21_complex)."""
    data = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('!') or line.startswith('#'):
                continue
            vals = [float(v) for v in line.split()]
            # Standard Touchstone format: freq S11_re S11_im S21_re S21_im ...
            freq = vals[0]  # Hz or GHz depending on header — check # line
            s21 = complex(vals[3], vals[4])
            data.append((freq, s21))
    freq = np.array([d[0] for d in data])
    s21  = np.array([d[1] for d in data])
    return freq, s21

# Load S-parameter files (adjust paths as needed)
f1, s21_lna = read_s2p('hardware/rf-chain/datasheet-s-parameters/ZX60-P162LN+/ZX60-P162LN+_4V_Plus25degC.s2p')
f2, s21_bpf = read_s2p('hardware/rf-chain/datasheet-s-parameters/ZX75BP-1450-S+/ZX75BP-1450-S+_Plus25degC.s2p')
f3, s21_amp = read_s2p('hardware/rf-chain/datasheet-s-parameters/ZX60-V63+/ZX60-V63+_5V_Plus25DegC.s2p')

# Interpolate to common frequency grid, compute cascade |S21|
# (See NumPy documentation for np.interp)
```

**Expected result:** The cascade gain near 1420 MHz should be approximately **+39.5 dB +/- 0.5 dB**, matching `hardware/simulation/awr/rf_chain_gain.png`. Note that the measured VNA cascade file has no sample exactly at 1420.405 MHz (~42.5 MHz point spacing).

#### B3 — Comparison with measured results

The VNA measurements in `measurements/rf-chain/vna/` were taken with the actual components. Load `cascade/cascaded chain.s2p` and overlay it with the simulation output. Discuss:

1. How well do the datasheet S-parameters predict the measured cascade gain?
2. At what frequencies is the prediction least accurate? Why?

---

## Expected Results Summary

| Metric | Simulated | Measured |
|---|---|---|
| Horn S11 at 1420 MHz | −30 dB (ideal) | −42 dB (actual) |
| Horn directivity at 1420 MHz | 16.9 dBi | — (no measurement setup available) |
| Cascade gain near 1420 MHz | ~39.5 dB | 39.5 dB +/- 0.5 dB (no VNA sample exactly at 1420.405 MHz) |
| Cascade NF | 0.77 dB (Friis) | about 1.5 dB (1.54 dB, cable-corrected) |

---

## Troubleshooting

**CST macro fails to run:** Verify that the macro language is set to VBA (not Python). Go to Macros → Macro Language → VBA.

**S-parameter file won't load:** The `.s2p` files use standard Touchstone format. If importing into a non-standard tool, ensure the tool handles RI (Real-Imaginary) format, which is what Mini-Circuits exports.

**Simulated S11 resonance is off-frequency:** Check that the frequency unit in the CST project matches the values in the parameter file (millimetres vs. metres).

---

## Further Reading

- Pozar, D.M. (2011). *Microwave Engineering*, 4th ed., Chapter 4 (noise) and Chapter 13 (horn antennas).
- Mini-Circuits application note AN-60-010: Cascaded IP3 and NF calculations.
- CST Studio Suite online documentation: Frequency-Domain Solver.
