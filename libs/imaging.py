import cv2
import numpy as np



def convert_bw(color_image):

    gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    return gray_image


