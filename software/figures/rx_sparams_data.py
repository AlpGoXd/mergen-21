"""Write the data table for the receiver S-parameter figure (paper Fig. 5).

Reads the calibrated ZNB8 sweep of the assembled receiver chain
(measurements/rf-chain/vna/cascade/cascaded chain.s2p, RI format) and writes
software/figures/tikz/data/rx_sparams.dat with columns
    f      frequency (GHz)
    s21    |S21| (dB) = 10 log10(Re^2 + Im^2)
    s11    |S11| (dB)
for the sweep points between 0.5 and 2.5 GHz (42.5 MHz grid, 47 points).
It also prints |S21| and |S11| at 1420.405 MHz, linearly interpolated in dB
between the two neighbouring sweep points (the circled values in the figure).

Usage (from the repo root):  python software/figures/rx_sparams_data.py
"""
import pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "measurements/rf-chain/vna/cascade/cascaded chain.s2p"
OUT = ROOT / "software/figures/tikz/data/rx_sparams.dat"
F0_HZ = 1420.405e6
FMIN_HZ, FMAX_HZ = 0.5e9, 2.5e9
UNIT = {"HZ": 1.0, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9}


def read_s2p(path):
    unit, fmt, rows = 1.0, "MA", []
    for line in open(path, encoding="latin-1"):
        s = line.split("!")[0].strip()
        if not s:
            continue
        if s.startswith("#"):
            t = s.upper().split()
            unit, fmt = UNIT[t[1]], t[3]
            continue
        v = [float(x) for x in s.split()]
        if len(v) != 9:          # stop at a noise-parameter block, if any
            break
        rows.append(v)
    a = np.array(rows)
    f = a[:, 0] * unit

    def mag_db(i):
        if fmt == "DB":
            return a[:, i]
        if fmt == "MA":
            return 20 * np.log10(a[:, i])
        return 10 * np.log10(a[:, i] ** 2 + a[:, i + 1] ** 2)      # RI

    return f, mag_db(1), mag_db(3)


def main():
    f, s11, s21 = read_s2p(SRC)
    k = (f >= FMIN_HZ) & (f <= FMAX_HZ)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="\n") as fh:
        fh.write("f s21 s11\n")
        for fi, a, b in zip(f[k] / 1e9, s21[k], s11[k]):
            fh.write(f"{fi:.6f} {a:.3f} {b:.3f}\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({int(k.sum())} points)")
    print(f"|S21| at 1420.405 MHz: {np.interp(F0_HZ, f, s21):.2f} dB (interpolated in dB)")
    print(f"|S11| at 1420.405 MHz: {np.interp(F0_HZ, f, s11):.2f} dB (interpolated in dB)")


if __name__ == "__main__":
    main()
