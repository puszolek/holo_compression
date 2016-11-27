#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import os
import math
import io
import sys
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

path = os.getcwd() + "\\Test"

def get_dirs():
    print('Finding folders with data')
    path = "F:\\Projekty\\holo_compression\\Test\\" 
    dirs = [d for d in os.listdir(path) if os.path.isdir(path + d)]
    return dirs
    
 
def get_files(directory):
    path = "F:\\Projekty\\holo_compression\\Test\\" + directory
    files = [f for f in os.listdir(path) if not f.endswith("bmp")]
    return files, path
    
    
def get_stats(files, path):
    stats = {}
    
    for f in files:
        size = os.path.getsize(path + "\\" + f)
        stats[f] = size
    return stats
    

def get_total_sizes_stats(total_sizes):
    
    sorted_files = sorted(list(total_sizes.keys()))
    sorted_sizes = []
    index = []
    
    for file in sorted_files:
        lens_f = int(file[4:8]) - 2000
        index.append(lens_f)
        sorted_sizes.append(total_sizes[file])
        
    index = np.array(index)
    sorted_sizes = np.array(sorted_sizes)
    
    return index, sorted_sizes
    
    
def main():
    dirs = get_dirs()
    stats = []
    total_sizes = {}
    
    print('Calculating statistics...')
    
    for d in dirs:
        files, path = get_files(d)

        stat = get_stats(files, path)
        stats.append((d, stat))
        total_size = np.sum(list(stat.values()))
        total_sizes[d] = total_size/1024.0
  
    # TOTAL SIZES
    index, sorted_sizes = get_total_sizes_stats(total_sizes)
    plt.plot(index, sorted_sizes, color = 'red')
    plt.grid(True)
    plt.title('Total size')
    plt.ylim(3000, 4400)
    plt.ylabel('SIze [kilobytes]')
    plt.xlabel('f [mm]')
    plt.savefig('F:\\Projekty\\holo_compression\\stats\\total_size.png')

    # PLOTS FOR EACH BITPLANE
    total_sizes_per_bitplane = {'0': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [],}
    for stat in stats:
        lens_f = int(stat[0][4:8]) - 2000
        sizes = stat[1]
        for s in sizes:
           total_sizes_per_bitplane[s].append((lens_f, sizes[s]))
           
    fontP = FontProperties()
    fontP.set_size('small')

    for key in total_sizes_per_bitplane:
        data = total_sizes_per_bitplane[key]
        index = []
        vals = []
        for d in data:
            index.append(d[0])
            vals.append(d[1]/1024.0)
        plt.figure(figsize = (10,5))
        data_plot = plt.plot(index, vals, color = 'red', label = 'data')
        avg_plot = plt.plot(index, len(index)*[np.average(vals)], color = 'blue', linestyle = '--', label = 'avg')
        
        plt.legend(loc=(1.015,0), prop = fontP)
        plt.grid(True)
        plt.title(key)
        
        textbox = ' bitplane: {}\n min: {:.4f}\n max: {:.4f}\n avg: {:.4f}\n stdev: {:.4f}\n median: {:.4f}\n data[0]: {:.4f}'.format(key, np.min(vals), np.max(vals), np.average(vals), np.std(vals), np.median(vals), vals[199])
        figtext = plt.figtext(0.91, 0.22, textbox, fontproperties = fontP)
        plt.ylabel('SIze [kilobytes]')
        plt.xlabel('f [mm]')
        plt.savefig('F:\\Projekty\\holo_compression\\stats\\{}.png'.format(key), bbox_extra_artists=(figtext,), bbox_inches='tight')
       
main()











