#!/usr/bin/env python2
##################################################
# GNU Radio Python Flow Graph
# Title: NOAA APT Satellite Receiver
# Author: Brian McLaughlin
# Generated: Sun Nov 29 11:32:07 2015
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

from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import scopesink2
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
        self.satellite_select = satellite_select = 137.62
        self.satellite_frequency = satellite_frequency = int(satellite_select * 1e6)
        self.rf_samp_rate = rf_samp_rate = 128e3
        self.if_samp_rate = if_samp_rate = 128e3
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
        self.baseband_notebook = self.baseband_notebook = wx.Notebook(self.top_notebook.GetPage(1).GetWin(), style=wx.NB_TOP)
        self.baseband_notebook.AddPage(grc_wxgui.Panel(self.baseband_notebook), "Spectrum")
        self.baseband_notebook.AddPage(grc_wxgui.Panel(self.baseband_notebook), "Analog Signal")
        self.top_notebook.GetPage(1).Add(self.baseband_notebook)
        self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
        	self.if_receive_notebook.GetPage(1).GetWin(),
        	baseband_freq=0,
        	dynamic_range=100,
        	ref_level=-10,
        	ref_scale=2.0,
        	sample_rate=if_samp_rate,
        	fft_size=512,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.1333,
        	title="Waterfall Plot",
        	win=window.flattop,
        )
        self.if_receive_notebook.GetPage(1).GridAdd(self.wxgui_waterfallsink2_0.win, 0, 0, 1, 1)
        self.wxgui_scopesink2_0 = scopesink2.scope_sink_f(
        	self.baseband_notebook.GetPage(1).GetWin(),
        	title="Scope Plot",
        	sample_rate=11.025e3,
        	v_scale=0,
        	v_offset=0,
        	t_scale=0.010,
        	ac_couple=False,
        	xy_mode=False,
        	num_inputs=1,
        	trig_mode=wxgui.TRIG_MODE_AUTO,
        	y_axis_label="Counts",
        )
        self.baseband_notebook.GetPage(1).Add(self.wxgui_scopesink2_0.win)
        self.wxgui_fftsink2_1 = fftsink2.fft_sink_f(
        	self.baseband_notebook.GetPage(0).GetWin(),
        	baseband_freq=0,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=11.025e3,
        	fft_size=1024,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.1333,
        	title="FFT Plot",
        	peak_hold=False,
        )
        self.baseband_notebook.GetPage(0).Add(self.wxgui_fftsink2_1.win)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.if_receive_notebook.GetPage(0).GetWin(),
        	baseband_freq=0,
        	y_per_div=5,
        	y_divs=10,
        	ref_level=-10,
        	ref_scale=2.0,
        	sample_rate=if_samp_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.1333,
        	title="Intermediate Frequency Receive Spectrum",
        	peak_hold=False,
        )
        self.if_receive_notebook.GetPage(0).GridAdd(self.wxgui_fftsink2_0.win, 0, 0, 1, 1)
        self._satellite_select_chooser = forms.drop_down(
        	parent=self.GetWin(),
        	value=self.satellite_select,
        	callback=self.set_satellite_select,
        	label="Satellite Select",
        	choices=[137.6200, 137.9125, 137.1000],
        	labels=['NOAA-15', 'NOAA-18', 'NOAA-19'],
        )
        self.GridAdd(self._satellite_select_chooser, 0, 0, 1, 1)
        self.rtlsdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.rtlsdr_source_0.set_sample_rate(rf_samp_rate)
        self.rtlsdr_source_0.set_center_freq(satellite_frequency, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(49.6, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna("", 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
          
        self.rational_resampler_xxx_0_0 = filter.rational_resampler_fff(
                interpolation=int(16e3),
                decimation=int(rf_samp_rate),
                taps=None,
                fractional_bw=None,
        )
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=baud_rate,
                decimation=int(16e3),
                taps=None,
                fractional_bw=None,
        )
        self.low_pass_filter_2 = filter.fir_filter_fff(1, firdes.low_pass(
        	1, rf_samp_rate, 3e3, 0.5e3, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0 = filter.fir_filter_fff(1, firdes.low_pass(
        	1, 16e3, 1.1e3, 50, firdes.WIN_HAMMING, 6.76))
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_float*1, "/home/brian/apt_rx/foo.bin", False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_abs_xx_0 = blocks.abs_ff(1)
        self.analog_fm_demod_cf_0 = analog.fm_demod_cf(
        	channel_rate=rf_samp_rate,
        	audio_decim=1,
        	deviation=17e3,
        	audio_pass=5e3,
        	audio_stop=6e3,
        	gain=1.0,
        	tau=0,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fm_demod_cf_0, 0), (self.low_pass_filter_2, 0))    
        self.connect((self.blocks_abs_xx_0, 0), (self.low_pass_filter_0, 0))    
        self.connect((self.blocks_complex_to_mag_0, 0), (self.rational_resampler_xxx_0, 0))    
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_complex_to_mag_0, 0))    
        self.connect((self.low_pass_filter_0, 0), (self.blocks_float_to_complex_0, 0))    
        self.connect((self.low_pass_filter_2, 0), (self.rational_resampler_xxx_0_0, 0))    
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_file_sink_0_0, 0))    
        self.connect((self.rational_resampler_xxx_0, 0), (self.wxgui_scopesink2_0, 0))    
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.blocks_abs_xx_0, 0))    
        self.connect((self.rational_resampler_xxx_0_0, 0), (self.wxgui_fftsink2_1, 0))    
        self.connect((self.rtlsdr_source_0, 0), (self.analog_fm_demod_cf_0, 0))    
        self.connect((self.rtlsdr_source_0, 0), (self.wxgui_fftsink2_0, 0))    
        self.connect((self.rtlsdr_source_0, 0), (self.wxgui_waterfallsink2_0, 0))    


    def get_satellite_select(self):
        return self.satellite_select

    def set_satellite_select(self, satellite_select):
        self.satellite_select = satellite_select
        self.set_satellite_frequency(int(self.satellite_select * 1e6))
        self._satellite_select_chooser.set_value(self.satellite_select)

    def get_satellite_frequency(self):
        return self.satellite_frequency

    def set_satellite_frequency(self, satellite_frequency):
        self.satellite_frequency = satellite_frequency
        self.rtlsdr_source_0.set_center_freq(self.satellite_frequency, 0)

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        self.rf_samp_rate = rf_samp_rate
        self.low_pass_filter_2.set_taps(firdes.low_pass(1, self.rf_samp_rate, 3e3, 0.5e3, firdes.WIN_HAMMING, 6.76))
        self.rtlsdr_source_0.set_sample_rate(self.rf_samp_rate)

    def get_if_samp_rate(self):
        return self.if_samp_rate

    def set_if_samp_rate(self, if_samp_rate):
        self.if_samp_rate = if_samp_rate
        self.wxgui_fftsink2_0.set_sample_rate(self.if_samp_rate)
        self.wxgui_waterfallsink2_0.set_sample_rate(self.if_samp_rate)

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = apt_rx()
    tb.Start(True)
    tb.Wait()
