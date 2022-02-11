from nd2reader import ND2Reader
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from bleedthrough import *

# with ND2Reader('test/test.nd2') as images:
#   plt.imshow(images[0])

file_path = tkFileDialog.askopenfilename()
if file_path.endswith("czi"):
  imageObj = czifile.imread(file_path)
  numChannel = len(imageObj[0][0])
  imgList = []
  for c in range(numChannel):
    imgList.append(imageObj[0][0][c][0][0].T[0])
  imgArray = np.stack(imgList).astype('float_')
if file_path.endswith("nd2"):
  imageObj = ND2Reader(file_path)
  imageObj.iter_axes = 'c'
  numChannel = len(imageObj)
  imgList = []
  for c in range(numChannel):
    imgList.append(imageObj[c])
  imgArray = np.stack(imgList).astype('float_')
if file_path.endswith("tif") or file_path.endswith("tiff"):
  imageObj = tifffile.imread(file_path)
  # imageObj.iter_axes = 'c'
  # numChannel = len(imageObj)
  # imgList = []
  # for c in range(numChannel):
  #   imgList.append(imageObj[c])
  # imgArray = np.stack(imgList).astype('float_')