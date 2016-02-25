import argparse
import math
import numpy as np
import os.path
import pmt
import struct
import sys
import matplotlib.pyplot as plt

from gnuradio.blocks import parse_file_metadata
from PIL import Image, ImageOps
from itertools import tee, izip_longest


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
parser.add_argument("input_file", help="Raw APT demodulated data file")
args = parser.parse_args()

input_file_directory = os.path.dirname(args.input_file)
input_filename_base, _ = os.path.splitext(os.path.basename(args.input_file))
header_file = input_file_directory + os.path.basename(args.input_file) + '.hdr'

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


            # print info

            if 'SyncA' in info:

                tmp_lines = info['nitems'] // 2080
                extra_pixels = info['nitems'] % 2080
                # print tmp_lines, extra_pixels, current_position
                info['index'] = current_position - 39
                # print info
                syncs.append(info)
            # print info
            current_position = current_position + info['nitems']

else:
    print('No Header File Found - Raw Processing')

print('Opening {}'.format(args.input_file))
with open(args.input_file, 'rb') as raw_data:
    raw_bytes = bytearray(raw_data.read())

samples_found = len(raw_bytes) // BYTES_PER_FLOAT
print('Found {} Samples'.format(samples_found))

unpack_format = '<' + ('f' * samples_found)
pixels = list(struct.unpack(unpack_format, raw_bytes))
# n, bins, patches = plt.hist(pixels, 256, facecolor='g')
# plt.plot(pixels)
# plt.show()
# if len(syncs):
#    pixels = pixels[syncs[0]['index']:]
print('Finding Sync Signals')
pre_syncs = []
new_pixels = []
if len(syncs):
    pre_syncs = pixels[0:syncs[0]['index']]
    additional_pixels = 2080 - (len(pre_syncs) % 2080)
    pre_syncs = ([0] * additional_pixels) + pre_syncs
    print '***Additional Pixels {} ***'.format(additional_pixels)
    pre_syncs = [list(line) for line in grouper(2080, pre_syncs, 0)]

    for sync in syncs:
        pixel_set = pixels[sync['index']:sync['index'] + sync['nitems']]
        pixel_set = [list(line) for line in grouper(2080, pixel_set, pixel_set[-1])]
        new_pixels.extend(pixel_set)


    aligned_start = len(pre_syncs)
    pixels = new_pixels
    pixels = pre_syncs + new_pixels

print('Syncs/Lines Ratio: {} / {} - {:.0f}%'.format(len(syncs), len(pixels), (len(syncs)/float(len(pixels))) * 100 ))
a_tlm = [line[tlm_frame_range['A'][0]:tlm_frame_range['A'][1]] for line in pixels[len(pre_syncs):]]
a_tlm = [sum(line)/len(line) for line in a_tlm]
b_tlm = [line[tlm_frame_range['B'][0]:tlm_frame_range['B'][1]] for line in pixels[len(pre_syncs):]]
b_tlm = [sum(line)/len(line) for line in b_tlm]
max_sample = max(max(a_tlm), max(b_tlm))
min_sample = min(min(a_tlm), min(b_tlm))

print('Scaling to 1-Byte Range')
for i, line in enumerate(pixels):
    l = np.clip(line, min_sample, max_sample)
    for j, pixel in enumerate(l):
        pixels[i][j] = int(round(map(pixel, min_sample, max_sample, 0, 255)))

print('Determining Telemetry Values')
a_tlm = [line[tlm_frame_range['A'][0]:tlm_frame_range['A'][1]] for line in pixels[len(pre_syncs):]]
b_tlm = [line[tlm_frame_range['B'][0]:tlm_frame_range['B'][1]] for line in pixels[len(pre_syncs):]]
a_telemetry = process_tlm(a_tlm)
b_telemetry = process_tlm(b_tlm)
unified_tlm = [sum(x)/2 for x in zip(a_telemetry[0:14], b_telemetry[0:14])]
telemetry = {'wedges':unified_tlm[0:8], 'zero_mod':unified_tlm[8],
             'thermistors':unified_tlm[9:14], 'a_chan_back':a_telemetry[14],
             'a_channel':a_telemetry[15], 'b_chan_back':b_telemetry[14],
             'b_channel':b_telemetry[15]}

telemetry['a_channel'] = closest(telemetry['a_channel'], telemetry['wedges']) + 1
telemetry['b_channel'] = closest(telemetry['b_channel'], telemetry['wedges']) + 1
print(telemetry)

raw_images = {}
# raw_images['A_FULL'] = [line[0:full_channel_width] for line in pixels]
# raw_images['A_SYNC'] = [line[sync_range[0]:sync_range[1]] for line in raw_images['A_FULL']]
# raw_images['A_SPACE'] = [line[space_mark_range[0]:space_mark_range[1]] for line in raw_images['A_FULL']]
# raw_images['A_IMAGE'] = [line[image_range[0]:image_range[1]] for line in raw_images['A_FULL']]
# raw_images['A_TLM'] = [line[tlm_frame_range[0]:tlm_frame_range[1]] for line in raw_images['A_FULL']]
# raw_images['B_FULL'] = [line[full_channel_width:] for line in pixels]
# raw_images['B_SYNC'] = [line[sync_range[0]:sync_range[1]] for line in raw_images['B_FULL']]
# raw_images['B_SPACE'] = [line[space_mark_range[0]:space_mark_range[1]] for line in raw_images['B_FULL']]
# raw_images['B_IMAGE'] = [line[image_range[0]:image_range[1]] for line in raw_images['B_FULL']]
# raw_images['B_TLM'] = [line[tlm_frame_range[0]:tlm_frame_range[1]] for line in raw_images['B_FULL']]
raw_images['F'] = pixels



# min_sample = min(pixels)
# max_sample = max(pixels)


# lines = len(pixels) // samples_per_line
#pixels = pixels[0:samples_per_line * lines]
for image in raw_images:
    print('Generating PNG Images')
    lines = len(raw_images[image])
    width = len(raw_images[image][0])
    pixels = [item for sublist in raw_images[image] for item in sublist]
    print('Found {} useable lines.'.format(lines))

    output_file = input_file_directory + input_filename_base + image + '.png'
    image = Image.new(GRAYSCALE, (width, lines))
    image.putdata(pixels)
    # image = ImageOps.equalize(image.rotate(180))
    image = image.rotate(180)
    image.save(output_file)
