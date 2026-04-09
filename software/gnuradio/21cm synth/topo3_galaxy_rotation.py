#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Topo 3: Galaxy Rotation
# Author: Mergen-21
# Description: Topo 3: 5-component Milky Way model
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import sip
import threading



class topo3_galaxy_rotation(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Topo 3: Galaxy Rotation", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Topo 3: Galaxy Rotation")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "topo3_galaxy_rotation")

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
        self.tx_atten = tx_atten = 50
        self.sky_offset_hz = sky_offset_hz = 230e3
        self.samp_rate = samp_rate = 3080000
        self.rx_gain = rx_gain = 30
        self.rf_bandwidth = rf_bandwidth = 3080000
        self.integration_time = integration_time = 1000
        self.fft_size = fft_size = 4096
        self.LO_freq = LO_freq = 1420405000

        ##################################################
        # Blocks
        ##################################################

        self._tx_atten_range = qtgui.Range(0, 89.75, 0.25, 50, 200)
        self._tx_atten_win = qtgui.RangeWidget(self._tx_atten_range, self.set_tx_atten, "TX Attenuation [dB]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._tx_atten_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._sky_offset_hz_range = qtgui.Range(-500e3, 500e3, 1e3, 230e3, 200)
        self._sky_offset_hz_win = qtgui.RangeWidget(self._sky_offset_hz_range, self.set_sky_offset_hz, "Sky Offset in Hertz", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._sky_offset_hz_win, 0, 4, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = qtgui.Range(0, 73, 1, 30, 200)
        self._rx_gain_win = qtgui.RangeWidget(self._rx_gain_range, self.set_rx_gain, "RX Gain [dB]", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 2, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.tx_adder = blocks.add_vcc(1)
        self.rot_warm_0 = blocks.rotator_cc(((2.0 * 3.141592653589793 * sky_offset_hz) / samp_rate), False)
        self.rot_warm = blocks.rotator_cc((2.0 * 3.14159265 * -23700.0 / samp_rate), False)
        self.rot_sgr = blocks.rotator_cc((2.0 * 3.14159265 * -94800.0 / samp_rate), False)
        self.rot_perseus = blocks.rotator_cc((2.0 * 3.14159265 * 189600.0 / samp_rate), False)
        self.rot_outer = blocks.rotator_cc((2.0 * 3.14159265 * 379200.0 / samp_rate), False)
        self.rot_local = blocks.rotator_cc((2.0 * 3.14159265 * 0.0 / samp_rate), False)
        self.qtgui_vector_sink_f_0 = qtgui.vector_sink_f(
            fft_size,
            (-samp_rate/2),
            (samp_rate/fft_size),
            "Frequency (Hz)",
            "Power",
            "Integrated Power Spectrum",
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_0.set_update_time(0.10)
        self.qtgui_vector_sink_f_0.set_y_axis(0, 1)
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
        self.top_grid_layout.addWidget(self._qtgui_vector_sink_f_0_win, 2, 0, 2, 6)
        for r in range(2, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_0 = qtgui.freq_sink_c(
            fft_size, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_0_win, 4, 0, 2, 6)
        for r in range(4, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pluto_rx = iio.fmcomms2_source_fc32('ip:192.168.20.1' if 'ip:192.168.20.1' else iio.get_pluto_uri(), [True, True], 32768)
        self.pluto_rx.set_len_tag_key('packet_len')
        self.pluto_rx.set_frequency(LO_freq)
        self.pluto_rx.set_samplerate(samp_rate)
        self.pluto_rx.set_gain_mode(0, 'manual')
        self.pluto_rx.set_gain(0, rx_gain)
        self.pluto_rx.set_quadrature(True)
        self.pluto_rx.set_rfdc(True)
        self.pluto_rx.set_bbdc(True)
        self.pluto_rx.set_filter_params('Auto', '', 0, 0)
        self.noise_warm = analog.noise_source_c(analog.GR_GAUSSIAN, 0.3, 4)
        self.noise_sgr = analog.noise_source_c(analog.GR_GAUSSIAN, 0.6, 3)
        self.noise_perseus = analog.noise_source_c(analog.GR_GAUSSIAN, 0.8, 1)
        self.noise_outer = analog.noise_source_c(analog.GR_GAUSSIAN, 0.5, 2)
        self.noise_local = analog.noise_source_c(analog.GR_GAUSSIAN, 1.0, 0)
        self.noise_floor = analog.noise_source_c(analog.GR_GAUSSIAN, 0.002, 42)
        self.lpf_warm = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                80509,
                47400,
                window.WIN_HAMMING,
                6.76))
        self.lpf_sgr = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                36220,
                21325,
                window.WIN_HAMMING,
                6.76))
        self.lpf_perseus = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                40254,
                23700,
                window.WIN_HAMMING,
                6.76))
        self.lpf_outer = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                50318,
                29625,
                window.WIN_HAMMING,
                6.76))
        self.lpf_local = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                30191,
                17775,
                window.WIN_HAMMING,
                6.76))
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('ip:192.168.20.1' if 'ip:192.168.20.1' else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(rf_bandwidth)
        self.iio_pluto_sink_0.set_frequency(LO_freq)
        self.iio_pluto_sink_0.set_samplerate(samp_rate)
        self.iio_pluto_sink_0.set_attenuation(0, tx_atten)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, window.blackmanharris(fft_size), True, 1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, 4096, 0)
        self.blocks_multiply_const_xx_0_0_0_0_0 = blocks.multiply_const_cc(7.6, 1)
        self.blocks_multiply_const_xx_0_0_0_0 = blocks.multiply_const_cc(8.2, 1)
        self.blocks_multiply_const_xx_0_0_0 = blocks.multiply_const_cc(8.7, 1)
        self.blocks_multiply_const_xx_0_0 = blocks.multiply_const_cc(7.6, 1)
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_cc(7.5, 1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((1.0/integration_time,) * fft_size)
        self.blocks_integrate_xx_0 = blocks.integrate_ff(integration_time, fft_size)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_size)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.rot_local, 0))
        self.connect((self.blocks_multiply_const_xx_0_0, 0), (self.rot_perseus, 0))
        self.connect((self.blocks_multiply_const_xx_0_0_0, 0), (self.rot_outer, 0))
        self.connect((self.blocks_multiply_const_xx_0_0_0_0, 0), (self.rot_sgr, 0))
        self.connect((self.blocks_multiply_const_xx_0_0_0_0_0, 0), (self.rot_warm, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.qtgui_vector_sink_f_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.lpf_local, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.lpf_outer, 0), (self.blocks_multiply_const_xx_0_0_0, 0))
        self.connect((self.lpf_perseus, 0), (self.blocks_multiply_const_xx_0_0, 0))
        self.connect((self.lpf_sgr, 0), (self.blocks_multiply_const_xx_0_0_0_0, 0))
        self.connect((self.lpf_warm, 0), (self.blocks_multiply_const_xx_0_0_0_0_0, 0))
        self.connect((self.noise_floor, 0), (self.tx_adder, 5))
        self.connect((self.noise_local, 0), (self.lpf_local, 0))
        self.connect((self.noise_outer, 0), (self.lpf_outer, 0))
        self.connect((self.noise_perseus, 0), (self.lpf_perseus, 0))
        self.connect((self.noise_sgr, 0), (self.lpf_sgr, 0))
        self.connect((self.noise_warm, 0), (self.lpf_warm, 0))
        self.connect((self.pluto_rx, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.pluto_rx, 0), (self.qtgui_freq_sink_0, 0))
        self.connect((self.rot_local, 0), (self.tx_adder, 0))
        self.connect((self.rot_outer, 0), (self.tx_adder, 2))
        self.connect((self.rot_perseus, 0), (self.tx_adder, 1))
        self.connect((self.rot_sgr, 0), (self.tx_adder, 3))
        self.connect((self.rot_warm, 0), (self.tx_adder, 4))
        self.connect((self.rot_warm_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.tx_adder, 0), (self.rot_warm_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "topo3_galaxy_rotation")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_tx_atten(self):
        return self.tx_atten

    def set_tx_atten(self, tx_atten):
        self.tx_atten = tx_atten
        self.iio_pluto_sink_0.set_attenuation(0,self.tx_atten)

    def get_sky_offset_hz(self):
        return self.sky_offset_hz

    def set_sky_offset_hz(self, sky_offset_hz):
        self.sky_offset_hz = sky_offset_hz
        self.rot_warm_0.set_phase_inc(((2.0 * 3.141592653589793 * self.sky_offset_hz) / self.samp_rate))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.iio_pluto_sink_0.set_samplerate(self.samp_rate)
        self.lpf_local.set_taps(firdes.low_pass(1, self.samp_rate, 30191, 17775, window.WIN_HAMMING, 6.76))
        self.lpf_outer.set_taps(firdes.low_pass(1, self.samp_rate, 50318, 29625, window.WIN_HAMMING, 6.76))
        self.lpf_perseus.set_taps(firdes.low_pass(1, self.samp_rate, 40254, 23700, window.WIN_HAMMING, 6.76))
        self.lpf_sgr.set_taps(firdes.low_pass(1, self.samp_rate, 36220, 21325, window.WIN_HAMMING, 6.76))
        self.lpf_warm.set_taps(firdes.low_pass(1, self.samp_rate, 80509, 47400, window.WIN_HAMMING, 6.76))
        self.pluto_rx.set_samplerate(self.samp_rate)
        self.qtgui_freq_sink_0.set_frequency_range(self.LO_freq, self.samp_rate)
        self.qtgui_vector_sink_f_0.set_x_axis((-self.samp_rate/2), (self.samp_rate/self.fft_size))
        self.rot_local.set_phase_inc((2.0 * 3.14159265 * 0.0 / self.samp_rate))
        self.rot_outer.set_phase_inc((2.0 * 3.14159265 * 379200.0 / self.samp_rate))
        self.rot_perseus.set_phase_inc((2.0 * 3.14159265 * 189600.0 / self.samp_rate))
        self.rot_sgr.set_phase_inc((2.0 * 3.14159265 * -94800.0 / self.samp_rate))
        self.rot_warm.set_phase_inc((2.0 * 3.14159265 * -23700.0 / self.samp_rate))
        self.rot_warm_0.set_phase_inc(((2.0 * 3.141592653589793 * self.sky_offset_hz) / self.samp_rate))

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.pluto_rx.set_gain(0, self.rx_gain)

    def get_rf_bandwidth(self):
        return self.rf_bandwidth

    def set_rf_bandwidth(self, rf_bandwidth):
        self.rf_bandwidth = rf_bandwidth
        self.iio_pluto_sink_0.set_bandwidth(self.rf_bandwidth)

    def get_integration_time(self):
        return self.integration_time

    def set_integration_time(self, integration_time):
        self.integration_time = integration_time
        self.blocks_multiply_const_vxx_0.set_k((1.0/self.integration_time,) * self.fft_size)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.blocks_multiply_const_vxx_0.set_k((1.0/self.integration_time,) * self.fft_size)
        self.fft_vxx_0.set_window(window.blackmanharris(self.fft_size))
        self.qtgui_vector_sink_f_0.set_x_axis((-self.samp_rate/2), (self.samp_rate/self.fft_size))

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        self.iio_pluto_sink_0.set_frequency(self.LO_freq)
        self.pluto_rx.set_frequency(self.LO_freq)
        self.qtgui_freq_sink_0.set_frequency_range(self.LO_freq, self.samp_rate)




def main(top_block_cls=topo3_galaxy_rotation, options=None):

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
