import cv2
import numpy as np
import wx


def convert_bw(color_image):
    '''
        Convert a color image to black and white     
    '''
    gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    return gray_image

def read_image_as_bitmap(filepath):
    '''
        Take in a filepath to a jpeg or png image and returns a bitmap
    '''
    bitmap = wx.Image(filepath, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
    return bitmap

def write_image(master,imagepathname):
    '''
        Save image to a file with what ever edits have been done.
    '''
    master.figure.savefig(imagepathname)


