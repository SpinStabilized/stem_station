#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: NOAA APT Satellite Receiver
# Author: Brian McLaughlin
# Generated: Mon Feb 29 06:26:59 2016
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
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import math
import osmosdr
import rigcontrol
import sip
import time


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
        self.satellite_frequency = satellite_frequency = 0
        self.variable_qtgui_label_0 = variable_qtgui_label_0 = '{:.6f} MHz'.format(satellite_frequency/1e6)
        self.signal_gain = signal_gain = 1
        self.rf_samp_rate = rf_samp_rate = 256e3
        self.rail_level = rail_level = 0.5
        self.fsk_deviation_hz = fsk_deviation_hz = 17000
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
        self._signal_gain_range = Range(1, 10, 0.1, 1, 200)
        self._signal_gain_win = RangeWidget(self._signal_gain_range, self.set_signal_gain, "Signal Gain", "counter", float)
        self.top_grid_layout.addWidget(self._signal_gain_win, 0, 1)
        self._variable_qtgui_label_0_tool_bar = Qt.QToolBar(self)
        
        if None:
          self._variable_qtgui_label_0_formatter = None
        else:
          self._variable_qtgui_label_0_formatter = lambda x: x
        
        self._variable_qtgui_label_0_tool_bar.addWidget(Qt.QLabel("Satellite Frequency"+": "))
        self._variable_qtgui_label_0_label = Qt.QLabel(str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0)))
        self._variable_qtgui_label_0_tool_bar.addWidget(self._variable_qtgui_label_0_label)
        self.top_grid_layout.addWidget(self._variable_qtgui_label_0_tool_bar, 0, 0)
          
        self.rtlsdr_source_1 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.rtlsdr_source_1.set_sample_rate(rf_samp_rate)
        self.rtlsdr_source_1.set_center_freq(satellite_frequency, 0)
        self.rtlsdr_source_1.set_freq_corr(9, 0)
        self.rtlsdr_source_1.set_dc_offset_mode(2, 0)
        self.rtlsdr_source_1.set_iq_balance_mode(2, 0)
        self.rtlsdr_source_1.set_gain_mode(False, 0)
        self.rtlsdr_source_1.set_gain(49.6, 0)
        self.rtlsdr_source_1.set_if_gain(20, 0)
        self.rtlsdr_source_1.set_bb_gain(20, 0)
        self.rtlsdr_source_1.set_antenna("", 0)
        self.rtlsdr_source_1.set_bandwidth(0, 0)
          
        self.rigcontrol_rigcontrol_0 = rigcontrol.rigcontrol(
            self.set_satellite_frequency if "satellite_frequency" in locals() else None,
            self.get_satellite_frequency if "satellite_frequency" in locals() else None,
            False)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	rf_samp_rate // 2, #bw
        	"", #name
                1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.50)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        
        if not False:
          self.qtgui_waterfall_sink_x_0.disable_legend()
        
        if complex == type(float()):
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
        	rf_samp_rate // 2, #samp_rate
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
        self.qtgui_freq_sink_x_1_0 = qtgui.freq_sink_c(
        	1024, #size
        	firdes.WIN_BLACKMAN_hARRIS, #wintype
        	0, #fc
        	16.64e3, #bw
        	"", #name
        	1 #number of inputs
        )
        self.qtgui_freq_sink_x_1_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_1_0.set_y_axis(-100, 0)
        self.qtgui_freq_sink_x_1_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_1_0.enable_grid(False)
        self.qtgui_freq_sink_x_1_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_1_0.enable_control_panel(False)
        
        if not True:
          self.qtgui_freq_sink_x_1_0.disable_legend()
        
        if complex == type(float()):
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
        	0, #fc
        	rf_samp_rate // 2, #bw
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
        
        if complex == type(float()):
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
        	4, rf_samp_rate // 2, 30e3, 5e3, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(2, firdes.low_pass(
        	1, rf_samp_rate, 40e3, 40e3, firdes.WIN_HAMMING, 6.76))
        self.blocks_socket_pdu_0 = blocks.socket_pdu("TCP_SERVER", "", "4532", 10000, False)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, "/home/brian/stem_station/noaa18_s_rf.bin", False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_file_meta_sink_0 = blocks.file_meta_sink(gr.sizeof_float*1, "/home/brian/stem_station/noaa18_s.dat", baud_rate, 1, blocks.GR_FILE_FLOAT, False, baud_rate * (60 * 20), "", True)
        self.blocks_file_meta_sink_0.set_unbuffered(False)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.apt_am_demod_0 = apt_am_demod(
            parameter_apt_gain=signal_gain,
            parameter_samp_rate=rf_samp_rate / 2,
        )
        self.analog_rail_ff_0_0 = analog.rail_ff(-rail_level, rail_level)
        self.analog_rail_ff_0 = analog.rail_ff(-rail_level, rail_level)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((rf_samp_rate // 2)/(2*math.pi*fsk_deviation_hz/8.0))
        self.analog_agc3_xx_0 = analog.agc3_cc(0.25, 0.5, 0.9, 1.0, 1)
        self.analog_agc3_xx_0.set_max_gain(1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0, 'pdus'), (self.rigcontrol_rigcontrol_0, 'in'))    
        self.msg_connect((self.rigcontrol_rigcontrol_0, 'out'), (self.blocks_socket_pdu_0, 'pdus'))    
        self.connect((self.analog_agc3_xx_0, 0), (self.blocks_complex_to_float_0, 0))    
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.apt_am_demod_0, 0))    
        self.connect((self.analog_rail_ff_0, 0), (self.blocks_float_to_complex_0, 0))    
        self.connect((self.analog_rail_ff_0_0, 0), (self.blocks_float_to_complex_0, 1))    
        self.connect((self.apt_am_demod_0, 0), (self.blocks_file_meta_sink_0, 0))    
        self.connect((self.apt_am_demod_0, 1), (self.qtgui_freq_sink_x_1_0, 0))    
        self.connect((self.apt_am_demod_0, 0), (self.qtgui_time_sink_x_0_0, 0))    
        self.connect((self.blocks_complex_to_float_0, 0), (self.analog_rail_ff_0, 0))    
        self.connect((self.blocks_complex_to_float_0, 1), (self.analog_rail_ff_0_0, 0))    
        self.connect((self.blocks_float_to_complex_0, 0), (self.low_pass_filter_0_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.analog_agc3_xx_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_freq_sink_x_1, 0))    
        self.connect((self.low_pass_filter_0_0, 0), (self.analog_quadrature_demod_cf_0, 0))    
        self.connect((self.low_pass_filter_0_0, 0), (self.qtgui_freq_sink_x_1, 1))    
        self.connect((self.low_pass_filter_0_0, 0), (self.qtgui_time_sink_x_0, 0))    
        self.connect((self.low_pass_filter_0_0, 0), (self.qtgui_waterfall_sink_x_0, 0))    
        self.connect((self.rtlsdr_source_1, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.rtlsdr_source_1, 0), (self.low_pass_filter_0, 0))    

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "apt_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_satellite_frequency(self):
        return self.satellite_frequency

    def set_satellite_frequency(self, satellite_frequency):
        with self._lock:
            self.satellite_frequency = satellite_frequency
            self.set_variable_qtgui_label_0(self._variable_qtgui_label_0_formatter('{:.6f} MHz'.format(self.satellite_frequency/1e6)))
            self.rtlsdr_source_1.set_center_freq(self.satellite_frequency, 0)

    def get_variable_qtgui_label_0(self):
        return self.variable_qtgui_label_0

    def set_variable_qtgui_label_0(self, variable_qtgui_label_0):
        with self._lock:
            self.variable_qtgui_label_0 = variable_qtgui_label_0
            Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_0_label, "setText", Qt.Q_ARG("QString", str(self.variable_qtgui_label_0)))

    def get_signal_gain(self):
        return self.signal_gain

    def set_signal_gain(self, signal_gain):
        with self._lock:
            self.signal_gain = signal_gain
            self.apt_am_demod_0.set_parameter_apt_gain(self.signal_gain)

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        with self._lock:
            self.rf_samp_rate = rf_samp_rate
            self.analog_quadrature_demod_cf_0.set_gain((self.rf_samp_rate // 2)/(2*math.pi*self.fsk_deviation_hz/8.0))
            self.apt_am_demod_0.set_parameter_samp_rate(self.rf_samp_rate / 2)
            self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.rf_samp_rate, 40e3, 40e3, firdes.WIN_HAMMING, 6.76))
            self.low_pass_filter_0_0.set_taps(firdes.low_pass(4, self.rf_samp_rate // 2, 30e3, 5e3, firdes.WIN_HAMMING, 6.76))
            self.qtgui_freq_sink_x_1.set_frequency_range(0, self.rf_samp_rate // 2)
            self.qtgui_time_sink_x_0.set_samp_rate(self.rf_samp_rate // 2)
            self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.rf_samp_rate // 2)
            self.rtlsdr_source_1.set_sample_rate(self.rf_samp_rate)

    def get_rail_level(self):
        return self.rail_level

    def set_rail_level(self, rail_level):
        with self._lock:
            self.rail_level = rail_level
            self.analog_rail_ff_0.set_lo(-self.rail_level)
            self.analog_rail_ff_0.set_hi(self.rail_level)
            self.analog_rail_ff_0_0.set_lo(-self.rail_level)
            self.analog_rail_ff_0_0.set_hi(self.rail_level)

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        with self._lock:
            self.fsk_deviation_hz = fsk_deviation_hz
            self.analog_quadrature_demod_cf_0.set_gain((self.rf_samp_rate // 2)/(2*math.pi*self.fsk_deviation_hz/8.0))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        with self._lock:
            self.baud_rate = baud_rate
            self.qtgui_time_sink_x_0_0.set_samp_rate(self.baud_rate)


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui','style','raster'))
    qapp = Qt.QApplication(sys.argv)
    tb = apt_rx()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None  # to clean up Qt widgets
