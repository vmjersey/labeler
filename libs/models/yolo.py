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
        self.class_threshold = 0.8
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
 
        # Convert image so prediction will work
        self.prepare_image()
        
        time_before = time.time()
        prediction = self.model.predict(self.pred_image)
        time_after = time.time()
        prediction_time = time_after - time_before
        print("Model Prediction took:", prediction_time)


        orig_width = self.parent.image_shape[1]
        orig_height = self.parent.image_shape[0]

        time_before = time.time()
        for i in range(len(prediction)):
            # decode the output of the network
            self.decode_netout(prediction[i][0], self.anchors[i], self.class_threshold, self.pred_height, self.pred_width)
        time_after = time.time()
        prediction_time = time_after - time_before
        print("Decode Time:", prediction_time)

        time_before = time.time()
        # correct the sizes of the bounding boxes for the shape of the image
        self.correct_yolo_boxes(orig_height, orig_width, self.pred_height, self.pred_width)
        time_after = time.time()
        prediction_time = time_after - time_before
        print("Correction Time:", prediction_time)

        time_before = time.time()
        # suppress non-maximal boxes
        self.do_nms(0.5)
        time_after = time.time()
        prediction_time = time_after - time_before
        print("Non-maximal Time:", prediction_time)

        time_before = time.time()
        # get the details of the detected objects
        v_boxes, v_labels, v_scores = self.get_boxes()
        time_after = time.time()
        prediction_time = time_after - time_before
        print("Get Boxes Time:", prediction_time)

        box_coords = []
        # summarize what we found
        for i in range(len(v_boxes)):
            print(v_labels[i], v_scores[i])
            box = v_boxes[i]

            y1 = box.ymin
            x1 = box.xmin
            y2 = box.ymax
            x2 = box.xmax
            
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
            self.boxes[i].xmin = int((self.boxes[i].xmin - x_offset) / x_scale * image_w)
            self.boxes[i].xmax = int((self.boxes[i].xmax - x_offset) / x_scale * image_w)
            self.boxes[i].ymin = int((self.boxes[i].ymin - y_offset) / y_scale * image_h)
            self.boxes[i].ymax = int((self.boxes[i].ymax - y_offset) / y_scale * image_h)

    def bbox_iou(self, box1, box2):
        
        x11, y11, x12, y12 = [box1.xmin, box1.ymin, box1.xmax, box1.ymax]
        x21, y21, x22, y22 = [box2.xmin, box2.ymin, box2.xmax, box2.ymax]
        xA = np.maximum(x11, np.transpose(x21))
        yA = np.maximum(y11, np.transpose(y21))
        xB = np.minimum(x12, np.transpose(x22))
        yB = np.minimum(y12, np.transpose(y22))
        interArea = np.maximum((xB - xA + 1), 0) * np.maximum((yB - yA + 1), 0)
        boxAArea = (x12 - x11 + 1) * (y12 - y11 + 1)
        boxBArea = (x22 - x21 + 1) * (y22 - y21 + 1)

        iou = interArea / (boxAArea + np.transpose(boxBArea) - interArea)

        return iou

    def get_boxes(self):
        v_boxes, v_labels, v_scores = list(), list(), list()
        # enumerate all boxes
        for box in self.boxes:
            # enumerate all possible labels
            for i in range(len(self.labels)):
                # check if the threshold for this label is high enough
                if box.classes[i] > self.class_threshold:
                    v_boxes.append(box)
                    v_labels.append(self.labels[i])
                    v_scores.append(box.classes[i]*100)
                    # don't break, many labels may trigger for one box
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
                box = BoundBox(x-w/2, y-h/2, x+w/2, y+h/2, objectness, classes)
                self.boxes.append(box)

    def do_nms(self, nms_thresh):
        if len(self.boxes) > 0:
            nb_class = len(self.boxes[0].classes)
        else:
            return
        print(nb_class)
        for c in range(nb_class):
            sorted_indices = np.argsort([-box.classes[c] for box in self.boxes])
            for i in range(len(sorted_indices)):
                index_i = sorted_indices[i]
                if self.boxes[index_i].classes[c] == 0:
                    continue
                for j in range(i+1, len(sorted_indices)):
                    index_j = sorted_indices[j]
                    if self.bbox_iou(self.boxes[index_i], self.boxes[index_j]) >= self.class_threshold:
                        self.boxes[index_j].classes[c] = 0


class BoundBox:
    def __init__(self, xmin, ymin, xmax, ymax, objness = None, classes = None):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.objness = objness
        self.classes = classes
        self.label = -1
        self.score = -1
 
    def get_label(self):
        if self.label == -1:
            self.label = np.argmax(self.classes)
 
        return self.label
 
    def get_score(self):
        if self.score == -1:
            self.score = self.classes[self.get_label()]
 
        return self.score

