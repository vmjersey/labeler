

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


def write_grid_csv(master):
    ''' 
        Writes out the contents of bounding box grid to a csv file.
    '''

    column_labels,grid_list = get_grid_list(master)
    print(column_labels)
    print(grid_list)



