import wx
from libs.imaging import convert_bw,convert_gs,extract_fg,extract_bg,average_filtering,gaussian_filtering,median_filtering,bilateral_filtering,erosion_morph,dilation_morph,open_morph,closing_morph,gradient_morph,laplacian_morph,sobelx_morph,sobely_morph,convert_canny,convert_watershed


class TransFrame(wx.Frame):
    ''' 
        A class to set up the image transformations control frame
    '''
    def __init__(self,thing,parent):
        self.parent = parent

        wx.Frame.__init__(self,thing, title="Image Tools", size=(200,100),style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.CLOSE_BOX)
       
         # Create Panel for Image Color Operations
        self.ColorPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.ColorPanel.SetBackgroundColour("dark gray")

        CPTitle= wx.StaticText(self.ColorPanel, -1,)
        font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        CPTitle.SetFont(font)
        CPTitle.SetLabel("Color Options")
       
        CPsizer = wx.GridSizer(1, 1, 5, 5)
        CPsizer.Add(CPTitle, 0, wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL)
        self.ColorPanel.SetSizer(CPsizer)



        # Checkbox to convert image to gray scale
        self.gsbox = wx.CheckBox(self.ColorPanel, label='Gray Scale', pos=(20,20))
        self.gsbox.SetValue(False)
        self.gsbox.Bind(wx.EVT_CHECKBOX, self.on_gs_check, self.gsbox)

        # Checkbox to convert image to black and white lines
        self.bwbox = wx.CheckBox(self.ColorPanel, label='Black and White', pos=(20,40))
        self.bwbox.SetValue(False)
        self.bwbox.Bind(wx.EVT_CHECKBOX, self.on_bw_check, self.bwbox)
        
        
        self.ColorPanel.SetSize(200,200)
        self.ColorPanel.SetPosition((5,5))


        # Create panel for morphological operations
        self.ExtractionPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.ExtractionPanel.SetBackgroundColour("dark gray")

        EPTitle= wx.StaticText(self.ExtractionPanel, -1,style = wx.ALIGN_CENTER)
        EPTitle.SetFont(font)
        EPTitle.SetLabel("Extraction")

        EPsizer = wx.GridSizer(1, 1, 5, 5)
        EPsizer.Add(EPTitle, 0, wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL)
        self.ExtractionPanel.SetSizer(EPsizer)


        # Checkbox to extract foreground
        self.fgbox = wx.CheckBox(self.ExtractionPanel, label='Extract Foreground', pos=(20,20))
        self.fgbox.SetValue(False)
        self.fgbox.Bind(wx.EVT_CHECKBOX, self.on_fg_check, self.fgbox)

        # Checkbox to extract background
        self.bgbox = wx.CheckBox(self.ExtractionPanel, label='Extract Background', pos=(20,40))
        self.bgbox.SetValue(False)
        self.bgbox.Bind(wx.EVT_CHECKBOX, self.on_bg_check, self.bgbox)

        # Checkbox to convert image to canny
        self.cbox = wx.CheckBox(self.ExtractionPanel, label='Canny', pos=(20,60))
        self.cbox.SetValue(False)
        self.cbox.Bind(wx.EVT_CHECKBOX, self.on_c_check, self.cbox)

        # Checkbox to convert image to canny
        self.wsbox = wx.CheckBox(self.ExtractionPanel, label='Watershed', pos=(20,80))
        self.wsbox.SetValue(False)
        self.wsbox.Bind(wx.EVT_CHECKBOX, self.on_ws_check, self.wsbox)




        self.ExtractionPanel.SetSize(200,200)
        self.ExtractionPanel.SetPosition((205,5))


        # Create panel for morphological operations
        self.BlurPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.BlurPanel.SetBackgroundColour("dark gray")

        BPTitle= wx.StaticText(self.BlurPanel, -1,style = wx.ALIGN_CENTER)
        BPsizer = wx.GridSizer(1, 1, 5, 5)
        BPsizer.Add(BPTitle, 0, wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL)
        self.BlurPanel.SetSizer(BPsizer)


        BPTitle.SetFont(font)
        BPTitle.SetLabel("Filtering")


        # Checkbox for average blurring
        self.afbox = wx.CheckBox(self.BlurPanel, label='Averaging Filter', pos=(20,20))
        self.afbox.SetValue(False)
        self.afbox.Bind(wx.EVT_CHECKBOX, self.on_af_check, self.afbox)

        # Checkbox for Gaussian Filtering
        self.gfbox = wx.CheckBox(self.BlurPanel, label='Gaussian Filter', pos=(20,40))
        self.gfbox.SetValue(False)
        self.gfbox.Bind(wx.EVT_CHECKBOX, self.on_gf_check, self.gfbox) 

        # Checkbox for Median Filtering
        self.mfbox = wx.CheckBox(self.BlurPanel, label='Median Filter', pos=(20,60))
        self.mfbox.SetValue(False)
        self.mfbox.Bind(wx.EVT_CHECKBOX, self.on_mf_check, self.mfbox)
        
        # Checkbox for Bilateral Filtering
        self.bfbox = wx.CheckBox(self.BlurPanel, label='Bilateral Filter', pos=(20,80))
        self.bfbox.SetValue(False)
        self.bfbox.Bind(wx.EVT_CHECKBOX, self.on_bf_check, self.bfbox)


        self.BlurPanel.SetSize(200,200)
        self.BlurPanel.SetPosition((205,205)) 


        # Create panel for morphological operations
        self.MorphPanel = wx.Panel(self,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.MorphPanel.SetBackgroundColour("dark gray")
       
        #Set title in center 
        MPTitle= wx.StaticText(self.MorphPanel, -1,style = wx.ALIGN_CENTER)
        MPsizer = wx.GridSizer(1, 1, 5, 5)
        MPsizer.Add(MPTitle, 0, wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL)
        self.MorphPanel.SetSizer(MPsizer)


        MPTitle.SetFont(font)
        MPTitle.SetLabel("Transformations")

        # Checkbox for Erosion Morphology
        self.embox = wx.CheckBox(self.MorphPanel, label='Erosion', pos=(20,20))
        self.embox.SetValue(False)
        self.embox.Bind(wx.EVT_CHECKBOX, self.on_em_check, self.embox)

        # Checkbox for Dialation Morphology
        self.dmbox = wx.CheckBox(self.MorphPanel, label='Dilation', pos=(20,40))
        self.dmbox.SetValue(False)
        self.dmbox.Bind(wx.EVT_CHECKBOX, self.on_dm_check, self.dmbox)

        # Checkbox for Opening Morphology
        self.ombox = wx.CheckBox(self.MorphPanel, label='Opening', pos=(20,60))
        self.ombox.SetValue(False)
        self.ombox.Bind(wx.EVT_CHECKBOX, self.on_om_check, self.ombox)

        # Checkbox for Closing Morphology
        self.cmbox = wx.CheckBox(self.MorphPanel, label='Closing', pos=(20,80))
        self.cmbox.SetValue(False)
        self.cmbox.Bind(wx.EVT_CHECKBOX, self.on_cm_check, self.cmbox)

        # Checkbox for Gradient Morphology
        self.gmbox = wx.CheckBox(self.MorphPanel, label='Gradient', pos=(20,100))
        self.gmbox.SetValue(False)
        self.gmbox.Bind(wx.EVT_CHECKBOX, self.on_gm_check, self.gmbox)

        # Checkbox for Laplacian Morphology
        self.lmbox = wx.CheckBox(self.MorphPanel, label='Laplacian', pos=(20,120))
        self.lmbox.SetValue(False)
        self.lmbox.Bind(wx.EVT_CHECKBOX, self.on_lm_check, self.lmbox)

        # Checkbox for Sobel X Morphology
        self.sxbox = wx.CheckBox(self.MorphPanel, label='Sobel X Axis', pos=(20,140))
        self.sxbox.SetValue(False)
        self.sxbox.Bind(wx.EVT_CHECKBOX, self.on_sx_check, self.sxbox)

        # Checkbox for Sobel Y Morphology
        self.sybox = wx.CheckBox(self.MorphPanel, label='Sobel Y Axis', pos=(20,160))
        self.sybox.SetValue(False)
        self.sybox.Bind(wx.EVT_CHECKBOX, self.on_sy_check, self.sybox)



        self.MorphPanel.SetSize(200,200)
        self.MorphPanel.SetPosition((5,205))


        self.SetSize(415,450)
        self.Show(True)

    def reset_boxes(self):
        '''
            Uncheck the boxes
        '''
        # Uncheck all the boxes
        self.bwbox.SetValue(False)
        self.gsbox.SetValue(False)
        self.cbox.SetValue(False)
        self.wsbox.SetValue(False)
        self.fgbox.SetValue(False)
        self.bgbox.SetValue(False)
        self.afbox.SetValue(False)
        self.gfbox.SetValue(False)
        self.mfbox.SetValue(False)
        self.bfbox.SetValue(False)
        self.embox.SetValue(False)
        self.dmbox.SetValue(False)
        self.ombox.SetValue(False)
        self.cmbox.SetValue(False)
        self.gmbox.SetValue(False)
        self.lmbox.SetValue(False)
        self.sxbox.SetValue(False)
        self.sybox.SetValue(False)

        # Put old image back
        self.parent.current_image = self.parent.original_image

    def on_sx_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.sxbox.GetValue() == True:
            self.parent.current_image = sobelx_morph(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_sy_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.sybox.GetValue() == True:
            self.parent.current_image = sobely_morph(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()

        else:
            self.reset_boxes()


    def on_lm_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.lmbox.GetValue() == True:
            self.parent.current_image = laplacian_morph(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()


    def on_cm_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.cmbox.GetValue() == True:
            self.parent.current_image = closing_morph(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()


    def on_gm_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.gmbox.GetValue() == True:
            self.parent.current_image = gradient_morph(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_om_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.ombox.GetValue() == True:
            self.parent.current_image = open_morph(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()


    def on_dm_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.dmbox.GetValue() == True:
            self.parent.current_image = dilation_morph(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_em_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.embox.GetValue() == True:
            self.parent.current_image = erosion_morph(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()


    def on_bf_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.bfbox.GetValue() == True:
            self.parent.current_image = bilateral_filtering(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_mf_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.mfbox.GetValue() == True:
            self.parent.current_image = median_filtering(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_gf_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.gfbox.GetValue() == True:
            self.parent.current_image = gaussian_filtering(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_af_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.afbox.GetValue() == True:
            self.parent.current_image = average_filtering(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_bg_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.bgbox.GetValue() == True:
            self.parent.current_image = extract_bg(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_fg_check(self,e):
        '''
            Action taken when box is checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.fgbox.GetValue() == True:
            self.parent.current_image = extract_fg(self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_gs_check(self,e):
        '''
            Action taken with box is either checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.gsbox.GetValue() == True:
            self.parent.current_image = convert_gs(self.parent,self.parent.current_image)
            # You're goint to want to uncheck the bwbox too
            #self.bwbox.SetValue(False)
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_bw_check(self,e):
        '''
            Action taken with box is either checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.bwbox.GetValue() == True:
            self.parent.current_image = convert_bw(self.parent.current_image)
            # You're going to want to uncheck gsbox too
            #self.gsbox.SetValue(False)
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_c_check(self,e):
        '''
            Action taken with box is either checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.cbox.GetValue() == True:
            self.parent.current_image = convert_canny(self.parent,self.parent.current_image)
            # You're going to want to uncheck gsbox too
            #self.gsbox.SetValue(False)
            self.parent.RefreshImage()
        else:
            self.reset_boxes()

    def on_ws_check(self,e):
        '''
            Action taken with box is either checked or unchecked
        '''
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.wsbox.GetValue() == True:
            self.parent.current_image = convert_watershed(self.parent,self.parent.current_image)
            # You're going to want to uncheck gsbox too
            #self.gsbox.SetValue(False)
            self.parent.RefreshImage()

        else:
            self.reset_boxes()

