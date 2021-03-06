"""
SZmicroscopy.py  -- packages for dealing with multi-dimensional microscopy data
Shuce Zhang, Sept 17, 2020
mailto:shuce@ualberta.ca
required packages: matplotlib, numpy, scipy, czifile, roipoly, tifffile
"""
import czifile
from nd2reader import ND2Reader
import matplotlib.pyplot as plt
import numpy as np
# import Tkinter as tk      #using python2
import tkinter as tk  # using python2
# import tkFileDialog       #using python2
import tkinter.filedialog as tkFileDialog  # using python3
from numpy.core.multiarray import ndarray
from roipoly import MultiRoi
from math import ceil, sqrt
import tifffile
from matplotlib.widgets import Slider
from scipy.stats import linregress


class imageStack():
    """
    imageStack is a ndarray for microscopy image stacks.
    """

    def __init__(self, imgArray, meta, *a, **k):
        """
        Initiate an imageStack object.
        :param imgArray: np.array, has to be built using a reader function.
        :param meta: 'CYX': requires imgArray to be 3-dimensional.
                    'TCYX': 4-dimensional
        """
        if meta == 'CYX':
            if len(imgArray.shape) == 3:
                self.meta = meta
                self.stack = imgArray
                (self.num_channel, self.num_y, self.num_x) = imgArray.shape
            else:
                raise Exception("Dimension of imgArray not consistent with meta!")
        if meta == 'TCYX':
            if len(imgArray.shape) == 4:
                self.meta = meta
                self.stack = imgArray
                (self.num_time, self.num_channel, self.num_y, self.num_x) = imgArray.shape
            else:
                raise Exception("Dimension of imgArray not consistent with meta!")

    def __iter__(self):
        yield from self.stack

    def show_all_channels(self, title=None):
        """
        show images of all channels in many rows. If image has time points, a slider bar will show up.
        :param title: text, title for GUI interface
        :return: fig object
        """
        if self.meta == 'CYX':
            fig = plt.figure()
            if self.num_channel >= 4:
                ncol = ceil(sqrt(self.num_channel))
                nrow = ceil(self.num_channel / ncol)
            else:
                ncol = self.num_channel
                nrow = 1
            for i in range(self.num_channel):
                fig.add_subplot(nrow, ncol, i + 1)
                plt.imshow(self.stack[i], cmap='gray')
                if title and i == 0:
                    plt.title(title)
            fig.show()
            return fig

        if self.meta == 'TCYX':
            fig = plt.figure()
            T = 0
            if self.num_channel >= 4:
                ncol = ceil(sqrt(self.num_channel))
                nrow = ceil(self.num_channel / ncol)
            else:
                ncol = self.num_channel
                nrow = 1
            im_list = []
            for i in range(self.num_channel):
                fig.add_subplot(nrow, ncol, i + 1)
                im_list.append(plt.imshow(self.stack[T][i], cmap='gray'))
                if title and i == 0:
                    plt.title(title)
            axb = plt.axes([0.15, 0.1, 0.65, 0.03])
            sb = Slider(axb, 'T', 0, (self.num_time - 1), valinit=T, valfmt='%d', valstep=1)

            def update(val):
                for i in range(self.num_channel):
                    T = sb.val
                    # fig.add_subplot(nrow, ncol, i + 1)
                    im_list[i].set_array(self.stack[int(T)][i])

            sb.on_changed(update)
            fig.show()
            return fig

    def draw_roi2(self, title="Click on the button to add a new ROI"):
        """
        Draw ROI when displaying all channels in a image stack
        :param multi_channel: image stack, np.array, generated by load_msr
        :param title: title for the GUI
        :return:multi_ROI object object
        """
        # fig = show_all_channels2(multi_channel, title=title)
        fig = self.show_all_channels(title=title)
        # plt.imshow(current_image, interpolation='nearest', cmap='gray')
        # plt.title(title)
        multi_roi = MultiRoi(fig=fig, ax=fig.axes[0])
        print("finished draw_roi")
        return multi_roi

    def get_intensity_list(self, multi_roi, average_all_roi=False):
        """
        Get the mean intensity of ROIs.
        :param multi_roi: ROI object obtained from `draw_roi2`
        :param average_all_roi: if True, calculate the average for all rois.
        Use True when you have multiple ROIs for background.
        :return: False, np.array (ROI, T, C) for 'TCYX' meta, (ROI, C) for 'CYX' meta
                True, np,array (T,C) for 'TCYX' meta, (C) for 'CYX' meta.
        """
        all_list = []
        if self.meta == 'CYX':
            if len(multi_roi.rois):
                for name, roi in multi_roi.rois.items():
                    temp_roi = np.array([])
                    for channel in self.stack:
                        mean, std = roi.get_mean_and_std(channel)
                        temp_roi = np.append(temp_roi, mean)
                    all_list.append(temp_roi)
                ## old implementation: return (C, ROI)
                # for channel in self.stack:
                #     channel_list = np.array([])
                #     for name, roi in multi_roi.rois.items():
                #         mean, std = roi.get_mean_and_std(channel)
                #         # print(mean)
                #         channel_list = np.append(channel_list, mean)
                #     all_list.append(channel_list)
                final_list = np.stack(all_list)  # type: ndarray
                if average_all_roi:
                    return np.mean(final_list, axis=0)
                else:
                    return final_list
            else:
                return 0
        if self.meta == 'TCYX':
            if len(multi_roi.rois):
                for name, roi in multi_roi.rois.items():
                    temp_roi = []
                    for time in self.stack:
                        temp_time = np.array([])
                        for channel in time:
                            mean, std = roi.get_mean_and_std(channel)
                            temp_time = np.append(temp_time, mean)
                        temp_roi.append(temp_time)
                    all_list.append(np.stack(temp_roi))
                final_list = np.stack(all_list)  # type: ndarray
                if average_all_roi:
                    return np.mean(final_list, axis=0)
                else:
                    return final_list
            else:
                return 0


    def get_noise_list(self, multi_roi, average_all_roi=False):
        """
        Get the mean intensity of ROIs.
        :param multi_roi: ROI object obtained from `draw_roi2`
        :param average_all_roi: if True, calculate the average for all rois.
        Use True when you have multiple ROIs for background.
        :return: False, np.array (ROI, T, C) for 'TCYX' meta, (ROI, C) for 'CYX' meta
                True, np,array (T,C) for 'TCYX' meta, (C) for 'CYX' meta.
        """
        all_list = []
        if self.meta == 'CYX':
            if len(multi_roi.rois):
                for name, roi in multi_roi.rois.items():
                    temp_roi = np.array([])
                    for channel in self.stack:
                        mean, std = roi.get_mean_and_std(channel)
                        temp_roi = np.append(temp_roi, std)
                    all_list.append(temp_roi)
                ## old implementation: return (C, ROI)
                # for channel in self.stack:
                #     channel_list = np.array([])
                #     for name, roi in multi_roi.rois.items():
                #         mean, std = roi.get_mean_and_std(channel)
                #         # print(mean)
                #         channel_list = np.append(channel_list, mean)
                #     all_list.append(channel_list)
                final_list = np.stack(all_list)  # type: ndarray
                if average_all_roi:
                    return np.mean(final_list, axis=0)
                else:
                    return final_list
            else:
                return 0
        if self.meta == 'TCYX':
            if len(multi_roi.rois):
                for name, roi in multi_roi.rois.items():
                    temp_roi = []
                    for time in self.stack:
                        temp_time = np.array([])
                        for channel in time:
                            mean, std = roi.get_mean_and_std(channel)
                            temp_time = np.append(temp_time, std)
                        temp_roi.append(temp_time)
                    all_list.append(np.stack(temp_roi))
                final_list = np.stack(all_list)  # type: ndarray
                if average_all_roi:
                    return np.mean(final_list, axis=0)
                else:
                    return final_list
            else:
                return 0

    def write_tiff(self, dtype='uint16', file_path=None):
        if not file_path:
            file_path = tkFileDialog.asksaveasfilename()
        array2write = self.stack.reshape(-2, self.num_y, self.num_x).astype(dtype)
        tifffile.imwrite(file_path, array2write, metadata={'axes': self.meta,
                                                           'images': array2write.shape[0],
                                                           'frames': self.num_time,
                                                           'channels': self.num_channel,
                                                           })
        return file_path

    def write_ome_tiff(self, dtype='uint16', file_path=None):
        if not file_path:
            file_path = tkFileDialog.asksaveasfilename()
        with tifffile.TiffWriter(file_path, imagej=True) as tif:
            array2write = self.stack.astype(dtype)
            tif.save(array2write, metadata={'axes': self.meta})
        return file_path


