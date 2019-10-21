#!/usr/bin/env python3

import wx
import wx.grid as gridlib
from libs.imaging import convert_bw
from libs.utils import check_inside_rect
import numpy as np
import cv2
from PIL import Image   
import matplotlib       
matplotlib.use('WXAgg')
# Matplotlib elements used to draw the bounding rectangle
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

class ImageLabeler(wx.App):
    '''
    The Main Application Class
    '''

    def __init__(self):

        wx.App.__init__(self) 

        self.frame = wx.Frame(None, title='Image Labeler')
        
        # Intitialise the matplotlib figure
        self.figure = Figure()

        # Create an axes, turn off the labels and add them to the figure
        self.axes = plt.Axes(self.figure,[0,0,1,1])      
        self.axes.set_axis_off() 
        self.figure.add_axes(self.axes) 

        # Add the figure to the wxFigureCanvas
        self.canvas = FigureCanvas(self.frame, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Hide()
        
        # Set Crosshair as mouse cursor.
        self.canvas.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        
        # What mode is the cursor in: bb,toolbar
        self.cursor_mode = "bb"

        # Connect the mouse events to their relevant callbacks
        self.canvas.mpl_connect('button_press_event',   self.OnLeftDown)
        self.canvas.mpl_connect('button_release_event', self.OnLeftUp)
        self.canvas.mpl_connect('motion_notify_event',  self.OnMotion)
        self.canvas.mpl_connect('key_press_event', self.OnKeyDown)

        # Lock to stop the motion event from behaving badly when the mouse isn't pressed
        self.frame.pressed = False

        # Setting up the menu.
        filemenu  = wx.Menu()
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", "Information About This Program")
        menuOpen  = filemenu.Append(wx.ID_OPEN,  "&Open",  "Open File")
        menuExit  = filemenu.Append(wx.ID_EXIT,  "&Exit",  "Exit Image Labeler")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.


        # Set events.
        self.frame.Bind(wx.EVT_MENU, self.OnFileAbout, menuAbout)
        self.frame.Bind(wx.EVT_MENU, self.OnFileOpen, menuOpen)
        self.frame.Bind(wx.EVT_MENU, self.OnFileExit, menuExit)

        #Keep track of how many images you have displayed
        self.imagecounter = 0

        self.imagepath = "./image.jpg"

        # Create Panel to display Bounding Box Coordinates
        self.BBPanel = wx.Panel(self.frame,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.BBPanel.SetBackgroundColour("red")


        # Create the Grid to Hold the Coordinates
        self.BBGrid = gridlib.Grid(self.BBPanel)
        self.BBGrid.CreateGrid(100, 5)
        self.BBGrid.SetColLabelValue(0, "X1")
        self.BBGrid.SetColLabelValue(1, "Y1")
        self.BBGrid.SetColLabelValue(2, "X2")
        self.BBGrid.SetColLabelValue(3, "Y2")
        self.BBGrid.SetColLabelValue(4, "Label")

 
        BBsizer = wx.BoxSizer(wx.VERTICAL)
        BBsizer.Add(self.BBGrid,1,wx.EXPAND|wx.ALL)
        self.BBPanel.SetSizer(BBsizer)
    


        # Create Panel for Image Controls.
        self.ControlPanel = wx.Panel(self.frame,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)

        # Set A box sizer and add image inside
        self.ControlBox = wx.BoxSizer(wx.VERTICAL)
        self.ControlBox.Add(self.ControlPanel)
        self.ControlPanel.SetBackgroundColour("red")

        # Convert image to black and white
        self.bwbox = wx.CheckBox(self.ControlPanel, label='Black and White', pos=(20,10))
        self.bwbox.SetValue(False)
        self.bwbox.Bind(wx.EVT_CHECKBOX, self.on_bw_check, self.bwbox)


         
        self.sibut = wx.ToggleButton(self.ControlPanel,2,"Zoom", pos=(400,5))
        self.sibut.Bind(wx.EVT_TOGGLEBUTTON,self.zoom)
         
        self.hmbut = wx.ToggleButton(self.ControlPanel,2,"Home", pos=(300,5))
        self.hmbut.Bind(wx.EVT_TOGGLEBUTTON,self.home)
         
        self.hibut = wx.ToggleButton(self.ControlPanel,2,"Pan",  pos=(200,5))
        self.hibut.Bind(wx.EVT_TOGGLEBUTTON,self.pan)
         



        # Hold list of rectangle coordinates
        self.rect_list = []
        # Hold list of rectangle objects
        self.rect_obj_list = []

        # A Statusbar in the bottom of the window
        self.frame.CreateStatusBar()
        self.frame.Show(True)

        self.NewImage() 


    def toggle_cursor_mode(self,button):
        '''  
            Change cursor_mode between bb and toolbar 
            Changes button color
        '''

        if self.cursor_mode == "toolbar":
            self.cursor_mode = "bb"
            button.SetBackgroundColour("green")

        else:
            self.cursor_mode = "toolbar"
            button.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        self.ControlPanel.Refresh()


    def zoom(self,event):
        ''' Use Matplotlibs zoom tool'''
        self.toggle_cursor_mode(self.sibut)
        self.toolbar.zoom()
 
    def home(self,event):
        ''' Return view back to original position'''
        self.toggle_cursor_mode(self.hmbut)
        self.toolbar.home()
         
    def pan(self,event):
        '''Uses Matplotlibs pan tool'''
        self.toggle_cursor_mode(self.hibut)
        self.toolbar.pan()
 

    def OnFileExit(self,event):
        print("Exiting...")
        self.frame.Close()        

    def OnFileOpen(self,event):
        # Get the file path you wan to open.
        with wx.FileDialog(self.frame, "Open Image File", 
            wildcard="Image Files *.png|*.jpg", 
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            self.imagepath = pathname

            self.NewImage()


    def OnFileAbout(self,event):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self.frame, "A GUI for labeling images", "About Image Labeler", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnKeyDown(self,event):
        if event.key == 'delete':
            self.OnDelete()

    def OnLeftDown(self, event):

        found = 0
        current_x = event.xdata
        current_y = event.ydata

        for i in range(len(self.rect_list)):
            rect = self.rect_list[i]
            result = check_inside_rect((current_x,current_y),rect)
            if result == 1:
                self.selected_rect = i
                found+=1        


        if found > 0:
            print("Found: ",self.selected_rect)
            self.change_rect_color()
            return 0


        if self.cursor_mode == "toolbar":
            return 0


        # Initialise the rectangle
        self.rect = Rectangle((0,0), 1, 1, facecolor='None', edgecolor='green',linewidth='2')

        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.axes.add_patch(self.rect)
        self.rect_obj_list.append(self.rect)


        # Check the mouse press was actually on the canvas
        if event.xdata is not None and event.ydata is not None:
            # Upon initial press of the mouse record the origin and record the mouse as pressed
            self.frame.pressed = True
            self.rect.set_linestyle('dashed')
            self.x0 = event.xdata
            self.y0 = event.ydata


    def OnLeftUp(self,event):

        # Check that the mouse was actually pressed on the canvas to begin with and this isn't a rouge mouse 
        # release event that started somewhere else
        if self.frame.pressed:

            # Upon release draw the rectangle as a solid rectangle
            self.frame.pressed = False
            self.rect.set_linestyle('solid')

            # Check the mouse was released on the canvas, and if it wasn't then just leave the width and 
            # height as the last values set by the motion event
            if event.xdata is not None and event.ydata is not None:
                self.x1 = event.xdata
                self.y1 = event.ydata

            # Set the width and height and origin of the bounding rectangle
            self.boundingRectWidth =  self.x1 - self.x0
            self.boundingRectHeight =  self.y1 - self.y0
            self.bouningRectOrigin = (self.x0, self.y0)

            # Draw the bounding rectangle
            self.rect.set_width(self.boundingRectWidth)
            self.rect.set_height(self.boundingRectHeight)
            self.rect.set_xy((self.x0, self.y0))
            self.canvas.draw()

            # Keep List of Bounding Boxes        
            self.rect_list.append([int(self.x0),int(self.y0),int(self.x1),int(self.y1)])

            # Fill the grid with the bounding boxes
            self.fill_grid()



    def NewImage(self):

        # Clear Rectangle List
        self.rect_list = []

        # Read new image off disk
        self.original_image = cv2.imread(self.imagepath)

        #Matplotlib is RGB, opencv is BGR
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.current_image = self.original_image.copy()
        self.DisplayImage()

    def DisplayImage(self):

        # Display new image to canvas and tiddy up        
        self.image_shape = self.current_image.shape
        # Set Frame to size of image, plust a little extra
        self.frame.SetSize((self.image_shape[1]+550, self.image_shape[0] + 200))
        
        # Set Matplotlib Canvas to size of image
        self.canvas.SetSize((self.image_shape[1], self.image_shape[0]))
        self.set_panels()

        # Display the image on the canvas
        self.axes.imshow(self.current_image) 
        self.canvas.draw()


    def OnMotion(self,event):

        # If the mouse has been pressed draw an updated rectangle when the mouse is 
        # moved so the user can see what the current selection is
        if self.frame.pressed:

            # Check the mouse was released on the canvas, 
            # and if it wasn't then just leave the width and 
            # height as the last values set by the motion event
            if event.xdata is not None and event.ydata is not None:
                self.x1 = event.xdata
                self.y1 = event.ydata
            
            # Set the width and height and draw the rectangle
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(self.y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            self.canvas.draw()



    def OnDelete(self):
        ''' Delete the selected rectangle'''
        
        # Don't try to delete if empty
        if len(self.rect_list)<1:
            print("There is nothing to delete.")
            return 1
        try:
            self.selected_rect
        except:
            print("You haven't selected a rectangle yet.")
            return 1 

        rectangle = self.rect_obj_list[self.selected_rect]
        # Remove object from canvas
        rectangle.remove()
        # Remove cordinates from list
        self.rect_list.remove(self.rect_list[self.selected_rect])
        # Remove object from list
        self.rect_obj_list.remove(rectangle)
        # Remove coordinates from grid
        self.BBGrid.DeleteRows(self.selected_rect)

        # redraw the canvas
        self.canvas.draw()

        # clear
        del self.selected_rect



    def change_rect_color(self):
        ''' change the line color of currently selected
        rectangle
        '''
        # Set selected rectangle line color black
        rect = self.rect_obj_list[self.selected_rect]

        #set everything back to green
        for i in range(len(self.rect_obj_list)):
            rect = self.rect_obj_list[i]
            # Set currently selected rect line as black
            if i == self.selected_rect:
                rect.set_edgecolor('red')
            else: # Set everything else as green
                rect.set_edgecolor('green')
            
        # Also highlight row in grid
        self.highlight_row(self.selected_rect)
        
        self.canvas.draw()

    def set_panels(self):
        self.ControlPanel.SetPosition((0,self.image_shape[0]+5))
        self.ControlPanel.SetSize((self.image_shape[1],50))
        self.BBPanel.SetPosition((self.image_shape[1]+5,0))
        self.BBPanel.SetSize((525,self.image_shape[0]))

    def highlight_row(self,rowselect):

        for rownum in range(len(self.rect_list)):
            row = self.rect_list[rownum]
            for colnum in range(len(row)):
                if rownum == rowselect:
                    self.BBGrid.SetCellBackgroundColour(rownum,colnum, "light blue")
                else:
                    self.BBGrid.SetCellBackgroundColour(rownum,colnum, "white")


        self.BBGrid.ForceRefresh()

    def fill_grid(self):
        for rownum in range(len(self.rect_list)):
            row = self.rect_list[rownum]
            for colnum in range(len(row)):
                self.BBGrid.SetCellValue(rownum,colnum, str(row[colnum]))

    def clear_boxes(self):
        # Uncheck all the boxes
        self.bwbox.SetValue(False)

    def on_bw_check(self,e):
        # If checked convert to black and white
        # If uncheck convert back to original image
        if self.bwbox.GetValue() == True:
            self.current_image = convert_bw(self.current_image)
            self.DisplayImage()
        else:
            self.current_image = self.original_image
            self.DisplayImage()



app = ImageLabeler()
app.MainLoop()



