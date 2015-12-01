import argparse
import math
import numpy
import os.path
import struct

from numpy.fft import fft, ifft
from numpy import conj
#from numpy.ndarray import astype
from itertools import zip_longest
from PIL import Image, ImageOps

BYTES_PER_FLOAT = 4
INPUT_FILENAME = '/home/brian/apt_rx/foo.bin'
BAUD_RATE = 4160
LINE_RATE = 0.5
GRAYSCALE = 'L'

pixels_per_line = int(BAUD_RATE * LINE_RATE)


def rescale(val, old_scale, new_scale):
    old_range = old_scale[1] - old_scale[0]
    new_range = new_scale[1] - new_scale[0]
    return (((val - old_scale[0]) * new_range) / old_range) + new_scale[0]

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Raw APT demodulated data file")
args = parser.parse_args()

input_file_directory = os.path.dirname(args.input_file)
input_filename_base, _ = os.path.splitext(os.path.basename(args.input_file))

print('Opening {}'.format(INPUT_FILENAME))
with open(args.input_file, 'rb') as raw_data:
    raw_bytes = bytearray(raw_data.read())

pixels_found = int(len(raw_bytes) / BYTES_PER_FLOAT)
print('Found {} Pixels'.format(pixels_found))

unpack_format = '<' + ('f' * pixels_found)
pixels = list(struct.unpack(unpack_format, raw_bytes))
lines = math.floor(len(pixels) / pixels_per_line)
print('Found {} Full Lines'.format(lines))

print('Scaling to 1-byte range')
old_range = (min(pixels), max(pixels))
new_range = (0, 255)
for i, pixel in enumerate(pixels):
	pixels[i] = abs(int(rescale(pixel, old_range, new_range)))

pixels = pixels[0:pixels_per_line * lines]

sync_pixels = list(pixels)
sync_signal = [0, 0, 255, 255] * (len(pixels) // 4)

pad = [0] * len(pixels)
sync_pixels.extend(pad)
sync_signal.extend(pad)
xcor = ifft(fft(sync_pixels)) * conj(fft(sync_signal))
xcor = xcor.astype(int)

with open('bar.bin', 'wb') as corr_data:
    corr_data.write(bytes(xcor))

output_file = input_file_directory + input_filename_base + '.png'
	
print('Generating PNG Image')
image = Image.new(GRAYSCALE, (pixels_per_line, lines))
image.putdata(pixels)
image = ImageOps.equalize(image.rotate(180))
image.save(output_file)
