#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import Image
import os
import math
import io

path = os.getcwd() + "\\Test\\"

def show_image(name, image):
	
	cv2.imshow(name, image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


def get_bit_plane(mat, mask):

	rows, cols = mat.shape
	bitplane = np.zeros(mat.shape, dtype=np.uint8)

	for i in range(0, rows):
		for j in range(0, cols):
			px = mat.item(i,j) & mask
			bitplane.itemset((i,j),px)
			
	return bitplane


def extract_bitplanes(image):

	if not os.path.exists(path):
		os.makedirs(path)

	bit_planes = 8
	for i in range(0, bit_planes):
		bit_plane = get_bit_plane(image, 0b00000001 << i)
		cv2.imwrite(path + "{}.bmp".format(i), bit_plane)
		print "Image {}.bmp has been successfully written to {}.".format(i,path)


def encode_RLE(file):

	mat = cv2.imread(path + file, cv2.CV_LOAD_IMAGE_GRAYSCALE)
	print path+file
	rows, cols = mat.shape
	print mat.shape
	RLE = []

	for i in range(0, rows):
		row = []
		if (mat.item(i,0) != 0):
			row.append(np.uint8(1))
		else:
			row.append(np.uint8(0))

		j = 0
		while j < cols:
			length = 1
			while ((j+1 < cols) and (mat.item(i,j) == mat.item(i,j+1))):
				length = length + 1
				j += 1
			j += 1
			row.append(np.uint8(length))

		RLE.append(row)
	return RLE


def decode_RLE(data, mask):
	
	rows = len(data)
	cols = np.sum(data[0][1:])
	
	decoded_image = np.zeros((rows, cols, 1), np.uint8)

	print np.sum(data[1023])


	for i in range(0, rows):
		tmp = 0
		if data[i][0] == 0:
			color = 0
		else:
			color = 1

		del(data[i][0])

		for j in range(0, len(data[i])):
			color = color % 2
			cv2.line(decoded_image, (tmp,i), (tmp+data[i][j],i), (color*mask,color*mask,color*mask), 1)
			tmp += data[i][j]
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


def main():

	file_name = "test_2000mm.bmp"
	image = cv2.imread(file_name, cv2.CV_LOAD_IMAGE_GRAYSCALE)
	show_image(file_name, image)
	extract_bitplanes(image)

	files = os.listdir(path)
	decoded_images = []
	counter = 0

	for file in files:
		RLE = encode_RLE(file)
		mask = 0b00000001 << counter
		decoded_image = decode_RLE(RLE, mask)
		decoded_images.append(decoded_image)
		counter += 1
		
	final_image = join_images(decoded_images)
	cv2.imwrite(path + 'final.bmp',final_image)
	show_image('final', final_image)


main()
