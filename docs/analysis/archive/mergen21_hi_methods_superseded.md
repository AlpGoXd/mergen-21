**SUPERSEDED.** Written before the cadence correction (0.5 s → 1.0 s rows) and before the sweep, kelvin and sigma results were withdrawn; see [PROVENANCE_ADDENDUM.md](../PROVENANCE_ADDENDUM.md).

# Mergen-21 first-light H I figure: methods, provenance and audit

This document accompanies `mergen21_hi_analysis.py`, which regenerates the
three-panel figure and every number quoted from it, starting from the raw
GNU Radio captures in the `mergen-21` repository.

Reproduction check: the script's `mergen21_hi_line_parameters.csv` matches the
previously archived summary table digit for digit in peak amplitude, centroid,
FWHM and LSR velocity. Galactic coordinates and the motion correction differ in
the first decimal because IERS auto-download is disabled here for offline
reproducibility, an effect well below the pointing uncertainty.

The single most important provenance finding is recorded first, because it is
the reason this package exists: **the lineage attached to the published figure
artifact is the superseded analysis**, the earlier interpretation in which the
spectral feature was taken to lie *below* the rest frequency. The figure as
published therefore had no recoverable generating script. It does now.

---

## 1. Instrument configuration, as read from the flowgraph

Read from `software/gnuradio/reciver.grc`, not assumed:

| quantity | value | source |
|---|---|---|
| FFT size | 2048 | `fft_size` |
| sample rate | 2.048 MS/s | `samp_rate` |
| channel bandwidth | 1.000 kHz | `samp_rate / fft_size` |
| integrations per saved row | 500 | `integration_time` |
| integration time per row | 0.500 s | `500 x 2048 / 2.048e6` |

Saved rows are `float32` power spectra. They are **already DC-centred**: the
FFT block runs with `shift: True`, so the channel order matches
`fftshift(fftfreq(2048, 1/2.048e6))` directly. Applying a second shift, as an
earlier pass did, moves the band-centre instrumental artifact to the band edge
and places the line at a spurious offset. This is the defect that produced the
superseded "feature below the rest frequency" reading.

On-source time is 51.5 to 53.0 s for the three static pointings (103 to 106
rows) and about 12.2 s for each of the 12 sweep blocks.

## 2. Spectral windows

| window | channels | purpose |
|---|---|---|
| line | 55 to 340 kHz | line search and Gaussian fit |
| baseline | 45 to 900 kHz, both signs, line excluded | cubic continuum fit |
| reference | 250 to 750 kHz | panel (a) normalization |
| noise | 450 to 880 kHz, both signs, 406 kHz spur excised | sensitivity |

The band-centre region `|f| < 45 kHz` is excluded everywhere. It carries an
instrumental artifact reaching 4.6x the continuum, sitting exactly on the rest
frequency because the local oscillator was tuned there. Offsetting the LO by a
few hundred kHz and translating in software would avoid the overlap in future
observations.

A narrowband spur at **+406 kHz** reaches 12% of continuum in the east
pointing. It is excised from the noise window; leaving it in inflates the east
channel rms from 0.86 to 1.42 K and is the largest single window sensitivity in
the analysis.

---

## 3. The five audit questions

### 3.1 Why the south peak is 25% in panel (a) but 18% in panel (c)

Both are correct. They are different quantities, and the earlier figure did not
say which was which.

- **Panel (a), 25.1%.** The spectrum is divided by the median of the line-free
  reference band (250 to 750 kHz) and plotted. The highest single channel in
  the line window sits 25.1% above that level.
- **Panel (c), 18.13 +/- 0.28%.** A Gaussian plus a *local* linear baseline is
  fitted jointly over the line window. The plotted quantity is the Gaussian
  amplitude, i.e. the line above the continuum immediately under it.

The 7-point gap has two independent causes, both physical rather than clerical:

1. **The local baseline is not the distant reference level.** Toward the plane
   the south spectrum has a broad pedestal, visible in panel (a) as wings
   extending well past the fit window. The local linear term absorbs part of
   that pedestal, so the Gaussian amplitude measures the line above its own
   wings, while the panel (a) reading measures everything above the far-field
   continuum.
