#!/usr/bin/python

"""
subtr_bleed.py  -- subtract bleed-through for experimental images
Shuce Zhang, 20 June 2019
mailto:shuce@ualberta.ca
Version 2 supporting python3   Oct 12, 2019
required packages: matplotlib, numpy, scipy, czifile, roipoly, tifffile
"""

from bleedthrough import *
import tifffile

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

# input bleed-though coefficient
root = tk.Tk()
bt = BleedThroughChart(master=root, nrow=3)
root.mainloop()
corrImg = subtract_bt(newImg, bt.array_all)
corrImg[corrImg < 0] = 0
# display corrected image
show_all_channels2(corrImg, "Corrected images")
corrImg = corrImg.astype('uint16')
# tifffile.imwrite("corrected.tiff", corrImg, metadata={'axes': 'CXY'}, dtype='uint16')
tifffile.imwrite("corrected.tiff", corrImg, metadata={'axes': 'CXY'})