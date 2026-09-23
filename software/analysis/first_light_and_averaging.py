#!/usr/bin/env python3
"""
Mergen-21: first-light spectra and the averaging comparison.

Builds <outdir>/figures/first_light_and_averaging.pdf (+ .png preview) and
<outdir>/averaging_noise.csv from the raw spectrometer captures.

Captures are read from <root>/observations/data/, falling back to
<root>/raw/ if not found there (see capture_path()). Run from anywhere:
    python3 software/analysis/first_light_and_averaging.py
    python3 first_light_and_averaging.py --root /path/to/mergen-21 --outdir .

------------------------------------------------------------------------
ACQUISITION FACTS
------------------------------------------------------------------------
Verified in this script from software/gnuradio/reciver.grc:
  samp_rate = 2 048 000 Sa/s, fft_size = 2048, K = 8 branches,
  Kaiser beta = 8.6, LO_freq = 1 420 405 000 Hz, rx_gain = 30 dB (manual),
  rf_bandwidth = 2 MHz, RX rfdc/bbdc/quadrature correction enabled.

  Channel spacing  = samp_rate / fft_size            = 1000 Hz
  FFT hop          = fft_size samples (the eight branches are offset by
                     fft_size each and every branch consumes fft_size
                     samples per output vector)
  Frame period     = fft_size / samp_rate            = 1.000 ms
  Row period       = M * 1.000 ms, M = integrate decimation

  The stored .dat is the LINEAR power spectrum: file sink (float, vlen
  2048) is fed from the integrate block via a scalar multiply.  The
  nlog10 block feeds only the on-screen vector sink, so no logarithm is
  applied to the recorded data.

Supplied by the observer (not recoverable from the files):
  W  bati       M = 1000 -> 1.0 s per row
  S  guney      M = 1000 -> 1.0 s per row
  E1 doggu      M = 1000 -> 1.0 s per row   (primary east)
  E2 Dogu_100   M =  100 -> 0.1 s per row   (additional east)

  E1 and E2 are SEPARATE acquisitions at the same nominal east pointing,
  2.7 min apart; the flowgraph was stopped, only the averaging variable
  was changed, it was regenerated, and it was restarted.  They are not
  one recording processed two ways.

METADATA DISCREPANCY, NOW CORRECTED IN THE FLOWGRAPH:
  At the time of the April 29 session, software/gnuradio/reciver.grc had
  integration_time = 500, which matched neither M = 1000 nor M = 100 of any
  real capture. The saved flowgraph state also carried the "500int" of the
  sweep capture's filename. The observer's confirmed per-capture values
  (below) are used here; the .grc value was never used for this figure.
  software/gnuradio/reciver.grc has since had its integration_time default
  corrected to 1000 (see that file's variable comment); this script's
  hardcoded CAPTURES table is unaffected either way, since it always used
  the observer's confirmed values, not the .grc default. Nothing in this
  figure depends on the sweep capture.
"""
import argparse
import pathlib
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- config
SAMP_RATE = 2_048_000.0
FFT_SIZE = 2048
LO_HZ = 1_420_405_000.0
HOP = FFT_SIZE                       # samples per FFT frame
FRAME_S = HOP / SAMP_RATE            # 1.000 ms
DF_KHZ = SAMP_RATE / FFT_SIZE / 1e3  # 1.000 kHz

CAPTURES = {                         # id -> (filename, M frames/row)
    "W":  ("mergen21_spec_20260429_045525_bati.dat", 1000),
    "S":  ("mergen21_spec_20260429_045857_guney.dat", 1000),
    "E1": ("mergen21_spec_20260429_050204_doggu.dat", 1000),
    "E2": ("mergen21_spec_20260429_050450_Dogu_100.dat", 100),
}
LABEL = {"W": "West", "S": "South", "E1": "East"}
COLOR = {"W": "#7fa8cd", "S": "#b2182b", "E1": "#1f6fb4", "E2": "#e08214"}

N_SKIP = 6            # startup rows dropped (see startup_sensitivity)
BASE_ORDER = 3        # continuum polynomial order (see order_sensitivity)
FIT_KHZ = 900.0       # |f| beyond this is analog filter roll-off
ART_KHZ = 15.0        # band-center instrumental artifact, masked
LINE_LO, LINE_HI = 25.0, 320.0   # line region, excluded from continuum fit
SPUR_THRESH = 1.04    # relative level that flags a narrowband spur
SPUR_HALF = 6.0       # kHz notched either side of a flagged spur
MIN_PAIRS = 5         # panel (b) cutoff: independent pairs required

