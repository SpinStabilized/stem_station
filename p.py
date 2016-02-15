import argparse
import os.path
import struct
import math

#import matplotlib.pyplot as plt
#from numpy import correlate, arange, argmax, histogram, interp, where
from PIL import Image, ImageOps

#from scipy.ndimage import gaussian_filter

from itertools import tee, izip_longest
from gnuradio.blocks import parse_file_metadata
# import parse_file_metadata
import pmt
import sys

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

BYTES_PER_FLOAT = 4
BAUD_RATE = 4160
SAMPLES_PER_PIXEL = 1
LINE_RATE = 0.5
GRAYSCALE = 'L'

samples_per_line = int((BAUD_RATE * SAMPLES_PER_PIXEL) * LINE_RATE)

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Raw APT demodulated data file")
args = parser.parse_args()

input_file_directory = os.path.dirname(args.input_file)
input_filename_base, _ = os.path.splitext(os.path.basename(args.input_file))
header_file = input_file_directory + os.path.basename(args.input_file) + '.hdr'
# print('Opening {}'.format(args.input_file))
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
                info['index'] = current_position - 40
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

# if len(syncs):
#    pixels = pixels[syncs[0]['index']:]
print('Finding Sync Signals')
if len(syncs):
    new_pixels = []
    pre_syncs = pixels[0:syncs[0]['index']]
    additional_pixels = 2080 - (len(pre_syncs) % 2080)
    pre_syncs = ([0] * additional_pixels) + pre_syncs
    print '***Additional Pixels {} ***'.format(additional_pixels)
    pre_syncs = [list(line) for line in grouper(2080, pre_syncs, 0)]

    for sync in syncs:
        pixel_set = pixels[sync['index']:sync['index'] + sync['nitems']]
        pixel_set = [list(line) for line in grouper(2080, pixel_set, pixel_set[-1])]
        new_pixels.extend(pixel_set)

    pixels = pre_syncs + new_pixels

raw_images = {'A':[], 'B':[]}
raw_images['A'] = [line[0:(2080//2)] for line in pixels]
raw_images['B'] = [line[(2080//2):] for line in pixels]

# lines = len(pixels) // samples_per_line
#pixels = pixels[0:samples_per_line * lines]
for image in raw_images:
    print('Generating PNG Images')
    lines = len(raw_images[image])
    width = len(raw_images[image][0])
    pixels = [item for sublist in raw_images[image] for item in sublist]

    print('Found {} useable lines.'.format(lines))

    print('Normalizing, Equalizing, & Scaling to 1-Byte Range')
    max_sample = max(pixels)
    min_sample = min(pixels)
    for i, pixel in enumerate(pixels):
        pixels[i] = int(map(pixel, min_sample, max_sample, 0, 255))
        # if pixels[i] < 0:
        #     pixels[i] = 0
        # pixels[i] = int((pixel / max_sample) * 255)

    output_file = input_file_directory + input_filename_base + image + '.png'
    image = Image.new(GRAYSCALE, (width, lines))
    image.putdata(pixels)
    image = ImageOps.equalize(image.rotate(180))
    image.save(output_file)
