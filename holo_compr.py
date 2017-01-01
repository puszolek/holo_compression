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


def encode_RLE(file, file_path):
    print(file_path + '\\' + file)
    mat = cv2.imread(file_path + '\\' + file, cv2.IMREAD_GRAYSCALE)
    rows, cols = mat.shape
    print(rows, cols)
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
    
    new_RLE = to_4bits(RLE)
    
    return new_RLE
    
  
def to_4bits(RLE):

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
    

def to_8bits(data):

    new_data = []

    for d in data:
        d1 = (d & 0b11110000) >> 4
        d2 = (d & 0b00001111)
        new_data.append(d1)
        new_data.append(d2)
        
    return new_data
        
    
def decode_RLE(data, file):

    mask = 0b00000001 << int(file)
    data = to_8bits(data)
    a = []    
    b = []
    counter = 0
    print(sum(data)/1024)
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

    print("{}: {}x{}".format(int(math.log(mask, 2)), rows, cols))

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
    decoded_images = []
    print(files)

    for file in files:
        f = open(file_path + '\\' + file, 'rb+')
        decoded_image = decode_RLE(f.read(), file)
        f.close()
        decoded_images.append(decoded_image)

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
