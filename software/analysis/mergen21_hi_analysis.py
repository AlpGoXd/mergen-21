#!/usr/bin/env python3
"""
Mergen-21 first-light 21 cm H I analysis: end-to-end reproduction.

Regenerates, from the raw GNU Radio spectrometer captures:

  * mergen21_hi_measurements.csv     15 measurements, full parameter set
  * mergen21_hi_line_parameters.csv  the 3-pointing summary table
  * mergen21_data_manifest.csv       sha256 references for every input file
  * mergen21_hi_derived.json         scalar results quoted in the manuscript
  * mergen21_hi_validation.png       the three-panel figure

Inputs are read from a checkout of the mergen-21 repository; nothing is
copied into the package. Set MERGEN21_ROOT or edit ROOT below.

Usage:  python mergen21_hi_analysis.py [--root /path/to/mergen-21] [--outdir .]

Provenance of every assumed (as opposed to measured) quantity is marked
ASSUMED in the comments and recorded in mergen21_hi_methods.md.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy import stats as sps

import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
from astropy.utils import iers

iers.conf.auto_download = False  # offline reproducibility; sub-arcsec effect

# ----------------------------------------------------------------------------
# 1. Configuration and provenance constants
# ----------------------------------------------------------------------------

C_KMS = 299792.458          # speed of light, km/s
F0_MHZ = 1420.405751768     # H I rest frequency, MHz
F0_KHZ = F0_MHZ * 1e3

# Solar motion w.r.t. the LSR, Schoenrich, Binney & Dehnen (2010), km/s.
U_SUN, V_SUN, W_SUN = 11.1, 12.24, 7.25

# Spectrometer configuration, read from software/gnuradio/reciver.grc. At the
# time of the April 29 session the flowgraph's saved integration_time was
# 500, matching no actual capture; software/gnuradio/reciver.grc has since
# had that default corrected to 1000 (see that file's variable comment).
# Neither value is read by this script; TAU_ROW_STATIC_S and
# TAU_ROW_SWEEP_S below are the observer-confirmed per-capture cadences.
#   fft_size = 2048, samp_rate = 2048000
FFT_SIZE = 2048
SAMP_RATE = 2_048_000.0
CHAN_BW_HZ = SAMP_RATE / FFT_SIZE            # 1000.0 Hz channel SPACING.
# NOT the effective noise bandwidth: the prototype filter is narrower than
# the spacing and its exact width is unsettled. See PROVENANCE_ADDENDUM.md
# section 5. Nothing below uses CHAN_BW_HZ for a noise prediction.

# Row cadence. The observer confirmed on 2026-09-13 that every capture from
# the April 29 session, including the sweep ("_180partygirl_500int.dat"),
# ran with integration_time = 1000 (1.0 s per row), despite that filename's
# misleading "500int". The committed flowgraph's saved integration_time
# (500 at session time, since corrected to 1000; see
# software/gnuradio/reciver.grc) records the END of the session and was
# never authoritative for any individual capture's cadence.
# PROVENANCE_ADDENDUM.md section 4. The sweep analysis itself is withdrawn
# (PROVENANCE_ADDENDUM.md section 1); this value does not change any number
# the paper quotes (verified: outputs regenerated before/after this edit are
# identical except for the withdrawn sweep-block on_source_s/utc_mid/tau_row_s
# columns and frequency_axis.tau_per_row_s_sweep in the derived JSON).
TAU_ROW_STATIC_S = 1.0
TAU_ROW_SWEEP_S = 1.0

# Site. ASSUMED from observations/README.md ("~41.0 N, 29.0 E"); no GPS fix
# was logged. A 0.1 deg error moves v_bary by <0.01 km/s.
SITE = EarthLocation(lat=41.0 * u.deg, lon=29.0 * u.deg, height=100 * u.m)

# Pointing elevation. ASSUMED 35 deg, read off the Stellarium charts in
# observations/. The observer states elevation was held only APPROXIMATELY
# fixed. The mount has no positioner or encoder.
ALT_DEG = 35.0

# File timestamps are local (UTC+3, Istanbul); converted to UTC here.
LOCAL_UTC_OFFSET_H = 3.0

# ASSUMED system temperature, used only to express fractional noise in
# kelvin. T_ant was NEVER MEASURED; the 70 K term is a literature value for
# the sky at this frequency, not an observation of this instrument. Every
# _K column below is therefore a fractional quantity times this number and
# carries its full unquantified error. Fractional columns are the
# measurement. PROVENANCE_ADDENDUM.md section 2.
T_SYS_K = 193.5
T_SYS_IS_ASSUMED = True

# Receiver-noise arithmetic, from measurements/rf-chain/nf/README.md.
P_OUT_DBM_HZ = -133.46      # measured output noise density, 50 ohm input
KT0_DBM_HZ = -173.9         # thermal floor at the measured 23.6 C
GAIN_DB = 39.5              # cascade gain, ZNB8, TOSM at the DUT ports
CABLE_LOSS_DB = 0.6         # measured, nf/cable_loss.DAT; +/-0.2 dB
CABLE_LOSS_TOL_DB = 0.2

STATIC = {
    # label: (filename, local HH:MM:SS from filename, azimuth deg ASSUMED)
    "W": ("mergen21_spec_20260429_045525_bati.dat", "04:55:25", 270.0),
    "S": ("mergen21_spec_20260429_045857_guney.dat", "04:58:57", 180.0),
    "E": ("mergen21_spec_20260429_050204_doggu.dat", "05:02:04", 90.0),
}
SWEEP = ("mergen21_spec_20260429_050554_180partygirl_500int.dat", "05:05:54")
N_BLOCKS = 12
# Sweep azimuth: WITHDRAWN. An earlier version of this script mapped row
# index linearly onto 90 -> 270 deg. The observer confirms the sweep was
# driven by hand, was irregular in azimuth and contained pauses, so no
# row-to-azimuth mapping exists. The 12 blocks are retained as repeat
# observations of UNKNOWN direction: their line profiles and noise are
# measurable, their pointing is not.

# Each entry lists the path in the mergen-21 repository first and the path in
# the exported reproducibility package second. The first one that exists wins.
AUX_FILES = [
    ("measurements/rf-chain/nf/README.md", "calibration/NF_README.md"),
    ("measurements/rf-chain/nf/cable_loss.DAT", "calibration/cable_loss.DAT"),
    ("measurements/rf-chain/nf/just cooked reciver.DAT",
     "calibration/just cooked reciver.DAT"),
    ("measurements/rf-chain/nf/match noise.DAT", "calibration/match noise.DAT"),
    ("software/gnuradio/reciver.grc", "acquisition/reciver.grc"),
]

# ----------------------------------------------------------------------------
# 2. Frequency axis and spectral windows
# ----------------------------------------------------------------------------

# Baseband channel frequencies in kHz, offset from the LO, which was tuned
# to F0. Channel 0 of the saved row is DC, so fftshift puts DC at index 1024.
FAX_KHZ = np.fft.fftshift(np.fft.fftfreq(FFT_SIZE, 1.0 / SAMP_RATE)) / 1e3

LINE_WIN = (FAX_KHZ > 55) & (FAX_KHZ < 340)      # line search / fit window
# Baseline window: exclude the band-centre instrumental artifact (|f|<45 kHz),
# the filter roll-off (|f|>900 kHz) and the line itself.
BASE_WIN = (np.abs(FAX_KHZ) > 45) & (np.abs(FAX_KHZ) < 900) & ~LINE_WIN
# Reference band used for the panel (a) normalization: line-free, flat.
NORM_WIN = (FAX_KHZ > 250) & (FAX_KHZ < 750)
# Line-free channels used for the sensitivity estimate. Both sidebands are
# used and the narrowband spur at +406 kHz (12% of continuum in the east
# pointing) is excised; leaving it in inflates the east rms from 0.86 to
# 1.42 K and is the single largest window sensitivity in the whole analysis.
SPUR_KHZ = 406.0
SPUR_HALFWIDTH_KHZ = 12.0
NOISE_WIN = ((np.abs(FAX_KHZ) > 450) & (np.abs(FAX_KHZ) < 880)
             & (np.abs(FAX_KHZ - SPUR_KHZ) > SPUR_HALFWIDTH_KHZ))

BASELINE_ORDER = 3


def capture_path(root, fn):
    """Captures live under observations/data/ in the mergen-21 repository and
    under raw/ in the exported reproducibility package. Accept either."""
    for sub in ("observations/data", "raw"):
        p = root / sub / fn
        if p.exists():
            return p
    raise FileNotFoundError(
        f"{fn} not found under {root}/observations/data or {root}/raw")


def load_rows(path):
    """Saved rows are float32 power spectra, FFT order, FFT_SIZE per row."""
    a = np.fromfile(path, dtype=np.float32)
    n = a.size // FFT_SIZE
    return a[: n * FFT_SIZE].reshape(n, FFT_SIZE).astype(np.float64)


def average_rows(rows):
    """Average the saved rows into one spectrum.

    No fftshift is applied: the GNU Radio log-power FFT block in reciver.grc
    emits DC-centred vectors, so the saved channel order already matches
    FAX_KHZ. Shifting again would move the band-centre artifact to the band
    edge and put the line at a spurious offset.
    """
    return rows.mean(axis=0)


def fractional_excess(spec):
    """Continuum-removed fractional excess and the fitted baseline."""
    cf = np.polyfit(FAX_KHZ[BASE_WIN], spec[BASE_WIN], BASELINE_ORDER)
    base = np.polyval(cf, FAX_KHZ)
    return (spec - base) / base, base


def gauss_lin(x, a, mu, sig, c0, c1):
    return a * np.exp(-0.5 * ((x - mu) / sig) ** 2) + c0 + c1 * x


FWHM_PER_SIGMA = 2.0 * np.sqrt(2.0 * np.log(2.0))   # 2.3548


def fit_gaussian(excess):
    """Gaussian + local linear baseline fit over LINE_WIN.

    Returns amplitude (fraction), centroid (kHz), FWHM (kHz) and their
    1-sigma formal errors from the covariance matrix.
    """
    x, y = FAX_KHZ[LINE_WIN], excess[LINE_WIN]
    p0 = [y.max(), x[int(np.argmax(y))], 45.0, 0.0, 0.0]
    p, cov = curve_fit(gauss_lin, x, y, p0=p0, maxfev=40000)
    e = np.sqrt(np.diag(cov))
    return dict(
        amp=p[0], amp_err=e[0],
        centroid=p[1], centroid_err=e[1],
        fwhm=FWHM_PER_SIGMA * abs(p[2]), fwhm_err=FWHM_PER_SIGMA * e[2],
    )


def moment_centroid(excess, smooth=9):
    """Estimator used for the sweep blocks in the published figure:
    9-channel boxcar, then the intensity-weighted mean of channels above
    half of the smoothed peak. No uncertainty is defined for it.
    """
    sm = np.convolve(excess, np.ones(smooth) / smooth, mode="same")
    masked = np.where(LINE_WIN, sm, -9.0)
    i = int(np.argmax(masked))
    pk = sm[i]
    idx = np.where(LINE_WIN & (sm > pk / 2.0))[0]
    ctr = float(np.sum(FAX_KHZ[idx] * sm[idx]) / np.sum(sm[idx])) if idx.size > 1 else FAX_KHZ[i]
    width = (FAX_KHZ[idx].max() - FAX_KHZ[idx].min()) if idx.size > 1 else np.nan
    return dict(peak=pk, centroid=ctr, halfpower_width=width)


# ----------------------------------------------------------------------------
# 3. Pointing geometry and velocity corrections
# ----------------------------------------------------------------------------

def geometry(az_deg, t_utc, alt_deg=ALT_DEG):
    """Return pointing coordinates and the two velocity corrections.

    v_bary : observer motion (Earth rotation + orbit) toward the pointing,
             from astropy's radial_velocity_correction (barycentric).
    v_solar: projection of the Sun's peculiar motion onto the sightline.
    Both are added to the observed radial velocity to reach v_LSR.
    """
    aa = AltAz(az=az_deg * u.deg, alt=alt_deg * u.deg, obstime=t_utc, location=SITE)
    icrs = SkyCoord(aa).transform_to("icrs")
    g = icrs.galactic
    lr, br = g.l.rad, g.b.rad
    v_bary = icrs.radial_velocity_correction().to(u.km / u.s).value
    v_solar = (U_SUN * np.cos(br) * np.cos(lr)
               + V_SUN * np.cos(br) * np.sin(lr)
               + W_SUN * np.sin(br))
    return dict(ra_deg=icrs.ra.deg, dec_deg=icrs.dec.deg,
                l_deg=g.l.deg, b_deg=g.b.deg,
                v_bary_kms=v_bary, v_solar_kms=v_solar)


def utc_from_local(hhmm):
    return Time(f"2026-04-29T{hhmm}", scale="utc") - LOCAL_UTC_OFFSET_H * u.hour


def doppler_kms(offset_khz):
    """Radial velocity of a line seen offset_khz ABOVE the rest frequency."""
    return -C_KMS * offset_khz / F0_KHZ


# ----------------------------------------------------------------------------
# 4. Build the 15-measurement table
# ----------------------------------------------------------------------------

def row_rms(rows):
    """Fractional rms of a SINGLE row, from successive-row differencing on
    the line-free window. Differencing removes gain drift and sky
    continuum, leaving the radiometric term. Used only for the
    assumption-free consistency check in measure()."""
    d = np.diff(rows, axis=0) / np.sqrt(2.0)
    return float(np.median(np.std(d, axis=0)[NOISE_WIN]
                           / rows.mean(axis=0)[NOISE_WIN]))


def measure(spec, n_rows, t_mid, az_deg, label, source, kind, tau_row,
            rms_row):
    """az_deg=None means the pointing is unknown (all sweep blocks). Every
    direction-dependent and velocity-frame column is then NaN rather than
    computed from a withdrawn assumption."""
    ex, base = fractional_excess(spec)
    g = fit_gaussian(ex)
    m = moment_centroid(ex)
    if az_deg is None:
        nan = float("nan")
        geo = {k: nan for k in ("ra_deg", "dec_deg", "l_deg", "b_deg",
                                "v_bary_kms", "v_solar_kms")}
        v_motion = nan
    else:
        geo = geometry(az_deg, t_mid)
        v_motion = geo["v_bary_kms"] + geo["v_solar_kms"]

    # Panel (a) reading: peak of the spectrum normalized to the median of a
    # line-free reference band. This is NOT the fitted amplitude; see methods.
    norm = spec / np.median(spec[NORM_WIN])
    raw_peak_excess = float(norm[LINE_WIN].max() - 1.0)

    # Two noise estimators, because they answer different questions.
    #  rms_frac  : scatter of the continuum-removed spectrum over line-free
    #              channels. Includes residual baseline structure, so it is
    #              an upper bound and is inflated where the line has wings.
    #  rms_diff  : robust scale of the successive-channel difference / sqrt(2).
    #              Immune to baseline curvature. The measured adjacent-channel
    #              correlation is 0.05, so this is effectively unbiased; an
    #              earlier comment here called it a lower bound, which was
    #              reasoning from the filter design rather than from the data.
    rms_frac = float(np.std(ex[NOISE_WIN]))
    d = np.diff(ex[NOISE_WIN]) / np.sqrt(2.0)
    rms_diff = float(1.4826 * np.median(np.abs(d - np.median(d))))
    tau_s = n_rows * tau_row

    return {
        "id": label, "kind": kind, "source_file": source,
        "utc_mid": t_mid.isot, "n_rows": n_rows, "on_source_s": round(tau_s, 2),
        "az_deg": az_deg if az_deg is not None else float("nan"),
        "alt_deg": ALT_DEG if az_deg is not None else float("nan"),
        "tau_row_s": tau_row,
        "ra_deg": round(geo["ra_deg"], 3), "dec_deg": round(geo["dec_deg"], 3),
        "l_deg": round(geo["l_deg"], 2), "b_deg": round(geo["b_deg"], 2),
        "centroid_kHz": round(g["centroid"], 2),
        "centroid_err_kHz": round(g["centroid_err"], 2),
        "centroid_moment_kHz": round(m["centroid"], 2),
        "amp_pct": round(100 * g["amp"], 3),
        "amp_err_pct": round(100 * g["amp_err"], 3),
        "smoothed_peak_pct": round(100 * m["peak"], 3),
        "raw_peak_excess_pct": round(100 * raw_peak_excess, 3),
        "fwhm_kHz": round(g["fwhm"], 2),
        "fwhm_err_kHz": round(g["fwhm_err"], 2),
        "fwhm_kms": round(C_KMS * g["fwhm"] / F0_KHZ, 2),
        "halfpower_width_kHz": round(m["halfpower_width"], 2),
        "v_bary_kms": round(geo["v_bary_kms"], 3),
        "v_solar_kms": round(geo["v_solar_kms"], 3),
        "v_motion_kms": round(v_motion, 3),
        "v_lsr_kms": round(doppler_kms(g["centroid"]) + v_motion, 2),
        "v_lsr_moment_kms": round(doppler_kms(m["centroid"]) + v_motion, 2),
        "rms_frac": round(rms_frac, 6),
        "rms_diff_frac": round(rms_diff, 6),
        "rms_row_frac": round(rms_row, 6),
        "dT_baseline_K": round(rms_frac * T_SYS_K, 3),
        "dT_diff_K": round(rms_diff * T_SYS_K, 3),
        # Consistency check that assumes nothing: the averaged spectrum
        # should be quieter than one row by sqrt(n_rows). Both sides
        # measured on the same line-free channels. No T_sys, no bandwidth,
        # no cadence enters. PROVENANCE_ADDENDUM.md section 5.
        "rms_expected_from_rows": round(rms_row / np.sqrt(n_rows), 6),
        "rms_ratio_meas_over_expected": round(
            rms_diff / (rms_row / np.sqrt(n_rows)), 3),
        "snr_peak": round(g["amp"] / rms_diff, 1),
    }


def build_table(root):
    recs, spectra = [], {}

    for k, (fn, hhmm, az) in STATIC.items():
        rows = load_rows(capture_path(root, fn))
        spec = average_rows(rows)
        t_mid = utc_from_local(hhmm) + (rows.shape[0] * TAU_ROW_STATIC_S / 2) * u.s
        recs.append(measure(spec, rows.shape[0], t_mid, az, k, fn, "static",
                            TAU_ROW_STATIC_S, row_rms(rows)))
        spectra[k] = spec

    fn, hhmm = SWEEP
    rows = load_rows(capture_path(root, fn))
    n = rows.shape[0]
    t0 = utc_from_local(hhmm)
    srms = row_rms(rows)
    for i, blk in enumerate(np.array_split(np.arange(n), N_BLOCKS), start=1):
        spec = average_rows(rows[blk])
        j = blk[len(blk) // 2]
        t_mid = t0 + j * TAU_ROW_SWEEP_S * u.s
        recs.append(measure(spec, blk.size, t_mid, None,
                            f"SW{i:02d}", fn, "sweep_block",
                            TAU_ROW_SWEEP_S, srms))

    return pd.DataFrame(recs), spectra


# ----------------------------------------------------------------------------
# 5. Kinematic regression and significance
# ----------------------------------------------------------------------------

def regression(df, ycol="centroid_kHz"):
    """WITHDRAWN, retained for inspection only. Not called by main().

    This regresses centroid on observer motion, whose x axis is computed
    from the withdrawn sweep azimuth ramp. With the sweep pointing
    gone only three points remain, which support neither a regression nor a
    correlation. PROVENANCE_ADDENDUM.md sections 1 and 6.
    """
    """OLS of observed line centroid on predicted observer+solar motion.

    A line at a single v_LSR gives slope = F0/c = 4.738 kHz per km/s and
    intercept 0. A signal fixed in the terrestrial frame gives slope 0.
    The reported significance is the t-statistic of the slope against zero.
    """
    x = df["v_motion_kms"].to_numpy()
    y = df[ycol].to_numpy()
    lr = sps.linregress(x, y)
    resid = y - (lr.intercept + lr.slope * x)
    n = len(x)

    # Lag-1 autocorrelation of the residuals, ordered as observed. Non-zero
    # values mean the 15 points are not independent and the t-statistic below
    # is optimistic; see the effective-N correction.
    order = np.argsort(df["utc_mid"].to_numpy())
    r1 = float(np.corrcoef(resid[order][:-1], resid[order][1:])[0, 1])
    n_eff = n * (1 - r1) / (1 + r1) if r1 > -1 else np.nan
    t_eff = lr.slope / (lr.stderr * np.sqrt(n / n_eff)) if np.isfinite(n_eff) and n_eff > 0 else np.nan

    return dict(
        n=n, slope=lr.slope, slope_err=lr.stderr,
        intercept=lr.intercept, intercept_err=lr.intercept_stderr,
        r=lr.rvalue, sigma_vs_zero=lr.slope / lr.stderr,
        theory_slope=F0_KHZ / C_KMS,
        resid_rms_kHz=float(np.std(resid, ddof=2)),
        lag1_autocorr=r1, n_effective=n_eff, sigma_autocorr_corrected=t_eff,
    )


def latitude_correlation(df):
    """WITHDRAWN, retained for inspection only. Not called by main().

    This correlates amplitude with Galactic latitude, which for the 12
    sweep blocks is computed from the withdrawn azimuth ramp. With the sweep pointing
    gone only three points remain, which support neither a regression nor a
    correlation. PROVENANCE_ADDENDUM.md sections 1 and 6.
    """
    """Panel (c): fitted amplitude against |b|."""
    x = np.abs(df["b_deg"].to_numpy())
    y = df["amp_pct"].to_numpy()
    r, p = sps.pearsonr(x, y)
    return dict(r=float(r), p=float(p), n=len(x))


# ----------------------------------------------------------------------------
# 6. Receiver noise with the cable reference plane resolved
# ----------------------------------------------------------------------------

def noise_figure():
    """Gain-method noise figure, with and without the cable correction.

    The ZNB8 cascade gain was TOSM-calibrated at the DUT ports, so the cable
    between the receiver output and the spectrum analyzer was de-embedded
    from the gain but NOT from the analyzer's noise reading. The measured
    output density is therefore 0.6 dB low and must be corrected upward.
    """
    out = {}
    for tag, corr in (("uncorrected", 0.0), ("corrected", CABLE_LOSS_DB)):
        nf_db = (P_OUT_DBM_HZ + corr) - KT0_DBM_HZ - GAIN_DB
        t_rx = 290.0 * (10 ** (nf_db / 10.0) - 1.0)
        out[tag] = dict(nf_db=round(nf_db, 3), t_rx_k=round(t_rx, 1))
    lo = (P_OUT_DBM_HZ + CABLE_LOSS_DB - CABLE_LOSS_TOL_DB) - KT0_DBM_HZ - GAIN_DB
    hi = (P_OUT_DBM_HZ + CABLE_LOSS_DB + CABLE_LOSS_TOL_DB) - KT0_DBM_HZ - GAIN_DB
    out["cable_tolerance_nf_db"] = [round(lo, 3), round(hi, 3)]
    out["cable_loss_db"] = CABLE_LOSS_DB
    return out


def sensitivity(df):
    """Measured per-channel sensitivity.

    The radiometer-equation column that used to live here is removed: it
    needed an effective channel bandwidth that is not established, and a row
    cadence that is inferred rather than recorded, so it was comparing a
    measurement against two assumptions. It is replaced by a check that
    assumes neither, the averaged spectrum against its own rows.

    The manuscript should quote the baseline rms of a LINE-FREE pointing
    (west); in the south pointing that estimator is dominated by the line's
    own wings. All kelvin values are fractional rms times an ASSUMED T_sys.
    """
    rows = []
    for _, r in df[df.kind == "static"].iterrows():
        rows.append(dict(
            id=r["id"], on_source_s=r["on_source_s"],
            rms_baseline_frac=r["rms_frac"], rms_diff_frac=r["rms_diff_frac"],
            dT_baseline_K_assumed_Tsys=r["dT_baseline_K"],
            dT_diff_K_assumed_Tsys=r["dT_diff_K"],
            rms_expected_from_rows=r["rms_expected_from_rows"],
            ratio_meas_over_expected=r["rms_ratio_meas_over_expected"],
            snr_peak=r["snr_peak"]))
    w = df[df.id == "W"].iloc[0]
    return dict(per_pointing=rows,
                recommended_quote_frac=w["rms_frac"],
                recommended_quote_K_assumed_Tsys=w["dT_baseline_K"],
                recommended_basis="west pointing, line-free, polynomial-baseline "
                                  "rms; kelvin value scaled by an ASSUMED T_sys")


# ----------------------------------------------------------------------------
# 7. Input manifest
# ----------------------------------------------------------------------------

def manifest(root):
    recs = []
    caps = [(STATIC[k][0], f"static pointing {k}") for k in STATIC]
    caps += [(SWEEP[0], "180 deg east-west sweep, 12 blocks")]
    wanted = []
    for fn, role in caps:
        try:
            wanted.append((str(capture_path(root, fn).relative_to(root)), role, True))
        except FileNotFoundError:
            wanted.append((fn, role, True))
    for alts in AUX_FILES:
        chosen = next((a for a in alts if (root / a).exists()), alts[0])
        wanted.append((chosen, "auxiliary / calibration reference", False))
    for rel, role, is_capture in wanted:
        p = root / rel
        if not p.exists():
            recs.append(dict(path=rel, role=role, bytes=-1, sha256="MISSING", rows=-1))
            continue
        b = p.read_bytes()
        rows = len(b) // (FFT_SIZE * 4) if is_capture else -1
        recs.append(dict(path=rel, role=role, bytes=len(b),
                         sha256=hashlib.sha256(b).hexdigest(), rows=rows))
    return pd.DataFrame(recs)


# ----------------------------------------------------------------------------
# 8. Figure
# ----------------------------------------------------------------------------

META_GREY = "#888888"
COL = {"S": "#1f6fb4", "E": "#d1741f", "W": "#7a7a7a"}


def apply_figure_style(sizes=(8, 7, 6)):
    import matplotlib as mpl
    base, secondary, tick = sizes
    mpl.rcParams.update({
        "font.family": "sans-serif", "font.size": base,
        "axes.labelsize": base, "axes.titlesize": base,
        "legend.fontsize": secondary,
        "xtick.labelsize": tick, "ytick.labelsize": tick,
        "axes.linewidth": 0.6,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3, "ytick.major.size": 3,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "legend.frameon": False,
        "figure.dpi": 200, "savefig.dpi": 300, "savefig.bbox": "tight",
        "axes.titleweight": "normal", "axes.titlelocation": "left",
        "lines.linewidth": 1.2, "patch.linewidth": 0.6,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def panel_letter(ax, letter, dx=-0.18, dy=1.02):
    import matplotlib.pyplot as plt
    ax.text(dx, dy, letter, transform=ax.transAxes, fontweight="bold",
            fontsize=plt.rcParams.get("font.size", 8) + 1, va="bottom", ha="left")


def make_figure(df, spectra, outpath):
    import matplotlib.pyplot as plt
    apply_figure_style()

    st = df.set_index("id")
    sw = df[df.kind == "sweep_block"]

    fig = plt.figure(figsize=(7.0, 5.1))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 1.0], hspace=0.52, wspace=0.30)

    # -- panel a: the three averaged spectra ---------------------------------
    ax = fig.add_subplot(gs[0, :])
    # Azimuth from the filename; Galactic latitude is NOT quoted here because
    # it depends on an elevation the observer held only approximately.
    lab = {"S": "south (az 180$^\\circ$)", "E": "east (az 90$^\\circ$)",
           "W": "west (az 270$^\\circ$)"}
    for k in ("W", "E", "S"):
        norm = spectra[k] / np.median(spectra[k][NORM_WIN])
        ax.plot(FAX_KHZ / 1e3, norm, lw=1.5 if k == "S" else 1.0,
                color=COL[k], label=lab[k], zorder=3 if k == "S" else 2)
    ax.axvspan(0.055, 0.340, color="#9ecae1", alpha=0.30, lw=0, zorder=0)
    ax.annotate("instrumental artifact on the\nrest frequency (4.6$\\times$ continuum)",
                xy=(0.0, 1.45), xytext=(-0.62, 1.36), fontsize=6, ha="left",
                color="0.25", arrowprops=dict(arrowstyle="-", lw=0.6, color="0.45"))
    # Both numbers quoted here are the ones tabulated for the same pointing:
    # the raw normalized peak (panel a's own scale) and the fitted FWHM.
    pk = st.loc["S", "raw_peak_excess_pct"]
    fw = st.loc["S", "fwhm_kHz"]
    fv = st.loc["S", "fwhm_kms"]
    ax.annotate(f"H I line: peak {pk:.0f}% above the reference band,\n"
                f"fitted FWHM {fw:.0f} kHz ({fv:.0f} km s$^{{-1}}$)",
                xy=(st.loc["S", "centroid_kHz"] / 1e3, 1.0 + pk / 100),
                xytext=(0.36, 1.24), fontsize=6, ha="left", color="0.25",
                arrowprops=dict(arrowstyle="-", lw=0.6, color="0.45"))
    ax.set_xlabel("frequency offset from 1420.405 MHz (MHz)")
    ax.set_ylabel("power (normalized)")
    ax.set_title("H I detected above the rest frequency in all three pointings")
    ax.set_xlim(-1.02, 1.02)
    ax.set_ylim(0.40, 1.52)
    ax.legend(loc="lower right", fontsize=6)
    panel_letter(ax, "a")

    # -- panel b: noise consistency, assumption-free -------------------------
    # Neither axis uses T_sys, channel bandwidth or cadence. If the rows of a
    # capture are independent, the averaged spectrum must be quieter than one
    # row by sqrt(n_rows). Replaces the withdrawn kinematic regression.
    axb = fig.add_subplot(gs[1, 0])
    xe = df["rms_expected_from_rows"].to_numpy() * 1e3
    ym = df["rms_diff_frac"].to_numpy() * 1e3
    lim = (0.85 * min(xe.min(), ym.min()), 1.18 * max(xe.max(), ym.max()))
    axb.plot(lim, lim, lw=3.0, color="#9ecae1", solid_capstyle="round", zorder=1,
             label="independent rows\n(prediction)")
    axb.plot(sw["rms_expected_from_rows"] * 1e3, sw["rms_diff_frac"] * 1e3,
             "o", ms=4, mfc="white", mec="0.35", mew=0.9, zorder=3,
             label="12 sweep blocks\n(direction unknown)")
    for k in ("W", "E", "S"):
        axb.plot(st.loc[k, "rms_expected_from_rows"] * 1e3,
                 st.loc[k, "rms_diff_frac"] * 1e3, "s", ms=6, color=COL[k],
                 mec="white", mew=0.7, zorder=4)
        axb.annotate(k, (st.loc[k, "rms_expected_from_rows"] * 1e3,
                         st.loc[k, "rms_diff_frac"] * 1e3),
                     textcoords="offset points",
                     xytext={"W": (9, -5), "S": (-3, 7), "E": (-11, 1)}[k],
                     fontsize=6, color=COL[k])
    axb.set_xscale("log"); axb.set_yscale("log")
    axb.set_xlim(*lim); axb.set_ylim(*lim)
    for ax_ in (axb.xaxis, axb.yaxis):
        ax_.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
        ax_.set_minor_formatter(plt.NullFormatter())
    axb.set_xticks([3, 5, 7, 10]); axb.set_yticks([3, 5, 7, 10])
    axb.set_xlabel("predicted from single-row noise ($\\times10^{-3}$)")
    axb.set_ylabel("measured in averaged spectrum ($\\times10^{-3}$)")
    _rat = float(df["rms_ratio_meas_over_expected"].mean())
    axb.set_title("Averaging integrates down to\nwithin %.0f%% of the row prediction"
                  % (abs(1 - _rat) * 100))
    axb.legend(loc="upper left", fontsize=5.2, handlelength=1.4, labelspacing=0.45)
    panel_letter(axb, "b")

    # -- panel c: fitted centroid against line strength ---------------------
    # Replaces the withdrawn amplitude-against-latitude panel. No pointing
    # enters. West is the line-free pointing, so its "centroid" is a fit to
    # noise; plotting centroid against amplitude shows exactly that, and
    # shows the centroid tightening as the line becomes detectable.
    axc = fig.add_subplot(gs[1, 1])
    cen, cerr = df["centroid_kHz"], df["centroid_err_kHz"]
    wmean = float(np.sum(cen / cerr ** 2) / np.sum(1 / cerr ** 2))
    sd = float(cen.std(ddof=1))
    axc.axhspan(wmean - sd, wmean + sd, color="#9ecae1", alpha=0.30, lw=0, zorder=0,
                label="all 15 measurements\n($\\pm$%.0f kHz)" % sd)
    axc.axhline(wmean, lw=0.8, ls="--", color=META_GREY, zorder=1)
    axc.errorbar(sw["amp_pct"], sw["centroid_kHz"], yerr=sw["centroid_err_kHz"],
                 fmt="o", ms=4, mfc="white", mec="0.35", mew=0.9, ecolor="0.6",
                 elinewidth=0.6, zorder=3, label="12 sweep blocks")
    for k in ("W", "S", "E"):
        axc.errorbar(st.loc[k, "amp_pct"], st.loc[k, "centroid_kHz"],
                     yerr=st.loc[k, "centroid_err_kHz"], fmt="s", ms=6,
                     color=COL[k], mec="white", mew=0.7, ecolor=COL[k],
                     elinewidth=0.7, zorder=4)
        axc.annotate(k, (st.loc[k, "amp_pct"], st.loc[k, "centroid_kHz"]),
                     textcoords="offset points",
                     xytext={"W": (9, -2), "S": (-11, -3), "E": (8, -6)}[k],
                     fontsize=6, color=COL[k])
    axc.set_xlabel("fitted line amplitude (% of continuum)")
    axc.set_ylabel("fitted line centroid (kHz)")
    # The scatter is reported against the formal errors, not against a
    # pointing model: with the sweep azimuths withdrawn there is no direction
    # to correlate it with. It is ~%s times the median fit error, so it is a
    # property of the measurements, not of the fitting.
    axc.set_title("Centroid scatters $\\pm$%.0f kHz, far beyond\nthe %.1f kHz median fit error"
                  % (sd, float(cerr.median())))
    axc.margins(x=0.14, y=0.16)
    axc.legend(loc="lower right", fontsize=5.2, handlelength=1.4, labelspacing=0.4)
    panel_letter(axc, "c")

    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    return fig


# ----------------------------------------------------------------------------
# 9. Driver
# ----------------------------------------------------------------------------

def main(root, outdir):
    root, outdir = Path(root), Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df, spectra = build_table(root)

    df.to_csv(outdir / "mergen21_hi_measurements.csv", index=False)

    st = df[df.kind == "static"].set_index("id")
    summary = pd.DataFrame([{
        "pointing": k,
        "l_deg": round(st.loc[k, "l_deg"], 1), "b_deg": round(st.loc[k, "b_deg"], 1),
        "peak_pct": round(st.loc[k, "amp_pct"], 2),
        "centroid_kHz": round(st.loc[k, "centroid_kHz"], 1),
        "fwhm_kHz": round(st.loc[k, "fwhm_kHz"], 1),
        "fwhm_kms": round(st.loc[k, "fwhm_kms"], 1),
        "v_bary_plus_solar_kms": round(st.loc[k, "v_motion_kms"], 1),
        "v_lsr_kms": round(st.loc[k, "v_lsr_kms"], 1),
    } for k in ("S", "E", "W")])
    summary.to_csv(outdir / "mergen21_hi_line_parameters.csv", index=False)

    manifest(root).to_csv(outdir / "mergen21_data_manifest.csv", index=False)

    derived = {
        "frequency_axis": {"channel_spacing_Hz": CHAN_BW_HZ,
                           "tau_per_row_s_static": TAU_ROW_STATIC_S,
                           "tau_per_row_s_sweep": TAU_ROW_SWEEP_S,
                           "f0_MHz": F0_MHZ},
        "withdrawn": {
            "note": "Computed by earlier versions of this script, removed "
                    "because every one of them takes sweep azimuth as an "
                    "input and the azimuth mapping is withdrawn. See "
                    "PROVENANCE_ADDENDUM.md sections 1 and 6.",
            "items": ["kinematic_regression_gaussian_centroid",
                      "kinematic_regression_published_moment_centroid",
                      "latitude_correlation",
                      "sweep block az_deg / l_deg / b_deg / v_lsr_kms"],
        },
        "sensitivity": sensitivity(df),
        "noise_figure": noise_figure(),
        "T_sys_K_ASSUMED": T_SYS_K,
        "assumptions": {
            "T_ant_never_measured": True,
            "all_K_columns_are_fractional_times_T_sys": True,
            "pointing_elevation_deg_approximate": ALT_DEG,
            "static_azimuth_from_filename_only": True,
            "sweep_azimuth": "withdrawn: manual, irregular, paused",
            "tau_row_inferred_not_recorded": True,
            "site_lat_lon_deg": [41.0, 29.0],
            "local_utc_offset_h": LOCAL_UTC_OFFSET_H,
        },
    }
    (outdir / "mergen21_hi_derived.json").write_text(json.dumps(derived, indent=2, default=float))

    make_figure(df, spectra, outdir / "mergen21_hi_validation.png")
    return df, derived


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("MERGEN21_ROOT", "repos/mergen-21"))
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()
    _df, _d = main(a.root, a.outdir)
    print(_df[["id", "utc_mid", "n_rows", "tau_row_s", "centroid_kHz", "centroid_err_kHz",
               "amp_pct", "amp_err_pct", "fwhm_kHz", "rms_diff_frac",
               "rms_ratio_meas_over_expected", "snr_peak"]]
          .to_string(index=False))
    print(json.dumps({k: _d[k] for k in ("sensitivity", "noise_figure",
                                         "withdrawn")}, indent=2, default=float))
