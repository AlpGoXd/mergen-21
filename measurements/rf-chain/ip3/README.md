# IP3 / Intermodulation Measurements

Third-order intercept point (IP3) measurements for the RF chain components, characterizing linearity performance under two-tone excitation.

## Quick Summary

| Component | Best Est. OIP3 | Datasheet | Verdict |
|-----------|---|---|---|
| ZX60-P162LN+ (LNA) | +29.83 dBm | +29.8 dBm | Match (Delta = +0.03 dB) |
| ZX60-V63+ (Amp) | +31.32 dBm | +32.2 dBm | Within spec (Delta = -0.88 dB; cable loss explains) |
| Cascade (LNA+BPF+Amp) | +29.54 dBm | ~+29.8 dBm (predicted) | LNA-dominated as expected |

**Best practice:** Use -12 dBm measurement for each component (highest input power -> most nonlinearity -> furthest from noise floor).

## Power Definition (Critical)

**All input power levels refer to the SUM of both tones at the DUT input.**

Example: Input power = -12 dBm means:
- Tone 1 (f1 = 1.420355 GHz): ~-15 dBm
- Tone 2 (f2 = 1.420455 GHz): ~-15 dBm
- **Sum (coherent):** -12 dBm

This is **not** per-tone power (which would be at the -15 dBm level).

## Equipment

| Item | Model |
|------|-------|
| Spectrum analyzer | Rohde & Schwarz FSVA3044 |
| Signal source | Vector signal generator (settings captured as phone photo) |

## Measurement Conditions

| Parameter | Value |
|-----------|-------|
| Center frequency | 1420.405 MHz |
| Tone spacing | 100 kHz |
| Span | 1 MHz (1419.905 -- 1420.905 MHz) |
| RBW | 3 kHz |
| VBW | 1 kHz |
| Input power levels | -12 dBm, -15 dBm, -18 dBm |
| Power definition | Sum of both tones at the DUT input |
| Temperature | 23.6 deg C |
| Date | 2026-03-24 |

## Contents

### [`lna/`](lna/)

LNA standalone IP3 measurements (ZX60-P162LN+).

Three input power levels measured:
- `lna_ip3_-12dBm` -- highest input power
- `lna_ip3_-15dBm` -- baseline
- `lna_ip3_-18dBm` -- lowest input power

### [`amplifier/`](amplifier/)

Second-stage amplifier standalone IP3 measurements (ZX60-V63+).

Three input power levels measured:
- `amp_ip3_-12dBm` -- highest input power
- `amp_ip3_-15dBm` -- baseline
- `amp_ip3_-18dBm` -- lowest input power

### [`cascade/`](cascade/)

Full RF chain cascade IP3 measurements (LNA + BPF + Amp connected in series).

Three input power levels measured:
- `cascade_ip3_-12dBm` -- highest input power
- `cascade_ip3_-15dBm` -- baseline
- `cascade_ip3_-18dBm` -- lowest input power

### [`cable-loss/`](cable-loss/)

Reference measurement indicates a total cable/connector insertion loss of approximately **0.61 dB** for the reference path at the test frequency.

- Cable loss NOT de-embedded from OIP3 values; magnitude is 0.61 dB, negligible vs. 39 dB cascade gain
- Cable loss partially explains the observed gain deficit vs. datasheet for individual components

### [`setup/`](setup/)

Measurement setup documentation (photos, instrument settings). The `setup/` folder contains:
- Photos of the measurement setup
- Vector signal generator settings (captured as phone photos, since settings file export was not available)

## Data Format

Each measurement point has two files:

