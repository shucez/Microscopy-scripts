#!/usr/bin/python

"""
SP8_tiff.py
Shuce Zhang, 20 Sept 2020
mailto:shuce@ualberta.ca

required packages: matplotlib, numpy, scipy, czifile, roipoly, tifffile
"""

from SZmicroscopy import *
import numpy as np

################ Set tiff format

# img_array = Read_1by1_TCYX(n_time=2, n_channel=3)          # for 1by1 reading
# img_array = Read_by_channel(n_channel=3)                   # Time lapse from SP8
img_array1 = Read_by_channel(3)[0:-1]
img_array2 = Read_by_channel(3)[0:-1]
img_array3 = Read_by_channel(3)[0:-1]
img_array = np.concatenate((img_array1, img_array2, img_array3), axis=0)
img_obj = imageStack(imgArray=img_array, meta='TCYX')
# (img_array, path) = load_msr()
# img_obj = imageStack(imgArray=img_array, meta='CYX')
bg_roi = img_obj.draw_roi2(title="Please draw background")

b = img_obj.get_intensity_list(bg_roi, average_all_roi=True)
sub_bg_obj = subtract_background(img_obj, b)

cell_roi = sub_bg_obj.draw_roi2(title="Please draw ROIs for the cells.")
cell = sub_bg_obj.get_intensity_list(cell_roi, average_all_roi=False)

cell_flat = np.concatenate((cell[:,:,0].T, cell[:,:,1].T, cell[:,:,2].T), axis=1)

file_path = tkFileDialog.asksaveasfilename()
np.savetxt(file_path,
           cell_flat, delimiter=",")

# ratio1 = np.nan_to_num(np.true_divide(sub_bg_obj.stack[:, 1], sub_bg_obj.stack[:, 0]))
# ratio2 = np.nan_to_num(np.true_divide(sub_bg_obj.stack[:, 1], sub_bg_obj.stack[:, 2]))
# ratio1.astype('float32')
# ratio2.astype('float32')
# # rArray = np.stack((ratio1, ratio2), axis=1).astype('float32')
# rArray = np.stack((ratio1, ratio2), axis=1)
#
# ratio_obj = imageStack(imgArray=rArray, meta='TCYX')
#
# file_path = sub_bg_obj.write_ome_tiff()
# ratio_obj.write_ome_tiff(dtype='float32',
#     file_path=file_path.split(".")[0] + "_ratio." + file_path.split(".")[1])


#tifffile.imwrite("corrected.tiff", corrImg, metadata={'axes': 'CYX'})