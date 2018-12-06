from stl import mesh
import numpy as np
import math
from PIL import Image
from nfov import *


vertices = np.array([\
    [-76, -76, -56],
    [+76, -76, -56],
    [+76, +76, -56],
    [-76, +76, -56],
    [-76, -76, 56],
    [+76, -76, 56],
    [+76, +76, 56],
    [-76, +76, 56]])


def translate(_solid, step, axis):
    if 'x' == axis:
        items = 0, 3, 6
    elif 'y' == axis:
        items = 1, 4, 7
    elif 'z' == axis:
        items = 2, 5, 8
    else:
        raise RuntimeError('Unknown axis %r, expected x, y or z' % axis)

    _solid.points[:, items] += step

def get_coordinates(vertices,face):

    x1 = vertices[face[0], 0] - vertices[face[1], 0]
    y1 = vertices[face[0], 1] - vertices[face[1], 1]
    z1 = vertices[face[0], 2] - vertices[face[1], 2]
    x2 = vertices[face[1], 0] - vertices[face[2], 0]
    y2 = vertices[face[1], 1] - vertices[face[2], 1]
    z2 = vertices[face[1], 2] - vertices[face[2], 2]

    return x1,y1,z1,x2,y2,z2


#TODO TEST WITH DIFFERENT SHAPES
def get_fov(vertices,face):

    fov = []

    #distances are abs of coordinates
    x1, y1, z1, x2, y2, z2 = map(abs, get_coordinates(vertices,face))

    print(x1, y1, z1, x2, y2, z2)

    if x1 > 0 and z2 > 0:
        width = x1
        height = z2
        distance =  abs(vertices[face[0],1])

    if y1 > 0 and z2 > 0:
        width = y1
        height = z2
        distance =  abs(vertices[face[0],0])

    if x1 > 0 and z2 == 0:
        width = x1
        height = y2
        distance = abs(vertices[face[0],2])

    if y1 > 0 and z2 == 0:
        width = y1
        height = x2
        distance = abs(vertices[face[0],2])

    print(width,height,distance)

    norm = 100

    fov.append( np.degrees( np.arctan( width/(2*distance)))/norm)
    fov.append( np.degrees( np.arctan( height/(2*distance)))/norm)

    return fov


#TODO TEST WITH L SHAPE
def get_faces(vertices):

    faces = []

    floor = []
    ceiling = []
    up = False

    for i in range(len(vertices)-1):

        if up == False:
            floor.append(i)

        if vertices[i+1][2] - vertices[i][2] != 0:
            up = True

        if up == True:
            ceiling.append(i+1)

    faces.append(floor)
    faces.append(ceiling)

    for i in floor:

        faces.append((floor[i-1],floor[i],ceiling[i-1],ceiling[i]))

    return faces


def wall_orientation(wall, vertices, face):

    x1, y1, z1, x2, y2, z2 = get_coordinates(vertices, face)



    return wall

for i, face in enumerate(get_faces(vertices)):
    print(get_fov(vertices,get_faces(vertices)[i]))

#img = Image.open('assets/pano.png')

#fov = [0.16, 0.3]
#height = 800
#width = 800
#img = perspective_view(img, fov, height, width)

#plt.imshow(img)
#plt.show()
#img = Image.fromarray(img)
#img.save('assets/result.png')

#def create_room(walls, vertices,position):

    #for i,wall in enumerate(walls):

        #translate(wall, , 'y')

    #room = mesh.Mesh(np.concatenate([room.data] + [wall.data]))

    #return room


#wall = mesh.Mesh.from_file('assets/room2.stl')

#wall.save('assets/2walls.stl')



