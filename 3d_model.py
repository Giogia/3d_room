from stl import mesh
import numpy as np
import math
from PIL import Image
from nfov import *


#vertices = np.array([
   # [-1, -1, -1],
  #  [+76, -76, -56],
  #  [+76, +76, -56],
   # [-76, +76, -56],
   # [-76, -76, 56],
   # [+76, -76, 56],
  #  [+76, +76, 56],
  #  [-76, +76, 56]])

def get_vertices(file):

    vertices = []

    for line in file:

        vertice = []

        for coordinate in line.split():

            vertice.append(float(coordinate))

        vertices.append(vertice)

    for vertice in vertices:

        for i in range(len(vertice)):

            vertice[i] = vertice[i] / vertices[-1][2]

    return np.array(vertices)


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

    x2 = vertices[face[3], 0] - vertices[face[0], 0]
    y2 = vertices[face[3], 1] - vertices[face[0], 1]
    z2 = vertices[face[3], 2] - vertices[face[0], 2]

    return x1,y1,z1,x2,y2,z2


def get_face(vertices,face):

    vectors = []
    for i in face:
        vector = []
        for coordinate in vertices[i]:
            vector.append(coordinate)

        vectors.append(vector)

    return vectors

def get_fov(vertices, face):

    fov = []

    print(face)
    vectors = get_face(vertices,face)

    for i in range(2):

        angle = np.arccos(np.dot(vectors[i], vectors[i+1]) / (np.linalg.norm(vectors[i]) * np.linalg.norm(vectors[i+1])))

        fov.append(angle)

    return fov


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

    for i in floor:

        faces.append((floor[i-1],floor[i],ceiling[i],ceiling[i-1]))

    #faces.append(ceiling)

    return faces


def wall_orientation(wall, vertices, face):

    x1, y1, z1, x2, y2, z2 = get_coordinates(vertices, face)

    #cannot distinguish floor from ceiling, floor is transformed here
    if face[0] == 0 and face[2] == 2:
        print("floor")
        wall.rotate([1,0,0], math.radians(90))

        translate(wall, -vertices[face[1], 0], 'x')
        translate(wall, -vertices[face[1], 1], 'z')
        translate(wall, vertices[face[1], 2], 'y')

    else:
        wall.rotate([0.0, -np.sign(y1), 0.0], math.radians(90))
        wall.rotate([0.0, np.sign(x1)-1, 0.0], math.radians(180))
        wall.rotate([np.sign(x2)+np.sign(y2),0.0, 0.0], math.radians(90))

        translate(wall, -vertices[face[0],0], 'x')
        translate(wall, -vertices[face[0],1], 'z')
        translate(wall, vertices[face[0],2], 'y')

    print(vertices[face[1],0])
    print(vertices[face[1],1])
    print(vertices[face[1],2])

    return wall

#for i, face in enumerate(get_faces(vertices)):
   #

img = Image.open('../LayoutNet/result/res_panofull_ts_box_joint/img/45.png')
file = open('../LayoutNet/result/res_panofull_ts_box_joint/box/45.txt','r')

vertices = get_vertices(file)

for i, face in enumerate(get_faces(vertices)):
    print(get_fov(vertices, face))
    fov= get_fov(vertices, face)
    #perspective_view(img, fov, height, width)


#fov = get_fov()
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

    #

    #return room



#wall = mesh.Mesh.from_file('assets/room2.stl')

#room = mesh.Mesh(np.zeros(100, dtype=mesh.Mesh.dtype))

#for i in range(5):

 #   face = get_faces(vertices)[i]

  #  print(face)

   # twall = mesh.Mesh(wall.data.copy())
    #twall = wall_orientation(twall, vertices, face)
    #room = mesh.Mesh(np.concatenate([room.data] + [twall.data]))

#room.save('assets/2walls.stl')




