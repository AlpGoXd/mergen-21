
"""Mergen-21 S11 figures from Touchstone files.

fig_s11_ideal      : |S11| of the ideal (simulated) horn, 1-2 GHz
fig_s11_assembly   : CST worst-case assembly vs ZNB8 measurement, markers at 1.4200 GHz
"""
import numpy as np
import matplotlib.pyplot as plt

F_MARK = 1.4200e9          # marker frequency requested (1.42 GHz)
F_HI   = 1420.405e6        # H I rest frequency, for the caption only

def read_touchstone(path):
    """Return (f_Hz, |S11|_dB). Handles MA / RI / DB and any frequency unit."""
    f_unit = fmt = None
    freq, val = [], []
    with open(path, errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("!"):
                continue
            if s.startswith("#"):
                tok = s[1:].split()
                f_unit, fmt = tok[0].upper(), tok[2].upper()
                continue
            p = s.split()
            freq.append(float(p[0])); val.append((float(p[1]), float(p[2])))
    mult = {"HZ": 1.0, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9}[f_unit]
    f = np.asarray(freq) * mult
    v = np.asarray(val)
    mag = {"MA": lambda v: v[:, 0],
           "RI": lambda v: np.hypot(v[:, 0], v[:, 1]),
           "DB": lambda v: 10 ** (v[:, 0] / 20)}[fmt](v)
    return f, 20 * np.log10(mag)

def at(f, d, f0):
    """Value at the sample nearest f0, plus that sample's frequency."""
    i = int(np.argmin(np.abs(f - f0)))
    return f[i], d[i]

def _decorate(ax, fmin, fmax, ymin, ymax):
    ax.set_xlim(fmin / 1e9, fmax / 1e9)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel(r"$|S_{11}|$ (dB)")
    ax.grid(True, which="major", lw=0.4, alpha=0.35)
    ax.tick_params(direction="in", top=True, right=True)

# ---------------------------------------------------------------- figure 1
def fig_s11_ideal(path, color="#1f4e79"):
    f, d = read_touchstone(path)
    fm, dm = at(f, d, F_MARK)
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    ax.plot(f / 1e9, d, color=color, lw=1.3)
    ax.axvline(fm / 1e9, color="0.35", lw=0.9, ls=(0, (4, 2.5)), zorder=1)
    ax.plot(fm / 1e9, dm, "o", ms=4.2, mfc="white", mec=color, mew=1.2, zorder=4)
    ax.annotate(f"\u2212{abs(dm):.1f} dB",
                xy=(fm / 1e9, dm), xytext=(40, -34), textcoords="offset points",
                fontsize=plt.rcParams["legend.fontsize"], color=color,
                arrowprops=dict(arrowstyle="-", lw=0.6, color=color,
                                shrinkA=0, shrinkB=3))
    _decorate(ax, f.min(), f.max(), np.floor(d.min() / 5) * 5 - 2, 0.5)
    fig.tight_layout()
    return fig, (fm, dm)

# ---------------------------------------------------------------- figure 2
def fig_s11_assembly(path_sim, path_meas,
                     c_sim="#b0552a", c_meas="#1f4e79",
                     fmin=1.0e9, fmax=2.0e9, figsize=(6.0, 2.6)):
    fs, ds = read_touchstone(path_sim)
    fmz, dmz = read_touchstone(path_meas)
    ks = (fs >= fmin) & (fs <= fmax)
    km = (fmz >= fmin) & (fmz <= fmax)
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(fs[ks] / 1e9, ds[ks], color=c_sim, lw=1.3, label="CST, worst case")
    ax.plot(fmz[km] / 1e9, dmz[km], color=c_meas, lw=1.3,
            marker="o", ms=2.0, mew=0, label="Measured (ZNB8)")
    ax.axvline(F_MARK / 1e9, color="0.35", lw=0.9, ls=(0, (4, 2.5)), zorder=1)
    out = {}
    for (f, d, c, dx, dy) in ((fs, ds, c_sim, 70, -16), (fmz, dmz, c_meas, 60, -4)):
        f0, d0 = at(f, d, F_MARK)
        out[c] = (f0, d0)
        ax.plot(f0 / 1e9, d0, "o", ms=4.2, mfc="white", mec=c, mew=1.2, zorder=4)
        ax.annotate(f"\u2212{abs(d0):.1f} dB", xy=(f0 / 1e9, d0),
                    xytext=(dx, dy), textcoords="offset points",
                    fontsize=plt.rcParams["legend.fontsize"], color=c,
                    arrowprops=dict(arrowstyle="-", lw=0.6, color=c,
                                    shrinkA=0, shrinkB=3))
    lo = min(ds[ks].min(), dmz[km].min())
    _decorate(ax, fmin, fmax, np.floor(lo / 5) * 5 - 2, 0.5)
    ax.legend(loc="lower right", frameon=False, handlelength=1.6,
              borderaxespad=0.3, labelspacing=0.3)
    fig.tight_layout()
    return fig, out
