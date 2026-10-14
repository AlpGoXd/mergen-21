# Verification: regenerated outputs against `reference_outputs/`

This file records a run of `software/analysis/mergen21_hi_analysis.py`,
`software/analysis/first_light_and_averaging.py` and
`software/analysis/stage_gains.py` against this checkout, and compares the
regenerated outputs in `software/analysis/outputs/` to the canonical values in
`software/analysis/reference_outputs/`.

## Environment

- Python 3.14.3, Windows 11 (Windows-11-10.0.26100-SP0)
- Packages (pinned in `software/requirements.txt`): numpy 2.4.4, scipy
  1.17.1, pandas 3.0.3, matplotlib 3.10.9, astropy 8.0.1
- `mergen21_hi_analysis.py` sets `iers.conf.auto_download = False`; this run
  was offline and no fresh IERS tables were downloaded. Galactic l/b and the
  motion correction can differ by up to about 0.1 (deg or km/s) from a run
  with fresh IERS tables.
- Commands run, from the repository root:
  ```
  python software/analysis/mergen21_hi_analysis.py --root . --outdir software/analysis/outputs
  python software/analysis/first_light_and_averaging.py --root . --outdir software/analysis/outputs
  python software/analysis/stage_gains.py
  ```
- The six CSV/JSON outputs (`averaging_noise.csv`,
  `mergen21_hi_line_parameters.csv`, `mergen21_hi_measurements.csv`,
  `mergen21_hi_derived.json`, `mergen21_data_manifest.csv`,
  `stage_gains.csv`) were then copied into `reference_outputs/`. A fresh run
  into a temporary directory reproduces all of them byte for byte (after
  normalizing CRLF to LF, which only matters for a Windows checkout of the
  committed files).
- `reference_outputs/mergen21_capture_metadata.csv` is not produced by any
  script; it is a hand-maintained table and was left unchanged.

## Verification table

| Quantity | Reference | Regenerated | Status |
|---|---|---|---|
| `averaging_noise.csv` E1 @ tau=1s `sigma_pct` | 3.528470 | 3.528470 | match |
| `averaging_noise.csv` E2 @ tau=1s `sigma_pct` | 3.526871 | 3.526871 | match |
| rows_used E1 / E2 / S / W | 98 / 165 / 97 / 100 | 98 / 165 / 97 / 100 | match |
| rows_skipped | 6 | 6 | match |
| n_pairs E1 @ tau=1/2/4/8 s | 49/24/12/6 | 49/24/12/6 | match |
| n_pairs E1 @ tau=16/24/32/48 s | 3/2/1/1 | 3/2/1/1 | match |
| `averaging_noise.csv` S, W @ tau=1s `sigma_pct` | 3.505305, 3.519058 | 3.505305, 3.519058 | match |
| `averaging_noise.csv` row count (E1, S, W: 8 block sizes each; E2: 7) | 31 | 31 | match |
| line-free channels in common mask | 1437 | 1437 | match |
| fitted peak % S/E/W | 18.13/7.87/5.45 | 18.13/7.87/5.45 | match |
| FWHM kHz S/E/W | 77.2/88.9/151.9 | 77.2/88.9/151.9 | match |
| centroid kHz S/E/W | 172.1/138.5/77.8 | 172.1/138.5/77.8 | match |
| galactic l (deg) S/E/W, elevation 30° | 12.8/87.5/7.3 | 12.8/87.5/7.3 | match |
| galactic b (deg) S/E/W, elevation 30° | -2.4/-35.5/73.8 | -2.4/-35.5/73.8 | match |
| v_bary_plus_solar / v_lsr (km/s) S | 38.2 / 1.8 | 38.2 / 1.8 | match |
| v_bary_plus_solar / v_lsr (km/s) E | 25.7 / -3.5 | 25.7 / -3.5 | match |
| v_bary_plus_solar / v_lsr (km/s) W | 1.8 / -14.7 | 1.8 / -14.7 | match |
| observer-motion line shift (kHz) S/E/W | 180.8/121.7/8.3 | 180.8/121.7/8.3 | match |
| noise figure, cable-corrected | 1.54 dB (-133.46 + 0.6 - (-173.9) - 39.5) | 1.54 dB | match |
| stage gains at 1420.405 MHz, VNA (dB) LNA/BPF/AMP/cascade | 19.24/-1.73/20.24/39.52 | 19.24/-1.73/20.24/39.52 | match |

