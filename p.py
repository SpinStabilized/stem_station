import argparse
import os.path
import struct

import matplotlib.pyplot as plt
from numpy import correlate, arange, argmax, histogram, interp, where
from PIL import Image, ImageOps

from scipy.ndimage import gaussian_filter

from itertools import tee
from gnuradio.blocks import parse_file_metadata
import pmt
import sys


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
sync_len = 42
syncs = []
if has_header:
    print('Opening {}'.format(os.path.basename(args.input_file) + '.hdr'))
    found_headers = 0
    debug = False


    last_position = 0
    current_position = 0
    ignore_next = False
    with open(header_file, 'rb') as handle:
        while True:
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


            current_position = current_position + info['nitems']
            if info['nitems'] > 2000 and not syncs:
                syncs.append(current_position)

else:
    print('No Header File Found - Raw Processing')

print('Opening {}'.format(args.input_file))
with open(args.input_file, 'rb') as raw_data:
    raw_bytes = bytearray(raw_data.read())

samples_found = len(raw_bytes) // BYTES_PER_FLOAT
print('Found {} Samples'.format(samples_found))

unpack_format = '<' + ('f' * samples_found)
pixels = list(struct.unpack(unpack_format, raw_bytes))

print('Normalizing, Equalizing, & Scaling to 1-Byte Range')
max_sample = max(pixels)
for i, pixel in enumerate(pixels):
    pixels[i] = int((pixel / max_sample) * 255)

if syncs[0] > sync_len:
    pixels = pixels[syncs[0] - sync_len:]

lines = len(pixels) // samples_per_line
pixels = pixels[0:samples_per_line * lines]

print('Found {} useable lines.'.format(lines))

print('Generating PNG Image')
output_file = input_file_directory + input_filename_base + '.png'
image = Image.new(GRAYSCALE, (samples_per_line, lines))
image.putdata(pixels)
image = ImageOps.equalize(image.rotate(180))
image.save(output_file)
