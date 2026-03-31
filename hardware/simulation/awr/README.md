# AWR Microwave Office — RF Chain Cascade Analysis

Cascaded S-parameter simulation of the full RF receive chain using manufacturer-provided `.s2p` data for each component. Individual component S-parameter files are in [`rf-chain/datasheet-s-parameters/`](../../rf-chain/datasheet-s-parameters/).

## Signal Path

```
Antenna → ZX60-P162LN+ (LNA) → ZX75BP-1450-S+ (BPF) → ZX60-V63+ (Amp) → pluto SDR
```

## Key Results

| Parameter | Value |
|-----------|-------|
| Peak cascaded gain (S21) | 40.7 dB @ 1.30 GHz |
| Gain at 1420 MHz | 39.9 dB |
| 3 dB passband | ~1.20–1.63 GHz |
| S11 at 1420 MHz | -18.0 dB |
| LNA noise figure | 0.7 dB @ 1420 MHz |
| Second amp noise figure | 3.7 dB |
| System NF (Friis) | ~0.7 dB (dominated by LNA) |

## Files

- `rf_chain_cascaded.s2p` — Cascaded 2-port S-parameters of the full chain (noise parameters in file are not valid, see note below)
- `rf_chain_gain.png` — S21 gain plot from AWR (0–2 GHz)
- `ZX60_P162LN_NF.txt` — Noise figure data for LNA, tabulated from datasheet
- `ZX60_V63_NF.txt` — Noise figure data for second amplifier, tabulated from datasheet

## Notes

- Component S-parameter data sourced from Mini-Circuits, freely available at [minicircuits.com](https://www.minicircuits.com)
- System noise figure: NF_sys ≈ NF₁ + (NF₂ − 1)/G₁ + (NF₃ − 1)/(G₁·G₂), heavily dominated by the first-stage LNA due to its high gain.
- The BPF center frequency is slightly below 1420 MHz, placing the HI line ~0.8 dB below peak gain — negligible impact on system performance.
