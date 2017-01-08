#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is an implementation of encoding algorithm for computer-generated holograms that reads bmp files and encodes them as sequences of 8 pixels written in 8-bits data.

This is a part of Bachelor's thesis: "Design of a lossless algorithm of computer-generated holograms".

Author: Paula Kochańska
Faculty of Physics
Warsaw University of Technology
Warsaw 2017
"""

import cv2
import numpy as np
import os
import math
import io
import sys
import time


def get_bit_plane(mat, mask):

    """Extracts single bitplane from given bmp file.

    Parameters
    ----------
    mat: 2D array_like
        Array representation of bmp file.
    mask: int
        Number representing bitplane.

    Returns
    -------
    bitplane: 2D array_like
        Extracted bitplane.
    """

    rows, cols = mat.shape
    bitplane = np.zeros(mat.shape, dtype=np.uint8)

    for i in range(0, rows):
        for j in range(0, cols):
            px = mat.item(i,j) & mask
            bitplane.itemset((i,j),np.uint8(px))

    return bitplane


def extract_bitplanes(image, file_path):

    """Extracts every bitplane from given image.

    Parameters
    ----------
    image: 2D array_like
        Array representation of bmp file.
    file_path: string
        Path to the bmp file.
    """

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    bit_planes = 8
    for i in range(0, bit_planes):
        bitplane = get_bit_plane(image, 0b00000001 << i)
        cv2.imwrite(file_path + "\{}_.bmp".format(i), bitplane)
        print ("Image {}.bmp".format(i))


def pxls_to_bytes(images, file_path):

    """Converts pixels to 8-bits data.

    Parameters
    ----------
    images: array_like
        List of bmp bitplane files.
    file_path: string
        Path to these files.
    """

    counter = 0

    for file in images:
        RLE = encode_pxls(file, file_path)
        file = io.open(file_path + '\\' + str(counter), 'wb+')
        for i in RLE:
            file.write(i)
        counter += 1


def encode_pxls(file, file_path):

    """Encodes data.

    Parameters
    ----------
    file: string
        Name of the bitplane file.
    file_path: string
        Path to the file.

    Returns
    -------
    bytes: 2D array_like
        Encoded pixel sequences from bitplane.
    """

    print(file_path + '\\' + file)
    mat = cv2.imread(file_path + '\\' + file, cv2.IMREAD_GRAYSCALE)
    rows, cols = mat.shape
    bytes = []

    for i in range(0, rows):
        row = bytearray()
        j = 0
        counter = 7
        byte = 0b00000000
        while j < cols:
            if counter == -1:
                byte = 0b00000000
                counter = 7
            if mat.item(i,j) != 0:
                byte = byte | (0b00000001 << counter)
            if counter == 0:
                row.append(np.uint8(byte))
            counter -= 1
            j += 1
        bytes.append(row)
    return bytes


def main():
    print('Bytes algorithm - compression')
    print('Author: Paula Kochańska')
    print('Faculty of Physics, Warsaw University of Technology')
    print('')

    sources_path = input('Path to source bitmaps: ')
    if not os.path.exists(sources_path):
        print('Wrong path')
        print('Program is closing')
        sys.exit(0)

    bin_files_path = input('Path to output binary files: ')
    if not os.path.exists(bin_files_path):
        os.makedirs(bin_files_path)

    file_names = [os.path.splitext(f)[0] for f in os.listdir(sources_path) if f.endswith('.bmp') or f.endswith('.BMP')]

    if (len(file_names) > 0):
        print('Found files: {}'.format(file_names))
    else:
        print('No files in source directory: {}'.format(sources_path))
        print('Program is closing')
        print ('')
        sys,exit(0)

    for file_name in file_names:
        dir_path = bin_files_path + '\\' + file_name
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        image_file = sources_path + '\\' + file_name + '.bmp'
        image = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        print ('Image {} loaded.'.format(image_file))

        start_time = time.time()
        print ('Extracting bitplanes to {}.'.format(dir_path))
        extract_bitplanes(image, dir_path)
        print('Extracting bitplanes took {} seconds'.format(time.time()- start_time))
        print ('')

        if len([f for f in os.listdir(dir_path)]) == 0:
            print ('No images to encode. Program is closing.')
            print('')
            sys.exit(0)

        start_time = time.time()
        print ("Encoding in progress...")
        images = [f for f in os.listdir(dir_path) if f.endswith('_.bmp')]
        pxls_to_bytes(images, dir_path)
        print('Data encoded.')
        print('Encoding binary files took {} seconds'.format(time.time()- start_time))
        print('')

    print ('Program closed.')


main()
