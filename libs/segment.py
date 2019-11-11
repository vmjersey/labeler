import wx
from libs.imaging import find_contours
from libs.grid import fill_grid
from matplotlib.patches import Rectangle

class SegmentFrame(wx.Frame):
    ''' 
        A class to set up the image transformations control frame
    '''
    def __init__(self,thing,parent):
        self.parent = parent

        wx.Frame.__init__(self,thing, title="Image Segmentation", size=(200,100),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.CLOSE_BOX)
       
         # Create Panel for Image Color Operations
        self.SegmentPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.SegmentPanel.SetBackgroundColour("dark gray")

        SPTitle= wx.StaticText(self.SegmentPanel, -1,)
        font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        SPTitle.SetFont(font)
        SPTitle.SetLabel("Suggest Bounding Boxes")
       
        SPsizer = wx.GridSizer(1, 1, 5, 5)
        SPsizer.Add(SPTitle, 0, wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL)
        self.SegmentPanel.SetSizer(SPsizer)



        # Checkbox to convert image to gray scale
        self.hbox = wx.CheckBox(self.SegmentPanel, label='Find Countours', pos=(20,20))
        self.hbox.SetValue(False)
        self.hbox.Bind(wx.EVT_CHECKBOX, self.on_h_check, self.hbox)

        
        self.SegmentPanel.SetSize(200,200)
        self.SegmentPanel.SetPosition((5,5))



        self.SetSize(415,450)
        self.Show(True)


    def on_h_check(self,event):
        '''
            Action taken when box is checked or unchecked
        '''
        if self.hbox.GetValue() == True:
            boxes = find_contours(self.parent,self.parent.current_image)
            # Draw all the rectangles
            for box in boxes:
                self.parent.draw_rect(box)

            # Populate grid
            fill_grid(self.parent)  
          
        self.parent.canvas.draw()