## Changes against the previous reference set

`first_light_and_averaging.py` was revised for Fig. 7: panel (b) now shows all
four first-light records (E1, E2, S, W) with blocks up to 48 s against the
zero-parameter radiometer line 1/sqrt(B tau) with B = 813.8 Hz, and panel (c)
uses 0.5 s sweep rows (`TAU_ROW_SWEEP_S`). Regenerating changed:

- **`averaging_noise.csv`** (and its `reference_outputs/` copy): the 10 rows
  of the previous file are unchanged; 21 rows were added (E1 at tau = 24, 32,
  48 s; E2 at 4 and 8 s; S and W at tau = 1 to 48 s, 8 block sizes each). The
  `included` flag still marks tau = 1 to 8 s for E1, S and W and 0.1 to 1 s
  for E2. S and W at tau = 1 s are 3.505 % and 3.519 %, against 3.528 % (E1)
  and 3.527 % (E2).
- **`figures/first_light_and_averaging.pdf`/`.png`**: panels (b) and (c) as
  above; panel (a) is unchanged. These figures are not in `reference_outputs/`.
- Every other output is unchanged (`mergen21_hi_*`, `mergen21_data_manifest.csv`,
  `stage_gains.csv`).

An earlier refresh of `reference_outputs/`, which had gone stale, changed:

- **Elevation now 30°** (observer-stated, not instrumented; previously
  assumed 35). This moves
  `l_deg`, `b_deg`, `v_bary_plus_solar_kms`, `v_lsr_kms` and `motion_shift_kHz` (a new
  column, `v_bary_plus_solar_kms * F0 / c`) for the static
  pointings (previously S 17.2/-0.1, E 85.5/-30.8, W 22.0/71.4 for l/b, and
  39.0/2.6, 27.2/-2.1, 4.5/-11.9 km/s for the velocities), and
  `assumptions.pointing_elevation_deg_approximate` in the derived JSON. Peak,
  FWHM and centroid do not depend on elevation and are unchanged.
- **Sweep row cadence 0.5 → 1.0 s** (`frequency_axis.tau_per_row_s_sweep`, and
  `utc_mid`, `on_source_s`, `tau_row_s` for the withdrawn `SW01`-`SW12` rows).
  No static-pointing number changes.
- **`withdrawn.note`** now cites PROVENANCE_ADDENDUM.md sections 1 and 6.
- **Manifest.** Paths are written with forward slashes on every platform
  (`as_posix()`), and the hashes of `measurements/rf-chain/nf/README.md` and
  `software/gnuradio/receiver.grc` follow their current contents.

## Line endings and the manifest

The manifest records the byte count and sha256 of each input. To make it
identical on every platform:

- `.gitattributes` marks `*.s1p`, `*.s2p` and `*.DAT` as `-text` and `*.dat`,
  `*.npy` as `binary`, so instrument exports are never CRLF-converted on a
  Windows checkout. Previously `cable_loss.DAT` read as 65852 bytes on
  Windows (CRLF) against 64821 bytes stored; it now reads 64821 everywhere.
- The two hashed text files, `*.grc` and `measurements/rf-chain/nf/README.md`,
  are checked out with `eol=lf`.
- All CSV/JSON outputs are written with `\n` line endings.

## WOLA check

`software/analysis/wola_window_check.py` needs `wola_taps_firdes.npy` next to
it. That file is not committed, so the first run must design the taps with
GNU Radio's `firdes` (`gnuradio.fft.window`, `gnuradio.filter.firdes`). GNU
Radio is not installed in this environment, so the WOLA check was not run
here. It is reported as not run, not as passing or failing.

## Remaining caveat

Galactic l/b and the derived velocities depend on the offline IERS tables
(see Environment). A run with fresh IERS tables can differ by up to about
0.1 (deg or km/s); every other output is independent of IERS.