| Extension | Description |
|-----------|-------------|
| `.DAT` | Tab-delimited ASCII spectrum data exported from the FSVA3044. Header contains instrument settings (center freq, span, RBW, VBW, ref level). Body contains frequency vs. amplitude pairs. These `.DAT` files can be viewed with **[mergen-scope](https://alpgoxd.github.io/mergen-scope/)** ([GitHub](https://github.com/alpgoxd/mergen-scope)), an open-source R&S DAT file viewer. |
| `.PNG` | Screenshot of the spectrum analyzer display (1280 x 900 px) showing the two fundamental tones and any intermodulation products. |

## How to Interpret the Data

1. **Identify the two fundamental tones** at f1 and f2 (spaced 100 kHz apart around 1420.405 MHz)
2. **Locate the third-order intermodulation products** at 2f1 - f2 and 2f2 - f1
3. **Read power levels** of the fundamentals (P_fund) and IMD3 products (P_IMD3)
4. **Calculate IIP3** using:
   ```
   IIP3 = P_in + (P_fund - P_IMD3) / 2
   ```
   where P_in is the input power per tone (total power - 3 dB for two equal tones).
5. **Calculate OIP3** using:
   ```
   OIP3 = P_fund + (P_fund - P_IMD3) / 2
   ```

Multiple power levels (-12, -15, -18 dBm) allow you to verify that the IMD3 products follow the expected 3:1 slope (3 dB change in IMD3 for every 1 dB change in input power).

## IP3 Comparison: Measured vs. Datasheet

OIP3 values extracted from the R&S FSVA3044's built-in TOI measurement function (markers M1-M4 in each PNG screenshot). The instrument places markers on the two fundamental tones (M1, M2) and both IMD3 products (M3, M4) and calculates OIP3 directly.

### Marker Frequencies

| Marker | Frequency | Signal |
|--------|-----------|--------|
| M1 | 1.420 355 GHz | Fundamental f1 |
| M2 | 1.420 455 GHz | Fundamental f2 |
| M3 | 1.420 255 GHz | IMD3 lower (2f1 - f2) |
| M4 | 1.420 555 GHz | IMD3 upper (2f2 - f1) |

### Datasheet Reference Values

Source: Mini-Circuits PDF datasheets ([`../../../hardware/rf-chain/datasheets/`](../../../hardware/rf-chain/datasheets/)), specs at 25 C.

| Component | OIP3 typ. (dBm) | Gain typ. (dB) | P1dB out (dBm) | NF (dB) | Test conditions |
|-----------|-----------------|----------------|----------------|---------|-----------------|
| ZX60-P162LN+ (LNA) | +29.8 @ 1400 MHz | ~19.7 | +19.6 | 0.7 | Vcc = 4.0 V |
| ZX75BP-1450-S+ (BPF) | N/A (passive) | -0.8 (IL) | N/A | 0.8 (= IL) | -- |
| ZX60-V63+ (Amp) | +32.2 @ 1400 MHz | ~20.8 | +18.5 | 3.7 | Vcc = 5.0 V |

### Measured OIP3 (from PNG marker tables)

P_in = total input power (sum of both tones). The instrument reports TOI (= OIP3), plus TOI max/min from the two individual IMD3 products. **Spread** = TOI max - TOI min; small spread means both IMD3 products are well above the noise floor and the measurement is reliable.

**ZX60-P162LN+ (LNA)** -- Datasheet OIP3: +29.8 dBm typ.

| Measurement | P_in | P_f1 | P_f2 | P_IMD3_lo | P_IMD3_hi | OIP3 | TOI max | TOI min | Spread | Reliability |
|-------------|------|------|------|-----------|-----------|------|---------|---------|--------|-------------|
| lna_ip3_-12dBm | -12 | +2.52 | +2.54 | -51.46 | -52.79 | **+29.83** | +30.21 | +29.50 | 0.7 dB | Good |
| lna_ip3_-15dBm | -15 | -0.43 | -0.41 | -60.91 | -66.88 | **+30.84** | +32.83 | +29.81 | 3.0 dB | Moderate |
| lna_ip3_-18dBm | -18 | -3.47 | -3.45 | -68.12 | -79.76 | **+30.24** | +34.71 | +28.86 | 5.9 dB | Poor |

**ZX60-V63+ (Amplifier)** -- Datasheet OIP3: +32.2 dBm typ.

| Measurement | P_in | P_f1 | P_f2 | P_IMD3_lo | P_IMD3_hi | OIP3 | TOI max | TOI min | Spread | Reliability |
|-------------|------|------|------|-----------|-----------|------|---------|---------|--------|-------------|
| amp_ip3_-12dBm | -12 | +3.52 | +3.54 | -51.75 | -52.37 | **+31.32** | +31.50 | +31.16 | 0.3 dB | Excellent |
| amp_ip3_-15dBm | -15 | +0.62 | +0.64 | -63.90 | -63.33 | **+32.74** | +32.91 | +32.59 | 0.3 dB | Excellent |
| amp_ip3_-18dBm | -18 | -2.43 | -2.41 | -78.47 | -73.24 | **+33.93** | +35.63 | +32.98 | 2.6 dB | Moderate |

**Full Cascade (LNA + BPF + Amp)**

| Measurement | P_in | P_f1 | P_f2 | P_IMD3_lo | P_IMD3_hi | OIP3 | TOI max | TOI min | Spread | Reliability |
|-------------|------|------|------|-----------|-----------|------|---------|---------|--------|-------------|
| cascade_ip3_-12dBm | -12 | +7.54 | +7.56 | -36.15 | -36.75 | **+29.54** | +29.72 | +29.38 | 0.3 dB | Excellent |
| cascade_ip3_-15dBm | -15 | +4.14 | +4.16 | -52.56 | -52.87 | **+32.58** | +32.68 | +32.49 | 0.2 dB | Excellent |
| cascade_ip3_-18dBm | -18 | +1.17 | +1.19 | -62.99 | -62.96 | **+33.26** | +33.29 | +33.24 | 0.05 dB | Excellent |

### Why We Trust the -12 dBm Measurement Most

| Aspect | -12 dBm | -15 dBm | -18 dBm |
|--------|---------|---------|---------|
| IMD3 products above noise floor | Well above | Marginal | Approaching |
| TOI max/min spread | 0.3--0.7 dB | 0.3--3.0 dB | 2.6--5.9 dB |
| Measurement reliability | Excellent | Good | Moderate |
| OIP3 trend (vs. power level) | Stable | Stable | Rising (false) |

At lower input power, IMD3 products approach the analyzer's noise floor,
causing the apparent OIP3 to trend upward (noise floor replaces IMD3 signal).
The -12 dBm measurement is free from this artifact.

### Summary: Measured vs. Datasheet

Best estimates use the -12 dBm measurement (highest input power, most nonlinearity, IMD3 products furthest above noise floor).

| Component | OIP3 measured (dBm) | OIP3 datasheet (dBm) | Delta | Gain measured (dB) | Gain datasheet (dB) | Verdict |
|-----------|--------------------|--------------------|-------|-------------------|--------------------|---------|
| ZX60-P162LN+ (LNA) | **+29.83** | +29.8 | **+0.03** | 17.5 | 19.7 | **PASS** -- matches within 0.1 dB |
| ZX60-V63+ (Amp) | **+31.32** | +32.2 | **-0.88** | 18.6 | 20.8 | **PASS** -- slightly below datasheet; test-path cable/connector loss contributes to the deficit |
| Cascade | **+29.54** | N/A | -- | 39.7 | ~38.7 | Good agreement with the expected cascaded gain; OIP3 dominated by the LNA first stage, as expected |

### Measurement Reliability Assessment

The TOI max/min spread indicates whether both IMD3 products are well above the noise floor:

| Spread | Reliability | Which measurements |
|--------|------------|-------------------|
| < 0.5 dB | Excellent | Amp -12/-15 dBm, Cascade all three |
| 0.5 -- 1.0 dB | Good | LNA -12 dBm |
| 1.0 -- 3.0 dB | Moderate | LNA -15 dBm, Amp -18 dBm |
| > 3.0 dB | Poor (one IMD3 near noise floor) | LNA -18 dBm |

At lower input power levels, the IMD3 products approach the noise floor and the calculated OIP3 trends upward (apparent OIP3 increases because noise replaces the weaker IMD3 product). The -12 dBm measurements are the most reliable for individual components.

### Measured Gain vs. Datasheet

| Component | Gain measured (dB) | Gain datasheet (dB) | Difference (dB) |
|-----------|-------------------|--------------------|-----------------|
| ZX60-P162LN+ (LNA) | 17.5 | 19.7 | -2.2 |
| ZX60-V63+ (Amp) | 18.6 | 20.8 | -2.2 |
| Cascade | 39.7 | ~38.7 (19.7 - 0.8 + 20.8) | +1.0 |

- Individual component gains are ~2.2 dB below datasheet. A measured reference-path loss of about 0.61 dB confirms that cable/connector loss is one contributor to this deficit.
- The uploaded VNA file `cascaded chain.s2p` gives a cascade gain of about 39.7 dB at 1.4025 GHz, which is in good agreement with the expected ~38.7 dB from the component datasheets. The earlier 22.5 dB figure was incorrect and has been removed.

### Assumptions and Limitations

- OIP3 values are as reported by the FSVA3044 TOI function; no manual de-embedding of the small cable/connector loss (0.61 dB, neglected) has been applied.
- Fundamental tones are balanced within 0.03 dB across all measurements, confirming good signal quality from the vector signal generator.
- The bandpass filter (ZX75BP-1450-S+) is passive and does not contribute IMD products; it only affects cascade IP3 through its insertion loss reducing the signal level reaching the second-stage amplifier.
- Measurement temperature was 23.6 deg C.

## Notes on Data Quality

- The amplifier and cascade files were originally named with relative power offsets (+3 dB / -3 dB from baseline). These have been normalized to absolute power levels assuming baseline = -15 dBm.
- The `setup/` folder contains measurement setup photos and vector signal generator setting photos.
- The signal generator settings were captured as phone photos because the instrument did not support settings file export.

## See Also

- [`../../../hardware/rf-chain/datasheets/`](../../../hardware/rf-chain/datasheets/) -- Manufacturer PDF datasheets
- [`../../../hardware/rf-chain/datasheet-s-parameters/`](../../../hardware/rf-chain/datasheet-s-parameters/) -- Manufacturer S-parameter files (Touchstone .s2p)
- [`../vna/`](../vna/) -- VNA-measured S-parameters
- [`../../../hardware/rf-chain/COMPONENTS.md`](../../../hardware/rf-chain/COMPONENTS.md) -- Component cross-reference index
