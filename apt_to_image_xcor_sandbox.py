import argparse
import os.path
import struct

import matplotlib.pyplot as plt
from numpy import correlate, arange, argmax, histogram, interp, where
from PIL import Image, ImageOps

from scipy.ndimage import gaussian_filter

from itertools import tee


def tuple_add(a, b):
    return tuple(sum(x) for x in zip(a, b))


def find_sync(data, sync_def, correlation_limit=0.9):
    correlation = correlate(sync_def, pixels, mode='full')
    correlation = correlation / correlation.max()

    # fixed_delta = len(sync_a)
    potential_syncs = where(correlation >= correlation_limit)[0]
    probabilities = []
    for pos in potential_syncs:
        probabilities.append(correlation[pos])
    # potential_syncs = potential_syncs + 28
    # potential_syncs = potential_syncs[::-1]

    for i, p in enumerate(potential_syncs[::-1]):
        potential_syncs[i] = len(pixels) - potential_syncs[i]

    return potential_syncs, probabilities[::-1]


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

# pixels, _ = histeq(pixels)

print('Searching for sync pulses')
print('    Finding first candidate sync pulse.')
sync_pulses = 7
sync_a = ([244, 244, 244, 244] * sync_pulses)

sync_a_loc, sync_a_prob = find_sync(pixels, sync_a, 0.8)
pixels = [(p, p, p) for p in pixels]

print('Coloring the cross correlations')

for loc in sync_a_loc:
    pixels[loc] = (0, 255, 0)

lines = len(pixels) // samples_per_line
pixels = pixels[0:samples_per_line * lines]

print('Found {} useable lines.'.format(lines))

print('Generating PNG Image')
output_file = input_file_directory + input_filename_base + '.png'
# image = Image.new(GRAYSCALE, (samples_per_line, lines))
image = Image.new('RGB', (samples_per_line, lines))
image.putdata(pixels)
#image = ImageOps.equalize(image.rotate(180))
image = ImageOps.equalize(image)
image.save(output_file)
