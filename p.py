import argparse
import datetime
import numpy as np
import os.path
import pmt
import struct
import sys
import matplotlib.pyplot as plt

from gnuradio.blocks import parse_file_metadata
from PIL import Image, ImageOps
from itertools import izip_longest


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def map(x, in_min, in_max, out_min, out_max):
    in_min = float(in_min)
    in_max = float(in_max)
    out_min = float(out_min)
    out_max = float(out_max)
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def npmax(l):
    max_idx = np.argmax(l)
    max_val = l[max_idx]
    return (max_idx, max_val)

def process_tlm(tlm_strip):
    tlm = [int(round(sum(line)/len(line))) for line in tlm_strip]
    deltas = []
    for i, point in enumerate(tlm):
        if i != 0:
            difference = abs(tlm[i] - tlm[i-1])
        else:
            difference = 0
        deltas.append(difference)
    frame_center, _ = npmax(deltas)
    frame_start = frame_center - 64
    frame_end = frame_start + 128
    tlm_frame = tlm[frame_start:frame_end]
    tlm_points = [int(sum(point)/len(point)) for point in grouper(8, tlm_frame, tlm_frame[-1])]
    return tlm_points

def closest(val, l):
    return min(range(len(l)), key=lambda i: abs(l[i]-val))

AVHRR_CHANNELS = {1:['1', (0.58, 0.68), 'Visible', 'Daytime cloud and surface mapping'],
                  2:['2', (0.73, 1.00), 'Near-IR', 'Land-water boundaries'],
                  3:['3A', (1.58, 1.65), 'Near-IR', 'Snow and ice detection'],
                  6:['3B', (3.55, 3.93), 'Near-IR', 'Night cloud mapping, sea surface temperature'],
                  4:['4', (10.30, 11.30), 'Mid-IR', 'Night cloud mapping, sea surface temperature'],
                  5:['5', (11.50, 12.50), 'Mid-IR', 'Sea surface temperature']}

CAL_DATA = {'NOAA-12':{'a':[[276.597, 0.051275, 1.36e-06, 0.0, 0.0],
                            [276.597, 0.051275, 1.36e-06, 0.0, 0.0],
                            [276.597, 0.051275, 1.36e-06, 0.0, 0.0],
                            [276.597, 0.051275, 1.36e-06, 0.0, 0.0]],
                       'b':[0.25, 0.25, 0.25, 0.25]},
            'NOAA-13':{'a':[[276.597, 0.051275, 1.36e-06, 0.0, 0.0],
                            [276.597, 0.051275, 1.36e-06, 0.0, 0.0],
                            [276.597, 0.051275, 1.36e-06, 0.0, 0.0],
                            [276.597, 0.051275, 1.36e-06, 0.0, 0.0]],
                       'b':[0.25, 0.25, 0.25, 0.25]},
            'NOAA-15':{'a':[[276.60157, 0.051045, 1.36328e-06, 0.0, 0.0],
                            [276.62531, 0.050909, 1.47266e-06, 0.0, 0.0],
                            [276.67413, 0.050907, 1.47656e-06, 0.0, 0.0],
                            [276.59258, 0.050906, 1.47656e-06, 0.0, 0.0]],
                       'b':[0.25, 0.25, 0.25, 0.25]},
            'NOAA-18':{'a':[[276.601, 0.05090, 1.657e-06, 0.0, 0.0],
                            [276.683, 0.05101, 1.482e-06, 0.0, 0.0],
                            [276.565, 0.05117, 1.313e-06, 0.0, 0.0],
                            [276.615, 0.05103, 1.484e-06, 0.0, 0.0]],
                       'b':[0.25, 0.25, 0.25, 0.25]},
            'NOAA-19':{'a':[[276.6067, 0.051111, 1.405783e-06, 0.0, 0.0],
                            [276.6119, 0.051090, 1.496037e-06, 0.0, 0.0],
                            [276.6311, 0.051033, 1.496990e-06, 0.0, 0.0],
                            [276.6268, 0.051058, 1.493110e-06, 0.0, 0.0]],
                       'b':[0.25, 0.25, 0.25, 0.25]}}

def avhrr_prt_cal(x, a):
    return sum([a[j] * x ** j for j in range(0, 5)])

def avhrr_bb_temp(T, b):
    return sum([T[i] * b[i] for i in range(0, 4)])

sync_width = 39
space_mark_width = 47
image_width = 909
tlm_frame_width = 45
full_channel_width = sync_width + space_mark_width + image_width + tlm_frame_width
full_line_width = full_channel_width * 2

sync_range = {'A':(0, sync_width),
              'B':(full_channel_width, full_channel_width + sync_width)}
space_mark_range = {'A':(sync_range['A'][1], sync_range['A'][1] + space_mark_width),
                    'B':(sync_range['B'][1], sync_range['B'][1] + space_mark_width)}
