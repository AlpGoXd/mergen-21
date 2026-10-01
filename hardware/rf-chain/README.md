# RF Receive Chain

```
Antenna → ZX60-P162LN+ (LNA) → ZX75BP-1450-S+ (BPF) → ZX60-V63+ (Amp) → SDR
```

Center frequency: 1420.405 MHz | Bandpass filter (datasheet `ZX75BP-1450-S+_Plus25degC.s2p`): 1 dB passband 1254–1625 MHz, 3 dB passband 1230–1645 MHz, insertion loss 0.79 dB at 1420.4 MHz, maximum at 1435 MHz

- [`datasheets/`](datasheets/) — Manufacturer PDF datasheets for each component
- [`datasheet-s-parameters/`](datasheet-s-parameters/) — Mini-Circuits manufacturer S-parameter Touchstone files (`.s2p`) at multiple temperatures
- [`COMPONENTS.md`](COMPONENTS.md) — Cross-reference index: component → datasheet → S-parameters → measurements
- Cascade analysis results in [`../simulation/awr/`](../simulation/awr/)
- VNA measurements (measured vs. datasheet) in [`../../measurements/rf-chain/vna/`](../../measurements/rf-chain/vna/)
- IP3 / intermodulation measurements in [`../../measurements/rf-chain/ip3/`](../../measurements/rf-chain/ip3/)
