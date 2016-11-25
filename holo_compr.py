#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
import math
import io
import sys

path = os.getcwd() + "\\Test"

def show_image(name, image):
    
    cv2.imshow(name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_bit_plane(mat, mask):

    rows, cols = mat.shape
    bitplane = np.zeros(mat.shape, dtype=np.uint8)
    print(rows, cols)

    for i in range(0, rows):
        for j in range(0, cols):
            px = mat.item(i,j) & mask
            bitplane.itemset((i,j),np.uint8(px))
           
    print(bitplane.shape)
    return bitplane


def extract_bitplanes(image, file_path):

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    bit_planes = 8
    for i in range(0, bit_planes):
        bit_plane = get_bit_plane(image, 0b00000001 << i)
        cv2.imwrite(file_path + "\{}.bmp".format(i), bit_plane)
        print ("Image {}.bmp".format(i))


def encode_RLE(file, file_path):

    print(file_path + '\\' + file)
    mat = cv2.imread(file_path + '\\' + file, cv2.IMREAD_GRAYSCALE)
    rows, cols = mat.shape
    print(rows, cols)
    RLE = []
    maxa = []
    
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
                print("Przekroczono zakres uint8! {}".format(length))
                n = length % 2
                row.append(np.uint8((length-n)/2))
                row.append(np.uint8(0))
                row.append(np.uint8(length - ((length-n)/2)))
            elif length in range(511, 766):
                print("Przekroczono zakres uint8! {}".format(length))
                n = length % 3
                row.append(np.uint8((length -n)/3))
                row.append(np.uint8(0))
                row.append(np.uint8((length - n)/3))
                row.append(np.uint8(0))
                row.append(np.uint8(length - 2*(length - n)/3))
            elif length in range(766, 1021):
                print("Przekroczono zakres uint8! {}".format(length))
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
        
    return RLE


def decode_RLE(data, mask):

    a = []    
    b = []
    counter = 0
    print(sum(data)/1024)

    for d in data:
        counter += d
        b.append(d)
        if counter >= 1024:
            a.append(b)
            counter = 0
            b = []

    rows = len(a)
    cols = np.sum(a[0])

    print("{}: {}x{}".format(int(math.log(mask,2)), rows, cols))

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
            cv2.line(decoded_image, (tmp,i), (tmp+a[i][j],i), (color*mask,color*mask,color*mask), 1)
            tmp += a[i][j]
            color += 1

    return decoded_image


def join_images(images):
    
    rows = len(images[0])
    cols = len(images[0][0])

    final_image = np.zeros((rows, cols, 1), np.uint8)

    for img in images:
        for row in range(0, len(final_image)):
            for col in range(0, len(final_image[0])):
                final_image[row][col] += img[row][col]

    return final_image


def do_RLE(images, file_path):
    
    counter = 0

    for file in images:
        RLE = encode_RLE(file, file_path)
        file = io.open(file_path + '\\' + str(counter), 'wb+')
        for i in RLE:
            file.write(i)
        counter += 1


def decode_files(file_path):

    files = [f for f in os.listdir(file_path) if not f.endswith('.bmp')]
    counter = 0
    decoded_images = []

    for file in files:
        mask = 0b00000001 << counter
        f = open(file_path + '\\' + file, 'rb+')
        decoded_image = decode_RLE(f.read(), mask)
        f.close()
        decoded_images.append(decoded_image)
        counter += 1

    return decoded_images


def main():

    sources_path =  os.getcwd() + "\\Source"
    file_names = [f for f in os.listdir(sources_path)]
    #file_names = file_names[]
    print(file_names)
    
    i = 0
    for file_name in file_names:
        print(i)
        i += 1
        file_path = path + '\\' + file_name
        print(file_path)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        print(sources_path + file_name)
        image = cv2.imread(sources_path + '\\' + file_name, cv2.IMREAD_GRAYSCALE)
        print ('Image {} loaded.'.format(file_name))
       
        """q = input('Do you want to me to display the image? (y/n) ')
        if q.lower() == 'y':    
            show_image(file_name, image)
            print ('')
        else:
            print ('')"""

        #q = input('Do you want to extract the bitplanes? (y/n) ')
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
        images = [f for f in os.listdir(file_path) if f.endswith('.bmp')]
    
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