image_range = {'A':(space_mark_range['A'][1], space_mark_range['A'][1] + image_width),
               'B':(space_mark_range['B'][1], space_mark_range['B'][1] + image_width)}
tlm_frame_range = {'A':(image_range['A'][1], image_range['A'][1] + tlm_frame_width),
                   'B':(image_range['B'][1], image_range['B'][1] + tlm_frame_width)}

BYTES_PER_FLOAT = 4
GRAYSCALE = 'L'

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Raw APT demodulated data file')
parser.add_argument('-s', '--spacecraft', default='NOAA-19', help='Spacecraft captured (for calibration)')
parser.add_argument('-d', '--direction', default='north', help='Pass to the \'north\' or \'south\'')
parser.add_argument('-a', '--all', action='store_true', default=False, help='Show all data lines, not just aligned')
args = parser.parse_args()

input_file_directory = os.path.dirname(args.input_file)
input_filename_base, _ = os.path.splitext(os.path.basename(args.input_file))
header_file = input_file_directory + os.path.basename(args.input_file) + '.hdr'

spacecraft = args.spacecraft
if spacecraft not in CAL_DATA:
    print('Warning spacecraft {} not found in calibration data. Defaulting to NOAA-19'.format(spacecraft))
    spacecraft = 'NOAA-19'

has_header = os.path.isfile(header_file)
first_sync = 0
sync_len = 40
syncs = []
lines = []
if has_header:
    print('Opening {}'.format(os.path.basename(args.input_file) + '.hdr'))
    found_headers = 0
    debug = False
    last_position = 0
    current_position = 0
    ignore_next = False
    with open(header_file, 'rb') as handle:
        file_length = os.path.getsize(header_file)
        double_length = 0
        while True:

            if (file_length - handle.tell()) < parse_file_metadata.HEADER_LENGTH:
                break

            header_str = handle.read(parse_file_metadata.HEADER_LENGTH)

            try:
                header = pmt.deserialize_str(header_str)
            except RuntimeError:
                sys.stderr.write('Could not deserialize header: invalid or corrupt data file.\n')
                sys.exit(1)

            found_headers += 1
            info = parse_file_metadata.parse_header(header, debug)
            if info['nbytes'] == 0:
                break

            if(info['extra_len'] > 0):
                extra_str = handle.read(info['extra_len'])
                if(len(extra_str) == 0):
                    break

                try:
                    extra = pmt.deserialize_str(extra_str)
                except RuntimeError:
                    sys.stderr.write('Could not deserialize extras: invalid or corrupt data file.\n')
                    sys.exit(1)

                extra_info = parse_file_metadata.parse_extra_dict(extra, info, debug)

            if 'SyncA' in info:
                tmp_lines = info['nitems'] // 2080
                extra_pixels = info['nitems'] % 2080
                info['index'] = current_position - (39 + double_length)
                syncs.append(info)
                double_lenth = 0

            current_position = current_position + info['nitems']

else:
    print('No Header File Found - Raw Processing')

print('Opening {}'.format(args.input_file))
with open(args.input_file, 'rb') as raw_data:
    raw_bytes = bytearray(raw_data.read())

samples_found = len(raw_bytes) // BYTES_PER_FLOAT

unpack_format = '<' + ('f' * samples_found)
pixels = list(struct.unpack(unpack_format, raw_bytes))
print 'Raw Min: {} -- Raw Max: {}'.format(min(pixels), max(pixels))
print 'Raw Signal Mean: {}'.format(sum(pixels)/len(pixels))
print('Finding Sync Signals')
pre_syncs = []
new_pixels = []
sync_lines = []
max_sample = 0
min_sample = 0

if len(syncs):
    pre_syncs = pixels[0:syncs[0]['index']]
    additional_pixels = 2080 - (len(pre_syncs) % 2080)
    pre_syncs = ([0] * additional_pixels) + pre_syncs
    pre_syncs = [list(line) for line in grouper(2080, pre_syncs, 0)]

    i = 0
    for sync in syncs:
        sync_lines.append(i)
        pixel_set = pixels[sync['index']:sync['index'] + sync['nitems']]
        pixel_set = [list(line) for line in grouper(2080, pixel_set, pixel_set[-1])]
        if all(x == pixel_set[-1][0] for x in pixel_set[-1]):
            del pixel_set[-1]
        i += len(pixel_set)
        new_pixels.extend(pixel_set)

    aligned_start = len(pre_syncs)
    pixels = new_pixels
    sync_ratio = len(syncs)/float(len(pixels))
    if args.all:
        pixels = pre_syncs + new_pixels

    if sync_ratio > 0.05:
        # a_tlm = [line[tlm_frame_range['A'][0]:tlm_frame_range['A'][1]] for line in pixels[len(pre_syncs):len(pre_syncs)+last_sync]]
        a_tlm = [line[tlm_frame_range['A'][0]:tlm_frame_range['A'][1]] for line in pixels]
        a_tlm = [sum(line)/len(line) for line in a_tlm]
        # b_tlm = [line[tlm_frame_range['B'][0]:tlm_frame_range['B'][1]] for line in pixels[len(pre_syncs):len(pre_syncs)+last_sync]]
        b_tlm = [line[tlm_frame_range['B'][0]:tlm_frame_range['B'][1]] for line in pixels]
        b_tlm = [sum(line)/len(line) for line in b_tlm]
        max_sample = max(max(a_tlm), max(b_tlm))
        min_sample = min(min(a_tlm), min(b_tlm))
    else:
        max_sample = max([max(line) for line in pixels])
        min_sample = min([min(line) for line in pixels])
