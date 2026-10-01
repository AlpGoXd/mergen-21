# Provenance addendum

Issued in response to the observer's finding that the azimuth sweep was
manual, irregular in azimuth and included pauses, that elevation was held
only approximately fixed, and that antenna temperature was never measured.

This addendum supersedes the affected parts of the earlier provenance and
methods notes (the methods document is archived as
`archive/mergen21_hi_methods_superseded.md`). The manuscript has not been
touched.

**The outputs generated before this addendum are superseded**: those
computed with the 0.5 s row cadence, the sweep-azimuth regressions and
latitude correlation, and the kelvin sensitivities. Nothing from them should
be quoted. The current `software/analysis/outputs/` were regenerated after
these corrections (1.0 s rows; the sweep regressions are listed under
`withdrawn` in `mergen21_hi_derived.json`); see
`software/analysis/outputs/VERIFICATION.md`. Their `dT_*_K_assumed_Tsys`
fields still rest on an assumed system temperature and should not be quoted
either.

---

## 1. Withdrawn

| withdrawn | reason |
|---|---|
| the linear time-to-azimuth mapping across the sweep | the sweep was manual and irregular with pauses, so elapsed time does not map to azimuth |
| azimuth, and therefore *l* and *b*, for all 12 sweep blocks | derived from that mapping |
| predicted radial velocity for all 12 sweep blocks | derived from that mapping |
| the 15-point regression of centroid against predicted motion, and its slope 2.63 +/- 0.32 | 12 of its 15 points are withdrawn |
| the 3.8 sigma exclusion of a fixed terrestrial frequency | same regression |
| the correlation of amplitude against \|b\|, r = -0.70 | 12 of its 15 points are withdrawn |
| every quantity in kelvin | T_sys was never measured; see section 2 |
| elevation 35 degrees as a fixed value (now 30°, observer-stated) | held only approximately, and never instrumented |

Panels (b) and (c) of the figure lose 12 of their 15 points. Three points do
not support a regression, a correlation coefficient, or a significance.

## 2. Antenna temperature was not measured

The analysis converted fractional quantities to kelvin using a single
constant, `T_SYS_K = 193.5`, formed from an assumed antenna temperature plus
a receiver temperature derived from the noise figure. The antenna
contribution was never measured, so every kelvin value in the package is
fractional data multiplied by an assumed scale factor.

**What survives:** all fractional quantities, which is what the instrument
actually measures. Line amplitude as a percentage of continuum, fractional
rms, and the ratio of the two are unaffected. The sensitivity discussion
should be conducted in fractional units, or in kelvin only with the
assumed scale stated at every occurrence.

The noise consistency test in section 5 is therefore formulated so that
T_sys cancels.

## 3. Which east capture

**`mergen21_spec_20260429_050204_doggu.dat`**, 104 rows, started 05:02:04
local. Confirmed by re-measuring both candidates and comparing against the
exported table:

| | rows | fitted amplitude | raw peak | centroid | FWHM |
|---|---|---|---|---|---|
| exported table, row E | 104 | 7.868 % | 12.281 % | | 88.89 kHz |
| `..._050204_doggu.dat` | 104 | 7.868 % | 12.225 % | 138.48 +/- 0.50 kHz | 88.89 kHz |
| `..._050450_Dogu_100.dat` | 171 | 6.930 % | 13.667 % | 117.94 +/- 1.53 kHz | 93.43 kHz |

The amplitude and FWHM match to all quoted digits, so the identification is
certain.

**A second east capture exists and was never used.** `Dogu_100` was recorded
166 s later at the same nominal pointing. Its centroid sits 20.5 kHz below
the used capture, a difference of 12.7 combined standard errors, equivalent
to 4.3 km/s. This is an unused repeat observation that disagrees with the
one that was reported by far more than its formal uncertainty. It bears
directly on how reproducible a single pointing's centroid is, and it should
be reckoned with before any centroid-based claim is rebuilt.

## 4. Acquisition settings: confirmed by the observer; the flowgraph does not describe them

**The observer confirmed these settings on 2026-09-13.** West, south, the
05:02:04 east capture and the sweep all used `integration_time = 1000`. Only
the 05:04:50 east capture used 100. The frame period is
`FFT_SIZE / SAMP_RATE = 1.000 ms` exactly, so `tau_row = N_int / 1000` s.

