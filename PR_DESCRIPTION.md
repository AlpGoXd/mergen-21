# Bring the repository in line with the submitted manuscript

Branch: `paper-release` (29 commits ahead of `origin/main`). Follows `REPO_FIX_PROMPT.md`'s 8-task
spec for reconciling this repo with the IEEE Antennas & Propagation Magazine (Education Corner) submission.

## Summary of changes

**Analysis code (tasks 1, 2, 5-script)**
- Added `software/analysis/mergen21_hi_analysis.py`, `first_light_and_averaging.py`, `wola_window_check.py`
  and `software/figures/{s11_figures.py,farfield_figures.py,tikz/}` from the canonical analysis workspace.
- `first_light_and_averaging.py` now takes `--root`/`--outdir` and falls back `observations/data` -> `raw`,
  matching `mergen21_hi_analysis.py`.
- Fixed `TAU_ROW_SWEEP_S` (0.5 -> 1.0 s), confirmed by a before/after run that it changes nothing the paper
  quotes (only the withdrawn sweep block's own timing fields).
- Fig. 5 formatting: removed panel titles, capitalized panel (a) legend, fixed panel (b) dashed-line label.
- Pinned `software/requirements.txt` (numpy 2.4.4, scipy 1.17.1, pandas 3.0.3, matplotlib 3.10.9,
  astropy 8.0.1; the versions that actually installed and ran here, Python 3.14.3 / Windows 11).
- Regenerated every output into `software/analysis/outputs/` and wrote `VERIFICATION.md` (table below).

**Acquisition documentation (task 4)**
- `observations/captures.csv`: acquisition metadata (integration settings, azimuth/elevation provenance,
  cadence) for the 5 characterized captures (W, S, E1, E2, sweep).
- `observations/README.md`: new "Acquisition settings" section; fixed a dead reference to a deleted
  `allahyok.png`; flagged the "Method" line as future work (a straggler the claim-correction pass missed).
- `software/gnuradio/reciver.grc`: filled in the `integration_time` variable's `comment` field with its
  history (500 -> 1000). Value itself was already 1000 from a prior local edit (see "Decisions" below).
  No blocks, taps, or connections touched.

**Known issue documentation (task 5-doc)**
- `software/gnuradio/README.md`: documented the disabled simulated-HI TX injector (different Pluto URIs for
  RX/TX, so it can't leak into a live capture) with a `TODO(Alp): confirm injector was disabled during all
  2026-04-29 captures` for you to resolve; documented the truncated WOLA prototype filter (32,299 taps
  designed, only 16,384 consumed) with a pointer to `wola_window_check.py`.

**Claim corrections (task 3)**
- Noise figure: `0.75 dB` -> **about 1.5 dB** (cable-corrected: `-133.46 + 0.6 - (-173.9) - 39.5 = 1.54 dB`,
  +/-0.5 dB from gain uncertainty; Friis prediction 0.77 dB; design requirement 0.96 dB). Full rewrite in
  `measurements/rf-chain/nf/README.md`.
- Cascade gain: `39.7 dB` -> **39.5 dB +/- 0.5 dB**; noted the VNA cascade file's ~42.5 MHz point spacing
  means there's no sample at 1420.405 MHz (nearest is 1402.5 MHz).
- Rotation curve reworded as future work everywhere (README, CLAUDE.md, docs/STATUS.md,
  `software/analysis/README.md`, lab manuals, observations/README.md). The released result is first-light,
  pointing-dependent detection (S/E/W line fits), not a rotation curve.
- Added a "Reproducing the paper" section to `README.md`.

**Citation, hygiene, missing-artifacts audit (tasks 6, 7, 8)**
- Fixed `CITATION.cff` (stale numbers, missing co-authors, keywords) and added `.zenodo.json` (drafts only).
- `git mv measurements/antenna/4_inside_aluminum_foil/alp_anten_lab_0_enhanced.s1p.s1p` -> `.s1p` (content
  byte-identical, sha256 `3c94bb30a220...` before and after; the one data-file rename the ground rules allow).
- `docs/analysis/MISSING_FROM_RELEASE.md`: reports presence/absence of everything task 8 asks about.

**Follow-up decisions applied**
- `rx_gain` restored to 30 in `reciver.grc`/`reciver.py` so the flowgraph matches how the 2026-04-29 data was
  captured (`reciver.py` synced by hand; grcc is not available). `log_dir` stays relative.
- Committed the docs index, BOM, build lab manual (Lab 2), and hardware READMEs. README.md already linked to
  them.
- American spelling and punctuation pass (no em dashes) on README.md, `docs/`, and the hardware READMEs.
  Also removed the README intro's claim that the telescope was used to map the Milky Way's rotation.
- Data in `observations/` and `measurements/` is now licensed CC BY 4.0 (`LICENSE-DATA`, official legal
  code), listed in README, CONTRIBUTING, CITATION.cff and `.zenodo.json`.

## Verification table (`software/analysis/outputs/VERIFICATION.md`)

| Quantity | Reference | Regenerated | Abs diff | Status |
|---|---|---|---|---|
| `averaging_noise.csv` E1 @ tau=1s `sigma_pct` | 3.528470 | 3.528470 | 0 | match |
| `averaging_noise.csv` E2 @ tau=1s `sigma_pct` | 3.526871 | 3.526871 | 0 | match |
| rows_used E1 / E2 | 98 / 165 | 98 / 165 | 0 | match |
| rows_skipped | 6 | 6 | 0 | match |
| n_pairs E1 @ tau=1/2/4/8s | 49/24/12/6 | 49/24/12/6 | 0 | match |
| line-free channels in common mask | 1437 | 1437 | 0 | match |
| fitted peak % S/E/W | 18.13/7.87/5.45 | 18.13/7.87/5.45 | 0 | match |
| FWHM kHz S/E/W | 77.2/88.9/151.9 | 77.2/88.9/151.9 | 0 | match |
| centroid kHz S/E/W | 172.1/138.5/77.8 | 172.1/138.5/77.8 | 0 | match |
| galactic l (deg) S/E/W | 17.2/85.4/21.9 | 17.2/85.5/22.0 | <=0.1 | match (offline-IERS caveat) |
| galactic b (deg) S/E/W | -0.0/-30.7/71.5 | -0.1/-30.8/71.4 | <=0.1 | match (offline-IERS caveat) |
| noise figure, cable-corrected | 1.54 dB | 1.54 dB | 0 | match |

Environment ran with `astropy.utils.iers.conf.auto_download = False` (offline); no IERS tables were
downloaded, which accounts for the <=0.1 degree drift on galactic coordinates. No other regenerated value
disagreed with the reference. Full byte-level diff/cmp notes are in `VERIFICATION.md` itself.

**WOLA check status:** blocked. `wola_taps_firdes.npy` does not exist and GNU Radio is not installed in this
environment (`import gnuradio` fails; no `grcc`/`gnuradio-companion` on PATH), so `wola_window_check.py
--regenerate` cannot run here. No numpy imitation of GNU Radio's `firdes.low_pass` output was fabricated or
committed, per the ground rules. This needs to run on a machine with GNU Radio 3.10+ installed.

## Proof greps

```
$ git grep -n "0\.75 dB"
(no output)

$ git grep -n "39\.7"
(only in raw datasheets/measurement exports/CST files where "39.7..." is a coincidental numeric token,
 and measurements/rf-chain/ip3/README.md's "39.7 dB at 1.4025 GHz" -- an honest, frequency-tagged VNA
 reading at the nearest actual sample point, within the corrected 39.5+/-0.5 dB range, left as-is)

$ git grep -in "tangent"
(only future-work wording, CITE.bib's thesis title (flagged below, not changed), and
 docs/lab-manual-04-observe.md's Part C, explicitly retitled "(future work)")

$ git grep -in "rotation curve"
(same pattern -- future-work wording throughout, plus CITE.bib and CONTRIBUTING.md's
 forward-looking "areas for contribution" bullet, neither of which claims a completed result)
```

## Decisions waiting on you

Resolved in this PR: the data license (CC BY 4.0), `rx_gain` (restored to 30), and the untracked docs
(committed). Still open:

1. **Optional renames** (not done; informal or misspelled names, listed for you to decide):
   - `software/gnuradio/reciver.grc` / `reciver.py` (misspelled "receiver")
   - `measurements/rf-chain/vna/*/mesured_*.pdf` / `.s2p` (three components)
   - `measurements/rf-chain/nf/just cooked reciver.DAT` / `.PNG`
   - `observations/data/mergen21_spec_20260429_050554_180partygirl_500int.dat`
   - `observations/data/mergen21_spec_20260429_050204_doggu.dat` (inconsistent transliteration vs. other files)
   - `measurements/antenna/antenna_photos/insidee_mesurment.jpeg` / `outside_mesurment.jpeg`
2. **Injector TODO.** `TODO(Alp): confirm injector was disabled during all 2026-04-29 captures` was left in
   `software/gnuradio/README.md`; please confirm and remove the TODO once you have.
3. **Stashed, unrelated edits.** Two uncommitted local changes were kept out of this branch as out of scope:
   a large block deletion in `software/gnuradio/21cm synth/topo2_single_gaussian.grc`/`.py`, and a binary
   change to `hardware/antenna/inventor/horn_v0.1.iam`. They are preserved in `git stash list` (`stash@{0}`,
   "out-of-scope: topo2_single_gaussian + horn iam edits, not part of paper-release"); `git stash pop` on
   `main` if you want to keep working on them.
4. **`.zenodo.json` license field.** Zenodo's schema takes one top-level license for the archive, but this
   repo has four (hardware/software/docs/data). The draft lists all four in a non-standard `license` object as
   a placeholder; pick a representative license or restructure before depositing.
5. **`CITE.bib` thesis title.** Its title, "...for Galactic Rotation Curve Observation," describes a result
   the paper does not claim yet. `CITATION.cff`'s `preferred-citation` mirrors it for consistency. Not changed
   here; worth revisiting once the thesis itself is finalized.
6. **Stray content noticed, not touched.** `starting-up/` at the repo root (untracked) is a large, unrelated
   workspace (drone-interceptor / "pocket multi-radio tool" market research: docx/pptx/xlsx, slide images, a
   BOM, LibreOffice lock files, and an orphaned duplicate of the antenna S11 measurement file). Worth
   reviewing before any public release; nothing here was deleted or modified.

## Draft repository description

> Open-source 21 cm hydrogen-line receiver for undergraduate RF education: sheet-metal pyramidal horn,
> characterized receiver chain, GNU Radio WOLA spectrometer, and first-light data.

## Zenodo steps (after merging, for you to do)

1. Enable the Zenodo-GitHub integration for this repository.
2. Tag a release `v1.0-apm`.
3. Zenodo will mint a DOI for that tag; put it into the paper's reference [16].
4. Resolve the `.zenodo.json` license-field issue (decision 4 above) before or during the deposit.

## Stray files at repo root (not part of the release)

`REPO_FIX_PROMPT.md` and the `mergen21_incoming.zip` staging archive are deleted as part of this branch's
final cleanup (they were inputs to this work, gitignored throughout, never committed). `CLAUDE.md` (Claude
Code guidance) is left in place unless you'd rather it not ship publicly.

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