def read_tiff(file_path=None):
    if not file_path:
        file_path = tkFileDialog.askopenfilename()
        imageObj = tifffile.imread(file_path)
    return (imageObj, file_path)


def Read_1by1_TCYX(n_time, n_channel):
    for t in range(n_time):
        c_temp_list = []
        for c in range(n_channel):
            c_temp_list.append(read_tiff()[0])
        tArray = np.stack(c_temp_list).astype('float_')
        if t == 0:
            # imgArray = tArray[np.newaxis,...].copy()
            imgArray = tArray[np.newaxis, ...]
        else:
            imgArray = np.vstack([imgArray, tArray[np.newaxis, ...]])
    return imgArray


def Read_by_channel(n_channel):
    c_temp_list = []
    for c in range(n_channel):
        c_temp_list.append(read_tiff()[0])
    tArray = np.stack(c_temp_list, axis=1).astype('float_')
    return tArray


def load_msr(file_path=None):
    """Loads data from the czi file. The data is in a numpy array.
    :param file_path: path for the .czi file. Ask for a file in GUI if not provided.
    :returns: A dict with the name of the stack and the corresponding data
    """
    if not file_path:
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
    return (imgArray, file_path)


def subtract_background(inputstack, bg_mean_list):
    """
    Subtract background
    :param inputstack: an imageStack object
    :param bg_mean_list: averaged intensity array from `get_intensity_list` with `average_all_roi=True`
    :return: imageStack object
    """
    if inputstack.meta == 'CYX' and len(bg_mean_list.shape) == 1:
        subtracted = inputstack.stack.copy()
        for c in range(inputstack.num_channel):
            subtracted[c] = inputstack.stack[c] - bg_mean_list[c]
        subtracted[subtracted < 0] = 0
        return imageStack(imgArray=subtracted, meta='CYX')
    if inputstack.meta == 'TCYX' and len(bg_mean_list.shape) == 2:
        subtracted = inputstack.stack.copy()
        for t in range(inputstack.num_time):
            # c_temp_list = []
            for c in range(inputstack.num_channel):
                subtracted[t, c] = inputstack.stack[t, c] - bg_mean_list[t, c]
        subtracted[subtracted < 0] = 0
        return imageStack(imgArray=subtracted, meta='TCYX')


if __name__ == "__main__":
    img_array = Read_1by1_TCYX(n_time=2, n_channel=3)
    img_obj = imageStack(imgArray=img_array, meta='TCYX')
    # (img_array, path) = load_msr()
    # img_obj = imageStack(imgArray=img_array, meta='CYX')
    bg_roi = img_obj.draw_roi2(title="Please draw background")
    a = img_obj.get_intensity_list(bg_roi)
    b = img_obj.get_intensity_list(bg_roi, average_all_roi=True)
    sub_bg_obj = subtract_background(img_obj, b)
    sub_bg_obj.show_all_channels()