| capture | setting | tau_row | rows | duration | source |
|---|---|---|---|---|---|
| `..._045525_bati.dat` (west) | 1000 | 1.0 s | 106 | 106.0 s | observer |
| `..._045857_guney.dat` (south) | 1000 | 1.0 s | 103 | 103.0 s | observer |
| `..._050204_doggu.dat` (east) | 1000 | 1.0 s | 104 | 104.0 s | observer |
| `..._050450_Dogu_100.dat` (east repeat) | 100 | 0.1 s | 171 | 17.1 s | observer, filename agrees |
| `..._050554_180partygirl_500int.dat` (sweep) | 1000 | 1.0 s | 293 | 293.0 s | observer; **filename disagrees** |

Every nominal duration is shorter than the gap to the next capture's start
time, which is a necessary consistency check and it passes for all five.

**Two written records contradict the observer, and neither is used.**
`software/gnuradio/reciver.grc` carried `integration_time = 500`, which matches no
capture in this package; the flowgraph was saved at the end of the session,
after the setting had last been changed. The `500int` in the sweep filename
likewise does not record that capture's setting. The observer states the
filename is misleading. Both disagreements are recorded here rather than
resolved silently, because a reader who opens the flowgraph will otherwise
find a number that matches nothing.

**What the previous revision inferred, and where it was wrong.** That
revision derived the cadence from per-row noise, calibrating `N_eff` against
the two captures whose filenames state a setting. It got the three static
captures right at 1000 and the sweep wrong at 500. The failure mode is now
identified. `N_eff` measured by differencing successive rows assumes the sky
is unchanged between them; the sweep was in manual motion, so consecutive
rows differ by real sky change as well as by noise, which inflates the
measured sigma and deflates the apparent `N_eff`. The sweep's apparent
`N_eff` of 366 is an artifact of pointing motion, not a record of its
cadence. **Row-differenced noise cannot be used to infer cadence on a moving
pointing**, and the previous revision did not carry that caveat.

A second, smaller leak affects the stationary captures. Receiver level swings
by 10 to 17 percent within a capture, and a plain row difference carries that
gain fluctuation into the noise estimate. Normalising each row by its own
mean level before differencing removes it and brings all four stationary
captures into agreement:

| capture | plain differencing | gain-normalised | `N_eff` | `B_eff` | level swing |
|---|---|---|---|---|---|
| west | 3.792 % | 3.493 % | 819.7 | 819.7 Hz | 16.6 % |
| south | 3.533 % | 3.489 % | 821.3 | 821.3 Hz | 13.3 % |
| east | 3.519 % | 3.500 % | 816.5 | 816.5 Hz | 10.3 % |
| east repeat | 11.080 % | 11.077 % | 81.5 | 814.9 Hz | 13.8 % |
| sweep (moving; excluded) | 5.228 % | 4.946 % | 408.8 | not estimable | 37.2 % |

The four stationary captures now agree on `B_eff` to 0.8 percent, where plain
differencing spread them over 17 percent. West was the worst affected and is
no longer an outlier.

**Consequence for the package.** The three static on-source times are
unchanged at 106, 103 and 104 s. The sweep's total duration is **293 s, not
the 146.5 s** the previous revision's 0.5 s cadence implied, and each sweep
block is 24 to 25 s rather than 12 to 12.5 s. No reported quantity depends on
the sweep's duration, since the sweep is retained only as a descriptive
time-frequency observation, but the table and figure now carry the correct
value. `analysis/mergen21_hi_analysis.py` no longer holds a single cadence
constant; it carries `INTEGRATION_FRAMES` per file, and
`analysis/outputs/mergen21_capture_metadata.csv` records the setting, the
derived cadence and the provenance of each alongside.

## 5. Exact filter and averaging implementation

Both `software/gnuradio/reciver.grc` and the generated `software/gnuradio/reciver.py`
are in this package. The signal path is:

```
Pluto source (LO 1 420 405 000 Hz, 2.048 MSa/s, 2 MHz BW, 30 dB manual gain)
  -> 8 parallel branches k = 0..7:
       delay(k * 2048 complex samples)
       stream_to_vector(2048)
       multiply_const_vcc(kaiser_window[k*2048 : (k+1)*2048])
  -> add_xx (sums the 8 windowed segments)
  -> fft_vcc(2048, forward=True, window=[], shift=True, nthreads=2)
  -> complex_to_mag_squared(2048)
  -> integrate_ff(integration_time, 2048)
  -> multiply_const_vff(1.0 / integration_time)
  -> file_sink(float32 * 2048)
```

