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
import os
import shutil
######################## User defined parameters ###################
# Pre-defined parameters
UsePrePara = True     # False then key in parameters.
matrix = [                                                               # for Confocal: mCh, cpV
    [0,                   0.0152799231,     0],
    [0.00213029372,       0,                0],
    [0,                   0,                0]
]

# matrix = [                                                               # for TIRF: mCer3, FRET, cpV, miR670
#     [0,                   0.593801816323638, 0.00215154144896414, 0],
#     [0,                   0,                 0,                   0],
#     [0.00444907313846516, 0.134907791322414, 0,                   0],
#     [0,                   0,                 0,                   0]
# ]

# FRET information
CalcRatio = False
CalcEapp = False
CFPIndex = 0  # first channel
FRETIndex = 1  # second channel

G = 2.845178   # if 0 then no Eapp calculation

# Measure ROIs

MeasureROIs = False
MeasureRaw = False

######################### Don't change after this line

# Reading files, creating new working directory
wkdir = os.getcwd()
# Read czi file
(rawImg, path) = load_msr()
print('reading file:', path)
prefix = os.path.basename(path).split(".")[0]
os.mkdir(prefix)
os.chdir(prefix)
newdir = os.getcwd()
print('current folder:', newdir)
shutil.copy(path, newdir)

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
if UsePrePara:
    bt = BleedThroughChart(master=root, nrow=len(rawImg), matrix=matrix)
else:
    bt = BleedThroughChart(master=root, nrow=len(rawImg))
root.mainloop()
corrImg = subtract_bt(newImg, bt.array_all)
if CalcRatio:
    RatioImg = np.nan_to_num(np.true_divide(corrImg[FRETIndex], corrImg[CFPIndex]))
    RatioImg[RatioImg < 0] = 0
    RatioImg = RatioImg.astype('float32')
    tifffile.imwrite("ratio.tiff", RatioImg, metadata={'axes': 'YX'})
    if CalcEapp and G:
        EappImg = np.nan_to_num(np.true_divide(RatioImg, RatioImg + G))
        EappImg[EappImg < 0] = 0
        EappImg = EappImg.astype('float32')
        tifffile.imwrite("Eapp.tiff", EappImg, metadata={'axes': 'YX'})

corrImg[corrImg < 0] = 0
# display corrected image

corrImg = corrImg.astype('uint16')
# tifffile.imwrite("corrected.tiff", corrImg, metadata={'axes': 'CXY'}, dtype='uint16')
tifffile.imwrite("corrected.tiff", corrImg, metadata={'axes': 'CYX'})

if MeasureROIs:
    cell_rois = draw_roi2(corrImg)
    if CalcRatio:
        ratio_list = [RatioImg]
        if CalcEapp:
            ratio_list.append(EappImg)
        ratio_stack = np.stack(ratio_list).astype('float_')
        allImg = np.vstack((corrImg, ratio_stack))
    else:
        allImg = corrImg.copy()
        # cell_list_ratio = get_intensity_list(cell_rois, ratio_stack)
        # cell_list = np.vstack((cell_list, cell_list_ratio))
    cell_list = get_intensity_list(cell_rois, allImg)
    # show_all_channels_with_roi2(allImg, cell_rois)
    show_all_channels_with_roi(allImg, cell_rois)
    OutTable = cell_list.transpose((1, 0))
    print("corrected ROIs:\n", OutTable)
    np.savetxt("measurements.csv", OutTable, delimiter=",")
else:
    show_all_channels2(corrImg, "Corrected images")

if MeasureRaw:
    raw_list = get_intensity_list(cell_rois, rawImg)
    RawTable = raw_list.transpose((1, 0))
    RawTable = np.vstack((bg_mean, RawTable))
    print("uncorrected ROIs:\n", RawTable)
    np.savetxt("raw.csv", RawTable, delimiter=",")

os.chdir(wkdir)