from keras.models import load_model
import cv2
import numpy as np
import matplotlib.pyplot as plt
from numpy import expand_dims
from matplotlib.patches import Rectangle
import os
import time
import tensorflow as tf


# Got the model and weights from here: 
# https://machinelearningmastery.com/how-to-perform-object-detection-with-yolov3-in-keras/

class YOLOv3():
    '''
        A class for the YOLO model
    '''

    def __init__(self,parent):
        self.parent = parent
        # Define the shape of the input image
        self.pred_height = 416
        self.pred_width = 416
        # Load the model architecture and weights from file
        self.model = load_model(self.parent.root_dir+"/libs/models/yolov3.h5")
        # Set Anchors file will use
        self.anchors = [[116,90, 156,198, 373,326], [30,61, 62,45, 59,119], [10,13, 16,30, 33,23]]
        self.class_threshold = 0.97
        self.labels = [
            "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck",
            "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
            "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
            "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
            "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
            "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana",
            "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
            "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor","laptop", "mouse",
            "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
            "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
            ]



    def predict(self):
       
        self.boxes = []
        self.classes = []
 
        # Convert image so prediction will work
        self.prepare_image()
        
        prediction = self.model.predict(self.pred_image)

        orig_width = self.parent.image_shape[1]
        orig_height = self.parent.image_shape[0]

        for i in range(len(prediction)):
            # decode the output of the network
            self.decode_netout(prediction[i][0], self.anchors[i], self.class_threshold, self.pred_height, self.pred_width)

        # correct the sizes of the bounding boxes for the shape of the image
        self.correct_yolo_boxes(orig_height, orig_width, self.pred_height, self.pred_width)

        # get the details of the detected objects
        v_boxes, v_labels, v_scores = self.get_boxes()

        box_coords = []
        # summarize what we found
        for i in range(len(v_boxes)):
            box = v_boxes[i]

            x1 = box[0]
            y1 = box[1]
            x2 = box[2]
            y2 = box[3]
            
            box_coords.append((int(x1),int(y1),int(x2),int(y2),v_labels[i]))

        return box_coords
        
    def prepare_image(self):
       
        self.pred_image = self.parent.current_image.copy()
        self.pred_image = cv2.resize(self.pred_image,(self.pred_width,self.pred_height))
        self.pred_image = self.pred_image.astype('float32')
        self.pred_image /= 255.0

        self.pred_image = expand_dims(self.pred_image, 0)

    def _sigmoid(self,x):
        return 1. / (1. + np.exp(-x))

    def correct_yolo_boxes(self, image_h, image_w, net_h, net_w):
        new_w, new_h = net_w, net_h

        for i in range(len(self.boxes)):
            x_offset, x_scale = (net_w - new_w)/2./net_w, float(new_w)/net_w
            y_offset, y_scale = (net_h - new_h)/2./net_h, float(new_h)/net_h
            self.boxes[i][0] = int((self.boxes[i][0] - x_offset) / x_scale * image_w)
            self.boxes[i][1] = int((self.boxes[i][1] - x_offset) / x_scale * image_w)
            self.boxes[i][2] = int((self.boxes[i][2] - y_offset) / y_scale * image_h)
            self.boxes[i][3] = int((self.boxes[i][3] - y_offset) / y_scale * image_h)

    def get_boxes(self):
        v_boxes, v_labels, v_scores = list(), list(), list()
        # enumerate all boxes
        for b in range(len(self.boxes)):
            box = self.boxes[b]
            # enumerate all possible labels
            indices = np.argwhere(self.classes[b] > self.class_threshold)

            if indices.shape[0] == 0:
                continue
            else:
                for indice in indices:
                    i = indice[0]
                    v_boxes.append(box)
                    v_labels.append(self.labels[i])
                    v_scores.append(self.classes[b][i]*100)

        return v_boxes, v_labels, v_scores

    def decode_netout(self, netout, anchors, obj_thresh, net_h, net_w):
        grid_h, grid_w = netout.shape[:2]
        nb_box = 3
        netout = netout.reshape((grid_h, grid_w, nb_box, -1))
        nb_class = netout.shape[-1] - 5
        netout[..., :2]  = self._sigmoid(netout[..., :2])
        netout[..., 4:]  = self._sigmoid(netout[..., 4:])
        netout[..., 5:]  = netout[..., 4][..., np.newaxis] * netout[..., 5:]
        netout[..., 5:] *= netout[..., 5:] > obj_thresh

        for i in range(grid_h*grid_w):
            row = i / grid_w
            col = i % grid_w
            for b in range(nb_box):
                # 4th element is objectness score
                objectness = netout[int(row)][int(col)][b][4]
                if(objectness.all() <= obj_thresh): continue
                # first 4 elements are x, y, w, and h
                x, y, w, h = netout[int(row)][int(col)][b][:4]
                x = (col + x) / grid_w # center position, unit: image width
                y = (row + y) / grid_h # center position, unit: image height
                w = anchors[2 * b + 0] * np.exp(w) / net_w # unit: image width
                h = anchors[2 * b + 1] * np.exp(h) / net_h # unit: image height
                # last elements are class probabilities
                classes = netout[int(row)][col][b][5:]
                box = np.array([x-w/2, y-h/2, x+w/2, y+h/2, objectness])
                self.classes.append(classes)
                self.boxes.append(box)