This is a weighted overlap-add filterbank with K = 8 branches, M = 2048
channels, a hop of 2048 samples, and therefore a window length of 16384
samples with eightfold overlap. The frame rate is 1000 per second. The FFT
runs with `shift=True`, which is why the stored rows are DC-centred. The
file sink is fed from the integrator through the 1/`integration_time`
scaling, so the stored values are **linear mean power**; the `nlog10` block
in the graph drives only the on-screen display. All four transmit blocks are
`state: disabled`.

### Prototype filter length: settled, and the truncation is real

GNU Radio is now installed, so the call was run rather than reconstructed:

```python
kaiser_window = firdes.low_pass(1.0, samp_rate, samp_rate/(4*fft_size),
                                samp_rate/(4*fft_size), window.WIN_KAISER, beta)
# = firdes.low_pass(1.0, 2048000, 250.0, 250.0, WIN_KAISER, 8.6)
```

It returns **32 299 taps**, confirming the `firdes::compute_ntaps` rule
(32 299) and refuting the `scipy.signal.kaiserord` rule (44 958). The
prototype peaks at tap **16 149**.

The eight branches consume `kaiser_window[0 : 8*2048]`, that is taps 0 to
16 383. So the cut falls **235 taps past the peak, at 99.4 percent of peak
height**, and **15 915 taps, 49 percent of the designed filter, are never
referenced by any block.** The intended symmetric taper has its entire
falling half discarded; what the filterbank actually applies is the rising
edge chopped off just after its maximum.

The delay-to-slice pairing was read from the flowgraph connections rather
than assumed: branch `delay = k*fft_size` receives
`kaiser_window[(7-k)*fft_size : (8-k)*fft_size]`, so the effective window is
exactly `taps[0:16384]` applied to one contiguous 16 384-sample span. The
chain is a textbook WOLA: eight delayed branches, `stream_to_vector`,
per-branch multiply, an 8-input adder, one `fft_size` FFT with `shift: True`,
magnitude-squared, `integrate` by `integration_time`, then a
`1/integration_time` scale (so rows are means, not sums).

**This confirms the claim that the previous revision of this section
retracted.** The retraction was wrong, and it was my error, not the data's:
my predicted `N_eff` for the truncated candidate (97.4) was computed
incorrectly, and so was the one for the complete taper (75.0). Simulating
white noise through the chain reconstructed above -- with frames hopping by
`fft_size` while spanning `8*fft_size`, so consecutive frames share seven
eighths of their samples -- gives:

| candidate window | `N_eff` at N_int = 100 | `B_eff` | lag-1 corr. |
|---|---|---|---|
| **measured (`Dogu_100`)** | **81.5** | **815 Hz** | **+0.051** |
| as built: first 16 384 of 32 299 | 82.4 | 824 Hz | +0.085 |
| complete symmetric 16 384-tap taper | 53.6 | 536 Hz | +0.023 |

`N_eff` is the discriminating statistic and it is decisive: the as-built
window predicts 82.4 against 81.5 measured, a one percent agreement, while a
correct taper predicts 53.6 and is wrong by 34 percent. `B_eff` agrees to 1.1
percent, now that the cadence entering the measured value is
observer-confirmed rather than inferred. The lag-1 channel correlation does **not** discriminate at this
precision -- its standard error is about 0.04 over 600 realisations, so the
+0.085 and +0.023 predicted for the two candidates are less than two standard
errors apart -- but the as-built value does
independently reproduce, from first principles, the +0.043 to
+0.050 measured on the real captures and quoted in the superseded methods document.

**What it costs the instrument.** The truncation is a genuine defect and may
be described as one in print, but its cost is spectral purity, not
sensitivity:

* Adjacent-channel rejection collapses from -95.6 dB to **-16.7 dB**. A
  monochromatic signal spills about 2 percent of its power into each
  neighbouring channel and 0.5 percent into the next one out. This bears
  directly on the narrowband spur at +406 kHz baseband, which reaches 12
  percent of continuum in the east pointing: it contaminates its neighbours
  at the few-tenths-of-a-percent level, and any narrow feature in these
  spectra is broader than the instrument's designed channel response.
