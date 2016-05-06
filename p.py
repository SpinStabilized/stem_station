from __future__ import division

import argparse
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import os.path
import pmt
import scipy.stats
import struct
import sys

from gnuradio.blocks import parse_file_metadata
from PIL import Image, ImageOps
from itertools import izip_longest

################################################################################
# Function Definitions
################################################################################
def grouper(n, iterable, fillvalue=None):
    '''Collect data into fixed-length chunks or blocks

    Breaks a list (iterable) into groups of n. The last list is filled with
    fillvalue to get to the n size if it is less than n. Sourced from:
    https://docs.python.org/2/library/itertools.html

    Args:
        n: Number of items in each resultant list
        iterable: List of items to break into smaller lists
        fillevalue: Optional parameter defines fill items for final list

    Returns:
        A list of lists where the input list is broken into lists of length n.
        For example:
            grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    '''
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def scale_pixels(pixels, out_min=0, out_max=255):
    in_max = max([max(line) for line in pixels])
    in_min = min([min(line) for line in pixels])
    for i, line in enumerate(pixels):
        for j, pixel in enumerate(line):
            pixels[i][j] = (pixel - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

            pixels[i][j] = int(round(pixels[i][j]))

    return pixels

def process_tlm(tlm_strip):
    tlm = [int(round(sum(line)/len(line))) for line in tlm_strip]
    deltas = []
    for i, point in enumerate(tlm):
        if i != 0:
            difference = abs(tlm[i] - tlm[i-1])
        else:
            difference = 0
        deltas.append(difference)
    frame_center = np.argmax(deltas)
    frame_start = frame_center - 64
    frame_end = frame_start + 128
    tlm_frame = tlm[frame_start:frame_end]
    tlm_points = [int(sum(point)/len(point)) for point in grouper(8, tlm_frame, tlm_frame[-1])]
    return tlm_points, tlm

def process_tlm2(tlm_strip):
    # plt.imshow(tlm_strip)
    # plt.show()
    tlm = [sum(line)/len(line) for line in tlm_strip]
    deltas = []
    for i, point in enumerate(tlm):
        if i != 0:
            difference = abs(tlm[i] - tlm[i-1])
        else:
            difference = 0
        deltas.append(difference)
    frame_center = np.argmax(deltas)
    frame_start = frame_center - 64
    frame_end = frame_start + 128
    tlm_frame = tlm[frame_start:frame_end]
    tlm_points = [sum(point)/len(point) for point in grouper(8, tlm_frame, tlm_frame[-1])]
    return tlm_points, tlm

def space_view(space_mark_strip):
    raw_strips = [int(round(sum(line)/len(line))) for line in space_mark_strip]
    # space_view_pixels = [pixel for line in space_mark_strip for pixel in line]
    hist = np.histogram(raw_strips, bins=256)
    hist_max = np.argmax(hist[0])
    if hist_max > 127:
        data = raw_strips
        for i, point in enumerate(data):
            if point < 127 and i is not 0:
                data[i] = data[i-1]
    else:
        data = raw_strips
        for i, point in enumerate(data):
            if point > 127 and i is not 0:
                data[i] = data[i-1]
    data_avg = int(round(np.mean(data)))
    return data_avg, data

def closest(val, l):
    '''Determines the closest value from a list to a value

    Args:
        val: Value to determine the closest to a value in l
        l: List of values

    Returns:
        Value from l closest to val. For example:

        closest(0.8, [0, 0.25, 0.5, 0.75, 1]) --> 0.75

    Source: http://goo.gl/kPeY0x
    '''
    return np.abs(np.array(l)-val).argmin()

def avhrr_prt_cal(x, a, eight_bits=True):
    '''NOAA AVHRR PRT Calibration Formula

    Args:
        x: Raw counts value
        a: PRT calibration table for a specific AVHRR

    Returns:
        Value of x as a temperature (Kelvin) for a specific AVHRR calibration
        table provided in a.
    '''
    if eight_bits:
        x = x * 4

    return sum([a[j] * x ** j for j in range(0, 5)])

def avhrr_bb_temp(T, b):
    '''NOAA AVHRR Blackbody Calibration Formula

    Args:
        T: List of PRT temperatures
        b: BB PRT weighting table for a specific AVHRR

    Returns:
        Returns a blackbody temperature (Kelvin) based on the calibrated
        weighting for a specific AVHRR.
    '''
    return sum([T[i] * b[i] for i in range(0, 4)])

def moving_average(l, window_size, pad=True):
    smoothed = list(np.convolve(l, np.ones((window_size,))/window_size, mode='valid')[(window_size-1):])

    if pad:
        pad_data = [smoothed[0]] * ((window_size-1) * 2)
        smoothed = pad_data + smoothed

    return smoothed

def parse_gnuradio_header(header_file, verbose=False):
    headers = []
    index = 0
    rx_time = datetime.timedelta(seconds = 0)
    with open(header_file, 'rb') as handle:
        file_length = os.path.getsize(header_file)
        while True:
            if file_length - handle.tell() < parse_file_metadata.HEADER_LENGTH:
                break

            header_str = handle.read(parse_file_metadata.HEADER_LENGTH)

            try:
                header = pmt.deserialize_str(header_str)
            except RuntimeError:
                break

            info = parse_file_metadata.parse_header(header, verbose)

            if info['nbytes'] == 0:
                break

            if(info['extra_len'] > 0):
                extra_str = handle.read(info['extra_len'])
                if(len(extra_str) == 0):
                    break

                try:
                    extra = pmt.deserialize_str(extra_str)
                except RuntimeError:
                    break

                parse_file_metadata.parse_extra_dict(extra, info, verbose)


            if len(headers) > 0:
                last_rx_time = headers[-1]['rx_time']
                samples_delta = headers[-1]['nitems'] / headers[-1]['rx_rate']
                samples_delta = datetime.timedelta(seconds=samples_delta)
                info['rx_time'] = last_rx_time + samples_delta

                info['index'] = index
                index = index + info['nitems']
            else:
                info['rx_time'] = datetime.timedelta(seconds=0.0)
                info['index'] = 0
                index = info['nitems']

            headers.append(info)

    return headers

################################################################################
# Define some constants and useful derived constants
################################################################################
PIXEL_MIN = 0
PIXEL_MAX = 255
SYNC_WIDTH = 39
SPACE_MARK_WIDTH = 47
IMAGE_WIDTH = 909
TLM_FRAME_WIDTH = 45
FULL_CHANNEL_WIDTH = SYNC_WIDTH + SPACE_MARK_WIDTH + IMAGE_WIDTH + TLM_FRAME_WIDTH
FULL_LINE_WIDTH = FULL_CHANNEL_WIDTH * 2

SYNC_RANGE = {'A':(0, SYNC_WIDTH),
              'B':(FULL_CHANNEL_WIDTH, FULL_CHANNEL_WIDTH + SYNC_WIDTH)}
SPACE_MARK_RANGE = {'A':(SYNC_RANGE['A'][1], SYNC_RANGE['A'][1] + SPACE_MARK_WIDTH),
                    'B':(SYNC_RANGE['B'][1], SYNC_RANGE['B'][1] + SPACE_MARK_WIDTH)}
IMAGE_RANGE = {'A':(SPACE_MARK_RANGE['A'][1], SPACE_MARK_RANGE['A'][1] + IMAGE_WIDTH),
               'B':(SPACE_MARK_RANGE['B'][1], SPACE_MARK_RANGE['B'][1] + IMAGE_WIDTH)}
TLM_FRAME_RANGE = {'A':(IMAGE_RANGE['A'][1], IMAGE_RANGE['A'][1] + TLM_FRAME_WIDTH),
                   'B':(IMAGE_RANGE['B'][1], IMAGE_RANGE['B'][1] + TLM_FRAME_WIDTH)}

BYTES_PER_FLOAT = 4
GRAYSCALE = 'L'

################################################################################
# Parse CLI Arguments
################################################################################
parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Raw APT demodulated data file')
parser.add_argument('-s', '--spacecraft', default='NOAA-19', help='Spacecraft captured (for calibration)')
parser.add_argument('-d', '--direction', default='north', help='Pass to the \'north\' or \'south\'')
parser.add_argument('-a', '--all', action='store_true', default=False, help='Show all data lines, not just aligned')
args = parser.parse_args()

input_file_directory = os.path.dirname(args.input_file) + '/'
input_filename_base, _ = os.path.splitext(os.path.basename(args.input_file))
header_file = input_file_directory + os.path.basename(args.input_file) + '.hdr'

with open('calibration/avhrr.json') as avhrr_cal_json:
    avhrr_cal = json.load(avhrr_cal_json)

CAL_DATA = avhrr_cal['CAL_DATA']
AVHRR_CHANNELS = avhrr_cal['AVHRR_CHANNELS']

spacecraft = args.spacecraft
if spacecraft not in CAL_DATA:
    print('Warning spacecraft {} not found in calibration data. Defaulting to NOAA-19'.format(spacecraft))
    spacecraft = 'NOAA-19'

# Parse the header file to find the SyncA markers
has_header = os.path.isfile(header_file)
syncs = []
if has_header:
    print('Opening {}'.format(header_file))

    headers = parse_gnuradio_header(header_file)
    start = datetime.datetime.now()
    # time_marks = [start + header['rx_time'] for header in headers]
    # for mark in time_marks:
    #     print mark
    last_rx_time = headers[-1]['rx_time']
    samples_delta = headers[-1]['nitems'] / headers[-1]['rx_rate']
    samples_delta = datetime.timedelta(seconds=samples_delta)
    end = start + (last_rx_time + samples_delta)
    capture_duration = end - start
    # print 'Capture Start:    {}'.format(start)
    # print 'Capture Finish:   {}'.format(end)
    # print 'Capture Duration: {}'.format(end - start)
    syncs = headers
    # debug = False
    # current_position = 0
    # with open(header_file, 'rb') as handle:
    #     file_length = os.path.getsize(header_file)
    #     while True:
    #
    #         if (file_length - handle.tell()) < parse_file_metadata.HEADER_LENGTH:
    #             break
    #
    #         header_str = handle.read(parse_file_metadata.HEADER_LENGTH)
    #
    #         try:
    #             header = pmt.deserialize_str(header_str)
    #         except RuntimeError:
    #             sys.stderr.write('Could not deserialize header: invalid or corrupt data file.\n')
    #             sys.exit(1)
    #
    #         info = parse_file_metadata.parse_header(header, debug)
    #         if info['nbytes'] == 0:
    #             break
    #
    #         if(info['extra_len'] > 0):
    #             extra_str = handle.read(info['extra_len'])
    #             if(len(extra_str) == 0):
    #                 break
    #
    #             try:
    #                 extra = pmt.deserialize_str(extra_str)
    #             except RuntimeError:
    #                 sys.stderr.write('Could not deserialize extras: invalid or corrupt data file.\n')
    #                 sys.exit(1)
    #
    #             extra_info = parse_file_metadata.parse_extra_dict(extra, info, debug)
    #
    #         if 'SyncA' in info:
    #             info['index'] = current_position - SYNC_WIDTH
    #             syncs.append(info)
    #
    #         current_position = current_position + info['nitems']

else:
    print('No Header File Found - Raw Processing')

# sys.exit(1)


print('Opening {}'.format(args.input_file))
with open(args.input_file, 'rb') as raw_data:
    raw_bytes = bytearray(raw_data.read())

samples_found = len(raw_bytes) // BYTES_PER_FLOAT

unpack_format = '<' + ('f' * samples_found)
pixels = list(struct.unpack(unpack_format, raw_bytes))

file_duration = datetime.timedelta(seconds = len(pixels) / (FULL_LINE_WIDTH * 2))
print('Capture Duration: {}'.format(capture_duration))

print('Aligning Sync Signals')
sync_ratio = 0

if len(syncs):
    pre_syncs = []
    new_pixels = []
    sync_lines = []
    # print syncs[1]
    # print next(header for header in syncs if 'SyncA' in header)
    first_sync = next(header for header in syncs if 'SyncA' in header)
    print first_sync
    pre_syncs = pixels[0:first_sync['index']]
    # pre_syncs = pixels[0:syncs[0]['index']]
    additional_pixels = FULL_LINE_WIDTH - (len(pre_syncs) % FULL_LINE_WIDTH)
    pre_syncs = ([0] * additional_pixels) + pre_syncs
    pre_syncs = [list(line) for line in grouper(FULL_LINE_WIDTH, pre_syncs, 0)]

    i = 0
    for sync in syncs:
        sync_lines.append(i)
        pixel_set = pixels[sync['index']:sync['index'] + sync['nitems']]
        pixel_set = [list(line) for line in grouper(FULL_LINE_WIDTH, pixel_set, pixel_set[-1])]
        if all(x == pixel_set[-1][0] for x in pixel_set[-1]):
            del pixel_set[-1]
        i += len(pixel_set)
        new_pixels.extend(pixel_set)

    aligned_start = len(pre_syncs)
    pixels = new_pixels
    sync_ratio = len(syncs)/float(len(pixels))
    if args.all:
        pixels = pre_syncs + new_pixels

else:
    print('No Syncs Found - Minimal Processing')
    pixels = [list(line) for line in grouper(FULL_LINE_WIDTH, pixels, 0)]
    pixels = scale_pixels(pixels)


plt.imshow(pixels)
plt.show()
sync_ratio = len(syncs)/float(len(pixels))

if sync_ratio > 0.05:
    print('Telemetry Processing - Find Analog to Digital Range From Wedges'.format(spacecraft))
    a_tlm = [line[TLM_FRAME_RANGE['A'][0]:TLM_FRAME_RANGE['A'][1]] for line in pixels]
    b_tlm = [line[TLM_FRAME_RANGE['B'][0]:TLM_FRAME_RANGE['B'][1]] for line in pixels]
    a_telemetry, _ = process_tlm2(a_tlm)
    b_telemetry, _ = process_tlm2(b_tlm)
    unified_tlm = [sum(x)/2 for x in zip(a_telemetry[0:14], b_telemetry[0:14])]
    telemetry = {'wedges':unified_tlm[0:8], 'zero_mod':unified_tlm[8]}

    print('Scaling to wedge calibration')
    pixels = [np.clip(line, telemetry['zero_mod'], telemetry['wedges'][-1]) for line in pixels]
    pixels = scale_pixels(pixels)

    print('Reprocessing of Telemetry for {}'.format(spacecraft))
    a_tlm = [line[TLM_FRAME_RANGE['A'][0]:TLM_FRAME_RANGE['A'][1]] for line in pixels]
    b_tlm = [line[TLM_FRAME_RANGE['B'][0]:TLM_FRAME_RANGE['B'][1]] for line in pixels]
    a_telemetry, tlm_a_strip = process_tlm(a_tlm)
    b_telemetry, tlm_b_strip = process_tlm(b_tlm)
    unified_tlm = [int(round(sum(x)/2)) for x in zip(a_telemetry[0:14], b_telemetry[0:14])]
    telemetry = {'wedges':unified_tlm[0:8], 'zero_mod':unified_tlm[8],
                 'bb_thermistors':unified_tlm[9:13], 'patch_thermistor':unified_tlm[13],
                 'a_bb':a_telemetry[14], 'a_channel':a_telemetry[15], 'a_space':0,
                 'b_bb':b_telemetry[14], 'b_channel':b_telemetry[15], 'b_space':0}

    ideal_curve = [int(255 * (i / len(telemetry['wedges']))) for i in range(len(telemetry['wedges'])+ 1)]
    initial_curve = [telemetry['zero_mod']] + telemetry['wedges']
    data_fit = scipy.stats.linregress(ideal_curve, initial_curve)
    telemetry['a_channel'] = closest(telemetry['a_channel'], telemetry['wedges'])+1
    telemetry['b_channel'] = closest(telemetry['b_channel'], telemetry['wedges'])+1
    telemetry['prt_temps'] = [avhrr_prt_cal(telemetry['bb_thermistors'][j], CAL_DATA[spacecraft]['a'][j]) for j in range(0, 4)]
    telemetry['bb_temp'] = avhrr_bb_temp(telemetry['prt_temps'], CAL_DATA[spacecraft]['b'])
    telemetry['patch_temp'] = (0.124 * telemetry['patch_thermistor']) + 90.113
    a_info = AVHRR_CHANNELS[str(telemetry['a_channel'])]
    b_info = AVHRR_CHANNELS[str(telemetry['b_channel'])]

    a_space_mark = [line[SPACE_MARK_RANGE['A'][0]:SPACE_MARK_RANGE['A'][1]] for line in pixels]
    b_space_mark = [line[SPACE_MARK_RANGE['B'][0]:SPACE_MARK_RANGE['B'][1]] for line in pixels]
    telemetry['a_space'], raw_a_space_mark_strip = space_view(a_space_mark)
    telemetry['b_space'], raw_b_space_mark_strip = space_view(b_space_mark)

    print('Image Information:')
    print('\tFrame A: AVHRR Channel {} - {} - {}'.format(a_info['channel_id'], a_info['type'], a_info['description']))
    print('\tFrame B: AVHRR Channel {} - {} - {}'.format(b_info['channel_id'], b_info['type'], b_info['description']))
    print('\tWedges: {}'.format(telemetry['wedges']))
    print('\tZero Mod Ref: {}'.format(telemetry['zero_mod']))
    print('\tA Blackbody/Space: {:3} / {:3}'.format(telemetry['a_bb'], telemetry['a_space']))
    print('\tB Blackbody/Space: {:3} / {:3}'.format(telemetry['b_bb'], telemetry['b_space']))
    print('\tPRTs (counts): {}'.format(' '.join(['{:<9.0f}'.format(samp) for samp in telemetry['bb_thermistors']])))
    print('\tPRTs (Kelvin): {}'.format('  '.join(['{:.2f} K'.format(temp) for temp in telemetry['prt_temps']])))
    print('\tBlackbody Ref Temp: {:.2f} K'.format(telemetry['bb_temp']))
    print('\tPatch Temp: {:.0f} cnts -- {:.2f} K'.format(telemetry['patch_thermistor'], telemetry['patch_temp']))

    print('Image Reception Quality:')
    print('\tSyncs ({})/Lines ({}) Ratio: {:.2%}'.format(len(syncs), len(pixels), sync_ratio))
    print('\tCalibration Linearity: {:.4%}'.format(data_fit.rvalue))

    print('Generating Calibration Curve Plots')
    # plt.style.use('dark_background')
    plt.suptitle(spacecraft, fontsize=15, fontweight='bold')

    plt.figure(0, figsize=(8.5, 11))
    plt.suptitle(spacecraft, fontsize=15, fontweight='bold')
    # plt.subplot(411)
    plt.subplot2grid((3,2), (0,1))
    handle_ideal, = plt.plot(ideal_curve, ideal_curve, 'g-', label='Ideal')
    handle_initial, _ = plt.plot(ideal_curve, initial_curve, 'r-', ideal_curve, initial_curve, 'r^', label='Received')
    plt.axis([0, 255, 0, 255])
    plt.xlabel('Ideal Curve Points')
    plt.ylabel('Received Curve Points')
    plt.title('Analog to Digital Cal Curve')
    plt.legend(handles=[handle_ideal, handle_initial], loc=4)
    plt.grid(b=True, which='major', color='grey', linestyle='--')
    plt.xticks(ideal_curve)
    plt.yticks(ideal_curve)
    # plt.savefig(input_file_directory + 'plot_cal_curves.png')

    # print('Generating Telemetry Text-Only Plot')
    # plt.figure(3, figsize=(10, 5))
    # plt.subplot(412)
    plt.subplot2grid((3,2), (0,0))
    plt.axis('off')
    plt.text(0, 0.95, 'Frame A: AVHRR Channel {} - {} - {}'.format(a_info['channel_id'], a_info['type'], a_info['description']))
    plt.text(0, 0.90, 'Frame B: AVHRR Channel {} - {} - {}'.format(b_info['channel_id'], b_info['type'], b_info['description']))
    plt.text(0, 0.85, 'PRTs: {}'.format('  '.join(['{:.2f} K'.format(temp) for temp in telemetry['prt_temps']])))
    plt.text(0, 0.80, 'Blackbody Ref Temp: {:.2f} K'.format(telemetry['bb_temp']))
    plt.text(0, 0.75, 'Patch Temp: {:.2f} K'.format(telemetry['patch_temp']))


    print('Generating Plot of Raw Telemetry Strips')
    # plt.figure(1, figsize=(12, 5))
    # plt.subplot(413)
    plt.subplot2grid((3,2), (1,0), colspan=2)
    plt.axis([0, max(len(tlm_a_strip), len(tlm_b_strip)), 0, 255])
    plt.xlabel('Line Number')
    plt.ylabel('Counts')
    plt.title('Telemetry Strips')
    plt.plot(tlm_a_strip, 'g', label='Channel A')
    plt.plot(tlm_b_strip, 'b', label='Channel B')
    plt.grid(b=True, which='major', color='grey', linestyle='--')
    plt.xticks(np.arange(0, len(tlm_a_strip), 16*8))
    plt.yticks(ideal_curve)
    # plt.savefig(input_file_directory + 'plot_tlm_strips.png')

    print('Generating Plot of Space View')
    # plt.figure(2, figsize=(12, 5))
    # plt.subplot(414)
    plt.subplot2grid((3,2), (2,0), colspan=2)
    plt.axis([0, max(len(tlm_a_strip), len(tlm_b_strip)), 0, 255])
    plt.xlabel('Line Number')
    plt.ylabel('Counts')
    plt.title('Space View Strips')
    raw_a_space_smoothed = moving_average(raw_a_space_mark_strip, 30)
    raw_b_space_smoothed = moving_average(raw_b_space_mark_strip, 30)
    plt.plot(raw_a_space_mark_strip, 'g', label='Channel A')
    plt.plot(raw_a_space_smoothed, 'r--')
    plt.plot(raw_b_space_mark_strip, 'b', label='Channel B')
    plt.plot(raw_b_space_smoothed, 'r--')
    plt.legend(loc='center right')
    plt.xticks(np.arange(0, len(tlm_a_strip), 16*8))
    plt.yticks(ideal_curve)
    plt.grid(b=True, which='major', color='grey', linestyle='--')
    # plt.savefig(input_file_directory + 'plot_space_view.png')
    plt.savefig(input_file_directory + 'plot_telemetry.png')
# else:


raw_images = {}
raw_images['F'] = pixels
if len(syncs):
    raw_images['A'] = [line[IMAGE_RANGE['A'][0]:IMAGE_RANGE['A'][1]] for line in pixels]
    raw_images['B'] = [line[IMAGE_RANGE['B'][0]:IMAGE_RANGE['B'][1]] for line in pixels]

for image in raw_images:
    lines = len(raw_images[image])
    width = len(raw_images[image][0])
    pixels = [item for sublist in raw_images[image] for item in sublist]

    output_file = input_file_directory + input_filename_base + image + '.png'
    image = Image.new(GRAYSCALE, (width, lines))
    image.putdata(pixels)
    if args.direction == 'north':
        image = image.rotate(180)
    if not len(syncs):
        image = ImageOps.equalize(image)
    image.save(output_file)
