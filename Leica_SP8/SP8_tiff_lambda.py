#!/usr/bin/python

"""
SP8_tiff.py
Shuce Zhang, 20 Sept 2020
mailto:shuce@ualberta.ca

required packages: matplotlib, numpy, scipy, czifile, roipoly, tifffile
"""

from SZmicroscopy import *
import numpy as np
import os

################ Set tiff format

array_480 = Read_1by1_TCYX(n_time=2, n_channel=10)          # for 1by1 reading
array_550 = Read_1by1_TCYX(n_time=2, n_channel=5)          # for 1by1 reading

# Time lapse from SP8
# img_array1 = Read_by_channel(3)[0:-1]
# img_array2 = Read_by_channel(3)[0:-1]
# img_array3 = Read_by_channel(3)[0:-1]
# img_array = np.concatenate((img_array1, img_array2, img_array3), axis=0)
img480_obj = imageStack(imgArray=array_480, meta='TCYX')
img550_obj = imageStack(imgArray=array_550, meta='TCYX')

# (img_array, path) = load_msr()
# img_obj = imageStack(imgArray=img_array, meta='CYX')

############ remove background
bg_roi = img550_obj.draw_roi2(title="Please draw background.")

bg480 = img480_obj.get_intensity_list(bg_roi, average_all_roi=True)
noise480 = img480_obj.get_noise_list(bg_roi, average_all_roi=True)
sub_bg480_obj = subtract_background(img480_obj, bg480)

bg550 = img550_obj.get_intensity_list(bg_roi, average_all_roi=True)
noise550 = img550_obj.get_noise_list(bg_roi, average_all_roi=True)
sub_bg550_obj = subtract_background(img550_obj, bg550)

############ measure cell ROIs
cell_roi = sub_bg550_obj.draw_roi2(title="Please draw ROIs for the cells.")
cell480 = sub_bg480_obj.get_intensity_list(cell_roi, average_all_roi=False)
cell550 = sub_bg550_obj.get_intensity_list(cell_roi, average_all_roi=False)

file_path = sub_bg480_obj.write_ome_tiff()
sub_bg550_obj.write_ome_tiff(dtype='float32',
    file_path=file_path.split(".")[0] + "_550." + file_path.split(".")[1])

cell480_flat = np.concatenate((cell480[:,0,:], cell480[:,1,:]), axis=1)
cell550_flat = np.concatenate((cell550[:,0,:], cell550[:,1,:]), axis=1)

np.savetxt(file_path.split(".")[0] + "_480" + ".csv",
           cell480_flat, delimiter=",")


np.savetxt(file_path.split(".")[0] + "_550" + ".csv",
           cell550_flat, delimiter=",")

bg480_flat = np.concatenate((bg480[0], bg480[1]))
bg550_flat = np.concatenate((bg550[0], bg550[1]))
noise480_flat = np.concatenate((noise480[0], noise480[1]))
noise550_flat = np.concatenate((noise550[0], noise550[1]))

sbr480 = cell480_flat.copy()
sbr550 = cell550_flat.copy()
snr480 = cell480_flat.copy()
snr550 = cell550_flat.copy()

for i in range(len(bg480_flat)):
    sbr480[:, i] = cell480_flat[:, i] / bg480_flat[i]
    snr480[:, i] = cell480_flat[:, i] / noise480_flat[i]

for i in range(len(bg550_flat)):
    sbr550[:, i] = cell550_flat[:, i] / bg550_flat[i]
    snr550[:, i] = cell550_flat[:, i] / noise550_flat[i]

np.savetxt(file_path.split(".")[0] + "_sbr480" + ".csv",
           sbr480, delimiter=",")


np.savetxt(file_path.split(".")[0] + "_sbr550" + ".csv",
           sbr550, delimiter=",")


np.savetxt(file_path.split(".")[0] + "_snr480" + ".csv",
           snr480, delimiter=",")


np.savetxt(file_path.split(".")[0] + "_snr550" + ".csv",
           snr550, delimiter=",")


# tifffile.imwrite("corrected.tiff", corrImg, metadata={'axes': 'CYX'})
