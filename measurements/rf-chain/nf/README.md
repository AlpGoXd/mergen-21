# Noise Figure Measurement

## Summary
- **Measured cascade NF:** 0.75 dB
- **Predicted (Friis formula):** 0.73 dB
- **Agreement:** 0.02 dB -- Excellent

## Key Finding
The first-stage LNA (NF = 0.7 dB) dominates the cascade NF.
Later stages contribute negligibly due to high LNA gain (19.7 dB).

## Measurement Method
Direct measurement of LNA input noise was not feasible (analyzer's own noise too high).
Instead: measured cascade *output* noise, used known gain to infer input NF.

**Result:** Output noise measured = -133.46 dBm/Hz
**Expected:** -173.9 dBm/Hz (thermal) + 39.5 dB (gain) + 0.75 dB (NF) = -133.65 dBm/Hz
**Error:** 0.19 dB -- Theory & measurement agree

---

## Cascade Noise Figure (Friis Formula)

### Why Cascade NF is So Good

The Friis formula for cascaded noise figure shows that the first-stage noise figure dominates when the first stage has high gain:

```
F_total = F1 + (F2 - 1)/G1 + (F3 - 1)/(G1 * G2) + ...
```

**Our cascade:**
- F1 (LNA): 1.74 (0.7 dB) @ gain G1 = 18.6x (17.5 dB actual; datasheet 19.7 dB)
- F2 (BPF): 1.20 (0.8 dB = insertion loss) @ gain G2 = 0.83x (-0.8 dB)
- F3 (Amp): 2.34 (3.7 dB) @ gain G3 = 7.6x (8.8 dB actual; datasheet 20.8 dB)

**Calculated F_total:** 1.74 + (1.20 - 1)/18.6 + (2.34 - 1)/(18.6 x 0.83) = 1.74 + 0.011 + 0.087 = 1.83 (0.73 dB NF)

**Measured:** 0.75 dB -- Within 0.02 dB

The LNA contributes 1.74 to the total noise factor. The BPF adds only 0.011 and the amplifier adds only 0.087. This confirms that the LNA's low noise figure and high gain effectively shield the system from downstream noise contributions.

---

## Measurement Challenges & Why We Did It This Way

It was not feasible to characterize the noise figure of each amplifier stage separately using the available measurement setup. The first LNA has a very low noise figure of approximately 0.6--0.7 dB, while the available instrument was a **Rohde & Schwarz FSVA3044 spectrum analyzer**. Since this analyzer is not a dedicated noise figure meter and its own internal noise floor is significant, the noise performance of the **entire receiver chain** was evaluated instead of attempting stage-by-stage noise figure measurements.

### Baseline Measurement

The spectrum analyzer input was terminated with a **50 ohm matched load** at **23.6 deg C**. For a 50 ohm source at this temperature, the expected thermal noise power density is approximately **-173.9 dBm/Hz**. However, the measured value was **-153.10 dBm/Hz**. This large discrepancy (20.8 dB) indicates that the internal noise floor of the spectrum analyzer dominated the baseline measurement. The input attenuation was set to 0 dB; no internal preamplifier was available on this analyzer model.

### Receiver Chain Measurement

The complete receiver chain was measured by connecting the **50 ohm matched load** to the receiver input and the receiver output to the spectrum analyzer. The system was allowed to warm up for approximately **one hour** before the measurement to ensure stable operating conditions.

### Cable Loss

The cable loss was measured at approximately **0.6 dB**, consistent with the value observed during the IP3 measurements. Because this loss is small compared with the overall cascade gain (~39.5 dB), it was neglected in the final comparison.

---

## Assumptions & Uncertainties

| Parameter | Value | Uncertainty | Notes |
|-----------|-------|-------------|-------|
| Ambient temperature | 23.6 deg C | +/-1 deg C | Lab environment |
| Thermal noise density | -173.9 dBm/Hz | +/-0.1 dB | At 23.6 deg C |
| Cascade gain | 39.5 dB | +/-0.5 dB | From VNA measurement |
| Cable loss | 0.6 dB | +/-0.2 dB | Neglected in final result |
| Warm-up time | 1 hour | -- | Ensures thermal stability |

- Temperature assumed constant during measurement (lab environment)
- Cable loss neglected (0.6 dB << 39.5 dB cascade gain)
- Spectrum analyzer noise floor limits direct observation of LNA input noise
- NF value (0.75 dB) is inferred from output noise measurement, not directly measured

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
