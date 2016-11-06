#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
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
		print ("Image {}.bmp".format(i))


def encode_RLE(file):

	mat = cv2.imread(path + file, cv2.IMREAD_GRAYSCALE)
	rows, cols = mat.shape
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
		RLE.append(bytearray(row))

	return RLE


def decode_RLE(file, mask):

	with open(path + file, 'rb') as f:
		data = f.read()

	a = []	
	b = []
	counter = 0

	print (len(data))

	for d in data:
		counter += int.from_bytes(d, byteorder="big")
		b.append(d)
		if counter >= 1024:
			a.append(b)
			counter = 0

	print (len(a))

	rows = len(a)
	print(a[0])
	print(len(a[0]))
	cols = np.sum(a[0])
	
	print(rows, cols)

	decoded_image = np.zeros((rows, cols, 1), np.uint8)

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


def do_RLE(images):
	
	counter = 0
	decoded_images = []
	suma = 0

	for file in images:
		RLE = encode_RLE(file)
		file = open(path + str(counter), 'wb+')
		for i in RLE:
			file.write(i)
		file.close()
		counter += 1


def decode_files(files):

	counter = 0
	decoded_images = []

	for file in files:

		print('Decoding file {}...'.format(file))
		mask = 0b00000001 << counter
		decoded_image = decode_RLE(file, mask)
		decoded_images.append(decoded_image)

		counter += 1

	return decoded_images


def main():

	file_name = "test_2000mm.BMP"
	image = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
	print ('Image {} loaded.'.format(file_name))
	q = input('Do you want to me to display the image? (y/n) ')
	if q.lower() == 'y':
		show_image(file_name, image)
		print ('')
	else:
		print ('')

	print ('Extracting bitplanes to {}.'.format(path))
	extract_bitplanes(image)

	print ('')
	print ("Coding RLE in progress...")
	images = [f for f in os.listdir(path) if f.endswith('.bmp')]
	do_RLE(images)
	print ('Data coded.')

	print ('')
	print ('Decoding data in progress...')
	files = [f for f in os.listdir(path) if not f.endswith('.bmp')]
	decoded_images = decode_files(files)
	print ('Data decoded.')

	print ('')
	print ('Creating final image...')
	final_image = join_images(decoded_images)
	cv2.imwrite('final.bmp',final_image)
	q = input('Do you want to me to display the final image? (y/n) ')
	if q.lower() == 'y':
		show_image('final', final_image)
		print ('')
	else:
		print ('')

	print ('Program closed.')


main()