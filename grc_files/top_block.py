#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Tue Dec  1 21:22:18 2015
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


class top_block(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 11025
        self.baud_rate = baud_rate = 4160

        ##################################################
        # Blocks
        ##################################################
        self.wxgui_scopesink2_0 = scopesink2.scope_sink_f(
        	self.GetWin(),
        	title="APT Image Data",
        	sample_rate=baud_rate,
        	v_scale=0,
        	v_offset=0,
        	t_scale=0.010,
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
        self.low_pass_filter_1 = filter.fir_filter_fff(1, firdes.low_pass(
        	1, samp_rate, 1.1e3, 20, firdes.WIN_BLACKMAN, 6.76))
        self.hilbert_fc_0 = filter.hilbert_fc(65, firdes.WIN_HAMMING, 6.76)
        self.fm_demodulated_source = blocks.wavfile_source("/Users/bjmclaug/source/stem_station/sample_files/N18_4827.wav", False)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_float*1, samp_rate,True)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*1, "/Users/bjmclaug/source/stem_station/raw.dat", False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_abs_xx_0 = blocks.abs_ff(1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_abs_xx_0, 0), (self.low_pass_filter_1, 0))    
        self.connect((self.blocks_complex_to_mag_0, 0), (self.rational_resampler_xxx_0, 0))    
        self.connect((self.blocks_throttle_0, 0), (self.blocks_abs_xx_0, 0))    
        self.connect((self.fm_demodulated_source, 0), (self.blocks_throttle_0, 0))    
        self.connect((self.hilbert_fc_0, 0), (self.blocks_complex_to_mag_0, 0))    
        self.connect((self.low_pass_filter_1, 0), (self.hilbert_fc_0, 0))    
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.rational_resampler_xxx_0, 0), (self.wxgui_scopesink2_0, 0))    


    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.samp_rate, 1.1e3, 20, firdes.WIN_BLACKMAN, 6.76))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.wxgui_scopesink2_0.set_sample_rate(self.baud_rate)


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = top_block()
    tb.Start(True)
    tb.Wait()
