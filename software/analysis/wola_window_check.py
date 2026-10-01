"""Does the committed flowgraph truncate its WOLA prototype filter?

The spectrometer in `software/gnuradio/reciver.grc` builds its analysis window with

    kaiser_window = firdes.low_pass(1.0, samp_rate, samp_rate/(4*fft_size),
                                    samp_rate/(4*fft_size), WIN_KAISER, beta)
    # = firdes.low_pass(1.0, 2048000, 250.0, 250.0, WIN_KAISER, 8.6)

and then hands eight `fft_size`-long slices of it to eight delayed branches,
consuming `kaiser_window[0 : 8*fft_size]`. Whether that truncates the filter
depends on how many taps `firdes` chose, which it picks from the attenuation
and transition width rather than being told.

GNU Radio returns 32299 taps for this call. The taps are stored next to this
script (`wola_taps_firdes.npy`) so the check reproduces without a GNU Radio
installation; regenerate them with `--regenerate` if you have one.

The discriminating measurement is `N_eff`, the effective number of
independent frames in one averaged row. Frames hop by `fft_size` but span
`8*fft_size`, so consecutive frames share seven eighths of their samples;
the resulting correlation is a function of the window shape, which is what
makes `N_eff` sensitive to truncation. Run:

    python wola_window_check.py

Reference values measured from `Dogu_100`: N_eff 81.5, B_eff 753 Hz,
lag-1 channel correlation +0.051.
"""
import argparse
import pathlib

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

SAMP_RATE = 2048000
FFT_SIZE = 2048
K_BRANCHES = 8
BETA = 8.6
CUTOFF_HZ = SAMP_RATE / (4 * FFT_SIZE)
N_CONSUMED = K_BRANCHES * FFT_SIZE
TAPS_FILE = pathlib.Path(__file__).with_name("wola_taps_firdes.npy")

MEASURED = {"N_eff": 81.5, "B_eff_hz": 753.0, "lag1": 0.051}


def firdes_taps(regenerate=False):
    """The prototype as GNU Radio designs it, from cache or from firdes."""
    if not regenerate and TAPS_FILE.exists():
        return np.load(TAPS_FILE)
    from gnuradio.fft import window
    from gnuradio.filter import firdes
    taps = np.array(firdes.low_pass(1.0, SAMP_RATE, CUTOFF_HZ, CUTOFF_HZ,
                                    window.WIN_KAISER, BETA))
    np.save(TAPS_FILE, taps)
    return taps


def complete_taper(n=N_CONSUMED, fc=CUTOFF_HZ, beta=BETA):
    """A correctly sized prototype: windowed sinc, exactly n taps."""
    m = np.arange(n) - (n - 1) / 2
    return 2 * fc / SAMP_RATE * np.sinc(2 * fc / SAMP_RATE * m) * np.kaiser(n, beta)


def wola_rows(x, w, n_frames):
    """Fold and transform exactly as the flowgraph does.

    Branch `delay = k*fft_size` is paired with slice
    `kaiser_window[(7-k)*fft_size : (8-k)*fft_size]`, which makes the
    effective window one contiguous `8*fft_size` span. Frames advance by
    `fft_size`.
    """
    w = w.reshape(K_BRANCHES, FFT_SIZE)
    blocks = sliding_window_view(x, K_BRANCHES * FFT_SIZE)[::FFT_SIZE][:n_frames]
    folded = (blocks.reshape(n_frames, K_BRANCHES, FFT_SIZE) * w).sum(axis=1)
    return np.abs(np.fft.fftshift(np.fft.fft(folded, axis=1), axes=1)) ** 2


def window_statistics(w, n_int=100, reps=600, seed=11,
                      channels=(700, 900, 1100, 1300)):
    """N_eff, B_eff and adjacent-channel correlation for white input."""
    rng = np.random.default_rng(seed)
    power, neigh = [], []
    for _ in range(reps):
        n = (n_int + K_BRANCHES - 1) * FFT_SIZE
        x = (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / np.sqrt(2)
        row = wola_rows(x, w, n_int).mean(axis=0)
        power.append(row[list(channels)])
        neigh.append(row[896:905])
    power, neigh = np.array(power), np.array(neigh)
    frac_rms = float(np.mean(power.std(0, ddof=1) / power.mean(0)))
    inflation = (frac_rms * np.sqrt(n_int)) ** 2
    centred = neigh - neigh.mean(0)
    sd = centred.std(0, ddof=1)
    lag1 = float(np.mean(centred[:, 4] * centred[:, 5]) / (sd[4] * sd[5]))
    return {"N_eff": n_int / inflation,
            "B_eff_hz": (SAMP_RATE / FFT_SIZE) / inflation,
            "lag1": lag1}


def tone_response(w, channel=900, n_either_side=4):
    """Channel response to a tone centred on one channel, in dB."""
    w2 = w.reshape(K_BRANCHES, FFT_SIZE)
    t = np.arange(K_BRANCHES * FFT_SIZE)
    tone = np.exp(2j * np.pi * (channel - FFT_SIZE // 2) * t / FFT_SIZE)
    v = np.abs(np.fft.fftshift(np.fft.fft((tone.reshape(K_BRANCHES, FFT_SIZE) * w2).sum(0)))) ** 2
    v /= v.max()
    pk = int(v.argmax())
    sl = slice(pk - n_either_side, pk + n_either_side + 1)
    return np.arange(-n_either_side, n_either_side + 1), 10 * np.log10(v[sl] + 1e-30)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--regenerate", action="store_true",
                    help="re-run firdes.low_pass (needs GNU Radio)")
    args = ap.parse_args()

    taps = firdes_taps(regenerate=args.regenerate)
    peak = int(np.argmax(taps))
    print("prototype designed        : %d taps" % len(taps))
    print("consumed by the branches  : %d taps" % N_CONSUMED)
    print("prototype peak at tap     : %d" % peak)
    print("cut is past the peak by   : %d taps, at %.1f%% of peak height"
          % (N_CONSUMED - peak, 100 * abs(taps[N_CONSUMED - 1]) / np.abs(taps).max()))
    print("never referenced          : %d taps (%.0f%% of the design)\n"
          % (len(taps) - N_CONSUMED, 100 * (len(taps) - N_CONSUMED) / len(taps)))

    candidates = {"as built (first %d of %d)" % (N_CONSUMED, len(taps)): taps[:N_CONSUMED],
                  "complete taper (%d taps)" % N_CONSUMED: complete_taper()}
    print("%-34s %8s %10s %9s" % ("", "N_eff", "B_eff/Hz", "lag-1"))
    print("%-34s %8.1f %10.1f %9.3f"
          % ("measured (Dogu_100)", MEASURED["N_eff"], MEASURED["B_eff_hz"], MEASURED["lag1"]))
    for name, w in candidates.items():
        s = window_statistics(w)
        print("%-34s %8.1f %10.1f %9.3f" % (name, s["N_eff"], s["B_eff_hz"], s["lag1"]))

    print("\nadjacent-channel leakage")
    for name, w in candidates.items():
        off, prof = tone_response(w)
        print("  %-32s %+.1f dB at offset 1" % (name, prof[len(prof) // 2 + 1]))


if __name__ == "__main__":
    main()
