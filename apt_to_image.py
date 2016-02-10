import argparse
import os.path
import struct

import matplotlib.pyplot as plt
from numpy import correlate, arange, argmax, histogram, interp, where
from PIL import Image, ImageOps

from scipy.ndimage import gaussian_filter

from itertools import tee

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

lines = len(pixels) // samples_per_line
pixels = pixels[0:samples_per_line * lines]

print('Found {} useable lines.'.format(lines))

print('Generating PNG Image')
output_file = input_file_directory + input_filename_base + '.png'
image = Image.new(GRAYSCALE, (samples_per_line, lines))
image.putdata(pixels)
image = ImageOps.equalize(image.rotate(180))
image.save(output_file)
