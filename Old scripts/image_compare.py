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


def show_image(name, image):

    cv2.imshow(name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def compare(img1, img2):

    rows, cols = img1.shape
    diff = np.zeros(img1.shape, dtype=np.uint8)
    identical = True

    for i in range(0, rows):
        for j in range(0, cols):
            px1 = img1.item(i,j)
            px2 = img2.item(i,j)
            diff.itemset((i,j),px1-px2)
            if (px1-px2 != 0):
                identical = False

    return diff, identical


def rmse(imageA, imageB):

	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	return np.sqrt(err)


def main():

    images = ['F:\\Projekty\\holo_compression\\CGH_compression\\folder\\lenna-4000.bmp', 'F:\\Projekty\\holo_compression\\CGH_compression\\folder\\JPEG1.bmp']

    print(images)
    img1 = load_image(images[0])
    img2 = load_image(images[1])

    if (img1.shape != img2.shape):
        print('Images must be the same size!')
        print('Program closed')
        sys.exit(0)

    diff, identical = compare(img1, img2)
    print('Are {} identical?: {}'.format(images, identical))

    err = rmse(img1, img2)
    print('Reconstruction error (RMSE): {}'.format(err))

    q = input('Do you want to me to display the difference? (y/n) ')
    if q.lower() == 'y':
        show_image('diff', diff)
        print ('')
    else:
        print ('')

    cv2.imwrite("C:\\Users\\puszol\\Desktop\\JPEG1_diff.bmp", diff);

    print('Program closed.')

main()
