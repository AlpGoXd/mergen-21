#!/usr/bin/env python3
"""
Mergen-21: RF-chain stage gains at the H I rest frequency.

Reads the measured (ZNB8 VNA) and Mini-Circuits datasheet Touchstone files,
interpolates |S21| in dB at 1420.405 MHz, and writes
<outdir>/stage_gains.csv with columns
    stage, measured_db, datasheet_db, nearest_sample_mhz
(nearest_sample_mhz is the measured file's sample closest to 1420.405 MHz).

Run from anywhere:
    python3 software/analysis/stage_gains.py
    python3 stage_gains.py --root /path/to/mergen-21 --outdir .
"""

import argparse
import csv
from pathlib import Path

import numpy as np

F0_MHZ = 1420.405

VNA = "measurements/rf-chain/vna"
DS = "hardware/rf-chain/datasheet-s-parameters"
STAGES = [
    ("LNA", f"{VNA}/ZX60-P162LN+/mesured_ZX60-P162LN+.s2p",
            f"{DS}/ZX60-P162LN+/ZX60-P162LN+_4V_Plus25degC.s2p"),
    ("BPF", f"{VNA}/ZX75BP-1450-S+/mesured_ZX75BP-1450+filter.s2p",
            f"{DS}/ZX75BP-1450-S+/ZX75BP-1450-S+_Plus25degC.s2p"),
    ("AMP", f"{VNA}/ZX60-V63+/mesured_ZX60-V63+.s2p",
            f"{DS}/ZX60-V63+/ZX60-V63+_5V_Plus25DegC.s2p"),
    ("CASCADE", f"{VNA}/cascade/cascaded chain.s2p", None),
]

UNITS = {"HZ": 1.0, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9}


def read_s21_db(path):
    """Return (freq_MHz, |S21| dB) from a 2-port Touchstone v1 file.

    Handles RI / MA / DB data in Hz, kHz, MHz or GHz. Stops at the noise
    block (first row whose frequency does not increase).
    """
    unit, fmt = 1e9, "MA"          # Touchstone defaults
    nums, freqs, s21 = [], [], []
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            tok = line[1:].upper().split()
            for t in tok:
                if t in UNITS:
                    unit = UNITS[t]
                elif t in ("RI", "MA", "DB"):
                    fmt = t
            continue
        nums += [float(x) for x in line.split()]
        while len(nums) >= 9:
            row, nums = nums[:9], nums[9:]
            f = row[0] * unit / 1e6
            if freqs and f <= freqs[-1]:
                return np.array(freqs), np.array(s21)
            a, b = row[3], row[4]   # S21 is the second pair in v1 order
            if fmt == "RI":
                db = 20 * np.log10(np.hypot(a, b))
            elif fmt == "MA":
                db = 20 * np.log10(a)
            else:
                db = a
            freqs.append(f)
            s21.append(db)
    return np.array(freqs), np.array(s21)


def gain_at(path, f0=F0_MHZ):
    f, g = read_s21_db(path)
    i = int(np.argmin(np.abs(f - f0)))
    return float(np.interp(f0, f, g)), float(f[i])


def main(root, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for stage, meas, ds in STAGES:
        m, nearest = gain_at(root / meas)
        d = gain_at(root / ds)[0] if ds else None
        rows.append({
            "stage": stage,
            "measured_db": f"{m:.2f}",
            "datasheet_db": "" if d is None else f"{d:.2f}",
            "nearest_sample_mhz": f"{nearest:.2f}",
        })
    out = outdir / "stage_gains.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print("{stage:8s} measured {measured_db:>7s} dB  datasheet {datasheet_db:>7s} dB"
              "  (nearest sample {nearest_sample_mhz} MHz)".format(**r))
    s = sum(float(r["measured_db"]) for r in rows if r["stage"] != "CASCADE")
    print(f"sum of measured stages: {s:.2f} dB")
    print(f"wrote {out}")


if __name__ == "__main__":
    _default_root = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(_default_root),
                    help="repository root (default: inferred from this file)")
    ap.add_argument("--outdir", default=None,
                    help="output folder (default: <root>/software/analysis/outputs)")
    a = ap.parse_args()
    root = Path(a.root)
    outdir = Path(a.outdir) if a.outdir else root / "software/analysis/outputs"
    main(root, outdir)
