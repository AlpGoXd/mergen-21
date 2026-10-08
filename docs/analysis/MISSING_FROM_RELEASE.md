# Missing from release: items the paper mentions but this audit could not find

This document reports, for each item below, whether it was found in the repository and at
what path, or whether it is absent. Nothing here is fabricated or reconstructed; each entry
reflects what was actually present in the working tree at the time of this audit
(2026-09-23, branch `paper-release`).

## 1. 50 ohm-terminated SDR capture (band-center artifact): now included

The paper's discussion of the band-center instrumental artifact (see
`software/analysis/mergen21_hi_analysis.py` line ~132, `first_light_and_averaging.py`
line ~83, and `docs/analysis/archive/mergen21_hi_methods_superseded.md` lines ~17-55, archived) refers to an artifact
that appears in the SDR power-spectrum output near band center.

- **Now included:** `observations/data/band_center_tests/` (re-measured 2026-10-08, Pluto input terminated
  in 50 ohms at three LO settings; see its README). The April sky files under `observations/data/` remain
  sky pointings.
- **Found, but a different measurement:** `measurements/extras/50ohm-match/` contains
  `MCL ANNE-50+.s1p` (a VNA S11 measurement of the 50 ohm matched load itself, i.e. how well
  it is matched) and `50-match.pdf`. This is a VNA characterization of the termination
  component, not an SDR power-spectrum capture, and it does not show the band-center
  artifact. Do not conflate the two: the matched-load S11 measurement exists; the SDR
  capture with that load on the Pluto input does not appear to be in the repository.

## 2. "Receiver connected vs. SDR input terminated" comparison spectra (0.056 dB SDR NF)

Searched the whole repository (all file types, filenames and content) for any reference to
an SDR-stage noise figure of about 0.056 dB, or to a paired comparison of "receiver
connected" vs. "SDR input terminated" spectra.

- The original receiver-connected comparison was not archived, and the receiver chain is no longer available. The SDR noise contribution is instead bounded by comparing the Pluto-terminated capture with the first-light sky records (same Pluto, gain and flowgraph): the SDR raises the system noise by about 4 % (0.18 dB). See `observations/data/band_center_tests/README.md`.

## 3. Output-cable loss file

- **`measurements/rf-chain/nf/cable_loss.DAT`: found.** Present alongside
  `cable_loss.PNG` in `measurements/rf-chain/nf/`. This is the file
  `software/analysis/mergen21_hi_analysis.py` (`CABLE_LOSS_DB = 0.6`, line ~94) references
  by path (`measurements/rf-chain/nf/cable_loss.DAT`).
- **`measurements/rf-chain/ip3/cable-loss/cable_loss_100kHz.DAT`: found**, alongside
  `cable_loss_100kHz.PNG`, at `measurements/rf-chain/ip3/cable-loss/`. This is a separate
  cable-loss measurement associated with the IP3 test setup (per
  `measurements/rf-chain/nf/README.md`'s "See Also" section, the IP3 and NF measurements
  share the same cable-loss reference value). It is not the file the analysis script reads;
  the script reads `nf/cable_loss.DAT` only.

## 4. Probe-trimming S11 sequence (antenna build, Section 2)

`measurements/antenna/` contains exactly five numbered milestone entries, as expected:

1. `1_outside_uncalibrated/alp_anten_uncal_0.s1p`
2. `2_outside_calibrated/alp_anten_cal_0.s1p`
3. `3_inside_calibrated/alp_anten_lab_0.s1p`
4. `4_inside_aluminum_foil/alp_anten_lab_0_enhanced.s1p` (renamed from the doubled
   `.s1p.s1p` extension in this same change set; see the "Fix doubled .s1p extension"
   commit)
5. `5_inside_cleaned_backshort/anten_son_horn.s1p` (the final, "definitive" state)

Plus a non-numbered `README.md` and an `antenna_photos/` subfolder. No finer-grained
intermediate probe-trimming cuts (e.g., per-millimeter probe depth steps) were found beyond
these five milestones; the milestone sequence is the complete measurement record present in
the repository.

## 5. CST project files

- **No `.cst` project file found** anywhere under `hardware/simulation/cst/` (or
  elsewhere in the repository). That directory contains only:
  - `assembly_worstcase/hornffrfr_assembly_worstcase.stp` (STEP geometry) plus
    `hornffrfr_assembly_worstcase_phi0.txt` / `_phi90.txt` (far-field cuts)
  - `ideal_horn/` with `ideal_hornfrfr_all_parameters.txt`,
    `ideal_hornfrfr_farfield_phi0.txt`, `ideal_hornfrfr_farfield_phi90.txt`
  - a `README.md`
  - (per the directory's own README, also an `.mcs.bas` macro and PDF reports are part of
    the intended content set; this audit did not re-verify every file, only confirmed the
    absence of any `.cst`)
- **Relevant context:** the repository's `.gitignore` already excludes `*.cst` and `*.awr`
  (lines 125-126), and `*.awr.bak` (line 61). Even if a `.cst` project file existed locally
  on the author's machine, it would not be trackable in this repository without an explicit
  `git add -f` or a `.gitignore` exception, so its absence here is expected regardless of
  whether one exists in the author's local CST workspace.

## 6. Far-field exports for Fig. 2(b,c) and TikZ polar figures

- **Raw numeric far-field `.txt` cuts: found**, under `hardware/simulation/cst/`:
  - `assembly_worstcase/hornffrfr_assembly_worstcase_phi0.txt` and `_phi90.txt`
  - `ideal_horn/ideal_hornfrfr_farfield_phi0.txt` and `_phi90.txt`
  - This audit did not verify the exact point count (360 points/cut) of each file; that
    would require parsing the files, which was out of scope for this presence/absence
    survey.
- **Rendered figure sources: found**, in `software/figures/` (added by a parallel agent
  working in that directory; present as of this audit):
  - `software/figures/s11_figures.py` and `software/figures/farfield_figures.py`
    (matplotlib figure generators)
  - `software/figures/tikz/` with `fig1_s11_ideal.tex`, `fig2_s11_assembly.tex`,
    `fig3_farfield_eplane.tex`, `fig4_farfield_hplane.tex`, and
    `software/figures/tikz/data/` containing `ff_eplane.dat`, `ff_hplane.dat`,
    `s11_assembly_cst.dat`, `s11_ideal.dat`, `s11_measured.dat`.
  - This audit did not check these files' content for correctness or completeness, only
    their presence, since another agent owns `software/figures/`.
