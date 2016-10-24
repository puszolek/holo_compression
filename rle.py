#!/usr/bin/env python
# -*- coding: utf-8 -*-

s = 'aaabbcdddddeeeeee'
data = []
counter = 1

for i in range(0, len(s)):
	if i+1 < len(s) and s[i] == s[i+1]:
		counter += 1
	else:
		data.append((s[i],counter))
		counter = 1

print(data)
# [('a', 3), ('b', 2), ('c', 1), ('d', 5), ('e', 6)]