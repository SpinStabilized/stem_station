#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: NOAA APT Satellite Receiver
# Author: Brian McLaughlin
# Generated: Sat Dec 12 17:04:01 2015
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
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import osmosdr
import time
import wx


class apt_rx(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="NOAA APT Satellite Receiver")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.satellite_freq = satellite_freq = 137.62e6
        self.rf_samp_rate = rf_samp_rate = 1.024e6
        self.baud_rate = baud_rate = 4160

        ##################################################
        # Blocks
        ##################################################
        self.top_notebook = self.top_notebook = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
        self.top_notebook.AddPage(grc_wxgui.Panel(self.top_notebook), "Satellite Receive")
        self.top_notebook.AddPage(grc_wxgui.Panel(self.top_notebook), "Baseband")
        self.Add(self.top_notebook)
        self.if_receive_notebook = self.if_receive_notebook = wx.Notebook(self.top_notebook.GetPage(0).GetWin(), style=wx.NB_TOP)
        self.if_receive_notebook.AddPage(grc_wxgui.Panel(self.if_receive_notebook), "FFT")
        self.if_receive_notebook.AddPage(grc_wxgui.Panel(self.if_receive_notebook), "Waterfall")
        self.top_notebook.GetPage(0).Add(self.if_receive_notebook)
        self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
        	self.if_receive_notebook.GetPage(1).GetWin(),
        	baseband_freq=satellite_freq,
        	dynamic_range=100,
        	ref_level=-10,
        	ref_scale=2.0,
        	sample_rate=baud_rate * 24,
        	fft_size=512,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.1333,
        	title="Waterfall Plot",
        	win=window.flattop,
        )
        self.if_receive_notebook.GetPage(1).GridAdd(self.wxgui_waterfallsink2_0.win, 0, 0, 1, 1)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.if_receive_notebook.GetPage(0).GetWin(),
        	baseband_freq=satellite_freq,
        	y_per_div=5,
        	y_divs=10,
        	ref_level=-10,
        	ref_scale=2.0,
        	sample_rate=baud_rate * 24,
        	fft_size=1024,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.1333,
        	title="Intermediate Frequency Receive Spectrum",
        	peak_hold=False,
        )
        self.if_receive_notebook.GetPage(0).GridAdd(self.wxgui_fftsink2_0.win, 0, 0, 1, 1)
        self.rtlsdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.rtlsdr_source_0.set_sample_rate(baud_rate * 24)
        self.rtlsdr_source_0.set_center_freq(satellite_freq, 0)
        self.rtlsdr_source_0.set_freq_corr(9, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(49.6, 0)
        self.rtlsdr_source_0.set_if_gain(0, 0)
        self.rtlsdr_source_0.set_bb_gain(0, 0)
        self.rtlsdr_source_0.set_antenna("", 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
          
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, "/home/brian/stem_station/raw_baud_x_24.bin", False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.baseband_notebook = self.baseband_notebook = wx.Notebook(self.top_notebook.GetPage(1).GetWin(), style=wx.NB_TOP)
        self.baseband_notebook.AddPage(grc_wxgui.Panel(self.baseband_notebook), "Spectrum")
        self.baseband_notebook.AddPage(grc_wxgui.Panel(self.baseband_notebook), "Analog Signal")
        self.top_notebook.GetPage(1).Add(self.baseband_notebook)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.rtlsdr_source_0, 0), (self.wxgui_fftsink2_0, 0))    
        self.connect((self.rtlsdr_source_0, 0), (self.wxgui_waterfallsink2_0, 0))    


    def get_satellite_freq(self):
        return self.satellite_freq

    def set_satellite_freq(self, satellite_freq):
        self.satellite_freq = satellite_freq
        self.rtlsdr_source_0.set_center_freq(self.satellite_freq, 0)
        self.wxgui_fftsink2_0.set_baseband_freq(self.satellite_freq)
        self.wxgui_waterfallsink2_0.set_baseband_freq(self.satellite_freq)

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        self.rf_samp_rate = rf_samp_rate

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.rtlsdr_source_0.set_sample_rate(self.baud_rate * 24)
        self.wxgui_fftsink2_0.set_sample_rate(self.baud_rate * 24)
        self.wxgui_waterfallsink2_0.set_sample_rate(self.baud_rate * 24)


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = apt_rx()
    tb.Start(True)
    tb.Wait()