2. **A single-channel maximum is biased high.** The peak channel is the maximum
   of about 285 noisy channels, so it sits roughly 1 sigma above the true
   profile peak, whereas the fitted amplitude averages over the 77 kHz line.

Both are now tabulated per measurement, as `raw_peak_excess_pct` and
`amp_pct`, so no reader has to guess which a figure is showing. For the
manuscript, quote the fitted amplitude with its uncertainty: it is the
estimator with a defined error bar and it is what panel (c) regresses.

### 3.2 How the significance was calculated, and what it covers

The statistic is the t-ratio of a regression slope, not a peak-to-noise ratio.

Ordinary least squares of the 15 observed line centroids on the
ephemeris-predicted radial motion of the observer (barycentric correction from
`astropy` plus the projection of the solar peculiar motion onto each
sightline):

```
centroid [kHz] = 60.2 (+/- 10.0) + 2.635 (+/- 0.318) x v_motion [km/s]
r = 0.917,  residual rms 14.1 kHz,  n = 15
```

A signal at a **fixed terrestrial frequency** predicts slope 0. The measured
slope is 2.635/0.318 = **8.3 sigma** from that null. That is the origin of the
"eight sigma" claim. The identical test in velocity space, where the
terrestrial null is slope +1, gives 0.444 +/- 0.067 against 1, again 8.3 sigma.

**What the 8.3 sigma includes.** Only the OLS slope standard error, which is
built from the scatter of the 15 points about the line. That scatter contains
the spectral noise propagated through the centroid fits, plus any
short-timescale pointing jitter that moves points randomly.

**What it excludes, in order of importance.**

1. **Serial correlation between sweep blocks.** The residuals have lag-1
   autocorrelation +0.65 in time order. The naive effective sample size
   `n (1-r)/(1+r)` is 3.2 rather than 15, which rescales the slope error and
   gives **3.8 sigma**. This is the number to quote if the 15 points are
   described as independent measurements.
2. **Pointing systematics.** The mount has no positioner or encoder. Elevation
   is assumed 35 degrees from the Stellarium charts, and the sweep azimuth is
   assumed to ramp linearly from 90 to 270 degrees. These errors move the
   predicted abscissae *coherently*, so they bias the slope rather than inflate
   its error, and no part of the quoted sigma protects against them.
3. **Analysis choices.** Baseline order, fit window and centroid estimator.
   Repeating the regression with the smoothed-moment centroid used in the
   published figure gives slope 1.99 +/- 0.30, 6.6 sigma against the
   terrestrial null and 3.0 sigma after the correlation correction.

**A second number a reviewer will compute.** The fitted slope 2.635 +/- 0.318
is also 6.6 sigma *below* the 4.738 kHz per km/s expected for a single line at
rest in the LSR. That is not a failure: over the sweep the sightline crosses a
wide range of Galactic longitude and latitude, so the emission-weighted LSR
velocity is not constant and Galactic rotation flattens the relation. Stating
this pre-empts the objection.

Recommended phrasing: report the slope with its error, state that it excludes a
terrestrially fixed signal at 3.8 sigma once block correlation is accounted
for, and name the pointing assumption as the dominant systematic.

### 3.3 Whether the blue line is a prediction or a fit

**A prediction, with zero free parameters.** It is
`centroid = (f0/c) x v_motion`, slope 4.738 kHz per km/s and intercept 0, the
locus for gas at rest in the LSR. Nothing in it is fitted to these data.

The fitted regression is the separate thin dark line, and the two are now
labelled with their slopes in the legend so they cannot be conflated. In the
published version only one line was drawn and its status was ambiguous, which
is what prompted this question.

### 3.4 How sweep-block independence was assessed

In the published version it was **not assessed**. The blocks are not
independent, and the package now quantifies it two ways.

By construction, the 12 blocks are contiguous equal-row slices of a single
continuous 146 s capture, so the mount drifts through them without
interruption. Two concrete measures:

