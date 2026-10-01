# RF Chain Measurements

Lab characterisation of the three-stage RF receiver front-end (LNA → BPF → amplifier). All measurements were performed at room temperature with a Rohde & Schwarz ZNB8 VNA and FSVA3044 spectrum analyser.

## Cascade Summary

| Parameter | Value | Method |
|---|---|---|
| Gain (LNA + BPF + Amp) | 39.5 dB +/- 0.5 dB | VNA S21 (~42.5 MHz point spacing; no sample exactly at 1420.405 MHz, nearest points 1402.50835 MHz and 1445.0083 MHz) |
| Noise figure (cascade, cable-corrected) | about 1.5 dB (1.54 dB) | Gain-method output-noise measurement; see `nf/README.md` for the arithmetic |
| OIP3 (cascade) | +29.54 dBm | Two-tone, −12 dBm/tone input |

## Directory Structure

```
rf-chain/
├── vna/        VNA S-parameter measurements (.s2p + .pdf per component)
│   ├── ZX60-P162LN+/       LNA S-parameters
│   ├── ZX60-V63+/          Second amplifier S-parameters
│   ├── ZX75BP-1450-S+/     Bandpass filter S-parameters
│   └── cascade/            Cascaded chain S-parameters
├── nf/         Noise figure measurements (.DAT + .PNG, Rohde & Schwarz format)
└── ip3/        Intermodulation / OIP3 measurements
    ├── lna/        LNA alone
    ├── amplifier/  ZX60-V63+ alone
    └── cascade/    Full chain
```

## VNA Measurements (`vna/`)

Each component has:
- `.s2p` — Touchstone S-parameter file (S11, S21, S12, S22 vs frequency)
- `.pdf` — VNA plot exported from the ZNB8

The `cascade/` subdirectory contains `cascaded chain.s2p`, the end-to-end S21 of the full chain (horn N-type connector to PlutoSDR SMA input).

The single-stage files are not de-embedded; the filter file includes test adapters and cables, which is why the stages sum to 37.8 dB against the 39.5 dB cascade. The cascade file is the reference for the chain gain. `software/analysis/stage_gains.py` computes all stage gains at 1420.405 MHz.

Compare with datasheet S-parameters in `hardware/rf-chain/datasheet-s-parameters/`.

## Noise Figure Measurements (`nf/`)

Measured with the R&S FSVA3044 using the gain method: the output noise density of the chain with its input terminated in 50 Ω, minus the known chain gain (not a Y-factor measurement). Files:
- `cable_loss.DAT` / `.PNG` — Cable insertion loss at 100 kHz steps (used for loss correction)
- `just cooked reciver.DAT` / `.PNG` — First NF measurement of the assembled receiver
- `match noise.DAT` — Repeated measurement after connector reseating (more consistent)
- `match noise again.PNG` — Overlay confirming repeatability

Setup photos are in `nf/setup/`.

## IP3 / Intermodulation Measurements (`ip3/`)

Two-tone IP3 test at three input power levels (−12, −15, −18 dBm per tone) for:
- LNA alone
- Second amplifier alone
- Full cascade

Each set contains `.DAT` (spectrum analyser trace data) and `.PNG` plots. Setup photos (VSG settings, bench layout) are in `ip3/setup/`.

See `hardware/rf-chain/COMPONENTS.md` for the component cross-reference linking these measurements to datasheet S-parameters and AWR simulations.
