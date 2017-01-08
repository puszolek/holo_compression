#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
import math
import io
import sys
import time

path = os.getcwd() + "\\Test"

def show_image(name, image):

    cv2.imshow(name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_bit_plane(mat, mask):

    rows, cols = mat.shape
    bitplane = np.zeros(mat.shape, dtype=np.uint8)
    bitplane_bin = np.zeros(mat.shape, dtype=np.uint8)

    print(rows, cols)

    for i in range(0, rows):
        for j in range(0, cols):
            px = mat.item(i,j) & mask
            bitplane.itemset((i,j),np.uint8(px))
            if px == 0:
                bitplane_bin.itemset((i,j),np.uint8(0))
            else:
                bitplane_bin.itemset((i,j),np.uint8(128))

    print(bitplane.shape)
    return bitplane, bitplane_bin


def extract_bitplanes(image, file_path):

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    bit_planes = 8
    for i in range(0, bit_planes):
        bitplane, bitplane_bin = get_bit_plane(image, 0b00000001 << i)
        cv2.imwrite(file_path + "\{}_.bmp".format(i), bitplane)
        cv2.imwrite(file_path + "\{}bin.bmp".format(i), bitplane_bin)
        print ("Image {}.bmp".format(i))


def join_images(images):

    rows = len(images[0])
    cols = len(images[0][0])

    final_image = np.zeros((rows, cols, 1), np.uint8)

    for img in images:
        for row in range(0, len(final_image)):
            for col in range(0, len(final_image[0])):
                final_image[row][col] += img[row][col]

    return final_image


def decode_files(file_path):

    files = [f for f in os.listdir(file_path) if not f.endswith('.bmp')]
    counter = 0
    decoded_images = []
    print(files)

    for file in files:
        mask = 0b00000001 << counter
        f = open(file_path + '\\' + file, 'rb+')
        decoded_image = bytes_to_pxls(f.read(), file)
        f.close()
        decoded_images.append(decoded_image)
        counter += 1

    return decoded_images


def bytes_to_pxls(data, file):
    print(file)
    len_data = len(data)
    size = len_data*8
    dim = np.sqrt(size)
    print(dim)
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
    pxls = []
    for i in range(0, 8):
        pxls.append(((d & (0b10000000 >> i)) >> (7-i)) & 0b11111111)

    return pxls


def pxls_to_byte(images, file_path):
    counter = 0

    for file in images:
        RLE = encode_pxls(file, file_path)
        file = io.open(file_path + '\\' + str(counter), 'wb+')
        for i in RLE:
            file.write(i)
        counter += 1


def encode_pxls(file, file_path):
    print(file_path + '\\' + file)
    mat = cv2.imread(file_path + '\\' + file, cv2.IMREAD_GRAYSCALE)
    rows, cols = mat.shape
    print(rows, cols)
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

    sources_path =  os.getcwd() + "\\Source"
    file_names = [f for f in os.listdir(sources_path)]
    print(file_names)

    i = 0
    for file_name in file_names:
        print(i)
        i += 1
        file_path = path + '\\' + file_name
        print(file_path)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        print(sources_path + '\\' + file_name)
        image = cv2.imread(sources_path + '\\' + file_name, cv2.IMREAD_GRAYSCALE)
        print ('Image {} loaded.'.format(file_name))

        q = input('Do you want to me to display the image? (y/n) ')
        if q.lower() == 'y':
            show_image(file_name, image)
            print ('')
        else:
            print ('')

        q = input('Do you want to extract the bitplanes? (y/n) ')
        if q.lower() == 'y':
            print ('Extracting bitplanes to {}.'.format(file_path))
            extract_bitplanes(image, file_path)
            print ('')
        else:
            print ('')

        if len([f for f in os.listdir(file_path)]) == 0:
            print ('No images to encode. Program is closing.')
            print('')
            sys.exit(0)

        print ("Coding RLE in progress...")
        images = [f for f in os.listdir(file_path) if f.endswith('_.bmp')]
        pxls_to_byte(images, file_path)
        print('Data encoded.')
        print('')

        print('Decoding in progress...')
        decoded_images = decode_files(file_path)
        print ('')
        print ('Data decoded.')

        print ('')
        print ('Creating final image...')
        final_image = join_images(decoded_images)
        cv2.imwrite(file_path + 'final.bmp',final_image)
        q = input('Do you want to me to display the final image? (y/n) ')
        if q.lower() == 'y':
            show_image('final', final_image)
            print ('')
        else:
            print ('')
    print ('Program closed.')


main()
