#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
import sys


path = os.getcwd()


def load_image(file_name):

    image = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
    print ('Image {} loaded.'.format(file_name))
    return image

def rmse(imageA, imageB):

	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	return np.sqrt(err)


def main():

    images = ['C:\\Users\\puszol\\Desktop\\do_pracy\\lena_crop\\stat\\Lenna_400_0.bmp',
    'C:\\Users\\puszol\\Desktop\\do_pracy\\lena_crop\\stat\\Lenna_400_1.bmp',
    'C:\\Users\\puszol\\Desktop\\do_pracy\\lena_crop\\stat\\Lenna_400_2.bmp',
    'C:\\Users\\puszol\\Desktop\\do_pracy\\lena_crop\\stat\\Lenna_400_3.bmp',
    'C:\\Users\\puszol\\Desktop\\do_pracy\\usaf_crop\\stat\\Usaf_400_0.bmp',
    'C:\\Users\\puszol\\Desktop\\do_pracy\\usaf_crop\\stat\\Usaf_400_1.bmp',
    'C:\\Users\\puszol\\Desktop\\do_pracy\\usaf_crop\\stat\\Usaf_400_2.bmp',
    'C:\\Users\\puszol\\Desktop\\do_pracy\\usaf_crop\\stat\\Usaf_400_3.bmp']

    print(images)
    for image in images:
        img = load_image(image)
        N, M = img.shape
        I = np.average(img)

        ones = np.ones(img.shape, dtype=np.uint8)*I

        rms = np.sum((img.astype("float")[300:600, 400:700] - ones[300:600, 400:700]) ** 2)
        rms /= float(N*M)
        print(np.sqrt(rms))


main()
