#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import Image
import os

def extract_bitplanes(image):

	path = os.getcwd() + "\\Test\\"
	if not os.path.exists(path):
		os.makedirs(path)

	bit_planes = 8
	for i in range(0,bit_planes):
		bit_plane = get_bit_plane(image, 0b00000001 << i)
		bit_plane.save(path + "{}.bmp".format(i))


def get_bit_plane(mat, mask):

	rows, cols, channels = mat.shape
	bitplane = np.zeros(mat.shape, dtype=np.uint8)

	for i in range(0, rows):
		for j in range(0, cols):
			px = mat.item(i,j,0) & mask
			bitplane.itemset((i,j,0),px)
			
	bp = Image.fromarray(bitplane)
	return bp

def main():

	file_name = "test_2000mm.bmp"
	image = cv2.imread(file_name)
	cv2.imshow('image', image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	extract_bitplanes(image)



main()
