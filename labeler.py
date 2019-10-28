#!/usr/bin/env python3

import wx
import wx.grid as gridlib
import wx.lib.agw.buttonpanel as BP
from libs.imaging import convert_bw,read_image_as_bitmap
from libs.utils import check_inside_rect,get_rect_coords
from libs.grid import write_grid_csv,get_grid_list
import numpy as np
import os
import cv2
from PIL import Image   
import matplotlib  
from matplotlib.backend_tools import Cursors     
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.patches import Rectangle
from matplotlib.widgets import RectangleSelector
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

matplotlib.use('WXAgg')


class ImageLabeler(wx.App):
    '''
    The Main Application Class
    '''

    def __init__(self):

        wx.App.__init__(self) 

        self.frame = wx.Frame(None, title='Image Labeler')

        root_dir = os.path.abspath(__file__)       

        # Intitialise the matplotlib figure
        self.figure = Figure()

        # Create an axes, turn off the labels and add them to the figure
        self.axes = plt.Axes(self.figure,[0,0,1,1])      
        self.axes.set_axis_off() 
        self.figure.add_axes(self.axes) 

        # Add the figure to the wxFigureCanvas
        self.canvas = FigureCanvas(self.frame, -1, self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        self.toolbar.Hide()
       
        
        # What mode is the cursor in: bb,toolbar
        self.cursor_mode = "nobb"

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
        menuSaveGrid = filemenu.Append(wx.ID_SAVE,  "&Save Grid",  "Save Coordinates to CSV file")
        menuExit  = filemenu.Append(wx.ID_EXIT,  "&Exit",  "Exit Image Labeler")
        


        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.


        # Set events.
        self.frame.Bind(wx.EVT_MENU, self.OnFileAbout, menuAbout)
        self.frame.Bind(wx.EVT_MENU, self.OnFileOpen, menuOpen)
        self.frame.Bind(wx.EVT_MENU, self.OnFileExit, menuExit)
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGrid, menuSaveGrid)

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
        self.ControlBox = wx.BoxSizer(wx.VERTICAL)
        self.ControlBox.Add(self.ControlPanel)
        self.ControlPanel.SetBackgroundColour("red")

        # Convert image to black and white
        self.bwbox = wx.CheckBox(self.ControlPanel, label='Black and White', pos=(20,10))
        self.bwbox.SetValue(False)
        self.bwbox.Bind(wx.EVT_CHECKBOX, self.on_bw_check, self.bwbox)

        # Create Buttons to help label image
        self.button_list = []

        self.sibut = wx.Button(self.ControlPanel,-1,"Zoom", pos=(400,5))
        self.sibut.Bind(wx.EVT_BUTTON,self.zoom)
        self.button_list.append(self.sibut)
         
        self.hmbut = wx.Button(self.ControlPanel,-1,"Home", pos=(300,5))
        self.hmbut.Bind(wx.EVT_BUTTON,self.home)
        self.button_list.append(self.hmbut)
         
        self.hibut = wx.Button(self.ControlPanel,-1,"Pan",  pos=(200,5))
        self.hibut.Bind(wx.EVT_BUTTON,self.pan)
        self.button_list.append(self.hibut)

        self.plotbut = wx.Button(self.ControlPanel,-1,"Plot", pos=(500,5))
        self.plotbut.Bind(wx.EVT_BUTTON,self.plot)
        self.button_list.append(self.plotbut) 

        # Create Panel for Grid controls
        self.GridControlPanel = wx.Panel(self.frame,style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.GridControlBox = wx.BoxSizer(wx.VERTICAL)
        self.GridControlBox.Add(self.GridControlPanel)
        self.GridControlPanel.SetBackgroundColour("blue")

        # Create buttons for Grid Control Panel
        self.grsavebut = wx.Button(self.GridControlPanel,-1,"Save", pos=(20,5))
        self.grsavebut.Bind(wx.EVT_BUTTON,self.save_grid)


        # Are we moving the rectangle or creating a new one
        self.is_moving = False
 
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

        for butt in self.button_list:
            if button == butt:
                butt.Hide()
            else:
                butt.Show()
        
        
    def zoom(self,event):
        '''
            Use Matplotlibs zoom tool
        '''
        self.cursor_mode = "nobb"
        self.toggle_cursor_mode(self.sibut)
        self.toolbar.zoom()
 
    def home(self,event):
        '''
            Return view back to original position
        '''
        self.cursor_mode = "nobb"
        self.toggle_cursor_mode(self.hmbut)
        self.toolbar.home()
        # Toggle off the zoom and pan buttons
        if self.toolbar._active == 'ZOOM':
            self.toolbar.zoom()
        elif self.toolbar._active == 'PAN':
            self.toolbar.pan()
 
    def pan(self,event):
        '''
            Uses Matplotlibs pan tool
        '''
        self.cursor_mode = "nobb"
        self.toggle_cursor_mode(self.hibut)
        self.toolbar.pan()

    def plot(self,event):
        '''
            Draw a rectangle on the canvas
        '''
        self.cursor_mode = "bb"
        self.toggle_cursor_mode(self.plotbut)
        # Set Crosshair as mouse cursor.
        # Toggle off zoom and pan buttons
        if self.toolbar._active == 'ZOOM':
            self.toolbar.zoom()
        elif self.toolbar._active == 'PAN':
            self.toolbar.pan() 
 
    def OnFileExit(self,event):
        print("Exiting...")
        self.frame.Close()        


    def OnSaveGrid(self,event):
        '''
            Choose filename to save a CSV with grid with the coordinates.
        '''
        with wx.FileDialog(self.frame, "Save CSV file", wildcard="CSV files (*.csv)",style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Get Pathname
            pathname = fileDialog.GetPath()
            
            # Write to that file
            write_grid_csv(self,pathname)


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
        '''
            Actions taken when mouse button is pressed
        '''

        # Is the click inside a rectangle?
        found = 0
        current_x = event.xdata
        current_y = event.ydata

        for i in range(len(self.rect_obj_list)):
            rect = self.rect_obj_list[i]
            result = check_inside_rect((current_x,current_y),rect)
            if result == 1:
                self.selected_rect = i
                found+=1        


        # We want to select this rectangle, and move it
        if found > 0:
            self.is_moving = True
            self.change_rect_color()
            self.selected_rect_obj = self.rect_obj_list[self.selected_rect]
            self.x0,self.y0 = self.selected_rect_obj.xy
            self.x1 = None
            self.y1 = None
            self.press = self.x0, self.y0, event.xdata, event.ydata
            return 0

        if self.cursor_mode == "nobb":
            return 0

        # If the above is not satisified, it is time to draw a new rectangle
        # Initialise the rectangle
        self.rect = Rectangle((0,0), 1, 1, facecolor='None', edgecolor='green',linewidth='2')

        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.axes.add_patch(self.rect)

        # Check the mouse press was actually on the canvas
        if event.xdata is not None and event.ydata is not None:
            # Upon initial press of the mouse record the origin and record the mouse as pressed
            self.frame.pressed = True
            self.rect.set_linestyle('dashed')
            self.x0 = event.xdata
            self.y0 = event.ydata

    def OnMotion(self,event):
        '''
            Action taken when mouse movement happens over the canvas
        '''

        # If a rectangle is selected and needs to be moved
        if self.is_moving == True:
            if event.xdata is not None and event.ydata is not None: 
                if self.press is None: return
                self.x0, self.y0, xpress, ypress = self.press
                dx = event.xdata - xpress
                dy = event.ydata - ypress
                self.x1 = self.x0+dx
                self.y1 = self.y0+dy
                self.selected_rect_obj.set_x(self.x1)
                self.selected_rect_obj.set_y(self.y1)
                self.selected_rect_obj.figure.canvas.draw()
            return 0
        # If the mouse has been pressed draw an updated rectangle when the mouse is 
        # moved so the user can see what the current selection is
        elif self.frame.pressed:

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

    def OnLeftUp(self,event):
        '''
            Actions taken with mouse button is released
        '''
        
        # Rectangle has finished moving and objects need to be updated.
        if self.is_moving == True:

            x0 = self.selected_rect_obj.get_bbox().x0
            y0 = self.selected_rect_obj.get_bbox().y0
            x1 = self.selected_rect_obj.get_bbox().x1
            y1 = self.selected_rect_obj.get_bbox().y1

            self.selected_rect_obj.figure.canvas.draw()
            self.is_moving = False

            self.press = None
            
            # Update Grid with new coordinates
            self.fill_grid()
            return 0
        # A new rectangle is finished being drawn
        elif self.frame.pressed:

            # Upon release draw the rectangle as a solid rectangle
            self.frame.pressed = False
            self.rect.set_linestyle('solid')

            # Check the mouse was released on the canvas, and if it wasn't then 
            # just leave the width and height as the last values set by the motion event
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

            # Keep list of rect objects
            self.rect_obj_list.append(self.rect)

            # Fill the grid with the bounding boxes
            self.fill_grid()
 
    def NewImage(self):
        '''
            A new image is selected and needs to be read in
        '''

        # Clear Rectangle List
        self.rect_obj_list = [] 

        # Read new image off disk
        self.original_image = cv2.imread(self.imagepath)

        #Matplotlib is RGB, opencv is BGR
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.current_image = self.original_image.copy()
        self.DisplayImage()

    def DisplayImage(self):
        '''
            Display new image to Matplotlib canvas and tiddy up
        '''

        self.image_shape = self.current_image.shape
        # Set Frame to size of image, plust a little extra
        self.frame.SetSize((self.image_shape[1]+550, self.image_shape[0] + 200))
        
        # Set Matplotlib Canvas to size of image
        self.canvas.SetSize((self.image_shape[1], self.image_shape[0]))
        self.set_panels()

        # Display the image on the canvas
        self.axes.imshow(self.current_image) 
        self.canvas.draw()

    def OnDelete(self):
        ''' 
            Delete the selected rectangle
        '''
        
        # Don't try to delete if empty
        if len(self.rect_obj_list)<1:
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
        # Remove object from list
        self.rect_obj_list.remove(rectangle)
        # Remove coordinates from grid
        self.BBGrid.DeleteRows(self.selected_rect)

        # redraw the canvas
        self.canvas.draw()

        # clear
        del self.selected_rect

    def change_rect_color(self):
        ''' 
            change the line color of currently selected rectangle
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
        '''
            Set the size and position of the pannels based on the images size.
        '''
        self.ControlPanel.SetPosition((0,self.image_shape[0]+5))
        self.ControlPanel.SetSize((self.image_shape[1],50))

        self.BBPanel.SetPosition((self.image_shape[1]+5,0))
        self.BBPanel.SetSize((525,self.image_shape[0]))

        self.GridControlPanel.SetPosition((self.image_shape[1]+5,self.image_shape[0]+5))
        self.GridControlPanel.SetSize((525,50))

    def highlight_row(self,rowselect):
        '''
            Highlight the row in the Grid of the selected rectangle
        '''

        column_labels,grid_list = get_grid_list(self)

        for rownum in range(len(grid_list)):
            for colnum in range(len(column_labels)):
                if rownum == rowselect:
                    self.BBGrid.SetCellBackgroundColour(rownum,colnum, "light blue")
                else:
                    self.BBGrid.SetCellBackgroundColour(rownum,colnum, "white")

        self.BBGrid.ForceRefresh()

    def save_grid(self,event):
        '''
            Save the selected bounding boxes to some file, database,etc 
        '''
        write_grid_csv(self)

        
    def fill_grid(self):
        '''
            Populate the grid from the list of coordinate found in the Rectangle
            objects in rect_obj_list 
        '''

        coord_list = get_rect_coords(self)
        for rownum in range(len(coord_list)):
            row = coord_list[rownum]
            for colnum in range(len(row)):
                self.BBGrid.SetCellValue(rownum,colnum, str(row[colnum]))

    def clear_boxes(self):
        '''
            Uncheck the boxes
        '''
        # Uncheck all the boxes
        self.bwbox.SetValue(False)

    def on_bw_check(self,e):
        '''
            Action taken with box is either checked or unchecked
        '''
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



