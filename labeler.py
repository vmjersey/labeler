#!/usr/bin/env python3

import wx
import wx.grid as gridlib
import wx.lib.agw.buttonpanel as BP
from libs.imaging import convert_bw,convert_gs,read_image_as_bitmap,write_image
from libs.utils import check_inside_rect
from libs.trans import TransFrame
from libs.segment import SegmentFrame
from libs.grid import write_grid_csv,get_grid_list,import_grid_csv,empty_grid,fill_grid,set_grid_edit,highlight_row
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

        # Frame that will contain image and grid
        self.frame = wx.Frame(None, title='Image Display')


        root_dir = os.path.dirname(os.path.abspath(__file__))
        self.CanvasPanel = wx.Panel(self.frame,
                    style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.CanvasPanel.SetBackgroundColour("dark gray")

        self.frame.Bind(wx.EVT_CLOSE, self.OnFileExit)

        # Intitialise the matplotlib figure
        self.figure = Figure()

        # Create an axes, turn off the labels and add them to the figure
        self.axes = plt.Axes(self.figure,[0,0,1,1])      
        self.axes.set_axis_off() 
        self.figure.add_axes(self.axes) 

        # Add the figure to the wxFigureCanvas
        self.canvas = FigureCanvas(self.CanvasPanel, -1, self.figure)
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
        menuOpenGrid  = filemenu.Append(wx.ID_FILE,  "&Open Grid",  "Open File Containing Bounding Boxes")
        menuOpenImage  = filemenu.Append(wx.ID_OPEN,  "&Open Image",  "Open Image File")
        menuSaveGrid = filemenu.Append(wx.ID_SAVE,  "&Save Grid",  "Save Bounding Boxes to CSV File")
        menuSaveImage = filemenu.Append(wx.ID_SAVEAS,  "&Save Image",  "Save Image")
        menuExit  = filemenu.Append(wx.ID_EXIT,  "&Exit",  "Exit Image Labeler")
        


        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.


        # Set events.
        self.frame.Bind(wx.EVT_MENU, self.OnFileAbout, menuAbout)
        self.frame.Bind(wx.EVT_MENU, self.OnFileOpen, menuOpenImage)
        self.frame.Bind(wx.EVT_MENU, self.OnImportGrid, menuOpenGrid)
        self.frame.Bind(wx.EVT_MENU, self.OnFileExit, menuExit)
        self.frame.Bind(wx.EVT_MENU, self.OnSaveGrid, menuSaveGrid)
        self.frame.Bind(wx.EVT_MENU, self.OnSaveImage, menuSaveImage)



        #Keep track of how many images you have displayed
        self.imagecounter = 0

        self.imagepath = "./image.jpg"

        # Create Panel to display Bounding Box Coordinates
        self.BBPanel = wx.Panel(self.frame,
                    style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.BBPanel.SetBackgroundColour("dark gray")

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

        # Do Some things when the mouse clicks inside of the Grid
        self.BBGrid.Bind(wx.grid.EVT_GRID_SELECT_CELL,self.OnGridLeft)
        # Do some things when delete key is pressed inside of the grid
        self.BBGrid.Bind(wx.EVT_KEY_DOWN,self.OnGridDelete)
        # Get rid of row labels
        self.BBGrid.SetRowLabelSize(0)
        # Set all columns to read only, except the Label column
        set_grid_edit(self)
        #self.BBGrid.EnableEditing(False)

        self.BBPanel.SetSizer(BBsizer)


        # Create Panel for Image Controls.
        self.ControlPanel = wx.Panel(self.frame,
                    style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.ControlBox = wx.BoxSizer(wx.VERTICAL)
        self.ControlBox.Add(self.ControlPanel)
        self.ControlPanel.SetBackgroundColour("dark gray")

        # Create Buttons to help label image
        self.button_list = []

        ControlSizer = wx.GridSizer(1,4,1,1)

        self.sibut = wx.Button(self.ControlPanel,-1)
        zoom_img = wx.Image(root_dir + '/icons/zoom.png', wx.BITMAP_TYPE_ANY)
        zoom_img = zoom_img.Scale(20,20)
        self.sibut.SetBitmap(wx.Bitmap(zoom_img))
        self.sibut.Bind(wx.EVT_BUTTON,self.zoom)
        self.button_list.append(self.sibut)
        ControlSizer.Add(self.sibut,0,wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

         
        self.hmbut = wx.Button(self.ControlPanel,-1)
        home_img = wx.Image(root_dir + '/icons/home.png', wx.BITMAP_TYPE_ANY)
        home_img = home_img.Scale(20,20)
        self.hmbut.SetBitmap(wx.Bitmap(home_img))
        self.hmbut.Bind(wx.EVT_BUTTON,self.home)
        self.button_list.append(self.hmbut)
        ControlSizer.Add(self.hmbut,0,wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL) 

 
        self.hibut = wx.Button(self.ControlPanel,-1)
        pan_img = wx.Image(root_dir + '/icons/pan.png', wx.BITMAP_TYPE_ANY)
        pan_img = pan_img.Scale(20,20)
        self.hibut.SetBitmap(wx.Bitmap(pan_img))
        self.hibut.Bind(wx.EVT_BUTTON,self.pan)
        self.button_list.append(self.hibut)
        ControlSizer.Add(self.hibut,0,wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL) 


        self.plotbut = wx.Button(self.ControlPanel,-1)
        box_img = wx.Image(root_dir + '/icons/bbox.png', wx.BITMAP_TYPE_ANY)
        box_img = box_img.Scale(20,20)
        self.plotbut.SetBitmap(wx.Bitmap(box_img))
        self.plotbut.Bind(wx.EVT_BUTTON,self.plot)
        self.button_list.append(self.plotbut) 
        ControlSizer.Add(self.plotbut,0,wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

        self.ControlPanel.SetSizer(ControlSizer) 

        # Create Panel for Grid controls
        self.GridControlPanel = wx.Panel(self.frame,
                    style=wx.BORDER_SUNKEN | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)
        self.GridControlBox = wx.BoxSizer(wx.VERTICAL)
        self.GridControlBox.Add(self.GridControlPanel)
        self.GridControlPanel.SetBackgroundColour("dark gray")

        GridControlSizer = wx.GridSizer(1,4,1,1)

        # Create buttons for Grid Control Panel
        self.imbut = wx.Button(self.GridControlPanel,-1)
        imp_img = wx.Image(root_dir + '/icons/import.png', wx.BITMAP_TYPE_ANY)
        imp_img = imp_img.Scale(20,20)
        self.imbut.SetBitmap(wx.Bitmap(imp_img))
        self.imbut.Bind(wx.EVT_BUTTON,self.OnImportGrid)
        GridControlSizer.Add(self.imbut,0,wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)


        # Create buttons for Grid Control Panel
        self.grsavebut = wx.Button(self.GridControlPanel,-1)
        save_img = wx.Image(root_dir + '/icons/filesave.png', wx.BITMAP_TYPE_ANY)
        save_img = save_img.Scale(20,20)
        self.grsavebut.SetBitmap(wx.Bitmap(save_img))
        self.grsavebut.Bind(wx.EVT_BUTTON,self.save_grid)
        GridControlSizer.Add(self.grsavebut,0,wx.ALL |wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

        self.GridControlPanel.SetSizer(GridControlSizer)


        # Are we moving the rectangle or creating a new one
        self.is_moving = False
 
        # Hold list of rectangle objects
        self.rect_obj_list = []

        # A Statusbar i the bottom of the window
        self.frame.CreateStatusBar()
        self.frame.Show(True)

        self.FirstImage() 

        # Frame for image transformations
        self.TransFrame = TransFrame(None,self)
        
        # Frame for image segmentation
        self.SegFrame = SegmentFrame(None,self)



    def OnGridLeft(self,event):
        '''
            Action taken when left click happens on grid
        '''
        row = event.GetRow()
        self.selected_rect = row
        self.change_rect_color()
        highlight_row(self,row)

    def OnGridDelete(self,event):
        '''
            Delete row in grid
        '''
        row = self.BBGrid.GetGridCursorRow()
        col = self.BBGrid.GetGridCursorCol()
       
        if event.GetKeyCode() == wx.WXK_DELETE:
            self.OnDelete()


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
        '''
            Close every frame in the app.
        '''
        self.frame.Destroy()
        self.TransFrame.Close()
        self.SegFrame.Close()

    def OnImportGrid(self,event):
        '''
            Choose CSV file with coordinates to import.
        '''
        with wx.FileDialog(self.frame, "Import CSV File", wildcard="*.csv",style=wx.FD_OPEN) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Get Pathname
            pathname = fileDialog.GetPath()

            # Read file into list
            new_coords = import_grid_csv(self,pathname)
            
            # Loop through coordinates and draw rectangle
            for coord in new_coords:
                self.draw_rect(coord)

            self.canvas.draw()

    def draw_rect(self,rect):
        if len(rect) > 4:
            x0,y0,x1,y1,label = rect
        else:
            x0,y0,x1,y1 = rect

        x0 = int(x0)
        y0 = int(y0)
        x1 = int(x1)
        y1 = int(y1)
        width = int(x1)-int(x0)
        height = int(y1)-int(y0)

        self.rect = Rectangle((int(x0),int(y0)), width, height, facecolor='None', edgecolor='green',linewidth='2')
        self.axes.add_patch(self.rect)
        self.rect_obj_list.append(self.rect)



    def OnSaveGrid(self,event):
        '''
            Choose filename to save a CSV with grid with the coordinates.
        '''
        with wx.FileDialog(self.frame, "Save CSV file", wildcard="*.csv",style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Get Pathname
            pathname = fileDialog.GetPath()
            
            # Write to that file
            write_grid_csv(self,pathname)

    def OnSaveImage(self,event):
        '''
            Choose filename to save the image.
        '''
        with wx.FileDialog(self.frame, "Save an image file",style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Get Pathname
            imagepathname = fileDialog.GetPath()

            # Write to that file
            write_image(self,imagepathname)

    def OnFileOpen(self,event):
        ''' 
            Open Dialog so user can select a new image. 
        '''
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
        '''
            Display information about the application
        '''
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self.frame, "A GUI for labeling images", "About Image Labeler", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnKeyDown(self,event):
        '''
            Actions to be taken when a key is pressed
        '''
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
            fill_grid(self)
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
            fill_grid(self)
 
    def NewImage(self):
        '''
            A new image needs to be read in, and various objects need to be cleaned up.
        '''

        # Delete all rectangles from the canvas
        self.clear_bb()

        # Clear Rectangle List
        self.rect_obj_list = [] 
        
        # Read image into original_image and current_image
        self.ReadImage()
        
        # Refresh the canvas
        self.RefreshImage()

    def ReadImage(self):
        ''' 
            Read image off disk
        '''
        self.original_image = cv2.imread(self.imagepath)

        #Matplotlib is RGB, opencv is BGR
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        self.current_image = self.original_image.copy()


    def FirstImage(self):
        '''
            The very first image is handled differently
        '''
        # Read image into the original_image and current_image
        self.ReadImage()

        self.image_shape = self.current_image.shape
        # Set Frame to size of image, plust a little extra
        self.frame.SetSize((self.image_shape[1]+550, self.image_shape[0] + 200))

        # Set Matplotlib Canvas to size of image
        self.canvas.SetSize((self.image_shape[1], self.image_shape[0]))
        self.set_panels()

        # Display the image on the canvas
        self.img_obj = self.axes.imshow(self.current_image,cmap='gray')
        self.canvas.draw()



    def RefreshImage(self):
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
        self.img_obj.set_array(self.current_image)
        self.canvas.draw_idle()

    def OnDelete(self):
        ''' 
            Delete the selected rectangle
        '''
        
        # Don't try to delete if empty
        if len(self.rect_obj_list)<1:
            self.user_error("There is nothing to delete.") 
            return 1
        
        try:
            self.selected_rect
        except:
            self.user_error("You haven't selected a rectangle yet.") 
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
        if len(self.rect_obj_list) < 1:
            return 0
        
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
        highlight_row(self,self.selected_rect)
        
        self.canvas.draw()


    def clear_bb(self):
        '''
            Remove all rectangles and empty grid
        '''

        for rectangle in self.rect_obj_list:
            # Remove object from canvas
            rectangle.remove()


        empty_grid(self)

        # Set the list back to empty
        self.rect_obj_list = []

        # redraw the canvas
        self.canvas.draw()

    def set_panels(self):
        '''
            Set the size and position of the pannels based on the images size.
        '''
        self.CanvasPanel.SetPosition((0,0)) 
        self.CanvasPanel.SetSize((self.image_shape[1],self.image_shape[0]))

        self.ControlPanel.SetPosition((0,self.image_shape[0]+5))
        self.ControlPanel.SetSize((self.image_shape[1],50))

        self.BBPanel.SetPosition((self.image_shape[1]+5,0))
        self.BBPanel.SetSize((525,self.image_shape[0]))

        self.GridControlPanel.SetPosition((self.image_shape[1]+5,self.image_shape[0]+5))
        self.GridControlPanel.SetSize((525,50))


    def save_grid(self,event):
        '''
            Save the selected bounding boxes to some file, database,etc 
        '''
        if len(self.rect_obj_list) < 1:
            self.user_error("You haven't selected a single bounding box yet.")
            return 1;
        else:
            write_grid_csv(self)
            return 0

    def user_info(self,message):
        wx.MessageBox(message,'Info', wx.OK)

    def user_error(self,message):
        wx.MessageBox(message, 'Error', wx.ICON_ERROR | wx.OK)
 
app = ImageLabeler()
app.MainLoop()



