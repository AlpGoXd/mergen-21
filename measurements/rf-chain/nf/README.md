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
Later stages contribute negligibly due to high LNA gain (19.87 dB datasheet, 19.24 dB VNA). The
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

**Our cascade (datasheet values):**
- F1 (LNA): 1.175 (0.7 dB) @ gain G1 = 93.3 (19.7 dB)
- F2 (BPF): 1.202 (0.8 dB = insertion loss) @ gain G2 = 0.832 (-0.8 dB)
- F3 (Amp): 2.344 (3.7 dB)

**Calculated F_total:** 1.175 + 0.202/93.3 + 1.344/(93.3 x 0.832) = 1.175 + 0.002 + 0.017 = 1.194 (0.77 dB NF)

With the VNA stage gains instead (G1 = 83.9 for 19.24 dB; BPF G2 = 0.671 for -1.73 dB, so F2 = 1.489), the same calculation gives 1.175 + 0.489/83.9 + 1.344/(83.9 x 0.671) = 1.205 (0.81 dB NF).

The LNA contributes 1.175 to the total noise factor. The BPF adds only 0.002 and the amplifier adds only 0.017 (datasheet case). This confirms that the LNA's low noise figure and high gain effectively shield the system from downstream noise contributions.

### Why measurement and Friis prediction differ

The cable-corrected measured NF (1.54 dB) is about 0.8 dB higher than the
0.77 dB Friis prediction from datasheet values, and above the 0.96 dB
design requirement. Candidate contributors, none confirmed or excluded by
data currently in this repository:

- Actual component NF at the operating temperature and bias point may
  differ from the datasheet spec used in the Friis calculation.
- The VNA stage gains are about 0.6 dB below datasheet (LNA 19.24 vs
  19.87 dB; amplifier 20.24 vs 20.82 dB; see
  `software/analysis/outputs/stage_gains.csv`). Using them raises the
  Friis prediction only to 0.81 dB. (The larger 2.2 dB figure in
  `../ip3/README.md` is the IP3 tone-level gain, which includes the test
  cables.)
- The 0.6 dB +/- 0.2 dB output-cable correction is itself an estimate
  carried over from the IP3 measurements, not a value measured
  simultaneously with this NF test.
- The method used here is the gain method (output noise density of the
  chain with its input terminated in 50 ohm, minus the known gain; see
  "Measurement Method" above). It is not a Y-factor (noise-source ENR)
  measurement, and it carries its own systematic uncertainty.

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
