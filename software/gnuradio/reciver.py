#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: reciver
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import datetime, os
import sip
import threading



class reciver(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "reciver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("reciver")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "reciver")

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
        self.samp_rate = samp_rate = 2048000
        self.fft_size = fft_size = 2048
        self.beta = beta = 8.6
        self.session_ts = session_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.rx_gain = rx_gain = 30
        self.rf_bandwidth = rf_bandwidth = 2000000
        self.log_dir = log_dir = "C:/Users/alpgo/Desktop/gits/mergen-21/software/gnuradio/logs"
        self.kaiser_window = kaiser_window = firdes.low_pass(1.0, samp_rate, samp_rate/(4*fft_size), samp_rate/(4*fft_size), window.WIN_KAISER, beta)
        self.integration_time = integration_time = 500
        self.LO_freq = LO_freq = 1420405000
        self.K = K = 8

        ##################################################
        # Blocks
        ##################################################

        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Integrated Power waterfall", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-110, -70)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 4, 0, 2, 8)
        for r in range(4, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_vector_sink_f_0 = qtgui.vector_sink_f(
            fft_size,
            (-samp_rate/2),
            (samp_rate/fft_size),
            "Frequency (Hz)",
            "dbm/bin",
            "Integrated Power Spectrum",
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_0.set_update_time(0.10)
        self.qtgui_vector_sink_f_0.set_y_axis((-120), (-50))
        self.qtgui_vector_sink_f_0.enable_autoscale(False)
        self.qtgui_vector_sink_f_0.enable_grid(True)
        self.qtgui_vector_sink_f_0.set_x_axis_units("Hz")
        self.qtgui_vector_sink_f_0.set_y_axis_units("")
        self.qtgui_vector_sink_f_0.set_ref_level(0)


        labels = ['Power', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_vector_sink_f_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_0.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_0.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_0.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_0.set_line_alpha(i, alphas[i])

        self._qtgui_vector_sink_f_0_win = sip.wrapinstance(self.qtgui_vector_sink_f_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_vector_sink_f_0_win, 1, 0, 3, 8)
        for r in range(1, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_0 = qtgui.freq_sink_c(
            fft_size, #size
            window.WIN_KAISER, #wintype
            LO_freq, #fc
            samp_rate, #bw
            "RX Quick-Look FFT", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_0.set_update_time(0.10)
        self.qtgui_freq_sink_0.set_y_axis((-140), (-20))
        self.qtgui_freq_sink_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_0.enable_autoscale(True)
        self.qtgui_freq_sink_0.enable_grid(True)
        self.qtgui_freq_sink_0.set_fft_average(1.0)
        self.qtgui_freq_sink_0.enable_axis_labels(True)
        self.qtgui_freq_sink_0.enable_control_panel(False)
        self.qtgui_freq_sink_0.set_fft_window_normalized(False)



        labels = ['RX', '', '', '', '',
            '', '', '', '', '']
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_0_win, 6, 0, 2, 8)
        for r in range(6, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pluto_rx = iio.fmcomms2_source_fc32('ip:192.168.10.1' if 'ip:192.168.10.1' else iio.get_pluto_uri(), [True, True], 32768)
        self.pluto_rx.set_len_tag_key('packet_len')
        self.pluto_rx.set_frequency(LO_freq)
        self.pluto_rx.set_samplerate(samp_rate)
        self.pluto_rx.set_gain_mode(0, 'manual')
        self.pluto_rx.set_gain(0, rx_gain)
        self.pluto_rx.set_quadrature(True)
        self.pluto_rx.set_rfdc(True)
        self.pluto_rx.set_bbdc(True)
        self.pluto_rx.set_filter_params('Auto', '', 0, 0)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, [], True, 2)
        self.blocks_stream_to_vector_0_2 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0_1_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0_0_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0_0_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, fft_size, 0)
        self.blocks_multiply_const_vxx_0_3 = blocks.multiply_const_vff((1.0/integration_time,) * fft_size)
        self.blocks_multiply_const_vxx_0_2 = blocks.multiply_const_vcc(kaiser_window[3*fft_size:4*fft_size])
        self.blocks_multiply_const_vxx_0_1_0 = blocks.multiply_const_vcc(kaiser_window[fft_size:2*fft_size])
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_vcc(kaiser_window[5*fft_size:6*fft_size])
        self.blocks_multiply_const_vxx_0_0_1 = blocks.multiply_const_vcc(kaiser_window[2*fft_size:3*fft_size])
        self.blocks_multiply_const_vxx_0_0_0_0 = blocks.multiply_const_vcc(kaiser_window[0:fft_size])
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_vcc(kaiser_window[4*fft_size:5*fft_size])
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vcc(kaiser_window[6*fft_size:7*fft_size])
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc(kaiser_window[7*fft_size:8*fft_size])
        self.blocks_integrate_xx_0 = blocks.integrate_ff(integration_time, fft_size)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*2048, os.path.join(log_dir, "mergen21_spec_" + session_ts + ".dat"), False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_delay_0_0_1_0_0_0_0 = blocks.delay(gr.sizeof_gr_complex*1, (fft_size*7))
        self.blocks_delay_0_0_1_0_0_0 = blocks.delay(gr.sizeof_gr_complex*1, (fft_size*6))
        self.blocks_delay_0_0_1_0_0 = blocks.delay(gr.sizeof_gr_complex*1, (fft_size*5))
        self.blocks_delay_0_0_1_0 = blocks.delay(gr.sizeof_gr_complex*1, (fft_size*4))
        self.blocks_delay_0_0_1 = blocks.delay(gr.sizeof_gr_complex*1, (fft_size*3))
        self.blocks_delay_0_0_0 = blocks.delay(gr.sizeof_gr_complex*1, (fft_size*2))
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, 0)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_size)
        self.blocks_add_xx_0 = blocks.add_vcc(fft_size)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_xx_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_delay_0_0_0, 0), (self.blocks_stream_to_vector_0_1, 0))
        self.connect((self.blocks_delay_0_0_1, 0), (self.blocks_stream_to_vector_0_0_0, 0))
        self.connect((self.blocks_delay_0_0_1_0, 0), (self.blocks_stream_to_vector_0_2, 0))
        self.connect((self.blocks_delay_0_0_1_0_0, 0), (self.blocks_stream_to_vector_0_0_1, 0))
        self.connect((self.blocks_delay_0_0_1_0_0_0, 0), (self.blocks_stream_to_vector_0_1_0, 0))
        self.connect((self.blocks_delay_0_0_1_0_0_0_0, 0), (self.blocks_stream_to_vector_0_0_0_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_multiply_const_vxx_0_3, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.blocks_add_xx_0, 3))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0, 0), (self.blocks_add_xx_0, 7))
        self.connect((self.blocks_multiply_const_vxx_0_0_1, 0), (self.blocks_add_xx_0, 5))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.blocks_multiply_const_vxx_0_1_0, 0), (self.blocks_add_xx_0, 6))
        self.connect((self.blocks_multiply_const_vxx_0_2, 0), (self.blocks_add_xx_0, 4))
        self.connect((self.blocks_multiply_const_vxx_0_3, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_3, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.qtgui_vector_sink_f_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0_1, 0), (self.blocks_multiply_const_vxx_0_0_1, 0))
        self.connect((self.blocks_stream_to_vector_0_1, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_stream_to_vector_0_1_0, 0), (self.blocks_multiply_const_vxx_0_1_0, 0))
        self.connect((self.blocks_stream_to_vector_0_2, 0), (self.blocks_multiply_const_vxx_0_2, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_delay_0, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_delay_0_0_0, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_delay_0_0_1, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_delay_0_0_1_0, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_delay_0_0_1_0_0, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_delay_0_0_1_0_0_0, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_delay_0_0_1_0_0_0_0, 0))
        self.connect((self.pluto_rx, 0), (self.qtgui_freq_sink_0, 0))
        self.connect((self.pluto_rx, 0), (self.qtgui_waterfall_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "reciver")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_kaiser_window(firdes.low_pass(1.0, self.samp_rate, self.samp_rate/(4*self.fft_size), self.samp_rate/(4*self.fft_size), window.WIN_KAISER, self.beta))
        self.pluto_rx.set_samplerate(self.samp_rate)
        self.qtgui_freq_sink_0.set_frequency_range(self.LO_freq, self.samp_rate)
        self.qtgui_vector_sink_f_0.set_x_axis((-self.samp_rate/2), (self.samp_rate/self.fft_size))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.set_kaiser_window(firdes.low_pass(1.0, self.samp_rate, self.samp_rate/(4*self.fft_size), self.samp_rate/(4*self.fft_size), window.WIN_KAISER, self.beta))
        self.blocks_delay_0_0.set_dly(int(self.fft_size))
        self.blocks_delay_0_0_0.set_dly(int((self.fft_size*2)))
        self.blocks_delay_0_0_1.set_dly(int((self.fft_size*3)))
        self.blocks_delay_0_0_1_0.set_dly(int((self.fft_size*4)))
        self.blocks_delay_0_0_1_0_0.set_dly(int((self.fft_size*5)))
        self.blocks_delay_0_0_1_0_0_0.set_dly(int((self.fft_size*6)))
        self.blocks_delay_0_0_1_0_0_0_0.set_dly(int((self.fft_size*7)))
        self.blocks_multiply_const_vxx_0.set_k(self.kaiser_window[7*self.fft_size:8*self.fft_size])
        self.blocks_multiply_const_vxx_0_0.set_k(self.kaiser_window[6*self.fft_size:7*self.fft_size])
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.kaiser_window[4*self.fft_size:5*self.fft_size])
        self.blocks_multiply_const_vxx_0_0_0_0.set_k(self.kaiser_window[0:self.fft_size])
        self.blocks_multiply_const_vxx_0_0_1.set_k(self.kaiser_window[2*self.fft_size:3*self.fft_size])
        self.blocks_multiply_const_vxx_0_1.set_k(self.kaiser_window[5*self.fft_size:6*self.fft_size])
        self.blocks_multiply_const_vxx_0_1_0.set_k(self.kaiser_window[self.fft_size:2*self.fft_size])
        self.blocks_multiply_const_vxx_0_2.set_k(self.kaiser_window[3*self.fft_size:4*self.fft_size])
        self.blocks_multiply_const_vxx_0_3.set_k((1.0/self.integration_time,) * self.fft_size)
        self.qtgui_vector_sink_f_0.set_x_axis((-self.samp_rate/2), (self.samp_rate/self.fft_size))

    def get_beta(self):
        return self.beta

    def set_beta(self, beta):
        self.beta = beta
        self.set_kaiser_window(firdes.low_pass(1.0, self.samp_rate, self.samp_rate/(4*self.fft_size), self.samp_rate/(4*self.fft_size), window.WIN_KAISER, self.beta))

    def get_session_ts(self):
        return self.session_ts

    def set_session_ts(self, session_ts):
        self.session_ts = session_ts
        self.blocks_file_sink_0.open(os.path.join(self.log_dir, "mergen21_spec_" + self.session_ts + ".dat"))

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.pluto_rx.set_gain(0, self.rx_gain)

    def get_rf_bandwidth(self):
        return self.rf_bandwidth

    def set_rf_bandwidth(self, rf_bandwidth):
        self.rf_bandwidth = rf_bandwidth

    def get_log_dir(self):
        return self.log_dir

    def set_log_dir(self, log_dir):
        self.log_dir = log_dir
        self.blocks_file_sink_0.open(os.path.join(self.log_dir, "mergen21_spec_" + self.session_ts + ".dat"))

    def get_kaiser_window(self):
        return self.kaiser_window

    def set_kaiser_window(self, kaiser_window):
        self.kaiser_window = kaiser_window
        self.blocks_multiply_const_vxx_0.set_k(self.kaiser_window[7*self.fft_size:8*self.fft_size])
        self.blocks_multiply_const_vxx_0_0.set_k(self.kaiser_window[6*self.fft_size:7*self.fft_size])
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.kaiser_window[4*self.fft_size:5*self.fft_size])
        self.blocks_multiply_const_vxx_0_0_0_0.set_k(self.kaiser_window[0:self.fft_size])
        self.blocks_multiply_const_vxx_0_0_1.set_k(self.kaiser_window[2*self.fft_size:3*self.fft_size])
        self.blocks_multiply_const_vxx_0_1.set_k(self.kaiser_window[5*self.fft_size:6*self.fft_size])
        self.blocks_multiply_const_vxx_0_1_0.set_k(self.kaiser_window[self.fft_size:2*self.fft_size])
        self.blocks_multiply_const_vxx_0_2.set_k(self.kaiser_window[3*self.fft_size:4*self.fft_size])

    def get_integration_time(self):
        return self.integration_time

    def set_integration_time(self, integration_time):
        self.integration_time = integration_time
        self.blocks_multiply_const_vxx_0_3.set_k((1.0/self.integration_time,) * self.fft_size)

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        self.pluto_rx.set_frequency(self.LO_freq)
        self.qtgui_freq_sink_0.set_frequency_range(self.LO_freq, self.samp_rate)

    def get_K(self):
        return self.K

    def set_K(self, K):
        self.K = K




def main(top_block_cls=reciver, options=None):

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
