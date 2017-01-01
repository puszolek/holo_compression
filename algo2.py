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
        decoded_image = decode_RLE(f.read(), mask, file)
        f.close()
        decoded_images.append(decoded_image)
        counter += 1

    return decoded_images


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
        #if q.lower() == 'y':
        if True:
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
        do_RLE(images, file_path)
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
        '''q = input('Do you want to me to display the final image? (y/n) ')
        if q.lower() == 'y':
            show_image('final', final_image)
            print ('')
        else:
            print ('')'''
    print ('Program closed.')


main()
