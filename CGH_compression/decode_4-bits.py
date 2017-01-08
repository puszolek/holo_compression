#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is an implementation of decoding algorithm for computer-generated holograms that reads binary files with 4-bits data representation and decodes it to create output bmp file.

This is a part of Bachelor's thesis: "Design of a lossless algorithm of computer-generated holograms".

Author: Paula Kochańska
Faculty of Physics
Warsaw University of Technology
Warsaw 2017
"""

import numpy as np
import os
import math
import io
import sys
import time

def to_8bits(data):

    """Converts 4-bits data to its 8-bits representation.

    Parameters
    ----------
    data: array_like
        Input 4-bits data read from binary file.

    Returns
    -------
    new_data: array_like
        8-bits representation of input data.
    """

    new_data = []

    for d in data:
        d1 = (d & 0b11110000) >> 4
        d2 = (d & 0b00001111)
        new_data.append(d1)
        new_data.append(d2)

    return new_data


def decode_RLE(data, file):

    """Decodes 4-bits data from file and creates output array that represents a bitplane.

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

    mask = 0b00000001 << int(file)
    data = to_8bits(data)
    a = []
    b = []
    counter = 0
    i = 0
    while i < len(data):
        counter += data[i]
        b.append(data[i])

        if counter == 1024:
            if (i+6< len(data) - 1) and data[i+1] == 0 and data[i+2] == 0 and data[i+3] == 15 and data[i+4] == 15 and data[i+5] == 15 and data[i+6] == 15:
                i += 6
            elif (i+5 < len(data) - 1) and data[i+1] == 0 and data[i+2] == 15 and data[i+3] == 15 and data[i+4] == 15 and data[i+5] == 15:
                i += 5
            elif (i+4 < len(data) - 1) and data[i+1] == 15 and data[i+2] == 15 and data[i+3] == 15 and data[i+4] == 15:
                i += 4
            a.append(b)
            counter = 0
            b = []
        i += 1

    rows = len(a)
    cols = np.sum(a[0])

    print("Bitplane {}, size: {}x{}".format(7 - int(math.log(mask, 2)), rows, cols))

    decoded_image = np.zeros((rows, cols, 1), np.uint8)

    for i in range(0, rows):
        tmp = 0
        if a[i][0] == 0:
            color = 0
            del(a[i][0])
        else:
            color = 1

        for j in range(0, len(a[i])):
            color = color % 2
            if a[i][j] != 0:
                cv2.line(decoded_image, (tmp,i), (tmp+a[i][j],i), (color*mask,color*mask,color*mask), 1)
                tmp += a[i][j]
            color += 1

    return decoded_image


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
        decoded_image = decode_RLE(f.read(), bin_file)
        f.close()
        decoded_images.append(decoded_image)

    return decoded_images


def main():
    print('4-bits algorithm - decompression')
    print('Author: Paula Kochańska')
    print('Faculty of Physics, Warsaw University of Technology')
    print('Warsaw 2017')
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
        print(output_path + '\\' + bin_dir + '_' + 'final.bmp')
        cv2.imwrite(output_path + '\\' + bin_dir + '_' + 'final.bmp', final_image)
        print('Done.')

        print('')

    print ('Program closed.')


main()
