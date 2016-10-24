#!/usr/bin/env python
# -*- coding: utf-8 -*-

data = [('a', 3), 
		('b', 2), 
		('c', 1), 
		('d', 5), 
		('e', 6)]
s = ''

for d in data:
	item = d[0]
	m = d[1]
	s += item*m

print(s)
# 'aaabbcdddddeeeeee'







