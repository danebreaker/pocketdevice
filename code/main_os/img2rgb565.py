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
    # file_names = ['zero.png', 'zero_sm.png', 'zero_sm_dark.png',
    #               'one.png', 'one_sm.png', 'one_sm_dark.png',
    #               'two.png', 'two_sm.png', 'two_sm_dark.png',
    #               'three.png', 'three_sm.png', 'three_sm_dark.png',
    #               'four.png', 'four_sm.png', 'four_sm_dark.png',
    #               'five.png', 'five_sm.png', 'five_sm_dark.png',
    #               'six.png', 'six_sm.png', 'six_sm_dark.png',
    #               'seven.png', 'seven_sm.png', 'seven_sm_dark.png',
    #               'eight.png', 'eight_sm.png', 'eight_sm_dark.png',
    #               'nine.png', 'nine_sm.png', 'nine_sm_dark.png']

    # for png_file_name in file_names:
    in_path = args[1]
    if not path.exists(in_path):
        error('File Not Found: ' + in_path)
    filename, ext = path.splitext(in_path)
    out_path = filename + '.raw'
    img = Image.open(in_path).convert('RGB')
    pixels = list(img.getdata())
    with open(out_path, 'wb') as f:
        write_bin(f, pixels)
    print('Saved: ' + out_path)
