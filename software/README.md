# Software Overview

Software stack for data acquisition and post-processing.

## Subfolders

- [`gnuradio/`](gnuradio/) - GNU Radio flowgraphs and acquisition notes
- [`analysis/`](analysis/) - Python analysis pipeline (calibration, line extraction, rotation curve)
- [`python-scripts/`](python-scripts/) - One-off utility scripts
- [`requirements.txt`](requirements.txt) - Python dependency list

## Viewing R&S DAT Files

`.DAT` files exported from the Rohde & Schwarz FSVA3044 can be opened with **[mergen-scope](https://alpgoxd.github.io/mergen-scope/)** ([GitHub](https://github.com/alpgoxd/mergen-scope)), an open-source R&S DAT file viewer.

## Current Status

- GNU Radio flowgraphs: in progress (structure ready, flowgraphs planned for commit)
- Analysis pipeline scripts: in progress (structure ready, scripts planned for commit)
- Utility scripts: available (`sanitize_sps.py`)

## Notes

This folder intentionally includes both stable utilities and in-progress research code.
