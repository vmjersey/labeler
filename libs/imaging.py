import cv2
import numpy as np
import wx


def gaussian_filtering(image):
    '''
        Apply a basic convolutional filter to image
    '''

    blur = cv2.GaussianBlur(image,(5,5),0)

    return blur


def average_filtering(image):
    '''
        Apply a basic convolutional filter to image
    '''

    blur = cv2.blur(image,(5,5))

    return blur 

def extract_bg(image):
    '''
        Extract foreground from image using basic OpenCV 
    '''
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)


    if len(image.shape) > 2:
        # if color image reshape mask back to three channels
        thresh = cv2.cvtColor(thresh,cv2.COLOR_GRAY2BGR)


    # Now subract the mask from the image
    segmented_image = cv2.subtract(image,thresh)

    return segmented_image

def extract_fg(image):
    '''
        Extract foreground from image using basic OpenCV 
    '''
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

   
    if len(image.shape) > 2:
        # if color image reshape mask back to three channels
        thresh = cv2.cvtColor(thresh,cv2.COLOR_GRAY2RGB)
        

    # Now subract the mask from the image
    segmented_image = cv2.subtract(image,thresh)

    return segmented_image

def convert_gs(master,image):
    '''
        Convert a color image to grayscale
    '''
    # If something is already a grayscale, probably need to convert 
    # back to original
    if len(image.shape) < 3:
        image = master.original_image.copy()
 
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

def convert_bw(image):
    '''
        Convert a color image to black and white     
    '''
    # If color convert to grayscale first
    if len(image.shape) >2:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image

    bw_image = cv2.adaptiveThreshold(gray_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    
    #(thresh, bw_image) = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY)
    
    return bw_image

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


