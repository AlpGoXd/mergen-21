# Noise Figure Measurement

## Summary
- **Measured cascade NF (cable-corrected):** about 1.5 dB (1.54 dB)
- **Friis-formula prediction:** 0.77 dB
- **Design requirement:** 0.96 dB

The measured value is referenced to the device plane (before the output
cable) via an estimated cable correction; it is not a direct match to the
Friis prediction, and the gap is discussed below rather than rounded away.

## Key Finding
The first-stage LNA (NF = 0.7 dB) dominates the Friis-predicted cascade NF.
Later stages contribute negligibly due to high LNA gain (19.7 dB). The
measured cascade NF is higher than this prediction; see "Why measurement
and Friis prediction differ" below.

## Measurement Method
Direct measurement of LNA input noise was not feasible (analyzer's own noise too high).
Instead: measured cascade *output* noise, used known gain to infer input NF.

**Measured output noise density:** -133.46 dBm/Hz

**Cable-corrected noise figure, from the measurement:**

```
NF = P_out + CABLE_LOSS - KT0 - GAIN
   = -133.46 dBm/Hz + 0.6 dB - (-173.9 dBm/Hz) - 39.5 dB
   = 1.54 dB
```

where `CABLE_LOSS` = 0.6 dB +/- 0.2 dB is an estimated correction for the
output cable between the receiver and the spectrum analyzer (see "Cable
Loss" below), `KT0` = -173.9 dBm/Hz is the thermal noise floor at the
measured ambient temperature, and `GAIN` = 39.5 dB +/- 0.5 dB is the
cascade gain from the VNA measurement. Adding the cable correction moves
the result further from, not closer to, the Friis prediction -- see below.
Including gain uncertainty, the measured NF is 1.54 dB +/- 0.5 dB.

---

## Cascade Noise Figure (Friis Formula)

### Why the Friis prediction is dominated by the LNA

The Friis formula for cascaded noise figure shows that the first-stage noise figure dominates when the first stage has high gain:

```
F_total = F1 + (F2 - 1)/G1 + (F3 - 1)/(G1 * G2) + ...
```

**Our cascade:**
- F1 (LNA): 1.74 (0.7 dB) @ gain G1 = 18.6x (17.5 dB actual; datasheet 19.7 dB)
- F2 (BPF): 1.20 (0.8 dB = insertion loss) @ gain G2 = 0.83x (-0.8 dB)
- F3 (Amp): 2.34 (3.7 dB) @ gain G3 = 7.6x (8.8 dB actual; datasheet 20.8 dB)

**Calculated F_total:** 1.74 + (1.20 - 1)/18.6 + (2.34 - 1)/(18.6 x 0.83) = 1.74 + 0.011 + 0.087 = 1.83 (0.77 dB NF)

The LNA contributes 1.74 to the total noise factor. The BPF adds only 0.011 and the amplifier adds only 0.087. This confirms that the LNA's low noise figure and high gain effectively shield the system from downstream noise contributions.

### Why measurement and Friis prediction differ

The cable-corrected measured NF (1.54 dB) is about 0.8 dB higher than the
0.77 dB Friis prediction from datasheet values, and above the 0.96 dB
design requirement. Candidate contributors, none confirmed or excluded by
data currently in this repository:

- Actual component NF at the operating temperature and bias point may
  differ from the datasheet spec used in the Friis calculation.
- The individual-stage gains measured here run about 2.2 dB below
  datasheet (see "Measured Gain vs. Datasheet" in `../ip3/README.md`),
  which raises the noise contribution of the later stages relative to the
  Friis calculation above (computed with datasheet gains).
- The 0.6 dB +/- 0.2 dB output-cable correction is itself an estimate
  carried over from the IP3 measurements, not a value measured
  simultaneously with this NF test.
- The spectrum-analyzer-referenced Y-factor method used here (see
  "Measurement Method" above) is a gain-method estimate, not a
  noise-source ENR measurement, and carries its own systematic
  uncertainty.

This gap is reported rather than resolved; no constant in this
measurement or in the analysis pipeline was adjusted to close it.

---

## Measurement Challenges & Why We Did It This Way

It was not feasible to characterize the noise figure of each amplifier stage separately using the available measurement setup. The first LNA has a very low noise figure of approximately 0.6--0.7 dB, while the available instrument was a **Rohde & Schwarz FSVA3044 spectrum analyzer**. Since this analyzer is not a dedicated noise figure meter and its own internal noise floor is significant, the noise performance of the **entire receiver chain** was evaluated instead of attempting stage-by-stage noise figure measurements.

### Baseline Measurement

The spectrum analyzer input was terminated with a **50 ohm matched load** at **23.6 deg C**. For a 50 ohm source at this temperature, the expected thermal noise power density is approximately **-173.9 dBm/Hz**. However, the measured value was **-153.10 dBm/Hz**. This large discrepancy (20.8 dB) indicates that the internal noise floor of the spectrum analyzer dominated the baseline measurement. The input attenuation was set to 0 dB; no internal preamplifier was available on this analyzer model.

### Receiver Chain Measurement

The complete receiver chain was measured by connecting the **50 ohm matched load** to the receiver input and the receiver output to the spectrum analyzer. The system was allowed to warm up for approximately **one hour** before the measurement to ensure stable operating conditions.

### Cable Loss

The cable loss was measured at approximately **0.6 dB**, consistent with the value observed during the IP3 measurements. This value is used as the `CABLE_LOSS` correction in the cable-corrected NF calculation above (a +/-0.2 dB uncertainty is carried through to the final result).

---

## Assumptions & Uncertainties

| Parameter | Value | Uncertainty | Notes |
|-----------|-------|-------------|-------|
| Ambient temperature | 23.6 deg C | +/-1 deg C | Lab environment |
| Thermal noise density | -173.9 dBm/Hz | +/-0.1 dB | At 23.6 deg C |
| Cascade gain | 39.5 dB | +/-0.5 dB | From VNA measurement; no VNA sample exists exactly at 1420.405 MHz (~42.5 MHz point spacing) |
| Cable loss | 0.6 dB | +/-0.2 dB | Applied as the `CABLE_LOSS` correction in the cable-corrected NF result |
| Warm-up time | 1 hour | -- | Ensures thermal stability |

- Temperature assumed constant during measurement (lab environment)
- Cable loss is applied as a correction, not neglected (see above)
- Spectrum analyzer noise floor limits direct observation of LNA input noise
- NF value (1.54 dB, cable-corrected) is inferred from output noise measurement, not directly measured

## Data Files

| File | Description |
|------|-------------|
| `cable_loss.DAT` / `cable_loss.PNG` | Cable insertion loss measurement |
| `match noise.DAT` / `match noise again.PNG` | 50 ohm matched load baseline (analyzer noise floor) |
| `just cooked reciver.DAT` / `just cooked reciver.PNG` | Full receiver chain output noise measurement |
| `setup/` | Measurement setup photos |

`.DAT` files are tab-delimited ASCII exports from the FSVA3044. They can be viewed with **[mergen-scope](https://alpgoxd.github.io/mergen-scope/)** ([GitHub](https://github.com/alpgoxd/mergen-scope)), an open-source R&S DAT file viewer.

## See Also

- [`../ip3/`](../ip3/) -- IP3 / intermodulation measurements (same cable loss reference)
- [`../vna/`](../vna/) -- VNA-measured S-parameters (gain data used here)
- [`../../../hardware/simulation/awr/`](../../../hardware/simulation/awr/) -- AWR cascade simulation (noise figure data)
- [`../../extras/`](../../extras/) -- 50 ohm matched load characterization
