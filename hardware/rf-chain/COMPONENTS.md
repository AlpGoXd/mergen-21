# Component Cross-Reference Index

Quick-reference mapping each RF chain component to its manufacturer data, lab measurements, and simulation files.

## RF Chain Signal Path

```
Antenna → ZX60-P162LN+ (LNA) → ZX75BP-1450-S+ (BPF) → ZX60-V63+ (Amp) → SDR
           Stage 1                 Stage 2                 Stage 3
```

## Component Index

### Stage 1: ZX60-P162LN+ (Low-Noise Amplifier)

| Resource | Path |
|----------|------|
| Manufacturer PDF | [`datasheets/ZX60-P162LN+.pdf`](datasheets/ZX60-P162LN+.pdf) |
| Manufacturer S2P (-45 C) | [`datasheet-s-parameters/ZX60-P162LN+/ZX60-P162LN+_4V_Minus45degC.s2p`](datasheet-s-parameters/ZX60-P162LN+/ZX60-P162LN+_4V_Minus45degC.s2p) |
| Manufacturer S2P (+25 C) | [`datasheet-s-parameters/ZX60-P162LN+/ZX60-P162LN+_4V_Plus25degC.s2p`](datasheet-s-parameters/ZX60-P162LN+/ZX60-P162LN+_4V_Plus25degC.s2p) |
| Manufacturer S2P (+85 C) | [`datasheet-s-parameters/ZX60-P162LN+/ZX60-P162LN+_4V_Plus85degC.s2p`](datasheet-s-parameters/ZX60-P162LN+/ZX60-P162LN+_4V_Plus85degC.s2p) |
| VNA measurement | [`../../measurements/rf-chain/vna/ZX60-P162LN+/mesured_ZX60-P162LN+.s2p`](../../measurements/rf-chain/vna/ZX60-P162LN+/mesured_ZX60-P162LN+.s2p) |
| VNA plot | [`../../measurements/rf-chain/vna/ZX60-P162LN+/mesured_ZX60-P162LN+.pdf`](../../measurements/rf-chain/vna/ZX60-P162LN+/mesured_ZX60-P162LN+.pdf) |
| IP3 measurements | [`../../measurements/rf-chain/ip3/lna/`](../../measurements/rf-chain/ip3/lna/) |

### Stage 2: ZX75BP-1450-S+ (Bandpass Filter)

| Resource | Path |
|----------|------|
| Manufacturer PDF | [`datasheets/ZX75BP-1450-S+.pdf`](datasheets/ZX75BP-1450-S+.pdf) |
| Manufacturer S2P (-40 C) | [`datasheet-s-parameters/ZX75BP-1450-S+/ZX75BP-1450-S+_Minus40degC.s2p`](datasheet-s-parameters/ZX75BP-1450-S+/ZX75BP-1450-S+_Minus40degC.s2p) |
| Manufacturer S2P (+25 C) | [`datasheet-s-parameters/ZX75BP-1450-S+/ZX75BP-1450-S+_Plus25degC.s2p`](datasheet-s-parameters/ZX75BP-1450-S+/ZX75BP-1450-S+_Plus25degC.s2p) |
| Manufacturer S2P (+85 C) | [`datasheet-s-parameters/ZX75BP-1450-S+/ZX75BP-1450-S+_Plus85degC.s2p`](datasheet-s-parameters/ZX75BP-1450-S+/ZX75BP-1450-S+_Plus85degC.s2p) |
| VNA measurement | [`../../measurements/rf-chain/vna/ZX75BP-1450-S+/mesured_ZX75BP-1450+filter.s2p`](../../measurements/rf-chain/vna/ZX75BP-1450-S+/mesured_ZX75BP-1450+filter.s2p) |
| VNA plot | [`../../measurements/rf-chain/vna/ZX75BP-1450-S+/mesured_ZX75BP-1450+.pdf`](../../measurements/rf-chain/vna/ZX75BP-1450-S+/mesured_ZX75BP-1450+.pdf) |
| IP3 measurements | N/A (passive component -- IP3 not applicable) |

