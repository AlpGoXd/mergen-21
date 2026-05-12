"""
Mergen-21 Waterfall Viewer  (v3 — auto-detect + memmap + decimation + threading)
================================================================================
 
GUI for viewing the timestamped .dat files produced by the Mergen-21
GNU Radio receiver flowgraph.
  
Requirements: Python 3.8+, numpy, matplotlib  (tkinter ships with CPython).
Run:          python mergen21_waterfall_viewer.py
"""
 
from __future__ import annotations
 
from pathlib import Path
import json
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
 
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk,
)
 
 
# --- defaults: match the flowgraph -------------------------------------------
DEFAULT_FFT_SIZE   = 2048
DEFAULT_SAMP_RATE  = 2_048_000
DEFAULT_LO_FREQ    = 1_420_405_000
DEFAULT_INTEG_TIME = 50
 
C_KMS      = 299_792.458
HI_REST_HZ = 1_420_405_751.768
 
# Cap on plotted waterfall rows. With fft_size=2048 this is ~20 MB float32.
MAX_WATERFALL_ROWS = 2500
 
 
# =============================================================================
# Parameter auto-detection
# =============================================================================
 
_HZ_UNITS  = {"hz": 1.0, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
_SPS_UNITS = {"sps": 1.0, "ksps": 1e3, "msps": 1e6}
 
 
def parse_filename_params(name: str) -> dict:
    """
    Pull parameters out of a filename based on suffix conventions.
 
    Recognised tokens (case-insensitive, anywhere in the name):
        <num><Hz|kHz|MHz|GHz>     -> lo_freq
        <num><sps|ksps|Msps>      -> samp_rate
        <int>fft                  -> fft_size
        <int>int                  -> integ_time
 
    Numbers may be decimal for frequency / rate; integers for fft and integ.
    The negative-lookahead `(?![A-Za-z])` keeps us from matching inside
    longer words (e.g. "interpolation").
    """
    out: dict = {}
 
    m = re.search(r"(\d+(?:\.\d+)?)\s*(GHz|MHz|kHz|Hz)(?![A-Za-z])",
                  name, re.IGNORECASE)
    if m:
        out["lo_freq"] = int(round(float(m.group(1)) * _HZ_UNITS[m.group(2).lower()]))
 
    m = re.search(r"(\d+(?:\.\d+)?)\s*(Msps|ksps|sps)(?![A-Za-z])",
                  name, re.IGNORECASE)
    if m:
        out["samp_rate"] = int(round(float(m.group(1)) * _SPS_UNITS[m.group(2).lower()]))
 
    m = re.search(r"(\d+)\s*fft(?![A-Za-z])", name, re.IGNORECASE)
    if m:
        out["fft_size"] = int(m.group(1))
 
    m = re.search(r"(\d+)\s*int(?![A-Za-z])", name, re.IGNORECASE)
    if m:
        out["integ_time"] = int(m.group(1))
 
    return out
 
 
def parse_sidecar(dat_path: Path) -> tuple[dict, Path | None]:
    """
    Look for <basename>.json or <basename>.txt next to the .dat file.
 
    JSON form:
        {"fft_size": 2048, "samp_rate": 2048000,
         "lo_freq": 1420405000, "integ_time": 50}
 
    TXT form (one key=value per line; '=' or ':' accepted; '#' = comment):
        fft_size = 2048
        samp_rate = 2048000
        lo_freq: 1420405000
        integ_time = 50
    """
    base = dat_path.with_suffix("")
    casters = {
        "fft_size":   lambda v: int(float(v)),
        "samp_rate":  lambda v: int(float(v)),
        "lo_freq":    lambda v: int(float(v)),
        "integ_time": lambda v: int(float(v)),
    }
 
    for ext in (".json", ".txt"):
        side = base.with_suffix(ext)
        if not side.exists():
            continue
        try:
            if ext == ".json":
                with open(side, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                if not isinstance(raw, dict):
                    continue
            else:
                raw = {}
                with open(side, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        sep = "=" if "=" in line else (":" if ":" in line else None)
                        if sep is None:
                            continue
                        k, v = line.split(sep, 1)
                        raw[k.strip()] = v.strip()
        except Exception:
            continue
 
        out: dict = {}
        for key, cast in casters.items():
            if key in raw:
                try:
                    out[key] = cast(raw[key])
                except (ValueError, TypeError):
                    pass
        if out:
            return out, side
 
    return {}, None
 
 
def detect_params(path: Path) -> tuple[dict, str]:
    """
    Try sidecar first (more explicit), then filename. Return
    (params_dict, source_label). Empty dict means nothing detected.
    """
    params, side = parse_sidecar(path)
    if params:
        return params, f"sidecar: {side.name}"
    params = parse_filename_params(path.name)
    if params:
        return params, "filename"
    return {}, "manual"
 
 
# =============================================================================
# Loading + decimation
# =============================================================================
 
def memmap_dat(path: Path, fft_size: int) -> np.ndarray:
    """
    Open a flowgraph .dat file as a read-only (n_rows, fft_size) memmap view.
    The trailing partial-frame is dropped. Returns an empty array if the file
    is shorter than one frame.
    """
    nbytes = path.stat().st_size
    n_floats = nbytes // 4  # float32
    n_rows = n_floats // fft_size
    if n_rows == 0:
        return np.empty((0, fft_size), dtype=np.float32)
    n_aligned = n_rows * fft_size
    mm = np.memmap(path, dtype=np.float32, mode="r", shape=(n_aligned,))
    return mm.reshape(n_rows, fft_size)
 
 
def decimate_stream(views: list[np.ndarray], block: int, fft_size: int) -> np.ndarray:
    """
    Block-average rows across a sequence of (n_i, fft_size) views, treating
    them as one logical concatenated stream. Yields (n_total // block, fft_size)
    float32. Trailing rows that don't fill a complete block are discarded.
 
    This walks the memmaps page by page rather than materialising the full
    concatenation, so peak memory stays at one block of rows.
    """
    if block <= 0:
        raise ValueError("block must be >= 1")
 
    total_rows = sum(v.shape[0] for v in views)
    n_groups = total_rows // block
    if n_groups == 0:
        return np.empty((0, fft_size), dtype=np.float32)
 
    out = np.empty((n_groups, fft_size), dtype=np.float32)
    accum = np.zeros(fft_size, dtype=np.float64)  # float64 accumulator
 
    g = 0
    in_group = 0
    for v in views:
        n = v.shape[0]
        i = 0
        while i < n and g < n_groups:
            take = min(block - in_group, n - i)
            chunk = np.asarray(v[i : i + take], dtype=np.float32)
            accum += chunk.sum(axis=0)
            in_group += take
            i += take
            if in_group == block:
                out[g] = (accum / block).astype(np.float32)
                g += 1
                in_group = 0
                accum.fill(0.0)
    return out
 
 
# =============================================================================
# The viewer
# =============================================================================
 
class MergenViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mergen-21 Waterfall Viewer")
        self.geometry("1300x820")
 
        self.files: list[Path] = []
        self._x = None
        self._t = None
        self._spec_db = None
        self._cbar = None
        self._busy = False
 
        self._build_ui()
 
    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # --- left: controls ---
        left = ttk.Frame(self, padding=8)
        left.pack(side="left", fill="y")
 
        # files
        files_lf = ttk.LabelFrame(left, text="Files (sorted by name)", padding=6)
        files_lf.pack(fill="x", pady=(0, 8))
 
        self.files_listbox = tk.Listbox(files_lf, height=9, selectmode="extended",
                                        exportselection=False)
        self.files_listbox.pack(fill="x")
 
        btns = ttk.Frame(files_lf)
        btns.pack(fill="x", pady=(4, 0))
        ttk.Button(btns, text="Add...",  command=self._add_files).pack(side="left", padx=2)
        ttk.Button(btns, text="Remove",  command=self._remove_files).pack(side="left", padx=2)
        ttk.Button(btns, text="Clear",   command=self._clear_files).pack(side="left", padx=2)
 
        # parameters
        params_lf = ttk.LabelFrame(left, text="Parameters", padding=6)
        params_lf.pack(fill="x", pady=(0, 8))
 
        self.var_fft   = tk.IntVar(value=DEFAULT_FFT_SIZE)
        self.var_samp  = tk.IntVar(value=DEFAULT_SAMP_RATE)
        self.var_lo    = tk.IntVar(value=DEFAULT_LO_FREQ)
        self.var_integ = tk.IntVar(value=DEFAULT_INTEG_TIME)
 
        for label, var in [
            ("FFT size",        self.var_fft),
            ("Sample rate Hz",  self.var_samp),
            ("LO frequency Hz", self.var_lo),
            ("Integration N",   self.var_integ),
        ]:
            row = ttk.Frame(params_lf)
            row.pack(fill="x", pady=1)
            ttk.Label(row, text=label, width=16).pack(side="left")
            ttk.Entry(row, textvariable=var, width=14).pack(side="left")
 
        # auto-detect indicator + manual re-detect button
        ind_row = ttk.Frame(params_lf)
        ind_row.pack(fill="x", pady=(6, 0))
        self.detect_label = tk.Label(
            ind_row, text="Manual input", fg="gray", anchor="w", justify="left",
            wraplength=200,
        )
        self.detect_label.pack(side="left", fill="x", expand=True)
        ttk.Button(ind_row, text="Re-detect", width=10,
                   command=self._auto_detect_params).pack(side="right")
 
        # display options
        disp_lf = ttk.LabelFrame(left, text="Display", padding=6)
        disp_lf.pack(fill="x", pady=(0, 8))
 
        ttk.Label(disp_lf, text="X axis").pack(anchor="w")
        self.var_xaxis = tk.StringVar(value="RF [MHz]")
        ttk.Combobox(
            disp_lf, textvariable=self.var_xaxis, state="readonly",
            values=["RF [MHz]", "Baseband [kHz]", "Velocity [km/s]"],
        ).pack(fill="x", pady=(0, 4))
 
        ttk.Label(disp_lf, text="Colormap").pack(anchor="w")
        self.var_cmap = tk.StringVar(value="viridis")
        ttk.Combobox(
            disp_lf, textvariable=self.var_cmap, state="readonly",
            values=["viridis", "magma", "inferno", "plasma",
                    "turbo", "cividis", "gray"],
        ).pack(fill="x", pady=(0, 4))
 
        # tells the viewer whether the file is already fftshifted.
        # The Mergen-21 flowgraph uses fft_vxx with shift=True, so default ON.
        self.var_preshifted = tk.BooleanVar(value=True)
        ttk.Checkbutton(disp_lf, text="Data already fftshifted (shift=True)",
                        variable=self.var_preshifted).pack(anchor="w")
 
        self.var_notch = tk.BooleanVar(value=True)
        ttk.Checkbutton(disp_lf, text="Notch DC bin (LO leakage)",
                        variable=self.var_notch).pack(anchor="w")
 
        self.var_baseline = tk.BooleanVar(value=False)
        ttk.Checkbutton(disp_lf, text="Divide by median bandpass",
                        variable=self.var_baseline).pack(anchor="w")
 
        self.var_auto = tk.BooleanVar(value=True)
        ttk.Checkbutton(disp_lf, text="Auto color range (5–99 %)",
                        variable=self.var_auto,
                        command=self._toggle_vminmax).pack(anchor="w")
 
        vmrow = ttk.Frame(disp_lf)
        vmrow.pack(fill="x", pady=(4, 0))
        ttk.Label(vmrow, text="vmin").pack(side="left")
        self.var_vmin = tk.DoubleVar(value=-90.0)
        self.entry_vmin = ttk.Entry(vmrow, textvariable=self.var_vmin,
                                    width=8, state="disabled")
        self.entry_vmin.pack(side="left", padx=4)
        ttk.Label(vmrow, text="vmax").pack(side="left")
        self.var_vmax = tk.DoubleVar(value=-50.0)
        self.entry_vmax = ttk.Entry(vmrow, textvariable=self.var_vmax,
                                    width=8, state="disabled")
        self.entry_vmax.pack(side="left", padx=4)
 
        # actions
        self.plot_button = ttk.Button(left, text="Plot", command=self._plot)
        self.plot_button.pack(fill="x", pady=(8, 2))
        ttk.Button(left, text="Save PNG...", command=self._save_png).pack(fill="x", pady=2)
 
        # status bar
        self.status = ttk.Label(left, text="No data loaded.", relief="sunken",
                                anchor="w", padding=4, wraplength=240)
        self.status.pack(fill="x", side="bottom", pady=(8, 0))
 
        # --- right: figure ---
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True)
 
        self.fig = Figure(figsize=(9, 7), dpi=100, constrained_layout=True)
        gs = self.fig.add_gridspec(2, 1, height_ratios=[3, 1])
        self.ax_w = self.fig.add_subplot(gs[0])
        self.ax_s = self.fig.add_subplot(gs[1], sharex=self.ax_w)
        self.ax_w.set_title("Load some .dat files and click Plot")
 
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, right)
        toolbar.update()
 
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.cursor_label = ttk.Label(right, text="", anchor="w", padding=4)
        self.cursor_label.pack(fill="x", side="bottom")
 
    # ----------------------------------------------------------- file mgmt
    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select Mergen-21 .dat files",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")],
        )
        for p in paths:
            self.files.append(Path(p))
        self._refresh_files_list()
        if self.files:
            self._auto_detect_params()
 
    def _remove_files(self):
        for i in reversed(self.files_listbox.curselection()):
            del self.files[i]
        self._refresh_files_list()
        if self.files:
            self._auto_detect_params()
 
    def _clear_files(self):
        self.files = []
        self._refresh_files_list()
        self._set_indicator("Manual input", "gray")
 
    def _refresh_files_list(self):
        self.files = sorted(self.files, key=lambda p: p.name)
        self.files_listbox.delete(0, "end")
        for p in self.files:
            self.files_listbox.insert("end", p.name)
 
    def _toggle_vminmax(self):
        state = "disabled" if self.var_auto.get() else "normal"
        self.entry_vmin.configure(state=state)
        self.entry_vmax.configure(state=state)
 
    # --------------------------------------------------------- auto-detect
    def _set_indicator(self, text: str, color: str):
        self.detect_label.configure(text=text, fg=color)
 
    def _auto_detect_params(self):
        if not self.files:
            self._set_indicator("Manual input", "gray")
            return
        first = self.files[0]
        params, source = detect_params(first)
        if not params:
            self._set_indicator("Manual input — no metadata found", "gray")
            return
 
        if "fft_size"   in params: self.var_fft.set(params["fft_size"])
        if "samp_rate"  in params: self.var_samp.set(params["samp_rate"])
        if "lo_freq"    in params: self.var_lo.set(params["lo_freq"])
        if "integ_time" in params: self.var_integ.set(params["integ_time"])
 
        keys = ", ".join(sorted(params.keys()))
        self._set_indicator(f"Auto-detected from {source}\n[{keys}]", "#1b5e20")
 
    # ---------------------------------------------------------- load + plot
    def _plot(self):
        if self._busy:
            return
        if not self.files:
            messagebox.showinfo("No files", "Add at least one .dat file first.")
            return
 
        # Read all tk vars on the main thread — IntVar/DoubleVar.get() is
        # not thread-safe. Then hand a plain dict to the worker.
        try:
            fft_size  = int(self.var_fft.get())
            samp_rate = float(self.var_samp.get())
            lo_freq   = float(self.var_lo.get())
            integ     = float(self.var_integ.get())
            if fft_size <= 0 or samp_rate <= 0 or integ <= 0:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Bad input",
                                 "FFT size / sample rate / integration must be positive.")
            return
 
        try:
            vmin_manual = float(self.var_vmin.get())
            vmax_manual = float(self.var_vmax.get())
        except (ValueError, tk.TclError):
            vmin_manual, vmax_manual = -90.0, -50.0
 
        params = dict(
            fft_size=fft_size, samp_rate=samp_rate, lo_freq=lo_freq, integ=integ,
            files=list(self.files),
            preshifted=bool(self.var_preshifted.get()),
            notch=bool(self.var_notch.get()),
            baseline=bool(self.var_baseline.get()),
            auto_color=bool(self.var_auto.get()),
            vmin_manual=vmin_manual, vmax_manual=vmax_manual,
            xmode=self.var_xaxis.get(),
            cmap=self.var_cmap.get(),
            max_rows=MAX_WATERFALL_ROWS,
        )
 
        self._busy = True
        self.plot_button.configure(state="disabled")
        self._set_status("Loading data and computing FFT-domain stats…")
        threading.Thread(
            target=self._compute_worker, args=(params,), daemon=True
        ).start()
 
    def _compute_worker(self, p: dict):
        """Runs in a background thread. Pure numpy — no tk, no matplotlib."""
        try:
            result = self._compute(p)
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            self.after(0, self._compute_failed, err)
            return
        self.after(0, self._render_result, result, p)
 
    @staticmethod
    def _compute(p: dict) -> dict:
        fft_size = p["fft_size"]
        files    = p["files"]
        max_rows = p["max_rows"]
 
        # ---- open memmaps ----
        views: list[np.ndarray] = []
        total_bytes = 0
        for path in files:
            v = memmap_dat(path, fft_size)
            if v.shape[0] > 0:
                views.append(v)
                total_bytes += path.stat().st_size
 
        if not views:
            raise RuntimeError("All selected files are empty or unreadable for "
                               f"fft_size={fft_size}.")
 
        total_rows = sum(v.shape[0] for v in views)
 
        # ---- decimate (if needed) into a small in-memory float32 array ----
        if total_rows <= max_rows:
            spec = np.empty((total_rows, fft_size), dtype=np.float32)
            off = 0
            for v in views:
                n = v.shape[0]
                spec[off:off + n] = v   # sequential page-in from disk
                off += n
            block = 1
        else:
            block = int(np.ceil(total_rows / max_rows))
            spec = decimate_stream(views, block, fft_size)
 
        # release memmaps so the OS can drop file handles / cached pages
        views.clear()
 
        # ---- post-processing on the in-memory array ----
        if not p["preshifted"]:
            spec = np.fft.fftshift(spec, axes=1)
 
        # spec[:, fft_size//2] is now DC == LO frequency.
        if p["notch"]:
            dc = fft_size // 2
            lo, hi = max(0, dc - 3), min(fft_size, dc + 4)
            ref = np.concatenate([spec[:, lo:dc - 1], spec[:, dc + 1:hi]], axis=1)
            spec[:, dc] = np.median(ref, axis=1) if ref.size else spec[:, dc]
 
        if p["baseline"]:
            bp = np.median(spec, axis=0)
            spec = spec / np.maximum(bp, 1e-30)
 
        spec_db = (10.0 * np.log10(np.maximum(spec, 1e-30))).astype(np.float32)
        avg_db  = (10.0 * np.log10(np.maximum(spec.mean(axis=0), 1e-30))).astype(np.float32)
 
        # ---- frequency / velocity axis ----
        bb = np.fft.fftshift(np.fft.fftfreq(fft_size, d=1.0 / p["samp_rate"]))
        xmode = p["xmode"]
        if xmode == "RF [MHz]":
            x = (p["lo_freq"] + bb) / 1e6
            xlabel = "RF Frequency [MHz]"
            hi_marker = HI_REST_HZ / 1e6
        elif xmode == "Baseband [kHz]":
            x = bb / 1e3
            xlabel = "Baseband Frequency [kHz]"
            hi_marker = (HI_REST_HZ - p["lo_freq"]) / 1e3
        else:
            f_obs = p["lo_freq"] + bb
            x = C_KMS * (HI_REST_HZ - f_obs) / HI_REST_HZ
            xlabel = "Doppler velocity [km/s]"
            hi_marker = 0.0
 
        # ---- time axis ----
        # dt_raw : seconds per raw spectrum coming out of the flowgraph
        # one plotted row corresponds to `block` raw spectra
        dt_raw  = (fft_size * p["integ"]) / p["samp_rate"]
        dt_plot = dt_raw * block
        t = np.arange(spec.shape[0]) * dt_plot
 
        # ---- color range ----
        if p["auto_color"]:
            vmin, vmax = np.percentile(spec_db, [5, 99])
        else:
            vmin, vmax = p["vmin_manual"], p["vmax_manual"]
 
        return dict(
            spec_db=spec_db, avg_db=avg_db,
            x=x, t=t, xlabel=xlabel, hi_marker=hi_marker,
            vmin=float(vmin), vmax=float(vmax),
            n_rows_plot=spec.shape[0], n_rows_raw=total_rows,
            dt_raw=dt_raw, dt_plot=dt_plot, block=block,
            total_bytes=total_bytes,
        )
 
    def _render_result(self, r: dict, p: dict):
        """Runs on the main thread. All matplotlib calls live here."""
        self._x = r["x"]
        self._t = r["t"]
        self._spec_db = r["spec_db"]
 
        self.ax_w.clear()
        self.ax_s.clear()
        if self._cbar is not None:
            try:
                self._cbar.remove()
            except Exception:
                pass
            self._cbar = None
 
        y_top = float(r["t"][-1]) if r["t"].size and r["t"][-1] > 0 else r["dt_plot"]
        im = self.ax_w.imshow(
            r["spec_db"], aspect="auto", origin="lower",
            extent=[float(r["x"][0]), float(r["x"][-1]), 0.0, y_top],
            cmap=p["cmap"], vmin=r["vmin"], vmax=r["vmax"],
            interpolation="nearest",
        )
        self.ax_w.set_ylabel("Time [s]")
        self.ax_w.set_title(self._title_text(r["n_rows_plot"], r["n_rows_raw"], r["block"]))
        self.ax_w.axvline(r["hi_marker"], color="red", lw=0.8, ls="--", alpha=0.7)
        self._cbar = self.fig.colorbar(im, ax=self.ax_w, label="Power [dB]", pad=0.01)
 
        self.ax_s.plot(r["x"], r["avg_db"], lw=0.8)
        self.ax_s.axvline(r["hi_marker"], color="red", lw=0.8, ls="--", alpha=0.7,
                          label="H I rest")
        self.ax_s.set_xlabel(r["xlabel"])
        self.ax_s.set_ylabel("Avg power [dB]")
        self.ax_s.grid(alpha=0.3)
        self.ax_s.legend(loc="upper right", fontsize=8)
 
        self.canvas.draw_idle()
 
        decim_note = f"   decimated ×{r['block']}" if r["block"] > 1 else ""
        size_mb = r["total_bytes"] / 1e6
        total_time = r["n_rows_raw"] * r["dt_raw"]
        self._set_status(
            f"{r['n_rows_raw']} raw spectra → {r['n_rows_plot']} plot rows{decim_note}   "
            f"{total_time:.2f} s total   "
            f"{r['dt_raw'] * 1000:.1f} ms / raw row   "
            f"{size_mb:.1f} MB on disk"
        )
 
        self._busy = False
        self.plot_button.configure(state="normal")
 
    def _compute_failed(self, msg: str):
        self._busy = False
        self.plot_button.configure(state="normal")
        self._set_status("Plot failed.")
        messagebox.showerror("Plot failed", msg)
 
    # ----------------------------------------------------------------- misc
    def _title_text(self, n_rows_plot: int, n_rows_raw: int, block: int) -> str:
        decim = f", ×{block} avg" if block > 1 else ""
        if len(self.files) == 1:
            return f"{self.files[0].name}   ({n_rows_raw} raw rows{decim})"
        return f"{len(self.files)} files concatenated   ({n_rows_raw} raw rows{decim})"
 
    def _set_status(self, text: str):
        self.status.configure(text=text)
 
    # -------------------------------------------------------------- cursor
    def _on_mouse_move(self, event):
        if event.inaxes is None or self._spec_db is None:
            return
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        ix = int(np.argmin(np.abs(self._x - x)))
        if event.inaxes is self.ax_w:
            it = int(np.argmin(np.abs(self._t - y)))
            it = max(0, min(it, self._spec_db.shape[0] - 1))
            val = self._spec_db[it, ix]
            self.cursor_label.configure(
                text=f"x = {x:.4f}    t = {y:.2f} s    power = {val:.1f} dB")
        else:
            self.cursor_label.configure(text=f"x = {x:.4f}    y = {y:.1f} dB")
 
    # ----------------------------------------------------------------- save
    def _save_png(self):
        if self._spec_db is None:
            messagebox.showinfo("Nothing to save", "Plot something first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save figure as PNG",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("All files", "*.*")],
        )
        if path:
            self.fig.savefig(path, dpi=150, bbox_inches="tight")
            self._set_status(f"Saved: {path}")
 
 
if __name__ == "__main__":
    app = MergenViewer()
    app.mainloop()
