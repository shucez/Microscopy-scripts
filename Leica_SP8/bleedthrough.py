"""
bleedthrough.py  -- packages for dealing with bleedthrough between channels
Shuce Zhang, 21 June 2019
mailto:shuce@ualberta.ca
Version 2 supporting python3   Oct 12, 2019
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


def read_tiff(file_path=None):
    if not file_path:
        file_path = tkFileDialog.askopenfilename()
        imageObj = tifffile.imread(file_path)
    return (imageObj, file_path)


def show_all_channels(multi_channel, title=None):
    """
    show images of all channels in many rows
    :param multi_channel: 3d np.array image stack
    :param title: text, title for GUI interface
    :return: 0
    """
    fig = plt.figure()
    if len(multi_channel) >= 4:
        ncol = ceil(sqrt(len(multi_channel)))
        nrow = ceil(len(multi_channel) / ncol)
    else:
        ncol = len(multi_channel)
        nrow = 1
    for i in range(len(multi_channel)):
        fig.add_subplot(nrow, ncol, i + 1)
        plt.imshow(multi_channel[i], cmap='gray')
        if title and i == 0:
            plt.title(title)
    fig.show()
    return fig


def show_all_channels2(multi_channel, title=None):
    """
    show images of all channels in 1 row
    :param multi_channel: 3d np.array image stack
    :param title: text, title for GUI interface
    :return: 0
    """
    fig = plt.figure()
    ncol = len(multi_channel)
    # nrow = ceil(len(multi_channel)/ncol)
    for i in range(len(multi_channel)):
        fig.add_subplot(1, ncol, i + 1)
        plt.imshow(multi_channel[i], cmap='gray')  # last one first
        if title and i == 0:
            plt.title(title)
    fig.show()
    return fig

def show_all_channels_TCYX(multi_channel, title=None):
    """
    show images of all channels in many rows
    :param multi_channel: 3d np.array image stack
    :param title: text, title for GUI interface
    :return: 0
    """
    if len(multi_channel.shape) == 3:
        fig = plt.figure()
        if len(multi_channel) >= 4:
            ncol = ceil(sqrt(len(multi_channel)))
            nrow = ceil(len(multi_channel) / ncol)
        else:
            ncol = len(multi_channel)
            nrow = 1
        for i in range(len(multi_channel)):
            fig.add_subplot(nrow, ncol, i + 1)
            plt.imshow(multi_channel[i], cmap='gray')
            if title and i == 0:
                plt.title(title)
        fig.show()
        return fig

    if len(multi_channel.shape) == 4:
        fig = plt.figure()
        n_T = multi_channel.shape[0]
        n_C = multi_channel.shape[1]
        T = 0
        if n_C >= 4:
            ncol = ceil(sqrt(n_C))
            nrow = ceil(n_C / ncol)
        else:
            ncol = n_C
            nrow = 1
        im_list = []
        for i in range(n_C):
            fig.add_subplot(nrow, ncol, i + 1)
            im_list.append(plt.imshow(multi_channel[T][i], cmap='gray'))
            if title and i == 0:
                plt.title(title)
        axb = plt.axes([0.15, 0.1, 0.65, 0.03])
        sb = Slider(axb, 'T', 0, (n_T - 1), valinit=T, valfmt='%0.0f', valstep=1)

        def update(val):
            for i in range(n_C):
                T = sb.val
                # fig.add_subplot(nrow, ncol, i + 1)
                im_list[i].set_array(multi_channel[T][i])

        sb.on_changed(update)
        fig.show()
        return fig


def draw_roi(current_image, title="Click on the button to add a new ROI"):
    """
    Draw ROI when based on 1 channel
    :param current_image: 2d np.array, one channel
    :param title: title for the GUI
    :return:multi_ROI object object
    """
    plt.imshow(current_image, interpolation='nearest', cmap='gray')
    # fig = plt.imshow(current_image, interpolation='nearest', cmap='gray')
    # plt.title(title)
    multi_roi = MultiRoi()
    # multi_roi = MultiRoi(fig=fig)
    print("finished draw_roi")
    return multi_roi


def draw_roi2(multi_channel, title="Click on the button to add a new ROI"):
    """
    Draw ROI when displaying all channels in a image stack
    :param multi_channel: image stack, np.array, generated by load_msr
    :param title: title for the GUI
    :return:multi_ROI object object
    """
    # fig = show_all_channels2(multi_channel, title=title)
    fig = show_all_channels(multi_channel, title=title)
    # plt.imshow(current_image, interpolation='nearest', cmap='gray')
    # plt.title(title)
    multi_roi = MultiRoi(fig=fig, ax=fig.axes[0])
    print("finished draw_roi")
    return multi_roi


def get_intensity_list(multi_roi, multi_channel):
    all_list = []
    if len(multi_roi.rois):
        for channel in multi_channel:
            channel_list = np.array([])
            for name, roi in multi_roi.rois.items():
                mean, std = roi.get_mean_and_std(channel)
                # print(mean)
                channel_list = np.append(channel_list, mean)
            all_list.append(channel_list)
        final_list = np.stack(all_list)  # type: ndarray
        return final_list
    else:
        return np.zeros(len(multi_channel))


def subtract_background(multi_channel, bg_mean_list):
    subtracted = multi_channel.copy()
    for i in range(len(multi_channel)):
        subtracted[i] = multi_channel[i] - bg_mean_list[i]
    return subtracted


def show_all_channels_with_roi(multi_channel, multi_roi):
    """
    show channels on many rows
    :param multi_channel: np.array, 3-d stack
    :param multi_roi: roi object
    :return: 0
    """
    fig = plt.figure()
    if len(multi_channel) >= 4:
        ncol = ceil(sqrt(len(multi_channel)))
        nrow = ceil(len(multi_channel) / ncol)
    else:
        ncol = len(multi_channel)
        nrow = 1
    for i in range(len(multi_channel)):
        fig.add_subplot(nrow, ncol, i + 1)
        plt.imshow(multi_channel[i], cmap='gray')
        names = []
        for name, roi in multi_roi.rois.items():
            roi.display_roi()
            roi.display_mean(multi_channel[i])
            names.append(name)
    # plt.legend(roi_names, bbox_to_anchor=(1.2, 1.05))
    fig.show()
    return fig


def show_all_channels_with_roi2(multi_channel, multi_roi):
    """
    show channels on 1 row
    :param multi_channel: np.array, 3-d stack
    :param multi_roi: roi object
    :return: 0
    """
    fig = plt.figure()
    ncol = len(multi_channel)
    # nrow = ceil(len(multi_channel)/ncol)
    for i in range(len(multi_channel)):
        fig.add_subplot(1, ncol, i + 1)
        plt.imshow(multi_channel[i], cmap='gray')
        names = []
        for name, roi in multi_roi.rois.items():
            roi.display_roi()
            roi.display_mean(multi_channel[i])
            names.append(name)
    # plt.legend(roi_names, bbox_to_anchor=(1.2, 1.05))
    plt.show()
    return 0


def get_slope(roi_list):
    """
    calculate the bleed-through coefficient by linear regression, y-intercept fixed at 0
    :param roi_list: intensity list generated by get_intensity_list
    :return: array of slopes, array of standard deviation
    """
    num_channel = len(roi_list)
    slope_array = np.zeros([num_channel, num_channel])
    rsq_array = np.zeros([num_channel, num_channel])
    for i in range(num_channel):
        for j in range(num_channel):
            # reg = linregress(roi_list[i], roi_list[j])
            # slope = reg.slope
            # rsq = reg.rvalue
            x = roi_list[i][:, np.newaxis]
            y = roi_list[j]
            slope, SSE, _, _, = np.linalg.lstsq(x, y, rcond=None)
            rsq = 1 - (SSE / ((y ** 2).sum() - (len(y) * (y.mean()) ** 2)))
            slope_array[i][j] = float(slope)
            rsq_array[i][j] = float(rsq)
            if i != j:
                print("Channel", i + 1, "to Channel", j + 1, slope, rsq)
    return slope_array, rsq_array


def get_coefficient(roi_list):
    """
    calculate the bleed-through coefficient by averaging the ratio
    :param roi_list: intensity list generated by get_intensity_list
    :return: array of slopes, array of standard deviation
    """
    num_channel = len(roi_list)
    slope_array = np.zeros([num_channel, num_channel])
    std_array = np.zeros([num_channel, num_channel])
    for i in range(num_channel):
        for j in range(num_channel):
            # reg = linregress(roi_list[i], roi_list[j])
            slp = roi_list[j] / roi_list[i]
            slope = slp.mean()
            sd = slp.std()
            slope_array[i][j] = slope
            std_array[i][j] = sd
            if i != j:
                print("Channel", i + 1, "to Channel", j + 1, slope, sd)
    return slope_array, std_array


def subtract_bt(multi_channel, bt_array):
    num_channel = len(multi_channel)
    new_list = []
    for j in range(num_channel):
        temp = multi_channel[j].copy()
        for i in range(num_channel):
            if i != j:
                temp = temp - bt_array[i][j] * multi_channel[i]
        new_list.append(temp)
    new_stack = np.stack(new_list)
    return new_stack


class BleedThroughChart(tk.Frame):
    def __init__(self, nrow, ncol=None, master=None, matrix=None):
        tk.Frame.__init__(self, master)
        self.grid()
        if not ncol:
            ncol = nrow
        self.nrow = nrow
        self.ncol = ncol
        self.entry_all = []
        self.array_all = np.zeros([self.nrow, self.ncol])
        if matrix:
            self.array_all = matrix
        self.create_widgets()

    def create_widgets(self):
        header = tk.Label(self, width=20, text="from {row} | to {column}")
        header.grid(row=0, column=0)
        for i in range(self.ncol):
            channel_label_row = tk.Label(self, text="Channel" + str(i + 1))
            channel_label_row.grid(row=i + 1, column=0)
        for j in range(self.ncol):
            channel_label_col = tk.Label(self, text="Channel" + str(j + 1))
            channel_label_col.grid(row=0, column=j + 1)
        self.entry_all = []
        for i in range(self.nrow):
            entry_row = []
            for j in range(self.ncol):
                if i == j:
                    lab = tk.Label(self, text="0")
                    lab.grid(column=j + 1, row=i + 1)
                    entry_row.append(0)
                else:
                    v = tk.StringVar(self, value=self.array_all[i][j])
                    e = tk.Entry(self, textvariable=v)
                    e.grid(column=j + 1, row=i + 1)
                    entry_row.append(e)
            self.entry_all.append(entry_row)
        tk.Button(text='Fetch', command=(lambda: self.on_press())).grid()

    def on_press(self):
        print("clicked")
        for i in range(self.nrow):
            for j in range(self.ncol):
                if self.entry_all[i][j]:
                    self.array_all[i][j] = float(self.entry_all[i][j].get())
                else:
                    self.array_all[i][j] = 0
        self.master.destroy()