FAX = (np.arange(FFT_SIZE) - FFT_SIZE // 2) * DF_KHZ   # kHz from nominal LO


# ------------------------------------------------------------- utilities
def capture_path(root, fn):
    """Captures live under observations/data/ in the mergen-21 repository and
    under raw/ in the exported reproducibility package. Accept either."""
    for sub in ("observations/data", "raw"):
        p = root / sub / fn
        if p.exists():
            return p
    raise FileNotFoundError(
        f"{fn} not found under {root}/observations/data or {root}/raw")


def load_rows(root, name):
    """Raw capture -> (n_rows, 2048) linear power, float64."""
    a = np.fromfile(capture_path(root, name), dtype=np.float32)
    if a.size % FFT_SIZE:
        raise ValueError(f"{name}: {a.size} floats is not a whole number of rows")
    return a.reshape(-1, FFT_SIZE).astype(np.float64)


def spur_mask(mean_spec):
    """Notch narrowband features outside the line region."""
    in_band = np.abs(FAX) <= FIT_KHZ
    med = np.median(mean_spec[in_band])
    flagged = np.zeros(FFT_SIZE, bool)
    hot = (mean_spec / med > SPUR_THRESH) & (np.abs(FAX) > LINE_HI) & in_band
    for f0 in FAX[hot]:
        flagged |= np.abs(FAX - f0) <= SPUR_HALF
    return flagged


def continuum(mean_spec, extra_mask=None, order=BASE_ORDER):
    """Polynomial continuum fitted off the line, artifact and spurs."""
    fit = (np.abs(FAX) <= FIT_KHZ) & (np.abs(FAX) > ART_KHZ) \
        & ~((FAX > LINE_LO) & (FAX < LINE_HI)) & ~spur_mask(mean_spec)
    if extra_mask is not None:
        fit &= ~extra_mask
    coef = np.polyfit(FAX[fit] / 1e3, mean_spec[fit], order)
    return np.polyval(coef, FAX / 1e3), fit


def fractional_excess(mean_spec, order=BASE_ORDER):
    base, fit = continuum(mean_spec, order=order)
    return (mean_spec - base) / base * 100.0, fit


# --------------------------------------------------- panel (b) estimator
def common_line_free(rows_by_id):
    """Channels usable in every record: no artifact, no line, no spur."""
    keep = (np.abs(FAX) <= FIT_KHZ) & (np.abs(FAX) > ART_KHZ) \
        & ~((FAX > LINE_LO) & (FAX < LINE_HI))
    for X in rows_by_id.values():
        keep &= ~spur_mask(X[N_SKIP:].mean(0))
    return keep


def normalize_rows(X, mask):
    """Divide each row by its own mean over the line-free channels.

    Removes the common gain/total-power factor that drifts through each
    record.  Cost: the line-free mean of every normalized row is exactly
    1, which ties the channels together with a correlation of -1/N_ch
    (N_ch ~ 860 here, so ~ -0.001) and removes any real total-power
    variation along with the drift.  Absolute level is therefore not
    recoverable from the normalized rows, by construction.
    """
    return X / X[:, mask].mean(1, keepdims=True)


def block_pair_noise(Xn, mask, n_block):
    """Fractional fluctuation from disjoint pairs of averaged blocks.

    Rows -> non-overlapping blocks of n_block -> disjoint consecutive
    pairs -> (B2 - B1)/sqrt(2) -> scatter across the line-free channels,
    pooled in quadrature over pairs.  Each row enters exactly one block
    and each block exactly one pair, so the pairs are independent.
    Differencing two block spectra also cancels any spectral structure
    that is fixed between them, which is why this tracks the thermal
    component and is NOT a measure of absolute sensitivity or of
    long-term total-power stability.
    """
    n_blocks = Xn.shape[0] // n_block
    if n_blocks < 2:
        return None
    B = Xn[:n_blocks * n_block].reshape(n_blocks, n_block, FFT_SIZE).mean(1)
    n_pairs = n_blocks // 2
    d = (B[1:2 * n_pairs:2] - B[0:2 * n_pairs:2]) / np.sqrt(2.0)
    var = d[:, mask].var(1, ddof=1)
    per_pair = np.sqrt(var)
    return dict(sigma_frac=float(np.sqrt(var.mean())),
                spread_frac=float(per_pair.std(ddof=1)) if n_pairs > 1 else np.nan,
                sem_frac=float(per_pair.std(ddof=1) / np.sqrt(n_pairs))
                if n_pairs > 1 else np.nan,
                n_pairs=int(n_pairs), n_blocks=int(n_blocks),
                n_channels=int(mask.sum()))


def temporal_lag1(Xn, mask):
    """Mean lag-1 correlation along time, per channel, over line-free channels."""
    Y = Xn[:, mask]
    Y = Y - Y.mean(0)
    num = (Y[:-1] * Y[1:]).mean(0)
    den = Y.var(0)
    return float(np.mean(num / den))


# ------------------------------------------------------------ main
def main(root, outdir):
    root, outdir = pathlib.Path(root), pathlib.Path(outdir)
    figdir = outdir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)
    raw = {k: load_rows(root, f) for k, (f, _) in CAPTURES.items()}
    tau_row = {k: M * FRAME_S for k, (_, M) in CAPTURES.items()}
    report = []

    # ---- diagnostics printed for the methods record -------------------
    report.append(f"frame period {FRAME_S*1e3:.3f} ms, channel spacing {DF_KHZ:.3f} kHz")
    for k, X in raw.items():
        report.append(f"{k}: {X.shape[0]} rows, M={CAPTURES[k][1]}, "
                      f"tau_row={tau_row[k]:.3f} s, span={X.shape[0]*tau_row[k]:.1f} s")

    mask = common_line_free(raw)
    report.append(f"common line-free channels: {int(mask.sum())} of {FFT_SIZE}; "
                  f"|f|<={FIT_KHZ:.0f} kHz, |f|>{ART_KHZ:.0f} kHz, "
                  f"excluding {LINE_LO:.0f}..{LINE_HI:.0f} kHz and all flagged spurs")

    # order sensitivity of the panel (a) amplitude scale
    order_sens = {}
    for k in ("W", "S", "E1"):
        m = raw[k][N_SKIP:].mean(0)
        line = (FAX > LINE_LO) & (FAX < LINE_HI)
        order_sens[k] = [float(fractional_excess(m, order=o)[0][line].max())
                         for o in (3, 5, 7, 9)]
        report.append(f"{k} line peak vs continuum order 3/5/7/9: "
                      + "/".join(f"{v:.1f}" for v in order_sens[k]) + " %")

    # startup sensitivity of the panel (b) point at one row per block
    for k in ("E1", "E2"):
        vals = []
        for skip in (2, 6, 15, 30):
            Xn = normalize_rows(raw[k][skip:], mask)
            vals.append(block_pair_noise(Xn, mask, 1)["sigma_frac"] * 100)
        report.append(f"{k} single-row noise vs rows skipped 2/6/15/30: "
                      + "/".join(f"{v:.3f}" for v in vals) + " %")

    # ---- panel (b) curves --------------------------------------------
    plans = {"E1": [1, 2, 4, 8, 16], "E2": [1, 2, 5, 10, 20]}
    recs = []
    for k, sizes in plans.items():
        Xn = normalize_rows(raw[k][N_SKIP:], mask)
        lag1 = temporal_lag1(Xn, mask)
        report.append(f"{k} lag-1 correlation along time (normalized rows): {lag1:+.3f}")
        for n in sizes:
            r = block_pair_noise(Xn, mask, n)
            if r is None:
                continue
            r.update(capture=k, M_frames=CAPTURES[k][1], rows_per_block=n,
                     tau_s=n * tau_row[k], rows_used=Xn.shape[0],
                     rows_skipped=N_SKIP, temporal_lag1=lag1,
                     included=r["n_pairs"] >= MIN_PAIRS)
            recs.append(r)
    tab = pd.DataFrame(recs)[
        ["capture", "M_frames", "rows_per_block", "tau_s", "sigma_frac",
         "spread_frac", "sem_frac", "n_pairs", "n_blocks", "rows_used", "rows_skipped",
         "n_channels", "temporal_lag1", "included"]]
    tab["sigma_pct"] = tab.sigma_frac * 100
    tab.to_csv(outdir / "averaging_noise.csv", index=False)
    shown = tab[tab.included]

    # tau^-1/2 reference, normalized to the included points (not a prediction)
    lg = np.log10(shown.tau_s.values)
    amp = 10 ** np.mean(np.log10(shown.sigma_pct.values) + 0.5 * lg)
    report.append(f"tau^-1/2 reference normalized to included points: "
                  f"{amp:.4f} %% at tau = 1 s")
    for k in plans:
        u = shown[shown.capture == k]
        p = np.polyfit(np.log10(u.tau_s), np.log10(u.sigma_pct), 1)
        res = np.std(np.log10(u.sigma_pct) - np.polyval(p, np.log10(u.tau_s)))
        report.append(f"{k} within-record slope {p[0]:+.4f} "
                      f"(resid {res:.4f} dex, {len(u)} points). NOTE: for rows "
                      f"that are independent in time, sigma(n) = sigma(1)/sqrt(n) "
                      f"holds identically, so this slope is largely a consequence "
                      f"of the measured lag-1 near zero and is not independent "
                      f"evidence of radiometric behavior.")
    for t in sorted(set(np.round(shown.tau_s, 3))):
        sub = shown[np.round(shown.tau_s, 3) == t]
        if len(sub) > 1:
            report.append("matched nominal tau=%.1f s: " % t + ", ".join(
                f"M={int(r.M_frames)} {r.sigma_pct:.4f}%" for r in sub.itertuples())
                + f"  ratio {sub.sigma_pct.max()/sub.sigma_pct.min():.3f}")

    # ---- figure -------------------------------------------------------
    mpl.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8.5,
        "axes.labelsize": 9, "axes.titlesize": 9.5, "legend.fontsize": 8,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.7, "lines.linewidth": 1.0,
        "xtick.major.width": 0.7, "ytick.major.width": 0.7,
        "figure.dpi": 150, "savefig.dpi": 400, "pdf.fonttype": 42,
    })
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(7.16, 2.85),
                                   gridspec_kw=dict(wspace=0.30))

    # (a) first-light spectra
    peak_art = {}
    for k in ("S", "E1", "W"):
        m = raw[k][N_SKIP:].mean(0)
        ex, _ = fractional_excess(m)
        peak_art[k] = ex[np.abs(FAX) <= 2].max()
        axA.plot(FAX, ex, color=COLOR[k], label=LABEL[k],
                 lw=0.9, zorder=3 if k == "S" else 2)
    axA.axhline(0, color="0.75", lw=0.6, zorder=1)
    axA.set_xlim(-260, 500)
    axA.set_ylim(-4, 27)
    axA.set_xlabel("Offset from nominal LO (kHz)")
    axA.set_ylabel("Fractional excess (%)")
    axA.annotate(f"band-center\ninstrumental artifact\n(off scale, {peak_art['S']:.0f}%)",
                 xy=(-6, 24.5), xytext=(-250, 21.0), fontsize=7, color="0.35",
                 ha="left", va="top",
                 arrowprops=dict(arrowstyle="-", color="0.55", lw=0.6,
                                 shrinkA=2, shrinkB=2))
    axA.annotate("narrowband spurs", xy=(404, 12.4), xytext=(470, 7.5),
                 fontsize=7, color="0.35", ha="right", va="bottom",
                 arrowprops=dict(arrowstyle="-", color="0.55", lw=0.6,
                                 shrinkA=0, shrinkB=3))
    axA.legend(frameon=False, loc="upper right", handlelength=1.3,
               borderaxespad=0.1, labelspacing=0.3,
               bbox_to_anchor=(1.02, 1.03))

    # (b) noise versus integration time
    tt = np.array([shown.tau_s.min() * 0.8, shown.tau_s.max() * 1.25])
    axB.plot(tt, amp * tt ** -0.5, color="0.6", lw=0.9, ls=(0, (4, 2)),
             zorder=1, label=r"$\tau^{-1/2}$, normalized to $M$ = 1000 at 1 s")
    style = {"E1": dict(fmt="o", ms=7.0, mfc="none", mew=1.2, zorder=3),
             "E2": dict(fmt="s", ms=3.6, mew=0.5, zorder=4)}
    for k in ("E1", "E2"):
        s = shown[shown.capture == k]
        st = dict(style[k])
        st.setdefault("mfc", COLOR[k])
        axB.errorbar(s.tau_s, s.sigma_pct, yerr=s.sem_frac * 100,
                     color=COLOR[k], mec=COLOR[k], elinewidth=0.8, capsize=2,
                     label=f"East, $M$ = {CAPTURES[k][1]}", **st)
    axB.set_xscale("log"); axB.set_yscale("log")
    axB.set_xlabel(r"Nominal integration time per block, $\tau$ (s)")
    axB.set_ylabel("Fractional fluctuation (%)")
    axB.legend(frameon=False, loc="lower left", handlelength=1.6,
               borderaxespad=0.2, labelspacing=0.35)
    for ax, lab in ((axA, "a"), (axB, "b")):
        ax.text(-0.155, 1.06, lab, transform=ax.transAxes,
                fontsize=11, fontweight="bold", va="bottom")

    fig.savefig(figdir / "first_light_and_averaging.pdf", bbox_inches="tight")
    fig.savefig(figdir / "first_light_and_averaging.png", bbox_inches="tight")
    print("\n".join(report))
    return fig, tab


if __name__ == "__main__":
    _default_root = pathlib.Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(_default_root),
                    help="mergen-21 repository root (default: resolved from this file's location)")
    ap.add_argument("--outdir", default=None,
                    help="output directory for CSV and figures/ "
                         "(default: <root>/software/analysis/outputs)")
    args = ap.parse_args()
    outdir = args.outdir or (pathlib.Path(args.root) / "software" / "analysis" / "outputs")
    main(args.root, outdir)
