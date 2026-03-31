# RF Receive Chain

```
Antenna → ZX60-P162LN+ (LNA) → ZX75BP-1450-S+ (BPF) → ZX60-V63+ (Amp) → SDR
```

Center frequency: 1420.405 MHz | Bandwidth: ~50 MHz

- [`datasheets/`](datasheets/) — Manufacturer PDF datasheets for each component
- [`datasheet-s-parameters/`](datasheet-s-parameters/) — Mini-Circuits manufacturer S-parameter Touchstone files (`.s2p`) at multiple temperatures
- [`COMPONENTS.md`](COMPONENTS.md) — Cross-reference index: component → datasheet → S-parameters → measurements
- Cascade analysis results in [`../simulation/awr/`](../simulation/awr/)
- VNA measurements (measured vs. datasheet) in [`../../measurements/rf-chain/vna/`](../../measurements/rf-chain/vna/)
- IP3 / intermodulation measurements in [`../../measurements/rf-chain/ip3/`](../../measurements/rf-chain/ip3/)
