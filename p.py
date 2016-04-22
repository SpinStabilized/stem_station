import argparse
import datetime
import json
import numpy as np
import os.path
import pmt
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

def scale_pixels(pixels, in_min, in_max, out_min, out_max):
    in_min = float(in_min)
    in_max = float(in_max)
    out_min = float(out_min)
    out_max = float(out_max)
    for i, line in enumerate(pixels):
        line = np.clip(line, in_min, in_max)
        line = [float(p) for p in line]
        for j, pixel in enumerate(line):
            pixels[i][j] = int(round((pixel - in_min) * (out_max - out_min) / (in_max - in_min) + out_min))
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
    return tlm_points

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

def avhrr_prt_cal(x, a):
    '''NOAA AVHRR PRT Calibration Formula

    Args:
        x: Raw counts value
        a: PRT calibration table for a specific AVHRR

    Returns:
        Value of x as a temperature (Kelvin) for a specific AVHRR calibration
        table provided in a.
    '''
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

has_header = os.path.isfile(header_file)
syncs = []
if has_header:
    print('Opening {}'.format(header_file))
    debug = False
    current_position = 0
    with open(header_file, 'rb') as handle:
        file_length = os.path.getsize(header_file)
        while True:

            if (file_length - handle.tell()) < parse_file_metadata.HEADER_LENGTH:
                break

            header_str = handle.read(parse_file_metadata.HEADER_LENGTH)

            try:
                header = pmt.deserialize_str(header_str)
            except RuntimeError:
                sys.stderr.write('Could not deserialize header: invalid or corrupt data file.\n')
                sys.exit(1)

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
                info['index'] = current_position - SYNC_WIDTH
                syncs.append(info)

            current_position = current_position + info['nitems']

else:
    print('No Header File Found - Raw Processing')

print('Opening {}'.format(args.input_file))
with open(args.input_file, 'rb') as raw_data:
    raw_bytes = bytearray(raw_data.read())

samples_found = len(raw_bytes) // BYTES_PER_FLOAT

unpack_format = '<' + ('f' * samples_found)
pixels = list(struct.unpack(unpack_format, raw_bytes))

print('Finding Sync Signals')
pre_syncs = []
new_pixels = []
sync_lines = []
max_sample = 0
min_sample = 0
sync_ratio = 0

if len(syncs):
    pre_syncs = pixels[0:syncs[0]['index']]
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

    if sync_ratio > 0.05:
        a_tlm = [line[TLM_FRAME_RANGE['A'][0]:TLM_FRAME_RANGE['A'][1]] for line in pixels]
        a_tlm = [sum(line)/len(line) for line in a_tlm]
        b_tlm = [line[TLM_FRAME_RANGE['B'][0]:TLM_FRAME_RANGE['B'][1]] for line in pixels]
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
    pixels = [list(line) for line in grouper(FULL_LINE_WIDTH, pixels, 0)]

file_duration = datetime.timedelta(seconds = len(pixels) / 2)
print('Capture Duration: {}'.format(file_duration))

print('Scaling to 1-Byte Range')
pixels = scale_pixels(pixels, min_sample, max_sample, PIXEL_MIN, PIXEL_MAX)

sync_ratio = len(syncs)/float(len(pixels))

if sync_ratio > 0.05:
    print('Processing Telemetry for {}'.format(spacecraft))
    a_tlm = [line[TLM_FRAME_RANGE['A'][0]:TLM_FRAME_RANGE['A'][1]] for line in pixels]
    b_tlm = [line[TLM_FRAME_RANGE['B'][0]:TLM_FRAME_RANGE['B'][1]] for line in pixels]
    a_telemetry = process_tlm(a_tlm)
    b_telemetry = process_tlm(b_tlm)
    unified_tlm = [sum(x)/2 for x in zip(a_telemetry[0:14], b_telemetry[0:14])]
    telemetry = {'wedges':unified_tlm[0:8], 'zero_mod':unified_tlm[8],
                 'thermistors':unified_tlm[9:14], 'a_bb':a_telemetry[14],
                 'a_channel':a_telemetry[15], 'b_bb':b_telemetry[14],
                 'b_channel':b_telemetry[15]}

    telemetry['a_channel'] = closest(telemetry['a_channel'], telemetry['wedges'])
    telemetry['b_channel'] = closest(telemetry['b_channel'], telemetry['wedges'])
    telemetry['prt_temps'] = [avhrr_prt_cal(telemetry['thermistors'][j], CAL_DATA[spacecraft]['a'][j]) for j in range(0, 4)]
    telemetry['bb_temp'] = avhrr_bb_temp(telemetry['prt_temps'], CAL_DATA[spacecraft]['b'])
    a_info = AVHRR_CHANNELS[str(telemetry['a_channel'])]
    b_info = AVHRR_CHANNELS[str(telemetry['b_channel'])]

    print('Image Information:')
    print('     Frame A: AVHRR Channel {} - {} - {}'.format(a_info['channel_id'], a_info['type'], a_info['description']))
    print('     Frame B: AVHRR Channel {} - {} - {}'.format(b_info['channel_id'], b_info['type'], b_info['description']))
    print('     Wedges: {}'.format(telemetry['wedges']))
    print('     Zero Mod Ref: {}'.format(telemetry['zero_mod']))
    print('     A Blackbody: {}'.format(telemetry['a_bb']))
    print('     B Blackbody: {}'.format(telemetry['b_bb']))
    print('     PRTs (counts): {}'.format(' '.join(['{:<9}'.format(samp) for samp in telemetry['thermistors']])))
    print('     PRTs (Kelvin): {}'.format('  '.join(['{:.2f} K'.format(temp) for temp in telemetry['prt_temps']])))
    print('     Blackbody Ref Temp: {:.2f} K'.format(telemetry['bb_temp']))
    print('Image Reception Quality:')
    print('     Radiometric Resolution Loss: {:.2f}%'.format((1-((telemetry['wedges'][-1]-telemetry['zero_mod'])+1)/256.0)*100))
    print('     Syncs/Lines Ratio: {} / {} - {:.0f}%'.format(len(syncs), len(pixels), sync_ratio * 100))

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
