#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os


def join_images(images):

    rows = len(images[0])
    cols = len(images[0][0])
    final_image = np.zeros((rows, cols, 1), np.uint8)
    print(len(images))
    for img in images:
        for row in range(0, len(final_image)):
            for col in range(0, len(final_image[0])):
                final_image[row][col] += img[row][col]

    return final_image


def main():

    path = os.getcwd() + "\\Test"
    dirs = [f for f in os.listdir(path) if not f.endswith('bmpfinal.bmp')]
    print(dirs)

    for d in dirs:
        files = [f for f in os.listdir(path+ "\\" + d) if f.endswith('_.bmp')]
        images = []

        for f in files:
            print(path + "\\" + d + "\\" + f)
            mat = cv2.imread(path + "\\" + d + "\\" + f, cv2.IMREAD_GRAYSCALE)
            images.append(mat)

        for i in range(0, 8):
            decoded_image = join_images(images[i:8])
            cv2.imwrite(path + "\\" + d + "\\" + "rec{}.bmp".format(i), decoded_image)


main()