- **Beam overlap.** The assumed 180 degree sweep over 12 blocks is 15 degrees
  of azimuth per block, against simulated 3 dB beamwidths of 25.2 degrees
  (H-plane) and 22.0 degrees (E-plane). Adjacent blocks therefore share well
  over half a beamwidth of sky and cannot be independent samples.
- **Residual autocorrelation.** Lag-1 autocorrelation of the regression
  residuals in time order is +0.65, giving an effective sample size of 3.2 and
  the 3.8 sigma of section 3.2.

The honest description is 15 correlated measurements along one continuous
track, equivalent to roughly three independent pointings. The three static
pointings are genuinely separate acquisitions and are the independent core of
the argument.

### 3.5 How the 1.08 K sensitivity and the 0.6 dB cable correction were obtained

**The 1.08 K does not reproduce, and should be replaced.**

It traces to an earlier session that reported per-channel sensitivities of
1.08 K south, 1.18 K east and 0.78 K west. Recomputed here from the same
captures with a two-sided line-free window and the 406 kHz spur excised:

| pointing | baseline rms | channel-differenced | radiometer prediction | on-source |
|---|---|---|---|---|
| west  | 0.802 K | 0.648 K | 0.841 K | 53.0 s |
| south | 1.425 K | 0.634 K | 0.853 K | 51.5 s |
| east  | 0.861 K | 0.627 K | 0.849 K | 52.0 s |

Only the west value reproduces. The south value is not noise: that estimator is
dominated by the line's own wings, which is why it is insensitive to the window
choice (1.36 to 1.52 K across five reasonable windows) while the east value
moves by a factor 1.6 depending on whether the spur is excised.

Two estimators are reported because they bracket the truth:

- **Baseline rms** is the scatter of the continuum-removed spectrum over
  line-free channels. It includes residual baseline structure, so it is an
  **upper bound**, and it is meaningless where the line has wings.
- **Channel-differenced** is the robust scale of the successive-channel
  difference divided by sqrt(2), immune to baseline curvature. It reads 0.63 to
  0.65 K identically in all three pointings, as it must if T_sys and tau are
  common. An earlier version of this note called it a lower bound, on the
  reasoning that the WOLA filterbank correlates adjacent channels. That has
  since been measured on the line-free window and the lag-1 correlation is
  only +0.043 to +0.050, so the estimator is biased low by about one percent
  and is effectively **unbiased**. The earlier claim was wrong. See
  `PROVENANCE.md` section 3 for the consequence, which is that the gap
  between this estimator and the line-free scatter is residual baseline
  structure rather than channel correlation.

The radiometer equation at T_sys = 193.5 K, B = 1 kHz and tau = 52 s predicts
0.84 K, which sits inside the bracket and agrees with the line-free west
pointing to 5%.

Recommendation: quote **0.80 K, measured in the line-free west pointing**, and
note agreement with the radiometer prediction. Quoting a south-pointing rms as
a sensitivity conflates signal with noise.

**The 0.6 dB is measured, not assumed.** It is the insertion loss at 1.42 GHz
of the cable between the receiver output and the spectrum analyzer, from the
FSVA3044 trace `measurements/rf-chain/nf/cable_loss.DAT`, carried with a stated
+/- 0.2 dB tolerance in `measurements/rf-chain/nf/README.md` and cross-checked
against the reference-path loss recorded in the IP3 measurement directory.

It enters the noise figure because of a calibration-plane mismatch. The ZNB8
cascade gain was TOSM-calibrated **at the DUT ports**, which de-embeds that
cable from the gain, while the analyzer's noise-density reading still contains
its loss. The output density is therefore 0.6 dB low relative to the gain
reference plane and must be corrected upward:

```
NF = (P_out + L_cable) - kT0 - G
   = (-133.46 + 0.60) - (-173.9) - 39.5 = 1.54 dB   ->  T_rx = 123 K
uncorrected:  0.94 dB  ->  T_rx = 70 K
tolerance:    1.34 to 1.74 dB from the +/- 0.2 dB cable figure
```

The corrected 1.54 dB fails the manuscript's 0.96 dB design budget and raises
the integration needed for 1 K in a 1 kHz channel from 20 to 37 s. Because the
S-parameter sweep was wideband and coarse and cannot be repeated, T_rx is
reported as an upper bound with the calibration plane named as the dominant
systematic.