* It does **not** measurably broaden the H I line. The leakage spans a few
  1 kHz channels against a fitted line width of 77 to 152 kHz.
* Sensitivity is not degraded. `B_eff` is 824 Hz as built against 536 Hz for
  a correct taper, so the radiometric noise per unit integration time is
  slightly *lower* than a correct implementation would deliver. No
  sensitivity figure in the manuscript is invalidated by this.
* The fix is one line: design the prototype to exactly `K*fft_size` taps, or
  pass the tap count explicitly, rather than letting `firdes` choose a length
  from the attenuation and transition width.

A two-panel truncation figure (not included in this release) showed the
designed prototype with the consumed and discarded spans, and the resulting
channel-leakage penalty against a correct taper. The whole check is
reproducible by `python software/analysis/wola_window_check.py`, which needs
GNU Radio on its first run to design the 32 299 taps (the cached
`wola_taps_firdes.npy` is not committed); Monte Carlo figures quoted above are that script's output and
carry a few percent of run-to-run scatter.

### Effective channel bandwidth: confirmed at 818 Hz

**This section was withdrawn two revisions ago, restored at 753 Hz in the
previous revision, and is now confirmed at 818 Hz.** The withdrawal argued
that reading `B_eff` from the measured `N_eff` assumes the row is an average
of `B_eff * tau_row` independent samples, which the overlap between the eight
hops violates. That objection was misdirected on two counts. First,
`B_eff = N_eff / tau_row` is a definition of effective noise bandwidth, not
an independence assumption; the physical content sits entirely in whether the
measured `N_eff` matches what the window and the frame overlap predict.
Second, the simulation in the previous subsection models that overlap
explicitly, so a prediction is available.

The measurement has since improved twice: the cadence is observer-confirmed
rather than inferred to 10 percent, and gain-normalised differencing removes
the receiver level drift described in section 4.

| | `B_eff` |
|---|---|
| **measured, four stationary captures** | **818.1 +- 2.9 Hz** |
| simulated, window as built | 824 Hz |
| simulated, complete taper (counterfactual) | 536 Hz |
| channel spacing, for reference | 1000 Hz |

Measurement and simulation now agree to **0.7 percent**, against 9 percent in
the previous revision, and the four captures agree among themselves to 0.8
percent. The counterfactual complete taper is off by 35 percent. **This is
the strongest available confirmation that the analysis window is truncated as
section 5 describes**, and it is independent of the tap-count argument: it
uses only the measured noise of four captures and a simulation of the
as-built chain.

Two consequences for the manuscript. The effective channel bandwidth is
narrower than the 1000 Hz channel spacing, by 18 percent rather than the 25
percent the previous revision reported. And substituting 818 Hz for the
previous 753 Hz lowers a radiometer-predicted channel sensitivity by 4.1
percent, since `dT` scales as `1/sqrt(B)`, moving the prediction toward the
measured value rather than away from it.

### Noise consistency, without any assumed quantity

The earlier radiometer test compared measured fractional noise against
`1 / sqrt(B_eff * tau)`. Because `B_eff` had itself been fitted from the same
noise data, that test was close to circular, and its claim to be
"independent corroboration" of the cadence is withdrawn.

The test below replaces it and assumes nothing at all. If the rows of a
capture are independent, the noise in the averaged spectrum must be the
per-row noise divided by the square root of the number of rows. Both sides
are measured on the same line-free channels of the same file. No system
temperature, no channel bandwidth, no cadence enters:

| pointing | rows | per-row fractional rms | predicted | measured | ratio |
|---|---|---|---|---|---|
| west | 106 | 0.0379 | 0.003683 | 0.003349 | 0.91 |
| south | 103 | 0.0353 | 0.003481 | 0.003276 | 0.94 |
| east | 104 | 0.0352 | 0.003450 | 0.003240 | 0.94 |

The averaged spectra are 6 to 9 percent quieter than independent rows
predict. That is a small residual in the safe direction for a detection
claim, and it is consistent with the successive-difference estimator
slightly overstating per-row noise. **The 23 percent shortfall flagged as
unresolved in the superseded methods document was an artifact of the assumed 1000 Hz bandwidth
and 0.5 s cadence, not a property of the data.** It does not survive a test
that makes no such assumptions, and it is closed on that basis rather than
by the bandwidth correction previously claimed.

