#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: Apt Test
# Generated: Mon Nov 30 18:33:01 2015
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

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.wxgui import scopesink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx


class apt_test(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Apt Test")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 11025
        self.baud_rate = baud_rate = 4160
        self.am_carrier = am_carrier = 2400

        ##################################################
        # Blocks
        ##################################################
        self.wxgui_scopesink2_0 = scopesink2.scope_sink_f(
        	self.GetWin(),
        	title="APT Image Data",
        	sample_rate=baud_rate,
        	v_scale=0,
        	v_offset=0,
        	t_scale=0,
        	ac_couple=False,
        	xy_mode=False,
        	num_inputs=1,
        	trig_mode=wxgui.TRIG_MODE_AUTO,
        	y_axis_label="Counts",
        )
        self.Add(self.wxgui_scopesink2_0.win)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=baud_rate,
                decimation=samp_rate,
                taps=None,
                fractional_bw=None,
        )
        self.low_pass_filter_1 = filter.interp_fir_filter_fff(1, firdes.low_pass(
        	1, samp_rate, 1100, 50, firdes.WIN_BLACKMAN, 6.76))
        self.fm_demodulated_source = blocks.wavfile_source("/home/brian/stem_station/sample_files/N18_4827.wav", False)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*1, samp_rate,True)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*1, "/home/brian/apt_rx/foo.bin", False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_abs_xx_0 = blocks.abs_ff(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_abs_xx_0, 0), (self.low_pass_filter_1, 0))    
        self.connect((self.blocks_complex_to_mag_0, 0), (self.rational_resampler_xxx_0, 0))    
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_complex_to_mag_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.blocks_abs_xx_0, 0))    
        self.connect((self.fm_demodulated_source, 0), (self.blocks_throttle_0, 0))    
        self.connect((self.low_pass_filter_1, 0), (self.blocks_float_to_complex_0, 0))    
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.rational_resampler_xxx_0, 0), (self.wxgui_scopesink2_0, 0))    


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.samp_rate, 1100, 50, firdes.WIN_BLACKMAN, 6.76))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.wxgui_scopesink2_0.set_sample_rate(self.baud_rate)

    def get_am_carrier(self):
        return self.am_carrier

    def set_am_carrier(self, am_carrier):
        self.am_carrier = am_carrier


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = apt_test()
    tb.Start(True)
    tb.Wait()
