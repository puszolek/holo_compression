#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is an implementation of decoding algorithm for computer-generated holograms that reads binary files with bytes data representation and decodes it to create output bmp file.

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


def bytes_to_pxls(data, file):

    """Decodes 8-bits data from file and creates output array that represents a bitplane.

    Parameters
    ----------
    data: array_like
        Input 4-bits data read from binary file.
    file: string
        Name of file that is being decoded.

    Returns
    -------
    decoded_image: 2D numpy array
        Output array representing decoded bitplane.
    """

    len_data = len(data)
    size = len_data*8
    dim = np.sqrt(size)
    decoded_image = np.zeros((int(dim), int(dim), 1), np.uint8)

    counter = 0
    b = []
    a = []
    for d in data:
        counter += 1
        pxls = byte_to_pxls(d)
        b += pxls

        if counter == (dim/8):
            a.append(b)
            b = []
            counter = 0

    for i in range(0, len(a)):
        for j in range(0, len(a[i])):
            decoded_image[i][j] = a[i][j] << int(file)

    return decoded_image


def byte_to_pxls(d):

    """Converts given number to 8 pixels.

    Parameters
    ----------
    d: int
        Given number representing 8 pixels sequence.

    Returns
    -------
    pxls: array_like
        List of pixels.
    """

    pxls = []
    for i in range(0, 8):
        pxls.append(((d & (0b10000000 >> i)) >> (7-i)) & 0b11111111)

    return pxls


def join_images(images):

    """Joins decoded images representing bitplanes to output bmp file.

    Parameters
    ----------
    image: array_like
        List of data decoded from binary files

    Returns
    -------
    final_image: 2D numpy array
        Output bmp file
    """

    rows = len(images[0])
    cols = len(images[0][0])

    final_image = np.zeros((rows, cols, 1), np.uint8)

    for img in images:
        for row in range(0, len(final_image)):
            for col in range(0, len(final_image[0])):
                final_image[row][col] += img[row][col]

    return final_image


def decode_files(file_path, n):

    """Decodes binary files.

    Parameters
    ----------
    file_path: string
        Path to the directory containing given binary files.

    Returns
    -------
    decoded_images: array_like
        List of decoded data from binary files.
    """

    files = [f for f in os.listdir(file_path) if not f.endswith('.bmp')]
    decoded_images = []
    print('Found files: {}'.format(files))

    for bin_file in files[(8-n):]:
        print(bin_file)
        f = open(file_path + '\\' + bin_file, 'rb+')
        decoded_image = bytes_to_pxls(f.read(), bin_file)
        f.close()
        decoded_images.append(decoded_image)

    return decoded_images


def main():
    print('Bytes algorithm - decompression')
    print('Author: Paula Kochańska')
    print('Faculty of Physics, Warsaw University of Technology')
    print('')

    bin_files_path = input('Path to input binary files: ')
    if not os.path.exists(bin_files_path):
        print('Wrong path: {}'.format(bin_files_path))
        print('Program is closing')
        print ('')
        sys.exit(0)

    output_path = input('Full path to output bmp files: ')
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    bin_dirs = [ bin_dir for bin_dir in os.listdir(bin_files_path)]

    if (len(bin_dirs) > 0):
        print('Found folders: {}'.format(bin_dirs))
    else:
        print('No folders in directory: {}'.format(bin_dirs))
        print('Program is closing')
        print ('')
        sys,exit(0)

    n = int(input('How many bitplanes do you want to decode? '))

    for bin_dir in bin_dirs:
        start_time = time.time()
        print('Decoding in progress...')
        print(bin_dir)
        decoded_images = decode_files(bin_files_path + '\\' + bin_dir, n)
        print ('')
        print ('Data decoded.')
        print('Decoding took {} seconds'.format(time.time()- start_time))

        print ('')
        print ('Writing final image...')
        final_image = join_images(decoded_images)
        print(output_path + bin_dir + '_' + 'final.bmp')
        cv2.imwrite(output_path + '\\' + bin_dir + '_' + 'final.bmp', final_image)
        print('Done.')

        print('')

    print ('Program closed.')


main()
