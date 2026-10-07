from sklearn.feature_extraction.image import extract_patches_2d
import os
import glob

def get_list_files(search_path):

    # Find all PNG files
    png_files = glob.glob(search_path + '/**/*.png', recursive=True)
    # Find all JPG files
    jpg_files = glob.glob(search_path + '/**/*.jpg', recursive=True)   

    files = png_files + jpg_files

    # Build an object that contains path, and other information about image
    file_obj = []
    for full_filepath in files:
        file_size = os.path.getsize(full_filepath)
        
        # Check to see if a CSV labels file exists for this image
        file_csv = os.path.splitext(full_filepath)[0] + ".csv"
        
        if os.path.exists(file_csv) == False:
            file_csv = None

        file_obj.append(
            { 
                "path" : full_filepath,
                "size" : file_size,
                "labels" : file_csv,
                "status" : 'in progress'
            }
        ) 


    if len(file_obj) == 0:
        return None
    else:
        return file_obj
        

    


def get_image_patches(image,patch_size=(10,10)):
    patches = extract_patches_2d(image, patch_size)
    return patches


def check_inside_rect(coord,rect):

    ''' 
        Check to is if a coordinate (x,y) is inside of
        rectangle ((x1,y1)(x2,y2)).
        rect : matplotlib.patches.Rectangle Object
        coord : (int,int) representing (x,y)
    '''

    x = coord[0]
    y = coord[1]

    x1 = rect.get_bbox().x0
    y1 = rect.get_bbox().y0
    x2 = rect.get_bbox().x1
    y2 = rect.get_bbox().y1

    # Bounding boxes may have been dragged with reversed corners,
    # so accept either ordering.  Inclusive bounds so that clicking
    # exactly on an edge still selects the box.
    if (x1 <= x <= x2) or (x2 <= x <= x1):
        xyes = True
    else:
        xyes = False

    if (y1 <= y <= y2) or (y2 <= y <= y1):
        yyes = True
    else:
        yyes = False

    if xyes and yyes: #FOUND!
        return 1
    else: # NOT FOUND!
        return 0

def get_rect_coords(master):
    '''
        Loop through all of the Rectangle object and return an Python list 
        with their (x0,y0) and (x1,y1) bounding box coordinates
    '''
    coords_list = []
    for i in range(len(master.rect_obj_list)):
        x0 = int(master.rect_obj_list[i].get_bbox().x0)
        y0 = int(master.rect_obj_list[i].get_bbox().y0)
        x1 = int(master.rect_obj_list[i].get_bbox().x1)
        y1 = int(master.rect_obj_list[i].get_bbox().y1) 
        
        # Some bounding boxes don't have a label
        coord = [x0,y0,x1,y1,master.rect_labels[i]]

        coords_list.append(coord)
    
    return coords_list
        


