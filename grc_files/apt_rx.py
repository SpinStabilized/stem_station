#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: NOAA APT Satellite Receiver
# Author: Brian McLaughlin
# Generated: Thu Mar 31 13:26:49 2016
##################################################
import threading

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt4 import Qt
from PyQt4.QtCore import QObject, pyqtSlot
from apt_am_demod import apt_am_demod  # grc-generated hier_block
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import gr, blocks
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import math
import sip


class apt_rx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "NOAA APT Satellite Receiver")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("NOAA APT Satellite Receiver")
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
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

        self.settings = Qt.QSettings("GNU Radio", "apt_rx")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        self._lock = threading.RLock()

        ##################################################
        # Variables
        ##################################################
        self.satellite_select = satellite_select = 137.62
        self.valid_gains = valid_gains = [0.0, 0.9, 1.4, 2.7, 3.7, 7.7, 8.7, 12.5, 14.4, 15.7, 16.6, 19.7, 20.7, 22.9, 25.4, 28.0, 29.7, 32.8, 33.8, 36.4, 37.2, 38.6, 40.2, 42.1, 43.4, 43.9, 44.5, 48.0, 49.6]
        self.satellite_frequency = satellite_frequency = satellite_select * 1e6
        self.rf_samp_rate = rf_samp_rate = 2.048e6
        self.max_doppler = max_doppler = 3000
        self.fsk_deviation_hz = fsk_deviation_hz = 17000
        self.am_carrier = am_carrier = 2400
        self.tuner_frequency = tuner_frequency = satellite_frequency - (rf_samp_rate / 4)
        self.rf_gain = rf_gain = valid_gains[-1]
        self.rail_level = rail_level = 0.5
        self.processing_rate = processing_rate = 256000
        self.fm_bandwidth = fm_bandwidth = (2 * (fsk_deviation_hz + am_carrier)) + max_doppler
        self.baud_rate = baud_rate = 4160

        ##################################################
        # Blocks
        ##################################################
        self.tabs_top = Qt.QTabWidget()
        self.tabs_top_widget_0 = Qt.QWidget()
        self.tabs_top_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_top_widget_0)
        self.tabs_top_grid_layout_0 = Qt.QGridLayout()
        self.tabs_top_layout_0.addLayout(self.tabs_top_grid_layout_0)
        self.tabs_top.addTab(self.tabs_top_widget_0, "RF Recieve")
        self.tabs_top_widget_1 = Qt.QWidget()
        self.tabs_top_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_top_widget_1)
        self.tabs_top_grid_layout_1 = Qt.QGridLayout()
        self.tabs_top_layout_1.addLayout(self.tabs_top_grid_layout_1)
        self.tabs_top.addTab(self.tabs_top_widget_1, "APT Signal")
        self.tabs_top_widget_2 = Qt.QWidget()
        self.tabs_top_layout_2 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_top_widget_2)
        self.tabs_top_grid_layout_2 = Qt.QGridLayout()
        self.tabs_top_layout_2.addLayout(self.tabs_top_grid_layout_2)
        self.tabs_top.addTab(self.tabs_top_widget_2, "APT Baseband")
        self.top_grid_layout.addWidget(self.tabs_top, 2, 0, 1, 4)
        self.tabs_rf = Qt.QTabWidget()
        self.tabs_rf_widget_0 = Qt.QWidget()
        self.tabs_rf_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_rf_widget_0)
        self.tabs_rf_grid_layout_0 = Qt.QGridLayout()
        self.tabs_rf_layout_0.addLayout(self.tabs_rf_grid_layout_0)
        self.tabs_rf.addTab(self.tabs_rf_widget_0, "Spectrum")
        self.tabs_rf_widget_1 = Qt.QWidget()
        self.tabs_rf_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_rf_widget_1)
        self.tabs_rf_grid_layout_1 = Qt.QGridLayout()
        self.tabs_rf_layout_1.addLayout(self.tabs_rf_grid_layout_1)
        self.tabs_rf.addTab(self.tabs_rf_widget_1, "Waterfall")
        self.tabs_rf_widget_2 = Qt.QWidget()
        self.tabs_rf_layout_2 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_rf_widget_2)
        self.tabs_rf_grid_layout_2 = Qt.QGridLayout()
        self.tabs_rf_layout_2.addLayout(self.tabs_rf_grid_layout_2)
        self.tabs_rf.addTab(self.tabs_rf_widget_2, "Scope")
        self.tabs_top_layout_0.addWidget(self.tabs_rf)
        self.tabs_apt_data = Qt.QTabWidget()
        self.tabs_apt_data_widget_0 = Qt.QWidget()
        self.tabs_apt_data_layout_0 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_apt_data_widget_0)
        self.tabs_apt_data_grid_layout_0 = Qt.QGridLayout()
        self.tabs_apt_data_layout_0.addLayout(self.tabs_apt_data_grid_layout_0)
        self.tabs_apt_data.addTab(self.tabs_apt_data_widget_0, "Scope")
        self.tabs_apt_data_widget_1 = Qt.QWidget()
        self.tabs_apt_data_layout_1 = Qt.QBoxLayout(Qt.QBoxLayout.TopToBottom, self.tabs_apt_data_widget_1)
        self.tabs_apt_data_grid_layout_1 = Qt.QGridLayout()
        self.tabs_apt_data_layout_1.addLayout(self.tabs_apt_data_grid_layout_1)
        self.tabs_apt_data.addTab(self.tabs_apt_data_widget_1, "Raster")
        self.tabs_top_layout_1.addWidget(self.tabs_apt_data)
        self._satellite_select_options = [137.62, 137.9125, 137.1]
        self._satellite_select_labels = ['NOAA 15 (137.62 MHz)', 'NOAA 18 (137.9125 MHz)', 'NOAA 19 (137.1 MHz)']
        self._satellite_select_tool_bar = Qt.QToolBar(self)
        self._satellite_select_tool_bar.addWidget(Qt.QLabel("Satellite Select"+": "))
        self._satellite_select_combo_box = Qt.QComboBox()
        self._satellite_select_tool_bar.addWidget(self._satellite_select_combo_box)
        for label in self._satellite_select_labels: self._satellite_select_combo_box.addItem(label)
        self._satellite_select_callback = lambda i: Qt.QMetaObject.invokeMethod(self._satellite_select_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._satellite_select_options.index(i)))
        self._satellite_select_callback(self.satellite_select)
        self._satellite_select_combo_box.currentIndexChanged.connect(
        	lambda i: self.set_satellite_select(self._satellite_select_options[i]))
        self.top_grid_layout.addWidget(self._satellite_select_tool_bar, 0, 0, 1, 1)
        self._rf_gain_options = valid_gains
        self._rf_gain_labels = map(str, self._rf_gain_options)
        self._rf_gain_tool_bar = Qt.QToolBar(self)
        self._rf_gain_tool_bar.addWidget(Qt.QLabel("RF Gain"+": "))
        self._rf_gain_combo_box = Qt.QComboBox()
        self._rf_gain_tool_bar.addWidget(self._rf_gain_combo_box)
        for label in self._rf_gain_labels: self._rf_gain_combo_box.addItem(label)
        self._rf_gain_callback = lambda i: Qt.QMetaObject.invokeMethod(self._rf_gain_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._rf_gain_options.index(i)))
        self._rf_gain_callback(self.rf_gain)
        self._rf_gain_combo_box.currentIndexChanged.connect(
        	lambda i: self.set_rf_gain(self._rf_gain_options[i]))
        self.top_grid_layout.addWidget(self._rf_gain_tool_bar, 0, 1 , 1, 1)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	satellite_frequency, #fc
        	processing_rate // 2, #bw
        	"", #name
                1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.50)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        
        if not False:
          self.qtgui_waterfall_sink_x_0.disable_legend()
        
        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_waterfall_sink_x_0.set_plot_pos_half(not True)
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])
        
        self.qtgui_waterfall_sink_x_0.set_intensity_range(-40, 0)
        
        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tabs_rf_layout_1.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
        	baud_rate / 2, #size
        	baud_rate, #samp_rate
        	'APT Full Line', #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-0.5, 1.5)
        
        self.qtgui_time_sink_x_0_0.set_y_label("Amplitude", "")
        
        self.qtgui_time_sink_x_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0.01, 0, 'SyncA')
        self.qtgui_time_sink_x_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0.enable_control_panel(False)
        
        if not False:
          self.qtgui_time_sink_x_0_0.disable_legend()
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.pyqwidget(), Qt.QWidget)
        self.tabs_apt_data_layout_0.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
        	1024, #size
        	processing_rate // 2, #samp_rate
        	"", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)
        
        self.qtgui_time_sink_x_0.set_y_label("Amplitude", "")
        
        self.qtgui_time_sink_x_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        
        if not True:
          self.qtgui_time_sink_x_0.disable_legend()
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        
        for i in xrange(2*1):
            if len(labels[i]) == 0:
                if(i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tabs_rf_layout_2.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_time_raster_sink_x_0 = qtgui.time_raster_sink_f(
        	baud_rate,
        	120*3,
        	baud_rate // 2,
        	([]),
        	([]),
        	"",
        	1,
        	)
        
        self.qtgui_time_raster_sink_x_0.set_update_time(0.10)
        self.qtgui_time_raster_sink_x_0.set_intensity_range(-0.5, 1.5)
        self.qtgui_time_raster_sink_x_0.enable_grid(False)
        
        labels = ["", "", "", "", "",
                  "", "", "", "", ""]
        colors = [1, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_raster_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_raster_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_raster_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_time_raster_sink_x_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_time_raster_sink_x_0_win = sip.wrapinstance(self.qtgui_time_raster_sink_x_0.pyqwidget(), Qt.QWidget)
        self.tabs_apt_data_layout_1.addWidget(self._qtgui_time_raster_sink_x_0_win)
        self.qtgui_freq_sink_x_1_0 = qtgui.freq_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	16.64e3, #bw
        	"", #name
        	1 #number of inputs
        )
        self.qtgui_freq_sink_x_1_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_1_0.set_y_axis(-40, 0)
        self.qtgui_freq_sink_x_1_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_1_0.enable_grid(False)
        self.qtgui_freq_sink_x_1_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_1_0.enable_control_panel(False)
        
        if not True:
          self.qtgui_freq_sink_x_1_0.disable_legend()
        
        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_freq_sink_x_1_0.set_plot_pos_half(not True)
        
        labels = ["Raw", "AGC Output", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_freq_sink_x_1_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_1_0.pyqwidget(), Qt.QWidget)
        self.tabs_top_layout_2.addWidget(self._qtgui_freq_sink_x_1_0_win)
        self.qtgui_freq_sink_x_1 = qtgui.freq_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	satellite_frequency, #fc
        	processing_rate // 2, #bw
        	"", #name
        	2 #number of inputs
        )
        self.qtgui_freq_sink_x_1.set_update_time(0.10)
        self.qtgui_freq_sink_x_1.set_y_axis(-100, 0)
        self.qtgui_freq_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_1.enable_grid(False)
        self.qtgui_freq_sink_x_1.set_fft_average(0.2)
        self.qtgui_freq_sink_x_1.enable_control_panel(False)
        
        if not True:
          self.qtgui_freq_sink_x_1.disable_legend()
        
        if "complex" == "float" or "complex" == "msg_float":
          self.qtgui_freq_sink_x_1.set_plot_pos_half(not True)
        
        labels = ["Raw", "AGC Output", "", "", "",
                  "", "", "", "", ""]
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        for i in xrange(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1.set_line_alpha(i, alphas[i])
        
        self._qtgui_freq_sink_x_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_1.pyqwidget(), Qt.QWidget)
        self.tabs_rf_layout_0.addWidget(self._qtgui_freq_sink_x_1_win)
        self.low_pass_filter_0_0 = filter.fir_filter_ccf(1, firdes.low_pass(
        	1, processing_rate // 2, fm_bandwidth + 1e3, 1e3, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(2, firdes.low_pass(
        	1, processing_rate, 60e3, 15e3, firdes.WIN_HAMMING, 6.76))
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, processing_rate,True)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, "/Users/bjmclaug/Downloads/noaa-12_256k.dat", False)
        self.blocks_file_meta_sink_0 = blocks.file_meta_sink(gr.sizeof_float*1, "/Users/bjmclaug/source/stem_station/noaa12_sample.dat", baud_rate, 1, blocks.GR_FILE_FLOAT, False, baud_rate * (60 * 20), "", True)
        self.blocks_file_meta_sink_0.set_unbuffered(False)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.apt_am_demod_0 = apt_am_demod(
            parameter_apt_gain=1,
            parameter_samp_rate=processing_rate / 2,
        )
        self.analog_rail_ff_0_0 = analog.rail_ff(-rail_level, rail_level)
        self.analog_rail_ff_0 = analog.rail_ff(-rail_level, rail_level)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((processing_rate // 2)/(2*math.pi*fsk_deviation_hz/8.0))
        self.analog_agc3_xx_0 = analog.agc3_cc(0.25, 0.5, 0.9, 1.0, 1)
        self.analog_agc3_xx_0.set_max_gain(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc3_xx_0, 0), (self.blocks_complex_to_float_0, 0))    
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.apt_am_demod_0, 0))    
        self.connect((self.analog_rail_ff_0, 0), (self.blocks_float_to_complex_0, 0))    
        self.connect((self.analog_rail_ff_0_0, 0), (self.blocks_float_to_complex_0, 1))    
        self.connect((self.apt_am_demod_0, 0), (self.blocks_file_meta_sink_0, 0))    
        self.connect((self.apt_am_demod_0, 0), (self.qtgui_time_raster_sink_x_0, 0))    
        self.connect((self.apt_am_demod_0, 0), (self.qtgui_time_sink_x_0_0, 0))    
        self.connect((self.blocks_complex_to_float_0, 0), (self.analog_rail_ff_0, 0))    
        self.connect((self.blocks_complex_to_float_0, 1), (self.analog_rail_ff_0_0, 0))    
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle_0, 0))    
        self.connect((self.blocks_float_to_complex_0, 0), (self.low_pass_filter_0_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.low_pass_filter_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.analog_agc3_xx_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_freq_sink_x_1, 0))    
        self.connect((self.low_pass_filter_0_0, 0), (self.analog_quadrature_demod_cf_0, 0))    
        self.connect((self.low_pass_filter_0_0, 0), (self.qtgui_freq_sink_x_1, 1))    
        self.connect((self.low_pass_filter_0_0, 0), (self.qtgui_time_sink_x_0, 0))    
        self.connect((self.low_pass_filter_0_0, 0), (self.qtgui_waterfall_sink_x_0, 0))    

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "apt_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()


    def get_satellite_select(self):
        return self.satellite_select

    def set_satellite_select(self, satellite_select):
        with self._lock:
            self.satellite_select = satellite_select
            self.set_satellite_frequency(self.satellite_select * 1e6)
            self._satellite_select_callback(self.satellite_select)

    def get_valid_gains(self):
        return self.valid_gains

    def set_valid_gains(self, valid_gains):
        with self._lock:
            self.valid_gains = valid_gains
            self.set_rf_gain(self.valid_gains[-1])

    def get_satellite_frequency(self):
        return self.satellite_frequency

    def set_satellite_frequency(self, satellite_frequency):
        with self._lock:
            self.satellite_frequency = satellite_frequency
            self.set_tuner_frequency(self.satellite_frequency - (self.rf_samp_rate / 4))
            self.qtgui_freq_sink_x_1.set_frequency_range(self.satellite_frequency, self.processing_rate // 2)
            self.qtgui_waterfall_sink_x_0.set_frequency_range(self.satellite_frequency, self.processing_rate // 2)

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        with self._lock:
            self.rf_samp_rate = rf_samp_rate
            self.set_tuner_frequency(self.satellite_frequency - (self.rf_samp_rate / 4))

    def get_max_doppler(self):
        return self.max_doppler

    def set_max_doppler(self, max_doppler):
        with self._lock:
            self.max_doppler = max_doppler
            self.set_fm_bandwidth((2 * (self.fsk_deviation_hz + self.am_carrier)) + self.max_doppler)

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        with self._lock:
            self.fsk_deviation_hz = fsk_deviation_hz
            self.set_fm_bandwidth((2 * (self.fsk_deviation_hz + self.am_carrier)) + self.max_doppler)
            self.analog_quadrature_demod_cf_0.set_gain((self.processing_rate // 2)/(2*math.pi*self.fsk_deviation_hz/8.0))

    def get_am_carrier(self):
        return self.am_carrier

    def set_am_carrier(self, am_carrier):
        with self._lock:
            self.am_carrier = am_carrier
            self.set_fm_bandwidth((2 * (self.fsk_deviation_hz + self.am_carrier)) + self.max_doppler)

    def get_tuner_frequency(self):
        return self.tuner_frequency

    def set_tuner_frequency(self, tuner_frequency):
        with self._lock:
            self.tuner_frequency = tuner_frequency

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        with self._lock:
            self.rf_gain = rf_gain
            self._rf_gain_callback(self.rf_gain)

    def get_rail_level(self):
        return self.rail_level

    def set_rail_level(self, rail_level):
        with self._lock:
            self.rail_level = rail_level
            self.analog_rail_ff_0.set_lo(-self.rail_level)
            self.analog_rail_ff_0.set_hi(self.rail_level)
            self.analog_rail_ff_0_0.set_lo(-self.rail_level)
            self.analog_rail_ff_0_0.set_hi(self.rail_level)

    def get_processing_rate(self):
        return self.processing_rate

    def set_processing_rate(self, processing_rate):
        with self._lock:
            self.processing_rate = processing_rate
            self.analog_quadrature_demod_cf_0.set_gain((self.processing_rate // 2)/(2*math.pi*self.fsk_deviation_hz/8.0))
            self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.processing_rate, 60e3, 15e3, firdes.WIN_HAMMING, 6.76))
            self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.processing_rate // 2, self.fm_bandwidth + 1e3, 1e3, firdes.WIN_HAMMING, 6.76))
            self.qtgui_freq_sink_x_1.set_frequency_range(self.satellite_frequency, self.processing_rate // 2)
            self.qtgui_time_sink_x_0.set_samp_rate(self.processing_rate // 2)
            self.qtgui_waterfall_sink_x_0.set_frequency_range(self.satellite_frequency, self.processing_rate // 2)
            self.apt_am_demod_0.set_parameter_samp_rate(self.processing_rate / 2)
            self.blocks_throttle_0.set_sample_rate(self.processing_rate)

    def get_fm_bandwidth(self):
        return self.fm_bandwidth

    def set_fm_bandwidth(self, fm_bandwidth):
        with self._lock:
            self.fm_bandwidth = fm_bandwidth
            self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.processing_rate // 2, self.fm_bandwidth + 1e3, 1e3, firdes.WIN_HAMMING, 6.76))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        with self._lock:
            self.baud_rate = baud_rate
            self.qtgui_time_sink_x_0_0.set_samp_rate(self.baud_rate)
            self.qtgui_time_raster_sink_x_0.set_num_cols(self.baud_rate // 2)


def main(top_block_cls=apt_rx, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
