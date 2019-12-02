import wx
from libs.imaging import find_contours
from libs.grid import fill_grid
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



        # Checkbox to convert image to gray scale
        self.hbox = wx.CheckBox(self.SegmentPanel, label='Find Countours', pos=(20,25))
        self.hbox.SetValue(False)
        self.hbox.Bind(wx.EVT_CHECKBOX, self.on_h_check, self.hbox)

        
        self.SegmentPanel.SetSize(200,200)
        self.SegmentPanel.SetPosition((5,5))


         # Create Panel for Applying Model Segmentation
        self.ModelPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.ModelPanel.SetBackgroundColour("dark gray")

        MPTitle= wx.StaticText(self.ModelPanel, -1,)
        MPTitle.SetFont(font)
        MPTitle.SetLabel("Apply Model")

        MPsizer = wx.GridSizer(1, 1, 5, 5)
        MPsizer.Add(MPTitle, 0, wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL)
        self.ModelPanel.SetSizer(MPsizer)

        self.yolobox = wx.CheckBox(self.ModelPanel, label='YOLOv3', pos=(20,25))
        self.yolobox.SetValue(False)
        self.yolobox.Bind(wx.EVT_CHECKBOX, self.on_yolo_check, self.yolobox)

        self.yolomodel = None

        self.ModelPanel.SetSize(200,200)
        self.ModelPanel.SetPosition((205,5))

        self.SetSize(415,450)
        self.Show(True)


    def on_h_check(self,event):
        '''
            Action taken when box is checked or unchecked
        '''
        if self.hbox.GetValue() == True:
            boxes = find_contours(self.parent,self.parent.current_image)
            # Draw all the rectangles on canvas
            for box in boxes:
                self.parent.draw_rect(box)
                
            # Populate grid
            fill_grid(self.parent)  
            
            self.parent.canvas.draw()

    def on_yolo_check(self,event):
        '''
            Action taken when box is checked or unchecked
        '''
        if self.yolobox.GetValue() == True:
            from libs.models.yolo import YOLOv3
            if self.yolomodel == None:
                print("defining model")
                self.yolomodel = YOLOv3(self.parent)

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

            self.parent.canvas.draw()


