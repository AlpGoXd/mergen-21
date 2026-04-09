#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Topo 3 Required Constants Meter
# Author: OpenAI
# Description: Measure raw branch RMS after LPFs and directly show required Multiply Const values.
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip
import threading



class topo3_required_constants(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Topo 3 Required Constants Meter", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Topo 3 Required Constants Meter")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "topo3_required_constants")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.target_warm_rms = target_warm_rms = 0.25
        self.target_sgr_rms = target_sgr_rms = 0.60
        self.target_perseus_rms = target_perseus_rms = 0.70
        self.target_outer_rms = target_outer_rms = 0.45
        self.target_local_rms = target_local_rms = 1.00
        self.target_floor_rms = target_floor_rms = 0.002
        self.samp_rate = samp_rate = 3080000
        self.probe_alpha = probe_alpha = 1e-7
        self.guard_offset_hz = guard_offset_hz = 250000
        self.fft_size = fft_size = 4096

        ##################################################
        # Blocks
        ##################################################

        self._target_warm_rms_range = qtgui.Range(0.01, 2.0, 0.01, 0.25, 200)
        self._target_warm_rms_win = qtgui.RangeWidget(self._target_warm_rms_range, self.set_target_warm_rms, "target_warm_rms", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._target_warm_rms_win, 4, 0, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._target_sgr_rms_range = qtgui.Range(0.01, 2.0, 0.01, 0.60, 200)
        self._target_sgr_rms_win = qtgui.RangeWidget(self._target_sgr_rms_range, self.set_target_sgr_rms, "target_sgr_rms", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._target_sgr_rms_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._target_perseus_rms_range = qtgui.Range(0.01, 2.0, 0.01, 0.70, 200)
        self._target_perseus_rms_win = qtgui.RangeWidget(self._target_perseus_rms_range, self.set_target_perseus_rms, "target_perseus_rms", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._target_perseus_rms_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._target_outer_rms_range = qtgui.Range(0.01, 2.0, 0.01, 0.45, 200)
        self._target_outer_rms_win = qtgui.RangeWidget(self._target_outer_rms_range, self.set_target_outer_rms, "target_outer_rms", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._target_outer_rms_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._target_local_rms_range = qtgui.Range(0.01, 2.0, 0.01, 1.00, 200)
        self._target_local_rms_win = qtgui.RangeWidget(self._target_local_rms_range, self.set_target_local_rms, "target_local_rms", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._target_local_rms_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._target_floor_rms_range = qtgui.Range(0.0001, 0.05, 0.0001, 0.002, 200)
        self._target_floor_rms_win = qtgui.RangeWidget(self._target_floor_rms_range, self.set_target_floor_rms, "target_floor_rms", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._target_floor_rms_win, 5, 0, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.target_warm_src = analog.sig_source_f(samp_rate, analog.GR_CONST_WAVE, 0, 0, target_warm_rms, 0)
        self.target_sgr_src = analog.sig_source_f(samp_rate, analog.GR_CONST_WAVE, 0, 0, target_sgr_rms, 0)
        self.target_perseus_src = analog.sig_source_f(samp_rate, analog.GR_CONST_WAVE, 0, 0, target_perseus_rms, 0)
        self.target_outer_src = analog.sig_source_f(samp_rate, analog.GR_CONST_WAVE, 0, 0, target_outer_rms, 0)
        self.target_local_src = analog.sig_source_f(samp_rate, analog.GR_CONST_WAVE, 0, 0, target_local_rms, 0)
        self.target_floor_src = analog.sig_source_f(samp_rate, analog.GR_CONST_WAVE, 0, 0, target_floor_rms, 0)
        self.sum_all = blocks.add_vcc(1)
        self.rot_warm = blocks.rotator_cc(((2.0 * 3.141592653589793 * -23700.0 / samp_rate)), False)
        self.rot_sgr = blocks.rotator_cc(((2.0 * 3.141592653589793 * -94800.0 / samp_rate)), False)
        self.rot_perseus = blocks.rotator_cc(((2.0 * 3.141592653589793 * 189600.0 / samp_rate)), False)
        self.rot_outer = blocks.rotator_cc(((2.0 * 3.141592653589793 * 379200.0 / samp_rate)), False)
        self.rot_local = blocks.rotator_cc(((2.0 * 3.141592653589793 * 0.0 / samp_rate)), False)
        self.rot_guard = blocks.rotator_cc(((2.0 * 3.141592653589793 * guard_offset_hz / samp_rate)), False)
        self.rms_warm = blocks.rms_cf(probe_alpha)
        self.rms_sgr = blocks.rms_cf(probe_alpha)
        self.rms_perseus = blocks.rms_cf(probe_alpha)
        self.rms_outer = blocks.rms_cf(probe_alpha)
        self.rms_local = blocks.rms_cf(probe_alpha)
        self.rms_floor = blocks.rms_cf(probe_alpha)
        self.qtgui_number_sink_raw = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            6,
            None # parent
        )
        self.qtgui_number_sink_raw.set_update_time(0.10)
        self.qtgui_number_sink_raw.set_title("Measured raw RMS after LPFs")

        labels = ["local raw rms", "perseus raw rms", "sgr raw rms", "outer raw rms", "warm raw rms",
            "floor raw rms", '', '', '', '']
        units = ["", "", "", "", "",
            "", '', '', '', '']
        colors = [("black", "black"), ("blue", "red"), ("black", "red"), ("black", "white"), ("white", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(6):
            self.qtgui_number_sink_raw.set_min(i, 0)
            self.qtgui_number_sink_raw.set_max(i, 2)
            self.qtgui_number_sink_raw.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_raw.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_raw.set_label(i, labels[i])
            self.qtgui_number_sink_raw.set_unit(i, units[i])
            self.qtgui_number_sink_raw.set_factor(i, factor[i])

        self.qtgui_number_sink_raw.enable_autoscale(True)
        self._qtgui_number_sink_raw_win = sip.wrapinstance(self.qtgui_number_sink_raw.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_raw_win, 0, 2, 4, 4)
        for r in range(0, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_k = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            6,
            None # parent
        )
        self.qtgui_number_sink_k.set_update_time(0.10)
        self.qtgui_number_sink_k.set_title("Required Multiply Const values")

        labels = ["local k", "perseus k", "sgr k", "outer k", "warm k",
            "floor k", '', '', '', '']
        units = ["", "", "", "", "",
            "", '', '', '', '']
        colors = [("black", "black"), ("blue", "red"), ("black", "red"), ("black", "white"), ("white", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(6):
            self.qtgui_number_sink_k.set_min(i, 0)
            self.qtgui_number_sink_k.set_max(i, 10)
            self.qtgui_number_sink_k.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_k.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_k.set_label(i, labels[i])
            self.qtgui_number_sink_k.set_unit(i, units[i])
            self.qtgui_number_sink_k.set_factor(i, factor[i])

        self.qtgui_number_sink_k.enable_autoscale(True)
        self._qtgui_number_sink_k_win = sip.wrapinstance(self.qtgui_number_sink_k.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_k_win, 4, 2, 4, 4)
        for r in range(4, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_0 = qtgui.freq_sink_c(
            fft_size, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Synthetic sky quick-look", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_0.set_update_time(0.10)
        self.qtgui_freq_sink_0.set_y_axis((-100), 10)
        self.qtgui_freq_sink_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_0.enable_autoscale(True)
        self.qtgui_freq_sink_0.enable_grid(True)
        self.qtgui_freq_sink_0.set_fft_average(0.2)
        self.qtgui_freq_sink_0.enable_axis_labels(True)
        self.qtgui_freq_sink_0.enable_control_panel(False)
        self.qtgui_freq_sink_0.set_fft_window_normalized(False)

        self.qtgui_freq_sink_0.disable_legend()


        labels = ["sum", "", "", "", "",
            "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_0_win = sip.wrapinstance(self.qtgui_freq_sink_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_0_win, 0, 6, 8, 4)
        for r in range(0, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(6, 10):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.noise_warm = analog.noise_source_c(analog.GR_GAUSSIAN, 0.15, 4)
        self.noise_sgr = analog.noise_source_c(analog.GR_GAUSSIAN, 0.5, 3)
        self.noise_perseus = analog.noise_source_c(analog.GR_GAUSSIAN, 0.6, 1)
        self.noise_outer = analog.noise_source_c(analog.GR_GAUSSIAN, 0.3, 2)
        self.noise_local = analog.noise_source_c(analog.GR_GAUSSIAN, 1.0, 0)
        self.noise_floor = analog.noise_source_c(analog.GR_GAUSSIAN, 0.002, 42)
        self.mult_warm = blocks.multiply_const_cc(1.0)
        self.mult_sgr = blocks.multiply_const_cc(1.0)
        self.mult_perseus = blocks.multiply_const_cc(1.0)
        self.mult_outer = blocks.multiply_const_cc(1.0)
        self.mult_local = blocks.multiply_const_cc(1.0)
        self.mult_floor = blocks.multiply_const_cc(1.0)
        self.lpf_warm = filter.fir_filter_ccf(1, firdes.low_pass(1, samp_rate, 80509, 47400, window.WIN_HAMMING, 6.76))
        self.lpf_warm.declare_sample_delay(0)
        self.lpf_sgr = filter.fir_filter_ccf(1, firdes.low_pass(1, samp_rate, 36220, 21325, window.WIN_HAMMING, 6.76))
        self.lpf_sgr.declare_sample_delay(0)
        self.lpf_perseus = filter.fir_filter_ccf(1, firdes.low_pass(1, samp_rate, 40254, 23700, window.WIN_HAMMING, 6.76))
        self.lpf_perseus.declare_sample_delay(0)
        self.lpf_outer = filter.fir_filter_ccf(1, firdes.low_pass(1, samp_rate, 50318, 29625, window.WIN_HAMMING, 6.76))
        self.lpf_outer.declare_sample_delay(0)
        self.lpf_local = filter.fir_filter_ccf(1, firdes.low_pass(1, samp_rate, 30191, 17775, window.WIN_HAMMING, 6.76))
        self.lpf_local.declare_sample_delay(0)
        self.div_warm_k = blocks.divide_ff(1)
        self.div_sgr_k = blocks.divide_ff(1)
        self.div_perseus_k = blocks.divide_ff(1)
        self.div_outer_k = blocks.divide_ff(1)
        self.div_local_k = blocks.divide_ff(1)
        self.div_floor_k = blocks.divide_ff(1)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_throttle2_0, 0), (self.qtgui_freq_sink_0, 0))
        self.connect((self.div_floor_k, 0), (self.qtgui_number_sink_k, 5))
        self.connect((self.div_local_k, 0), (self.qtgui_number_sink_k, 0))
        self.connect((self.div_outer_k, 0), (self.qtgui_number_sink_k, 3))
        self.connect((self.div_perseus_k, 0), (self.qtgui_number_sink_k, 1))
        self.connect((self.div_sgr_k, 0), (self.qtgui_number_sink_k, 2))
        self.connect((self.div_warm_k, 0), (self.qtgui_number_sink_k, 4))
        self.connect((self.lpf_local, 0), (self.mult_local, 0))
        self.connect((self.lpf_local, 0), (self.rms_local, 0))
        self.connect((self.lpf_outer, 0), (self.mult_outer, 0))
        self.connect((self.lpf_outer, 0), (self.rms_outer, 0))
        self.connect((self.lpf_perseus, 0), (self.mult_perseus, 0))
        self.connect((self.lpf_perseus, 0), (self.rms_perseus, 0))
        self.connect((self.lpf_sgr, 0), (self.mult_sgr, 0))
        self.connect((self.lpf_sgr, 0), (self.rms_sgr, 0))
        self.connect((self.lpf_warm, 0), (self.mult_warm, 0))
        self.connect((self.lpf_warm, 0), (self.rms_warm, 0))
        self.connect((self.mult_floor, 0), (self.sum_all, 5))
        self.connect((self.mult_local, 0), (self.rot_local, 0))
        self.connect((self.mult_outer, 0), (self.rot_outer, 0))
        self.connect((self.mult_perseus, 0), (self.rot_perseus, 0))
        self.connect((self.mult_sgr, 0), (self.rot_sgr, 0))
        self.connect((self.mult_warm, 0), (self.rot_warm, 0))
        self.connect((self.noise_floor, 0), (self.mult_floor, 0))
        self.connect((self.noise_floor, 0), (self.rms_floor, 0))
        self.connect((self.noise_local, 0), (self.lpf_local, 0))
        self.connect((self.noise_outer, 0), (self.lpf_outer, 0))
        self.connect((self.noise_perseus, 0), (self.lpf_perseus, 0))
        self.connect((self.noise_sgr, 0), (self.lpf_sgr, 0))
        self.connect((self.noise_warm, 0), (self.lpf_warm, 0))
        self.connect((self.rms_floor, 0), (self.div_floor_k, 1))
        self.connect((self.rms_floor, 0), (self.qtgui_number_sink_raw, 5))
        self.connect((self.rms_local, 0), (self.div_local_k, 1))
        self.connect((self.rms_local, 0), (self.qtgui_number_sink_raw, 0))
        self.connect((self.rms_outer, 0), (self.div_outer_k, 1))
        self.connect((self.rms_outer, 0), (self.qtgui_number_sink_raw, 3))
        self.connect((self.rms_perseus, 0), (self.div_perseus_k, 1))
        self.connect((self.rms_perseus, 0), (self.qtgui_number_sink_raw, 1))
        self.connect((self.rms_sgr, 0), (self.div_sgr_k, 1))
        self.connect((self.rms_sgr, 0), (self.qtgui_number_sink_raw, 2))
        self.connect((self.rms_warm, 0), (self.div_warm_k, 1))
        self.connect((self.rms_warm, 0), (self.qtgui_number_sink_raw, 4))
        self.connect((self.rot_guard, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.rot_local, 0), (self.sum_all, 0))
        self.connect((self.rot_outer, 0), (self.sum_all, 3))
        self.connect((self.rot_perseus, 0), (self.sum_all, 1))
        self.connect((self.rot_sgr, 0), (self.sum_all, 2))
        self.connect((self.rot_warm, 0), (self.sum_all, 4))
        self.connect((self.sum_all, 0), (self.rot_guard, 0))
        self.connect((self.target_floor_src, 0), (self.div_floor_k, 0))
        self.connect((self.target_local_src, 0), (self.div_local_k, 0))
        self.connect((self.target_outer_src, 0), (self.div_outer_k, 0))
        self.connect((self.target_perseus_src, 0), (self.div_perseus_k, 0))
        self.connect((self.target_sgr_src, 0), (self.div_sgr_k, 0))
        self.connect((self.target_warm_src, 0), (self.div_warm_k, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "topo3_required_constants")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_target_warm_rms(self):
        return self.target_warm_rms

    def set_target_warm_rms(self, target_warm_rms):
        self.target_warm_rms = target_warm_rms
        self.target_warm_src.set_offset(self.target_warm_rms)

    def get_target_sgr_rms(self):
        return self.target_sgr_rms

    def set_target_sgr_rms(self, target_sgr_rms):
        self.target_sgr_rms = target_sgr_rms
        self.target_sgr_src.set_offset(self.target_sgr_rms)

    def get_target_perseus_rms(self):
        return self.target_perseus_rms

    def set_target_perseus_rms(self, target_perseus_rms):
        self.target_perseus_rms = target_perseus_rms
        self.target_perseus_src.set_offset(self.target_perseus_rms)

    def get_target_outer_rms(self):
        return self.target_outer_rms

    def set_target_outer_rms(self, target_outer_rms):
        self.target_outer_rms = target_outer_rms
        self.target_outer_src.set_offset(self.target_outer_rms)

    def get_target_local_rms(self):
        return self.target_local_rms

    def set_target_local_rms(self, target_local_rms):
        self.target_local_rms = target_local_rms
        self.target_local_src.set_offset(self.target_local_rms)

    def get_target_floor_rms(self):
        return self.target_floor_rms

    def set_target_floor_rms(self, target_floor_rms):
        self.target_floor_rms = target_floor_rms
        self.target_floor_src.set_offset(self.target_floor_rms)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.lpf_local.set_taps(firdes.low_pass(1, self.samp_rate, 30191, 17775, window.WIN_HAMMING, 6.76))
        self.lpf_outer.set_taps(firdes.low_pass(1, self.samp_rate, 50318, 29625, window.WIN_HAMMING, 6.76))
        self.lpf_perseus.set_taps(firdes.low_pass(1, self.samp_rate, 40254, 23700, window.WIN_HAMMING, 6.76))
        self.lpf_sgr.set_taps(firdes.low_pass(1, self.samp_rate, 36220, 21325, window.WIN_HAMMING, 6.76))
        self.lpf_warm.set_taps(firdes.low_pass(1, self.samp_rate, 80509, 47400, window.WIN_HAMMING, 6.76))
        self.qtgui_freq_sink_0.set_frequency_range(0, self.samp_rate)
        self.rot_guard.set_phase_inc(((2.0 * 3.141592653589793 * self.guard_offset_hz / self.samp_rate)))
        self.rot_local.set_phase_inc(((2.0 * 3.141592653589793 * 0.0 / self.samp_rate)))
        self.rot_outer.set_phase_inc(((2.0 * 3.141592653589793 * 379200.0 / self.samp_rate)))
        self.rot_perseus.set_phase_inc(((2.0 * 3.141592653589793 * 189600.0 / self.samp_rate)))
        self.rot_sgr.set_phase_inc(((2.0 * 3.141592653589793 * -94800.0 / self.samp_rate)))
        self.rot_warm.set_phase_inc(((2.0 * 3.141592653589793 * -23700.0 / self.samp_rate)))
        self.target_floor_src.set_sampling_freq(self.samp_rate)
        self.target_local_src.set_sampling_freq(self.samp_rate)
        self.target_outer_src.set_sampling_freq(self.samp_rate)
        self.target_perseus_src.set_sampling_freq(self.samp_rate)
        self.target_sgr_src.set_sampling_freq(self.samp_rate)
        self.target_warm_src.set_sampling_freq(self.samp_rate)

    def get_probe_alpha(self):
        return self.probe_alpha

    def set_probe_alpha(self, probe_alpha):
        self.probe_alpha = probe_alpha
        self.rms_floor.set_alpha(self.probe_alpha)
        self.rms_local.set_alpha(self.probe_alpha)
        self.rms_outer.set_alpha(self.probe_alpha)
        self.rms_perseus.set_alpha(self.probe_alpha)
        self.rms_sgr.set_alpha(self.probe_alpha)
        self.rms_warm.set_alpha(self.probe_alpha)

    def get_guard_offset_hz(self):
        return self.guard_offset_hz

    def set_guard_offset_hz(self, guard_offset_hz):
        self.guard_offset_hz = guard_offset_hz
        self.rot_guard.set_phase_inc(((2.0 * 3.141592653589793 * self.guard_offset_hz / self.samp_rate)))

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size




def main(top_block_cls=topo3_required_constants, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
