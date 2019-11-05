import csv
import os



def import_grid_csv(master,pathname):
    '''
        Fill grid with bounding boxes from csv file
    '''
    
    lines = []     

    with open(pathname) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        rownum=0
        for row in csv_reader:
            # Don't read in header
            if rownum == 0:
                next
            else:
                for colnum in range(len(row)):
                    master.BBGrid.SetCellValue(rownum-1, colnum,row[colnum])
                
                lines.append(row)
            
            rownum+=1
   
    return lines     


 

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