### What the cadence inference rested on, and why it is superseded

The previous revision calibrated `N_eff` against the two captures whose
filenames state a setting, and concluded `tau_row ~ 1.0 s` for the static
pointings from two anchors agreeing to 10 percent. That reasoning is now
superseded by the observer's confirmation, and section 4 records where it
failed: one of its two anchors, the `500int` filename, does not record its
capture's setting at all. The inference reached the right answer for the
three static captures for partly wrong reasons, and the wrong answer for the
sweep. It is retained here as a worked example of what noise statistics can
and cannot settle without a session record.

## 6. The rebuilt figure and table

The pipeline was rerun with the withdrawn geometry removed, the cadence
corrected to the observer-confirmed per-file integration settings, and every kelvin quantity flagged as resting on an assumed
`T_sys`. Two of the three figure panels had to be replaced, because both of
them took sweep azimuth as an input.

| Panel | Was | Is now |
|---|---|---|
| (a) | three averaged spectra, labelled by Galactic latitude | unchanged, but labelled by azimuth: the latitude of a static pointing depends on an elevation the observer held only approximately |
| (b) | fitted centroid against predicted observer motion, 15 points | measured noise in the averaged spectrum against the noise predicted from its own rows |
| (c) | fitted amplitude against \|b\|, Pearson r | fitted centroid against fitted amplitude, with the scatter of all 15 |

Panel (b) is the replacement worth keeping regardless of whether the pointing
is ever recovered: neither of its axes uses `T_sys`, channel bandwidth, or
row cadence. It compares the noise measured in each averaged spectrum against
`sigma_row / sqrt(n_rows)` measured from the same capture's own rows. All 15
measurements land between 0.85 and 1.00 of that prediction, mean 0.92. The
averaged spectra are therefore integrating down as independent samples would,
slightly better than the row estimator predicts; that estimator is itself
differenced, which biases it marginally high.

### The centroid scatters far more than the fits admit

This is new, and it bears on the manuscript. Across the 15 measurements the
fitted line centroid spans 75 to 180 kHz, standard deviation 34 kHz. The
formal fit errors are 0.5 to 2.9 kHz for the 14 well-detected measurements,
median 0.8 kHz. The scatter is therefore roughly 40 times the formal error.

Two consequences:

* **No centroid uncertainty derived from a single fit should be quoted.** The
  fit error describes how well a Gaussian localizes a fixed line shape in
  noise. It does not describe how much the answer moves between
  measurements, which is the quantity a reader needs. If a centroid is
  quoted, the uncertainty should be the scatter across repeats.
* It is the same effect seen in section 3, where the two east captures taken
  four minutes apart gave centroids differing by far more than either fit
  error. That disagreement is not anomalous; it is this scatter.

The cause is not established. Real structure along different sight lines
would produce it, and so would a pointing that drifted, and so would
baseline-fit sensitivity in the low-amplitude captures. With the sweep
azimuths withdrawn there is no direction to correlate it against, so it
cannot be separated here.

### West is not line-free

`sensitivity()` recommends the west pointing as the noise reference on the
grounds that it is line-free, and panel (a) shows it as much the flattest of
the three. But its own Gaussian fit returns an amplitude of 5.4 percent of
continuum with a 152 kHz FWHM, the broadest in the set. West has the
weakest line, not no line.

The noise recommendation survives this, because it uses the residual about a
fitted polynomial baseline over a window offset from the line, not the raw
rms. But "line-free" is the wrong word for it in a manuscript, and a 5.4
percent fitted amplitude should not be reported as a detection either.

## 7. What is now blocked

* No pointing direction for the sweep can be recovered from the files. If no
  external record of the manual sweep exists, the 12 blocks are usable only
  as repeat observations of unknown direction.
* ~~The prototype tap count needs a GNU Radio installation.~~ **Settled**
  (section 5): `firdes` returns 32 299 taps, the branches consume the first
  16 384, and the truncation is confirmed by three statistics of the real
  captures.
* The row cadence rests on inference from noise statistics. Only an external
  record of the session, or a repeat measurement with a known setting, can
  make it certain.
* Antenna temperature would have to be measured, for example against a
  known load or by a sky dip, before any kelvin quantity is quoted as
  measured.
