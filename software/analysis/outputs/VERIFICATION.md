# Verification: regenerated outputs against `reference_outputs/`

This file records a run of `software/analysis/mergen21_hi_analysis.py` and
`software/analysis/first_light_and_averaging.py` against this checkout, and
compares the regenerated outputs in `software/analysis/outputs/` to the
canonical values in `software/analysis/reference_outputs/`.

## Environment

- Python 3.14.3, Windows 11 (Windows-11-10.0.26100-SP0)
- Packages (pinned in `software/requirements.txt`, from `pip show` after
  `pip install`): numpy 2.4.4, scipy 1.17.1, pandas 3.0.3, matplotlib
  3.10.9, astropy 8.0.1
- `mergen21_hi_analysis.py` sets `iers.conf.auto_download = False`; this run
  was offline and no fresh IERS tables were downloaded. Per the script's own
  documentation, galactic l/b may differ from the
  reference by up to about 0.1 degree for this reason. This is exactly what
  was observed (see table below).
- Commands run, from the repository root:
  ```
  python software/analysis/mergen21_hi_analysis.py --root . --outdir software/analysis/outputs
  python software/analysis/first_light_and_averaging.py --root . --outdir software/analysis/outputs
  ```

## Verification table

| Quantity | Reference | Regenerated | Abs diff | Status |
|---|---|---|---|---|
| `averaging_noise.csv` E1 @ tau=1s `sigma_pct` | 3.528470 | 3.528470 | 0 | match |
| `averaging_noise.csv` E2 @ tau=1s `sigma_pct` | 3.526871 | 3.526871 | 0 | match |
| rows_used E1 | 98 | 98 | 0 | match |
| rows_used E2 | 165 | 165 | 0 | match |
| rows_skipped | 6 | 6 | 0 | match |
| n_pairs E1 @ tau=1/2/4/8s | 49/24/12/6 | 49/24/12/6 | 0 | match |
| line-free channels in common mask | 1437 | 1437 | 0 | match |
| fitted peak % S/E/W | 18.13/7.87/5.45 | 18.13/7.87/5.45 | 0 | match |
| FWHM kHz S/E/W | 77.2/88.9/151.9 | 77.2/88.9/151.9 | 0 | match |
| centroid kHz S/E/W | 172.1/138.5/77.8 | 172.1/138.5/77.8 | 0 | match |
| galactic l (deg) S/E/W, elevation 30° | 12.8/87.5/7.3 | 12.8/87.5/7.3 | 0 | match (elevation changed from 35° to 30°, observer-stated) |
| galactic b (deg) S/E/W, elevation 30° | -2.4/-35.5/73.8 | -2.4/-35.5/73.8 | 0 | match (elevation changed from 35° to 30°, observer-stated) |
| noise figure, cable-corrected | 1.54 dB (-133.46 + 0.6 - (-173.9) - 39.5) | 1.54 dB | 0 | match |

All values not listed as differing (fitted peak, FWHM, centroid, noise
figure, the `n_pairs`/`sigma_pct` averaging-noise table, and the raw data
manifest's byte counts/hashes for the four `.dat` captures) reproduce
exactly, to every quoted digit.

`mergen21_hi_derived.json`'s `noise_figure.corrected.nf_db` is 1.54, matching
`-133.46 + 0.6 - (-173.9) - 39.5 = 1.54` (`P_OUT + CABLE_LOSS - KT0 - GAIN`);
this is the direct cross-check against the derived JSON asked for in the
task, and it matches the reference JSON exactly.

## Byte-level diff / cmp summary

`diff` was run twice per file: raw, and with `--strip-trailing-cr` to factor
out line-ending differences.

- **`averaging_noise.csv`**: byte-for-byte identical in content
  (`diff --strip-trailing-cr` shows no differences). The raw `diff` reports
  every line as changed; this is caused entirely by the reference file being
  LF-only while pandas/Windows wrote the regenerated file with CRLF line
  endings, confirmed by inspecting both files' bytes directly (reference has
  no `\r\n`, regenerated is all `\r\n`). Not a data difference.
- **`mergen21_hi_measurements.csv`**: the three static rows (W, S, E) are
  identical to every quoted digit. The twelve sweep-block rows (`SW01`-`SW12`)
  differ only in `utc_mid`, `on_source_s`, and `tau_row_s`, which is the
  expected and intended effect of the `TAU_ROW_SWEEP_S` correction (see
  below); every other column for those rows, including centroid, amplitude,
  and FWHM, is unchanged.
- **`mergen21_hi_line_parameters.csv`**: `peak_pct`, `centroid_kHz`,
  `fwhm_kHz`, `fwhm_kms` match exactly for S/E/W. `l_deg`, `b_deg`,
  `v_bary_plus_solar_kms`, and `v_lsr_kms` differ by up to 0.1 (deg or
  km/s), consistent with the offline-IERS caveat.
