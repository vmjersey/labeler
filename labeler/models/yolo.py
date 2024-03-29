from imageai.Detection import ObjectDetection
import labeler

# Got the model and weights from here: 
# https://machinelearningmastery.com/how-to-perform-object-detection-with-yolov3-in-keras/

class YOLOv3():
    '''
        A class for the YOLO model
    '''

    def __init__(self,parent):
    
        self.models_path = labeler.__path__
        self.parent = parent 

        self.detector = ObjectDetection()
        self.detector.setModelTypeAsYOLOv3()
        
        self.detector.setModelPath(self.models_path + "/models/yolov3.h5")
        
        self.detector.loadModel()


    def predict(self):

        detections = self.detector.detectObjectsFromImage(
            input_image=self.parent.imagepath, 
            output_image_path="/tmp/test.jpg",
            minimum_percentage_probability=30)


        box_coords = []
        i=0
        for label in detections:

            print(i,": ",self.parent.imagepath,"\n    Label: ", label["name"] , "\n","   Probability: ", label["percentage_probability"], "\n","   Coordinates: ", label["box_points"] )
            print("--------------------------------")
            box=label["box_points"]            

            x1 = box[0]
            y1 = box[1]
            x2 = box[2]
            y2 = box[3]
            
            box_coords.append((int(x1),int(y1),int(x2),int(y2),label["name"]))
            i+=1
    

        return box_coords
        
