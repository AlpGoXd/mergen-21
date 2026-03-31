# Measurements

Real-world measurements taken with calibrated test equipment, covering the RF chain components, full cascade, and the horn antenna.

## Equipment

| Item | Model |
|------|-------|
| VNA | Rohde & Schwarz ZNB8 |
| Spectrum Analyzer | Rohde & Schwarz FSVA3044 |
| Calibration kit | ZV-Z270 |
| Calibration method | TOSM (full 2-port) |



## Contents

- [`rf-chain/`](rf-chain/) — All RF chain measurements, organized by type:
  - [`rf-chain/vna/`](rf-chain/vna/) — VNA-measured S-parameters using R&S ZNB8 (individual components + full cascade)
  - [`rf-chain/ip3/`](rf-chain/ip3/) — IP3 / intermodulation measurements (LNA, amp, cascade, cable-loss reference)
  - [`rf-chain/nf/`](rf-chain/nf/) — Noise figure measurements *(measured)*
- [`extras/`](extras/) — Test/debug components not in the final signal path (attenuators, 50 ohm matches)
- [`antenna/`](antenna/) — Horn antenna S11 measurements under various conditions, plus manufacturing defect documentation

## File Conventions

Each measurement folder contains:
- `.s2p` — Touchstone S-parameter data exported from the ZNB8
- `.pdf` — VNA screenshot/export showing S21 and S11 plots

## Viewing DAT Files

`.DAT` files in this folder are tab-delimited ASCII exports from the Rohde & Schwarz FSVA3044 spectrum analyzer. They can be opened with **[mergen-scope](https://alpgoxd.github.io/mergen-scope/)** ([GitHub](https://github.com/alpgoxd/mergen-scope)), an open-source R&S DAT file viewer.

## See Also

- [`hardware/rf-chain/datasheet-s-parameters/`](../hardware/rf-chain/datasheet-s-parameters/) — Manufacturer S-parameter files (Mini-Circuits)
- [`hardware/rf-chain/datasheets/`](../hardware/rf-chain/datasheets/) — Manufacturer PDF datasheets
- [`hardware/simulation/awr/`](../hardware/simulation/awr/) — AWR cascade simulation using datasheet data
- [`hardware/simulation/cst/`](../hardware/simulation/cst/) — CST antenna EM simulations
