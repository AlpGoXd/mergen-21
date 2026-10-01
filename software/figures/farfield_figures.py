
"""Mergen-21 far-field polar cuts from CST 'XY Data Exchange Format V2' exports.

Column layout of each export (361 rows, verified on read):
  col0 = polar plot angle 0..359 (+ a closing 0), monotonic
  col1 = theta; equals col0 for col0<=180 (the phi cut) and 360-col0 beyond it
         (the phi+180 half of the great circle)
  col2 = directivity in dBi, decimal comma
col0 is therefore used directly as the polar angle, which avoids the
non-monotonic-theta trap of interpolating on col1.

The 8-column CST far-field ASCII export committed in hardware/simulation/cst/
(header `Theta [deg.]  Phi [deg.]  Abs(Dir.) ...`) is also accepted: rows at
the first phi map to +theta and rows at phi+180 to -theta (plot angle
360-theta), sorted and closed with a copy of the first point, so both formats
return the same (meta, angle, Abs(Dir)) layout.
"""
import numpy as np
import matplotlib.pyplot as plt

def _read_cst_ascii(path):
    rows = []
    for line in open(path, errors="replace").read().splitlines()[2:]:
        p = line.split()
        if len(p) == 8:
            rows.append((float(p[0]), float(p[1]), float(p[2])))
    a = np.asarray(rows)
    th, ph, D = a[:, 0], a[:, 1], a[:, 2]
    phi0 = ph[0]
    back = np.isclose((ph - phi0) % 360, 180)
    assert np.all(np.isclose(ph[~back], phi0)), "more than two phi values in cut"
    ang = np.where(back, 360 - th, th) % 360
    o = np.argsort(ang); ang, D = ang[o], D[o]
    assert np.all(np.diff(ang) > 0), "duplicate plot angles"
    ang = np.append(ang, ang[0]); D = np.append(D, D[0])
    meta = {"Format": "CST ASCII far-field cut", "Phi": f"{phi0:g}", "Npoints": str(len(ang))}
    return meta, ang, D

def read_cst_polar(path):
    with open(path, errors="replace") as fh:
        if fh.readline().lstrip().startswith("Theta"):
            return _read_cst_ascii(path)
    meta, rows = {}, []
    for line in open(path, errors="replace").read().splitlines():
        s = line.strip()
        if not s:
            continue
        if "=" in s:
            k, v = s.split("=", 1); meta[k.strip()] = v.strip(); continue
        p = s.replace(",", ".").split("\t")
        if len(p) == 3:
            try:
                rows.append(tuple(float(x) for x in p))
            except ValueError:
                pass
    a = np.asarray(rows)
    ang, th, D = a[:, 0], a[:, 1], a[:, 2]
    assert len(a) == int(meta["Npoints"]), "row count != Npoints"
    assert np.all(np.diff(ang[:-1]) > 0), "plot-angle column not monotonic"
    assert np.allclose(th[ang <= 180], ang[ang <= 180]) and \
           np.allclose(th[ang > 180], 360 - ang[ang > 180]), "unexpected theta layout"
    return meta, ang, D

def pattern_metrics(ang, D):
    """Peak, -3 dB beamwidth (linear interp), main-lobe edges, minor lobes (dB rel. peak)."""
    a, d = ang[:-1], D[:-1]
    x = np.where(a > 180, a - 360, a); o = np.argsort(x); x, d = x[o], d[o]
    i0 = int(np.argmax(d)); pk = d[i0]; rel = d - pk
    r = i0
    while rel[r] > -3: r += 1
    l = i0
    while rel[l] > -3: l -= 1
    xr = np.interp(-3, [rel[r], rel[r - 1]], [x[r], x[r - 1]])
    xl = np.interp(-3, [rel[l], rel[l + 1]], [x[l], x[l + 1]])
    rr = i0
    while rr + 1 < len(d) and d[rr + 1] < d[rr]: rr += 1
    ll = i0
    while ll - 1 >= 0 and d[ll - 1] < d[ll]: ll -= 1
    minor = [(x[i], rel[i]) for i in range(1, len(d) - 1)
             if d[i] >= d[i - 1] and d[i] >= d[i + 1] and (i > rr or i < ll)]
    back = rel[np.argmin(np.abs(np.abs(x) - 180))]
    return dict(peak=pk, hpbw=xr - xl, xl=xl, xr=xr, lobe_edge=(x[ll], x[rr]),
                minor=sorted(minor, key=lambda t: -t[1]), back_rel=back)

