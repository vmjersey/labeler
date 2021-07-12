import wx
from labeler.imaging import find_contours
from labeler.grid import fill_grid
from matplotlib.patches import Rectangle
import time

class SegmentFrame(wx.Frame):
    ''' 
        A class to set up the image transformations control frame
    '''
    def __init__(self,thing,parent):
        self.parent = parent

        wx.Frame.__init__(self,thing, title="Image Segmentation", size=(200,100),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.CLOSE_BOX)
       
         # Create Panel for Image Segmentation
        self.SegmentPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.SegmentPanel.SetBackgroundColour("dark gray")

        SPTitle= wx.StaticText(self.SegmentPanel, -1,)
        font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        SPTitle.SetFont(font)
        SPTitle.SetLabel("Suggest Labels")
       
        SPsizer = wx.GridSizer(1, 1, 5, 5)
        SPsizer.Add(SPTitle, 0, wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL)
        self.SegmentPanel.SetSizer(SPsizer)



        # Checkbox to get contours
        self.hbox = wx.CheckBox(self.SegmentPanel, label='Find Countours', pos=(20,25))
        self.hbox.SetValue(False)
        self.hbox.Bind(wx.EVT_CHECKBOX, self.on_h_check, self.hbox)

        
        self.SegmentPanel.SetSize(200,200)
        self.SegmentPanel.SetPosition((5,5))


        # Create Panel for Applying Standard Model Segmentation
        self.ModelPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.ModelPanel.SetBackgroundColour("dark gray")

        MPTitle= wx.StaticText(self.ModelPanel, -1,)
        MPTitle.SetFont(font)
        MPTitle.SetLabel("Standard Models")

        MPsizer = wx.GridSizer(1, 1, 5, 5)
        MPsizer.Add(MPTitle, 0, wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL)
        self.ModelPanel.SetSizer(MPsizer)

        self.yolobox = wx.CheckBox(self.ModelPanel, label='YOLOv3', pos=(20,30))
        self.yolobox.SetValue(False)
        self.yolobox.Bind(wx.EVT_CHECKBOX, self.on_yolo_check, self.yolobox)

        self.yolobut = wx.Button(self.ModelPanel,label='Run',size=(50,30),pos=(110,30))
        self.yolobut.Bind(wx.EVT_BUTTON,self.on_yolo_run)

        self.yolomodel = None

        self.ModelPanel.SetSize(200,200)
        self.ModelPanel.SetPosition((205,5))


        # Create a Panel for applying custom user models
        self.UserPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.UserPanel.SetBackgroundColour("dark gray")

        UPTitle= wx.StaticText(self.UserPanel, -1,)
        UPTitle.SetFont(font)
        UPTitle.SetLabel("Custom Models")

        self.UserPanel.SetSize(200,200)
        self.UserPanel.SetPosition((5,205))



        self.SetSize(415,450)
        self.Show(True)


    def on_h_check(self,event):
        '''
            Action taken when box is checked or unchecked
        '''
        if self.hbox.GetValue() == True:
            boxes = find_contours(self.parent,self.parent.current_image)

            if len(boxes) > 99:
                self.parent.user_error("This algorithm found "+str(len(boxes))+" bounding boxes.  This is probalby not the correct method for segmenting this image.")
                return 0                

            # Draw all the rectangles on canvas
            for box in boxes:
                self.parent.draw_rect(box)
                
            # Populate grid
            fill_grid(self.parent)  
            
            self.parent.canvas.draw()

    def on_yolo_run(self,event):
        '''
            Action taken when yolo button is pushed
        '''

        if self.yolobox.GetValue() == False:
            # Load model and check box
            self.yolobox.SetValue(True)
            from labeler.models.yolo import YOLOv3
            if self.yolomodel == None:
                print("Defining YoloV3  model and loading weights")
                self.yolomodel = YOLOv3(self.parent)

        # Now run predictions
        time_before = time.time()
        boxes = self.yolomodel.predict()
        time_after = time.time()
        prediction_time = time_after - time_before
        print("Total Prediction Time:", prediction_time)

        # Draw all the rectangles on canvas
        for box in boxes:
            self.parent.draw_rect(box)

        # Populate grid
        fill_grid(self.parent)

        # Draw bounding boxes on canvas
        self.parent.canvas.draw()

    def on_yolo_check(self,event):
        '''
            Action taken when box is checked or unchecked: load the model but don't run prediction
        '''
        if self.yolobox.GetValue() == True:
            from labeler.models.yolo import YOLOv3
            if self.yolomodel == None:
                print("defining model")
                self.yolomodel = YOLOv3(self.parent)

