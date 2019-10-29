import wx
from libs.imaging import convert_bw,convert_gs,extract_fg,extract_bg,average_filtering,gaussian_filtering


class TransFrame(wx.Frame):
    ''' 
        A class to set up the image transformations control frame
    '''
    def __init__(self,thing,parent):
        self.parent = parent

        wx.Frame.__init__(self,thing, title="Image Tools", size=(200,100))
        # Create Panel for Image Transformations Tools
        self.TransPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.TransBox = wx.BoxSizer(wx.VERTICAL)
        self.TransBox.Add(self.TransPanel)
        self.TransPanel.SetBackgroundColour("green")

        
        # Check boxes to convert image to gray scale
        self.gsbox = wx.CheckBox(self.TransPanel, label='Gray Scale', pos=(20,10))
        self.gsbox.SetValue(False)
        self.gsbox.Bind(wx.EVT_CHECKBOX, self.on_gs_check, self.gsbox)

        # Check box to convert image to black and white lines
        self.bwbox = wx.CheckBox(self.TransPanel, label='Black and White', pos=(250,10))
        self.bwbox.SetValue(False)
        self.bwbox.Bind(wx.EVT_CHECKBOX, self.on_bw_check, self.bwbox)

        # Checkbox to extract foreground
        self.fgbox = wx.CheckBox(self.TransPanel, label='Extract Foreground', pos=(20,40))
        self.fgbox.SetValue(False)
        self.fgbox.Bind(wx.EVT_CHECKBOX, self.on_fg_check, self.fgbox)

        # Checkbox to extract background
        self.bgbox = wx.CheckBox(self.TransPanel, label='Extract Background', pos=(250,40))
        self.bgbox.SetValue(False)
        self.bgbox.Bind(wx.EVT_CHECKBOX, self.on_bg_check, self.bgbox)

        # Checkbox for average blurring
        self.afbox = wx.CheckBox(self.TransPanel, label='Averaging Filter', pos=(20,200))
        self.afbox.SetValue(False)
        self.afbox.Bind(wx.EVT_CHECKBOX, self.on_af_check, self.afbox)

        # Checkbox for Gaussian Filtering
        self.gfbox = wx.CheckBox(self.TransPanel, label='Gaussian Filter', pos=(20,220))
        self.gfbox.SetValue(False)
        self.gfbox.Bind(wx.EVT_CHECKBOX, self.on_gf_check, self.gfbox) 

        

        self.SetSize(500,500)
        self.Show(True)

    def clear_boxes(self):
        '''
            Uncheck the boxes
        '''
        # Uncheck all the boxes
        self.bwbox.SetValue(False)
        self.gsbox.SetValue(False)
        self.fgbox.SetValue(False)
        self.bgbox.SetValue(False)
        self.afbox.SetValue(False)
        self.gfbox.SetValue(False)

    def on_gf_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.gfbox.GetValue() == True:
            self.parent.current_image = gaussian_filtering(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.DisplayImage()
        else:
            self.parent.current_image = self.parent.original_image
            self.clear_boxes()
            self.parent.DisplayImage()

    def on_af_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.afbox.GetValue() == True:
            self.parent.current_image = average_filtering(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.DisplayImage()
        else:
            self.parent.current_image = self.parent.original_image
            self.clear_boxes()
            self.parent.DisplayImage()

    def on_bg_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.bgbox.GetValue() == True:
            self.parent.current_image = extract_bg(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.DisplayImage()
        else:
            self.parent.current_image = self.parent.original_image
            self.clear_boxes()
            self.parent.DisplayImage()


    def on_fg_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.fgbox.GetValue() == True:
            self.parent.current_image = extract_fg(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.DisplayImage()
        else:
            self.parent.current_image = self.parent.original_image
            self.clear_boxes()
            self.parent.DisplayImage()

    def on_gs_check(self,e):
        '''
            Action taken with box is either checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.gsbox.GetValue() == True:
            self.parent.current_image = convert_gs(self.parent,self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.bwbox.SetValue(False)
            self.parent.DisplayImage()
        else:
            self.parent.current_image = self.parent.original_image
            self.clear_boxes()
            self.parent.DisplayImage()

    def on_bw_check(self,e):
        '''
            Action taken with box is either checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.bwbox.GetValue() == True:
            self.parent.current_image = convert_bw(self.parent.current_image)
            # You're going to want to uncheck gsbox too
            self.gsbox.SetValue(False)
            self.parent.DisplayImage()
        else:
            self.parent.current_image = self.parent.original_image
            self.clear_boxes()
            self.parent.DisplayImage()