else:
    print('No Syncs Found - Minimal Processing')
    max_sample = max(pixels)
    min_sample = min(pixels)
    pixels = [list(line) for line in grouper(2080, pixels, 0)]

file_duration = datetime.timedelta(seconds = len(pixels) / 2)
print('Capture Duration: {}'.format(file_duration))

print('Scaling to 1-Byte Range')
for i, line in enumerate(pixels):
    line = np.clip(line, min_sample, max_sample)
    line = [float(p) for p in line]
    for j, pixel in enumerate(line):
        pixels[i][j] = int(round(map(pixel, min_sample, max_sample, 0, 255)))

sync_ratio = len(syncs)/float(len(pixels))
print('Syncs/Lines Ratio: {} / {} - {:.0f}%'.format(len(syncs), len(pixels), sync_ratio * 100))
if len(syncs) and sync_ratio > 0.05:
    print('Processing Telemetry for {}'.format(spacecraft))
    # a_tlm = [line[tlm_frame_range['A'][0]:tlm_frame_range['A'][1]] for line in pixels[len(pre_syncs):]]
    a_tlm = [line[tlm_frame_range['A'][0]:tlm_frame_range['A'][1]] for line in pixels]
    b_tlm = [line[tlm_frame_range['B'][0]:tlm_frame_range['B'][1]] for line in pixels]
    a_telemetry = process_tlm(a_tlm)
    b_telemetry = process_tlm(b_tlm)
    unified_tlm = [sum(x)/2 for x in zip(a_telemetry[0:14], b_telemetry[0:14])]
    telemetry = {'wedges':unified_tlm[0:8], 'zero_mod':unified_tlm[8],
                 'thermistors':unified_tlm[9:14], 'a_bb':a_telemetry[14],
                 'a_channel':a_telemetry[15], 'b_bb':b_telemetry[14],
                 'b_channel':b_telemetry[15]}

    telemetry['a_channel'] = closest(telemetry['a_channel'], telemetry['wedges']) + 1
    telemetry['b_channel'] = closest(telemetry['b_channel'], telemetry['wedges']) + 1
    telemetry['prt_temps'] = [avhrr_prt_cal(telemetry['thermistors'][j], CAL_DATA[spacecraft]['a'][j]) for j in range(0, 4)]
    telemetry['bb_temp'] = avhrr_bb_temp(telemetry['prt_temps'], CAL_DATA[spacecraft]['b'])
    print('Image Information:')
    a_info = AVHRR_CHANNELS[telemetry['a_channel']]
    b_info = AVHRR_CHANNELS[telemetry['b_channel']]
    print('     Frame A: AVHRR Channel {} - {} - {}'.format(a_info[0], a_info[2], a_info[3]))
    print('     Frame B: AVHRR Channel {} - {} - {}'.format(b_info[0], b_info[2], b_info[3]))
    print('     Wedges: {}'.format(telemetry['wedges']))
    print('     Zero Modulation Reference: {}'.format(telemetry['zero_mod']))
    print('     A Blackbody: {}'.format(telemetry['a_bb']))
    print('     B Blackbody: {}'.format(telemetry['b_bb']))
    print('     Thermistors: {}'.format(telemetry['thermistors']))
    print('     Thermistor Temps: {}'.format('  '.join(['{:.2f} K'.format(temp) for temp in telemetry['prt_temps']])))
    print('     Blackbody Reference Temp (K): {:.2f} K'.format(telemetry['bb_temp']))
    a_space = [line[space_mark_range['A'][0]+10:space_mark_range['A'][1]-7] for line in pixels]
    a_space = [sum(line)/len(line) for line in a_space]
    b_space = [line[space_mark_range['B'][0]+10:space_mark_range['B'][1]-7] for line in pixels]
    b_space = [sum(line)/len(line) for line in b_space]
    # plt.plot(a_space)
    # plt.plot(b_space)
    # plt.show()

raw_images = {}
raw_images['F'] = pixels
if len(syncs):
    raw_images['A'] = [line[image_range['A'][0]:image_range['A'][1]] for line in pixels]
    raw_images['B'] = [line[image_range['B'][0]:image_range['B'][1]] for line in pixels]

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