- **`mergen21_data_manifest.csv`**: the four capture files' `bytes`/`sha256`
  are identical to the reference. Two differences, both environmental
  rather than raw-data changes, are described under Findings below: (1)
  path separators are OS-native (`\` on this Windows run vs `/` in the
  reference), and (2) the four auxiliary/calibration files under
  `measurements/rf-chain/nf/` and `software/gnuradio/receiver.grc` show
  different `bytes`/`sha256` than the reference.
- **`mergen21_hi_derived.json`**: identical except (a) `tau_per_row_s_sweep`
  (0.5 -> 1.0, the intended effect of the TAU_ROW_SWEEP_S correction), and
  (b) the `withdrawn.note` text, which already differed between the shipped
  script and `reference_outputs/` before any edit in this pass (see
  Findings).

## TAU_ROW_SWEEP_S before/after check (task 3)

Ran `mergen21_hi_analysis.py` with `TAU_ROW_SWEEP_S = 0.5` (as received) into
a scratch directory, then again with `TAU_ROW_SWEEP_S = 1.0` (the corrected
value) into another scratch directory, and diffed every output.

Result: **no static-pointing or manuscript-quoted number changed.**
`mergen21_hi_line_parameters.csv` (the S/E/W summary table) is byte-for-byte
identical between the two runs. `mergen21_data_manifest.csv` is identical.
The only differences are, as expected, confined to the withdrawn sweep
analysis: the twelve `SW01`-`SW12` rows' `utc_mid`, `on_source_s`, and
`tau_row_s` in `mergen21_hi_measurements.csv`, and
`frequency_axis.tau_per_row_s_sweep` in `mergen21_hi_derived.json`. The
sweep analysis is withdrawn per `docs/analysis/PROVENANCE_ADDENDUM.md`
section 1, so none of these changed values are quoted by the paper. The edit
was kept.

## WOLA check (task 5, script half)

`software/analysis/wola_window_check.py` requires `wola_taps_firdes.npy`
next to it, which does not exist in this checkout (confirmed:
`software/analysis/wola_taps_firdes.npy` is absent). Regenerating it needs
`--regenerate`, which imports `gnuradio.fft.window` and
`gnuradio.filter.firdes`. This environment does not have GNU Radio
installed: `import gnuradio` raises `ModuleNotFoundError: No module named
'gnuradio'`, and neither `grcc` nor `gnuradio-companion` is on PATH.

**The WOLA check could not be run in this environment and is reported as
blocked, not as passing or failing.** No `.npy` file was created or
committed, and no numpy reimplementation of `firdes.low_pass` was written to
stand in for GNU Radio's output.

As a side observation only (not a substitute for the real check): the
number of taps the eight WOLA branches actually consume is
`K_BRANCHES * FFT_SIZE = 8 * 2048 = 16384`, which is a fixed geometric
quantity independent of `firdes` and requires no GNU Radio to compute. This
says nothing about how many taps `firdes.low_pass` itself designs (reported
in the script's docstring as 32299, from a prior GNU Radio run); that number
can only come from GNU Radio's `firdes`, which is not available here.

## Findings

1. **Galactic l/b and derived velocities differ by up to 0.1 (deg or
   km/s).** Expected per the offline-IERS caveat documented in
   `mergen21_hi_analysis.py`. Not a code issue.

2. **`mergen21_data_manifest.csv` path separators are OS-native.**
   `manifest()` builds the `path` column with
   `capture_path(root, fn).relative_to(root)`, which on Windows yields
   backslash-separated paths (`observations\data\...`) where the reference
   (generated on a POSIX system) has forward slashes. This is a
   cross-platform formatting difference in the manifest, not a change to
   any raw file's content, byte count, or hash. The code was not changed
   to match the reference format during this run.

3. **Four auxiliary/calibration files in the manifest show different
   `bytes`/`sha256` than the reference**, for
   `measurements/rf-chain/nf/cable_loss.DAT`,
   `measurements/rf-chain/nf/just cooked reciver.DAT`,
   `measurements/rf-chain/nf/match noise.DAT`, and
   `software/gnuradio/receiver.grc`. Diagnosis:
   - The three `.DAT` files: byte-count increases are each exactly equal to
     that file's line count (verified for `cable_loss.DAT`: reference
     64821 bytes vs. regenerated 65852 bytes, a difference of 1031 bytes,
     and the checked-out file has exactly 1031 line endings, all `\r\n`).
     This is Git's `autocrlf` normalizing these text-format VNA/power-meter
     exports to CRLF on this Windows checkout; the reference manifest was
     generated on a system where they stayed LF-only. No data value in
     these files changed; only the line-ending bytes did. Raw measurement
     files under `measurements/` were not modified.
   - `software/gnuradio/receiver.grc`: this file was edited during the
     same release preparation to correct its saved `integration_time`
     default from 500 to 1000 and add a provenance comment. The manifest
     hash difference reflects that edit, not an error in the analysis
     scripts.

4. **`mergen21_hi_derived.json`'s `withdrawn.note` text already differed
   from `reference_outputs/` before this verification run.** The
   script reads "...the
   azimuth mapping is withdrawn. See PROVENANCE_ADDENDUM.md **sections 1
   and 6**." while the shipped reference file reads "...**section 1**."
   only. This is a wording-only difference (which PROVENANCE_ADDENDUM.md
   section(s) are cited), not a numeric one; it predates this verification run
   and was left unchanged.

5. **No other regenerated value disagrees with the reference.** Every
   fitted line parameter (amplitude, centroid, FWHM), every averaging-noise
   row, the line-free channel count, and the noise-figure arithmetic
   (including the cable-corrected 1.54 dB) reproduce exactly.