def fig_polar(path, title, plane_left, plane_right, color="#1f4e79",
              rmin=-40, rmax=20, callout="first_sidelobe"):
    meta, ang, D = read_cst_polar(path)
    m = pattern_metrics(ang, D)
    fs_small = plt.rcParams["legend.fontsize"]
    fig = plt.figure(figsize=(3.5, 3.75 if title else 3.55))
    ax = fig.add_subplot(projection="polar")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    th = np.deg2rad(ang)
    ax.plot(th, np.clip(D, rmin, None), color=color, lw=1.3, zorder=2.2)
    ax.set_rlim(rmin, rmax)
    ax.set_rticks(np.arange(rmin + 10, rmax + 1, 10))
    rt = list(range(rmin + 10, rmax, 10))
    ax.set_rticks(rt)
    ax.set_yticklabels([(f"{v:d}".replace("-", "\u2212") + (" dBi" if v == rt[-1] else "")) for v in rt],
                       fontsize=plt.rcParams["ytick.labelsize"])
    ax.set_rlabel_position(202.5)
    ax.yaxis.set_zorder(2.6)
    for t in ax.get_yticklabels():
        t.set_bbox(dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    ticks = np.arange(0, 360, 30)
    ax.set_xticks(np.deg2rad(ticks))
    ax.set_xticklabels([f"{t if t <= 180 else 360 - t:d}\u00b0" for t in ticks])
    ax.tick_params(axis="x", pad=1)
    ax.grid(True, lw=0.4, alpha=0.45)
    ax.spines["polar"].set_linewidth(0.8)
    # -3 dB circle and crossings
    tt = np.linspace(0, 2 * np.pi, 400)
    ax.plot(tt, np.full_like(tt, m["peak"] - 3), color="0.45", lw=0.7, ls=(0, (3, 2)), zorder=2)
    for xa in (m["xl"], m["xr"]):
        ax.plot(np.deg2rad(xa), m["peak"] - 3, "o", ms=3.2, mfc="white", mec=color, mew=1.0, zorder=4)
    # cut identity at the two ends of the great circle
    fig.text(0.98, 0.03, f"Right half: {plane_right}\nLeft half: {plane_left}",
             ha="right", va="bottom", fontsize=fs_small, color="0.3", linespacing=1.25)
    # headline numbers
    txt = f"Peak directivity {m['peak']:.1f} dBi\nHPBW {m['hpbw']:.1f}\u00b0"
    if callout == "first_sidelobe":
        xs, rs = max([t for t in m["minor"] if t[0] > 0], key=lambda t: t[1])
        ax.annotate(f"\u2212{abs(rs):.1f} dB", xy=(np.deg2rad(xs), m["peak"] + rs),
                    xytext=(0.97, 0.87), textcoords="figure fraction",
                    fontsize=fs_small, color=color, ha="right", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color=color, shrinkA=1, shrinkB=2))
        txt += f"\nFirst sidelobe \u2212{abs(rs):.1f} dB"
    elif callout == "back_lobe":
        ax.annotate(f"back lobe \u2212{abs(m['back_rel']):.1f} dB",
                    xy=(np.pi, m["peak"] + m["back_rel"]),
                    xytext=(0.97, 0.215), textcoords="figure fraction",
                    fontsize=fs_small, color=color, ha="right", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color=color, shrinkA=1, shrinkB=2))
        near = [v for x_, v in m["minor"] if abs(x_) < 150]
        txt += f"\nOther minor lobes \u2264 \u2212{abs(max(near)):.1f} dB" if near else ""
    fig.text(0.02, 0.03, txt, ha="left", va="bottom", fontsize=fs_small, color=color,
             linespacing=1.25)
    if title:
        fig.text(0.02, 0.975, title, ha="left", va="top", fontsize=plt.rcParams["axes.titlesize"])
    fig.subplots_adjust(left=0.1, right=0.9, top=0.84 if title else 0.90, bottom=0.14)
    return fig, m
