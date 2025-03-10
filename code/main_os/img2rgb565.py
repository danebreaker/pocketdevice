# -*- coding: utf-8 -*-
"""Utility to convert images to raw RGB565 format.

Usage:
    python img2rgb565.py <your_image>
    <your_image> is the full path to the image file you want to convert.
"""

from PIL import Image
from struct import pack
from os import path
import sys


def error(msg):
    """Display error and exit."""
    print (msg)
    sys.exit(-1)


def write_bin(f, pixel_list):
    """Save image in RGB565 format."""
    for pix in pixel_list:
        r = (pix[0] >> 3) & 0x1F
        g = (pix[1] >> 2) & 0x3F
        b = (pix[2] >> 3) & 0x1F
        f.write(pack('>H', (r << 11) + (g << 5) + b))


if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        error('Please specify input file: ./img2rgb565.py test.png')
#     file_names = ['zero.png', 'zero_sm.png', 'zero_tiny.png',
#                   'one.png', 'one_sm.png', 'one_tiny.png',
#                   'two.png', 'two_sm.png', 'two_tiny.png',
#                   'three.png', 'three_sm.png', 'three_tiny.png',
#                   'four.png', 'four_sm.png', 'four_tiny.png',
#                   'five.png', 'five_sm.png', 'five_tiny.png',
#                   'six.png', 'six_sm.png', 'six_tiny.png',
#                   'seven.png', 'seven_sm.png', 'seven_tiny.png',
#                   'eight.png', 'eight_sm.png', 'eight_tiny.png',
#                   'nine.png', 'nine_sm.png', 'nine_tiny.png',
#                   'wifi.png', 'dots.png']
    file_names = [
            'zero_tiny_dark.png', 'one_tiny_dark.png', 'two_tiny_dark.png', 'three_tiny_dark.png', 'four_tiny_dark.png',
            'five_tiny_dark.png', 'six_tiny_dark.png', 'seven_tiny_dark.png', 'eight_tiny_dark.png', 'nine_tiny_dark.png',
            'wifi.png', 'slash_dark.png', 'dots.png'
        ]
    for png_file_name in file_names:
        in_path = png_file_name#args[1]
        if not path.exists(in_path):
            error('File Not Found: ' + in_path)

        filename, ext = path.splitext(in_path)
        out_path = filename + '.raw'
        img = Image.open(in_path).convert('RGB')
        pixels = list(img.getdata())
        with open(out_path, 'wb') as f:
            write_bin(f, pixels)
        print('Saved: ' + out_path)
