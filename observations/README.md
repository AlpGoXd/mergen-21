# Observation Data

Raw telescope observations of the 21 cm hydrogen line (1420.405 MHz).

## Data Organization

Files follow naming: `YYYYMMDD_HHMM_lXXX_bYYY.c64`

- `YYYYMMDD` -- Observation date (ISO 8601)
- `HHMM` -- Start time (UTC)
- `lXXX` -- Galactic longitude (deg, 0--360)
- `bYYY` -- Galactic latitude (deg, -90 to +90)
- `.c64` -- Complex 32-bit float (ADALM-PLUTO native)

## Contents

- `data/` -- Raw observation files (*.c64, *.metadata.txt)
- `plots/` -- Generated figures (spectra, dynamic spectra, profiles)

## Site

- **Location:** Istanbul, Turkey (~41.0 deg N, 29.0 deg E)

[To be populated after first-light observations]
