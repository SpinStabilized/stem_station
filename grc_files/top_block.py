#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Thu Feb 11 20:17:05 2016
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import gr, blocks
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import sip
import sys


class top_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
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

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Variables
        ##################################################
        self.factor_of_baud = factor_of_baud = 8
        self.baud_rate = baud_rate = 4160
        self.samp_rate = samp_rate = 11025
        self.demod_rate = demod_rate = baud_rate * factor_of_baud

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_1 = filter.rational_resampler_fff(
                interpolation=demod_rate,
                decimation=samp_rate,
                taps=None,
                fractional_bw=None,
        )
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
        	baud_rate / 2, #size
        	baud_rate, #samp_rate
        	'APT Full Line', #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-0.5, 1.5)
        
        self.qtgui_time_sink_x_0.set_y_label("Amplitude", "")
        
        self.qtgui_time_sink_x_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0.01, 0, 'SyncA')
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        
        if not False:
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
        
        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])
        
        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_time_raster_sink_x_0 = qtgui.time_raster_sink_f(
        	baud_rate,
        	128,
        	int(baud_rate / 2),
        	([]),
        	([]),
        	"",
        	1,
        	)
        
        self.qtgui_time_raster_sink_x_0.set_update_time(0.5)
        self.qtgui_time_raster_sink_x_0.set_intensity_range(-0.5, 1)
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
        self.top_layout.addWidget(self._qtgui_time_raster_sink_x_0_win)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_fcf(1, (firdes.low_pass(1, demod_rate, demod_rate / 2, demod_rate / 4)), 2400, demod_rate)
        self.fm_demodulated_source = blocks.wavfile_source("/Users/bjmclaug/source/stem_station/sample_files/N18_4827.wav", False)
        self.digital_correlate_access_code_tag_bb_0_0 = digital.correlate_access_code_tag_bb('00' + ('0011' * 7) + ('0' * 10), 0, "SyncA")
        self.blocks_uchar_to_float_0_0 = blocks.uchar_to_float()
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*1, samp_rate,True)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(-0.1, 0.1, 0)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_rms_xx_0 = blocks.rms_ff(0.0001)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vff((0, ))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((5, ))
        self.blocks_float_to_uchar_0 = blocks.float_to_uchar()
        self.blocks_file_meta_sink_0 = blocks.file_meta_sink(gr.sizeof_float*1, "/Users/bjmclaug/source/stem_station/raw_meta.dat", baud_rate, 1, blocks.GR_FILE_FLOAT, False, baud_rate * (60 * 20), "", True)
        self.blocks_file_meta_sink_0.set_unbuffered(False)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.analog_am_demod_cf_0 = analog.am_demod_cf(
        	channel_rate=demod_rate,
        	audio_decim=factor_of_baud,
        	audio_pass=1080,
        	audio_stop=1500,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_am_demod_cf_0, 0), (self.blocks_add_xx_0, 0))    
        self.connect((self.analog_am_demod_cf_0, 0), (self.blocks_rms_xx_0, 0))    
        self.connect((self.analog_am_demod_cf_0, 0), (self.blocks_sub_xx_0, 0))    
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_file_meta_sink_0, 0))    
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_time_raster_sink_x_0, 0))    
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_time_sink_x_0, 0))    
        self.connect((self.blocks_float_to_uchar_0, 0), (self.digital_correlate_access_code_tag_bb_0_0, 0))    
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.analog_am_demod_cf_0, 0))    
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 1))    
        self.connect((self.blocks_rms_xx_0, 0), (self.blocks_sub_xx_0, 1))    
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_threshold_ff_0, 0))    
        self.connect((self.blocks_threshold_ff_0, 0), (self.blocks_float_to_uchar_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.rational_resampler_xxx_1, 0))    
        self.connect((self.blocks_uchar_to_float_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))    
        self.connect((self.digital_correlate_access_code_tag_bb_0_0, 0), (self.blocks_uchar_to_float_0_0, 0))    
        self.connect((self.fm_demodulated_source, 0), (self.blocks_throttle_0, 0))    
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_multiply_const_vxx_0, 0))    
        self.connect((self.rational_resampler_xxx_1, 0), (self.freq_xlating_fir_filter_xxx_0, 0))    

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_factor_of_baud(self):
        return self.factor_of_baud

    def set_factor_of_baud(self, factor_of_baud):
        self.factor_of_baud = factor_of_baud
        self.set_demod_rate(self.baud_rate * self.factor_of_baud)

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.set_demod_rate(self.baud_rate * self.factor_of_baud)
        self.qtgui_time_raster_sink_x_0.set_num_cols(int(self.baud_rate / 2))
        self.qtgui_time_sink_x_0.set_samp_rate(self.baud_rate)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_demod_rate(self):
        return self.demod_rate

    def set_demod_rate(self, demod_rate):
        self.demod_rate = demod_rate
        self.freq_xlating_fir_filter_xxx_0.set_taps((firdes.low_pass(1, self.demod_rate, self.demod_rate / 2, self.demod_rate / 4)))


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        Qt.QApplication.setGraphicsSystem(gr.prefs().get_string('qtgui','style','raster'))
    qapp = Qt.QApplication(sys.argv)
    tb = top_block()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()
    tb = None  # to clean up Qt widgets