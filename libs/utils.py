

def check_inside_rect(coord,rect):

    ''' Check to is if a coordinate (x,y) is inside of
        rectangle ((x1,y1)(x2,y2)).
    '''

    x = coord[0]
    y = coord[1]

    xyes = 0
    yyes = 0
    x1,y1,x2,y2 = rect

    # Check if mouse is between x1 and x2
    if x1 < x2:
        if (x > x1) & (x < x2):
            xyes += 1
    else:
        if (x < x1) & (x>x2):
            xyes += 1

    # Check if mouse is between y1 and y2
    if y1 < y2:
        if (y > y1) & (y < y2):
            yyes += 1
    else:
        if (y < y1) & (y>y2):
            yyes += 1


    if (xyes > 0) & (yyes > 0): #FOUND!
        return 1
    else: # NOT FOUND!
        return 0



