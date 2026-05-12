# Software

Data acquisition and analysis stack for Mergen-21.

## Structure

```
software/
├── gnuradio/       GNU Radio flowgraphs (acquisition)
├── analysis/       Python analysis scripts
└── requirements.txt
```

## Subfolders

- [`gnuradio/`](gnuradio/) — GNU Radio flowgraphs for the ADALM-PLUTO SDR
- [`analysis/`](analysis/) — Spectrum viewer, utilities, and calibration pipeline

## Viewing R&S DAT Files

`.DAT` files from the Rohde & Schwarz FSVA3044 can be opened with **[mergen-scope](https://alpgoxd.github.io/mergen-scope/)** ([GitHub](https://github.com/alpgoxd/mergen-scope)).

## Install

```bash
pip install -r requirements.txt
```
