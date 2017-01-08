#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is an implementation of encoding algorithm for computer-generated holograms that reads bmp files and encodes them as 4-bits data using RLE algorithm.

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


def encode_RLE(file, file_path):

    """Encodes data using RLE algorithm.

    Parameters
    ----------
    file: string
        Name of the bitplane file.
    file_path: string
        Path to the file.

    Returns
    -------
    RLE: 2D array_like
        Encoded pixel sequences from bitplane using RLE algorithm.
    """

    print(file_path + '\\' + file)
    mat = cv2.imread(file_path + '\\' + file, cv2.IMREAD_GRAYSCALE)
    rows, cols = mat.shape
    RLE = []

    for i in range(0, rows):
        row = bytearray()
        if (mat.item(i,0) == 0):
            row.append(np.uint8(0))

        j = 0
        while j < cols:
            length = 1
            while ((j+1 < cols) and (mat.item(i,j) == mat.item(i,j+1))):
                length = length + 1
                j += 1
            j += 1

            if length in range(256,511):
                n = length % 2
                row.append(np.uint8((length-n)/2))
                row.append(np.uint8(0))
                row.append(np.uint8(length - ((length-n)/2)))
            elif length in range(511, 766):
                n = length % 3
                row.append(np.uint8((length -n)/3))
                row.append(np.uint8(0))
                row.append(np.uint8((length - n)/3))
                row.append(np.uint8(0))
                row.append(np.uint8(length - 2*(length - n)/3))
            elif length in range(766, 1021):
                n = length % 4
                for i in range(0,3):
                    row.append(np.uint8((length -n)/4))
                    row.append(np.uint8(0))
                row.append(np.uint8(length - 3*(length - n)/4))
            elif length in range(1021, 1025):
                for i in range(0,4):
                    row.append(np.uint8(255))
                    row.append(np.uint8(0))
                row.append(np.uint8(length - 1020))
            else:
                row.append(np.uint8(length))
        RLE.append(row)
    RLE = to_4bits(RLE)

    return RLE


def to_4bits(RLE):

    """Converts 8-bit data to 4-bits representation.

    Parameters
    ----------
    RLE: 2D array_like
        Encoded pixel sequences in 8-bits representation from bitplane using RLE algorithm.

    Returns
    -------
    new_RLE: 2D array_like
        Encoded pixel sequences in 4-bits representation from bitplane using RLE algorithm.
    """

    new_RLE = []
    for row in RLE:
        new_row = bytearray()
        i = 0
        counter = 0
        while i < len(row):
            if row[i] <= 15 and i+1 < len(row) and row[i+1] <= 15:

                hi = (row[i] << 4)
                lo = row[i+1]
                new_row.append(np.uint8(hi+lo))
                i += 1

            elif row[i] <= 15 and i+1 < len(row) and row[i+1] > 15:
                hi = (row[i] << 4)
                lo_1 = row[i+1] & 0b00001111
                hi_1 = row[i+1] & 0b11110000

                new_row.append(np.uint8(hi + lo_1))

                n = int(hi_1 / 8)
                for j in range(0, n):
                    new_row.append(np.uint8(0b00001000))
                i += 1

            elif row[i] > 15 and i+1 < len(row) and row[i+1] <= 15:

                if row[i] & 0b00001111 != 0:
                    lo = ((row[i] & 0b00001111) << 4)
                    new_row.append(np.uint8(lo))

                hi = (row[i] & 0b11110000)
                n = int(hi / 8)
                for j in range(0, n-1):
                    new_row.append(np.uint8(0b10000000))
                new_row.append(np.uint8(0b10000000 + row[i+1]))

                i += 1

            elif row[i] > 15 and i+1 < len(row) and row[i+1] > 15:

                if row[i] & 0b00001111 != 0:
                    lo = ((row[i] & 0b00001111) << 4)
                    new_row.append(np.uint8(lo))

                hi = (row[i] & 0b11110000)
                n = int(hi / 8)
                for j in range(0, n-1):
                    new_row.append(np.uint8(0b10000000))

                new_row.append(np.uint8(0b10000000 + (row[i+1] & 0b00001111)))
                hi2 = row[i+1] & 0b11110000
                n2 = int(hi2 / 8)
                for j in range(0, n2):
                    new_row.append(np.uint8(0b00001000))

                i += 1

            elif row[i] <= 15 and i == len(row)-1:
                new_row.append(np.uint8(row[i] << 4))

            elif row[i] > 15 and i == len(row)-1:
                new_row.append(np.uint8(row[i] << 4))
                hi = row[i] & 0b11110000
                n = int(hi / 8)
                for j in range(0, n):
                    new_row.append(np.uint8(0b10000000))
            i += 1

        new_row.append(np.uint8(0b11111111))
        new_row.append(np.uint8(0b11111111))
        new_RLE.append(new_row)

    return new_RLE


def do_RLE(images, file_path):

    """Do RLE encoding for every bitplane file.

    Parameters
    ----------
    images: array_like
        List of bmp bitplane files.
    file_path: string
        Path to these files.
    """

    counter = 0

    for file in images:
        RLE = encode_RLE(file, file_path)
        file = io.open(file_path + '\\' + str(counter), 'wb+')
        for i in RLE:
            file.write(i)
        counter += 1


def main():
    print('4-bits algorithm - compression')
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

    file_names = [f for f in os.listdir(sources_path) if f.endswith('.bmp') or f.endswith('.BMP')]

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

        image_file = sources_path + '/' + file_name
        print(image_file)
        image = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        print(image)
        cv2.imshow('elo', image)
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
        do_RLE(images, dir_path)
        print('Data encoded.')
        print('Encoding binary files took {} seconds'.format(time.time()- start_time))
        print('')

    print ('Program closed.')


main()