### Stage 3: ZX60-V63+ (Second-Stage Amplifier)

| Resource | Path |
|----------|------|
| Manufacturer PDF | [`datasheets/ZX60-V63+.pdf`](datasheets/ZX60-V63+.pdf) |
| Manufacturer S2P (-45 C) | [`datasheet-s-parameters/ZX60-V63+/ZX60-V63+_5V_Minus45DegC.s2p`](datasheet-s-parameters/ZX60-V63+/ZX60-V63+_5V_Minus45DegC.s2p) |
| Manufacturer S2P (+25 C) | [`datasheet-s-parameters/ZX60-V63+/ZX60-V63+_5V_Plus25DegC.s2p`](datasheet-s-parameters/ZX60-V63+/ZX60-V63+_5V_Plus25DegC.s2p) |
| Manufacturer S2P (+85 C) | [`datasheet-s-parameters/ZX60-V63+/ZX60-V63+_5V_Plus85DegC.s2p`](datasheet-s-parameters/ZX60-V63+/ZX60-V63+_5V_Plus85DegC.s2p) |
| VNA measurement | [`../../measurements/rf-chain/vna/ZX60-V63+/mesured_ZX60-V63+.s2p`](../../measurements/rf-chain/vna/ZX60-V63+/mesured_ZX60-V63+.s2p) |
| VNA plot | [`../../measurements/rf-chain/vna/ZX60-V63+/mesured_ZX60-V63+.pdf`](../../measurements/rf-chain/vna/ZX60-V63+/mesured_ZX60-V63+.pdf) |
| IP3 measurements | [`../../measurements/rf-chain/ip3/amplifier/`](../../measurements/rf-chain/ip3/amplifier/) |

### Full Cascade

| Resource | Path |
|----------|------|
| VNA measurement (cascade) | [`../../measurements/rf-chain/vna/cascade/cascaded chain.s2p`](../../measurements/rf-chain/vna/cascade/cascaded chain.s2p) |
| VNA plot (cascade) | [`../../measurements/rf-chain/vna/cascade/cascade chain.pdf`](../../measurements/rf-chain/vna/cascade/cascade chain.pdf) |
| IP3 measurements (cascade) | [`../../measurements/rf-chain/ip3/cascade/`](../../measurements/rf-chain/ip3/cascade/) |
| AWR cascade simulation | [`../simulation/awr/rf_chain_cascaded.s2p`](../simulation/awr/rf_chain_cascaded.s2p) |

## Datasheets vs. S-Parameter Files

| Type | What it is | Format | Location |
|------|-----------|--------|----------|
| **PDF Datasheet** | Complete manufacturer data sheet with specifications, application notes, pin diagrams, absolute maximum ratings, and typical performance curves | `.pdf` | [`datasheets/`](datasheets/) |
| **S-Parameter File** | Frequency-dependent scattering parameters (S11, S21, S12, S22) extracted from the manufacturer's characterization data. Used for circuit simulation and cascade analysis. | `.s2p` (Touchstone) | [`datasheet-s-parameters/`](datasheet-s-parameters/) |
| **VNA Measurement** | S-parameters measured in-house with a calibrated VNA. Reflects the actual device performance (including PCB, connectors, bias). | `.s2p` + `.pdf` | [`../../measurements/rf-chain/vna/`](../../measurements/rf-chain/vna/) |

The manufacturer S-parameter files come from Mini-Circuits' website and are provided at multiple temperatures (-45/40 C, +25 C, +85 C). The VNA measurements were taken at room temperature with the actual components soldered onto the RF chain PCB.

## Missing Data

<!-- Update this section as data is added -->
- [ ] Add per-stage NF comparison table once stage-level noise measurements are available.
