import csv
import os
from labeler.utils import get_rect_coords



def import_grid_csv(master,pathname):
    '''
        Read csv file
    '''
    
    lines = []     

    with open(pathname) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        rownum=0
        for row in csv_reader:
            # Don't read in header
            if rownum == 0:
                rownum+=1
                next
            else:
                lines.append(row)
            rownum+=1
            
    fill_grid(master)  

    return lines     


def fill_grid(master):
    '''
        Populate the grid from the list of coordinate found in the Rectangle
        objects in rect_obj_list 
    '''

    coord_list = get_rect_coords(master)
    for rownum in range(len(coord_list)):
        row = coord_list[rownum]
        for colnum in range(len(row)):
            master.BBGrid.SetCellValue(rownum,colnum, str(row[colnum]))

    master.BBGrid.ForceRefresh()

def empty_grid(master):
    '''
        Blank out all the cells in the grid
    '''    
    for col in range(master.BBGrid.GetNumberCols()):
        for row in range(master.BBGrid.GetNumberRows()):
            master.BBGrid.SetCellValue(row,col,"")


def get_grid_list(master):
    '''
        Ouputs the grid as a python list
    '''
    
    num_cols = master.BBGrid.GetNumberCols()
    num_rows = master.BBGrid.GetNumberRows()

    column_labels = []
    grid_list = []
    for row in range(num_rows):

        row_list = []
        for col in range(num_cols):
            if row==0:
                column_labels.append(master.BBGrid.GetColLabelValue(col))
            value = master.BBGrid.GetCellValue(row, col)
            row_list.append(value)
        # Make sure it is not blank
        if row_list[0] == '':
            continue
        else:
            grid_list.append(row_list)

    return column_labels,grid_list


def write_grid_csv(master,default_csvfile=''):
    ''' 
        Writes out the contents of bounding box grid to a csv file.
    '''

    if default_csvfile == '':
        # By default we want to name the csv file with the same file prefix.
        fileroot = os.path.basename(master.imagepath)
        id = os.path.splitext(fileroot)[0]
        default_csvfile = id+".csv"


    # Get column titles and coordinates in string from
    column_labels,grid_list = get_grid_list(master)
    with open(default_csvfile,'w') as label_file:
        wr = csv.writer(label_file)   
        wr.writerow(column_labels)
        for coords in grid_list:
            wr.writerow(coords)

    master.user_info("Grid saved as " + default_csvfile)



def set_grid_edit(master):
    '''
        Make it so that only certain columns can be edited
    '''
    for col in range(master.BBGrid.GetNumberCols()):
        for row in range(master.BBGrid.GetNumberRows()):
            if col == 4:
                master.BBGrid.SetReadOnly(row, col, False)
            else:
                master.BBGrid.SetReadOnly(row, col, True)


def highlight_row(master,rowselect):
    '''
        Highlight the row in the Grid of the selected rectangle
    '''

    column_labels,grid_list = get_grid_list(master)

    for rownum in range(len(grid_list)):
        for colnum in range(len(column_labels)):
            if rownum == rowselect:
                master.BBGrid.SetCellBackgroundColour(rownum,colnum, "light blue")
            else:
                master.BBGrid.SetCellBackgroundColour(rownum,colnum, "white")

    master.BBGrid.ForceRefresh()



