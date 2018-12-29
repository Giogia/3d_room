from stl import mesh
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image
from nfov import *

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


def get_face_vertices(vertices, face):

    points = []
    for i in face:
        point = []
        for coordinate in vertices[i]:
            point.append(coordinate)

        points.append(point)

    return points


def get_medium_points(face, offset):

    medium_points = []

    for i in range(len(face)):

        #face[i - 1][2] = 0

        #face[i][2] = 0

        medium_point = 0.5*(np.array(face[i-1]) + np.array(face[i])) - np.array(offset)

        medium_points.append(medium_point)

    return medium_points


def get_orientation(face, center):

    vector = get_medium_points(face, center)[1]
    if vector[0] > 0:
        angle = 0.5 / (1 + math.exp(-vector[1]/vector[0])) + 0.5

    if vector[0] < 0:
        angle = 0.5 / (1 + math.exp(-vector[1]/vector[0]))

    return angle


def get_fov(vertices, face, center):

    fov = []

    face = get_face_vertices(vertices, face)

    vectors = get_medium_points(face, center)

    for i in range(2):

        angle = 0.45 * np.arccos(np.dot(vectors[i-1], vectors[i+1]) / (np.linalg.norm(vectors[i-1]) * np.linalg.norm(vectors[i+1])))

        fov.append(angle)

    return fov


def get_dimensions(vertices, face):

    vectors = get_face_vertices(vertices, face)

    width = math.sqrt( ((vectors[0][0] - vectors[1][0])**2) + ((vectors[0][1] - vectors[1][1])**2) + ((vectors[0][2] - vectors[1][2])**2) )
    height = math.sqrt( ((vectors[0][0] - vectors[3][0])**2) + ((vectors[0][1] - vectors[3][1])**2) + ((vectors[0][2] - vectors[3][2])**2) )

    resolution_constant = 2000

    width = int(resolution_constant*width)
    height = int(resolution_constant*height)

    return width,height


def get_center_offset(vertices):

    floor = get_faces(vertices)[0]
    points = get_face_vertices(vertices, floor)

    x = [p[0] for p in points]
    y = [p[1] for p in points]
    offset = (sum(x) / len(points), sum(y) / len(points), 0)

    return offset


def wall_orientation(wall, vertices, face):

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


def get_files(filename):

    img = Image.open('../LayoutNet/result/res_panofull_ts_box_joint/img/'+filename+'.png')
    txt = open('../LayoutNet/result/res_panofull_ts_box_joint/box/'+filename+'.txt','r')

    return img, txt


for i in range(4,46):

    img, txt = get_files(str(i))
    vertices = get_vertices(txt)

    for i in range(len(get_faces(vertices))):

        face = get_faces(vertices)[i]

        center = get_center_offset(vertices)

        fov = get_fov(vertices, face, center)

        width, height = get_dimensions(vertices, face)

        orientation = get_orientation(get_face_vertices(vertices,face),center)

        wall_center = get_medium_points(get_face_vertices(vertices,face), center)[1]

        #normalization to 1
        wall_center = (wall_center) / (max(wall_center) - min(wall_center))

        #coordinates incompatibility
        wall_center[0] = - wall_center[0]

        offset = sum(np.array(center) * np.array(wall_center))

        if i == 0:
            persp = perspective_view(img, fov, width, height, [orientation,1], center)

        if i != 0:
            persp = perspective_view(img, fov, width, height, [1 - orientation, 0.5], [offset,0])

        plt.imshow(persp)
        plt.show()

    #img = perspective_view(img, fov, width, height,[0.5,1], center) #[0.5,1.25]  #[0.25,-0.5]
    #img = perspective_view(img, fov, width, height,[0.755,0.5], [center[0],0]) #[0.4,0.55] #[-0.22,0.15]
    #img = perspective_view(img, fov, width, height,[0.502,0.5],[-center[1],0])  #[0.38,0.5] #[-0.15,0.05]
    #img = perspective_view(img, fov, width, height,[0.25,0.5],[-center[0],0])  #[0.3,0.45] #[0.15,0.05]
    #img = perspective_view(img, fov, width, height,[0,0.5],[center[1],0])  #[0.55,0.75] #[0.35,0.1]




    #plt.imshow(img)
    #plt.show()
    #img = Image.fromarray(img)

    #img = img.resize((10*img.size[0],10*img.size[1]), Image.BILINEAR)
    #img.save('assets/result.jpg')








