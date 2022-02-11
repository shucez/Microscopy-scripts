#!/usr/bin/python

"""
calc_bleed.py  -- Calculate bleed-through coefficent from single-stained control
Shuce Zhang, 20 June 2019
mailto:shuce@ualberta.ca
Version 2 supporting python3   Oct 12, 2019
required packages: matplotlib, numpy, scipy, czifile, roipoly, tifffile
"""

from bleedthrough import *

# Read czi file
rawImg = load_msr()

# Define ROIs for the background
bg_rois = draw_roi2(rawImg, title="Please define ROIs for the background.")
bg_list = get_intensity_list(bg_rois, rawImg)
try:
    bg_mean = np.mean(bg_list, axis=1)
except IndexError:
    bg_mean = bg_list
print("Background values are:\n", bg_list)
print("Mean background values:\n", bg_mean)

# subtract background for all channels
newImg = subtract_background(rawImg, bg_mean)
newImg[newImg < 0] = 0
# show_all_channels_with_roi(newImg, bg_rois)

# Define ROIs with cells
cell_rois = draw_roi2(newImg)
cell_list = get_intensity_list(cell_rois, newImg)
print("cell ROI values are:\n", cell_list)
show_all_channels_with_roi2(newImg, cell_rois)
slopes, rsqs = get_slope(cell_list)
print("slope\t from {rows} | to {columns} \n", slopes)
print("r-value\t from {rows} | to {columns} \n", rsqs)