**Uncertainty on this number is incomplete, by decision rather than by
oversight.** The 1.54 dB is carried as the central estimate without a full
error budget: the cable tolerance alone spans 1.34 to 1.74 dB, and the gain
term carries a further uncertainty the coarse sweep does not resolve and that
cannot now be quantified. The manuscript states this explicitly and directs
anyone reproducing the build to measure interconnect and gain at a common
reference plane rather than adopt the value.

---

## 3.6 Decisions taken on the manuscript

Settled with the author after this audit, and now written into `main.tex`:

- The estimator clarification of section 3.1 is accepted; panels (a) and (c)
  are described as the different quantities they are, in the caption.
- The corrected 1.54 dB noise figure is retained as the central estimate,
  carrying the incomplete-uncertainty caveat above.
- **The 1.08 K is not reinstated.** Table III and the abstract now quote
  0.80 K from the line-free west pointing, with the radiometer agreement
  stated.
- **No "8 sigma confirmation" is reinstated.** The abstract, the results
  section and the figure caption quote 3.8 sigma, name the block correlation
  that forces it, and state that the elevation assumption biases the slope
  rather than widening its error.
- The peak signal-to-noise is restated as roughly 25, the fitted amplitude
  against the line-free per-channel noise, replacing the previous 33 which
  paired the raw peak with a line-contaminated noise estimate.

---

## 4. Quantities that are assumed rather than measured

These are marked `ASSUMED` inline in the script and are the honest limits of
the pointing-dependent results.

| quantity | value | why it is assumed | effect |
|---|---|---|---|
| elevation | 35 deg | no positioner or encoder on the mount; read off the Stellarium charts | dominant systematic on `l`, `b` and the motion correction |
| sweep azimuth | linear 90 to 270 deg | direction and extent from the observation log and filename; no per-row record | biases the panel (b) slope coherently |
| site | 41.0 N, 29.0 E, 100 m | no GPS fix logged | below 0.01 km/s on the motion correction |
| local time offset | UTC+3 | filenames carry local time | 1 h error would shift the motion correction by about 1 km/s |
| T_sys | 193.5 K | 70 K antenna plus 123 K receiver, the latter itself an upper bound | scales all kelvin sensitivities linearly |

## 5. Files

| file | contents |
|---|---|
| `mergen21_hi_analysis.py` | the complete analysis, one entry point |
| `mergen21_hi_measurements.csv` | 15 measurements, 31 columns |
| `mergen21_hi_line_parameters.csv` | 3-pointing summary, matches the archived table |
| `mergen21_data_manifest.csv` | sha256, byte count and row count for every input |
| `mergen21_hi_derived.json` | regressions, sensitivity, noise figure, assumptions |
| `mergen21_hi_validation.png` | the three-panel figure |

Inputs are referenced by checksum, not copied. Point the script at a checkout:

```
python mergen21_hi_analysis.py --root /path/to/mergen-21 --outdir out
```

### Columns of `mergen21_hi_measurements.csv`

`id`, `kind`, `source_file`, `utc_mid`, `n_rows`, `on_source_s`, `az_deg`,
`alt_deg`, `ra_deg`, `dec_deg`, `l_deg`, `b_deg`, `centroid_kHz`,
`centroid_err_kHz`, `centroid_moment_kHz`, `amp_pct`, `amp_err_pct`,
`smoothed_peak_pct`, `raw_peak_excess_pct`, `fwhm_kHz`, `fwhm_err_kHz`,
`fwhm_kms`, `halfpower_width_kHz`, `v_bary_kms`, `v_solar_kms`,
`v_motion_kms`, `v_lsr_kms`, `v_lsr_moment_kms`, `rms_frac`,
`dT_baseline_K`, `dT_diff_K`, `dT_radiometer_K`, `snr_peak`, `az_step_deg`.

Uncertainties on `centroid`, `amp` and `fwhm` are formal 1-sigma values from
the covariance matrix of the Gaussian-plus-linear fit. They do not include
pointing error, which is not random.
