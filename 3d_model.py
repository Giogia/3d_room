from stl import mesh
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image
import os
from utils import *


def translate(_solid, step, axis):
    if 0 == axis:

        items = 0, 3, 6
        _solid.points[:, items] += step

    elif 1 == axis:

        items = 2, 5, 8
        _solid.points[:, items] -= step

    elif 2 == axis:

        items = 1, 4, 7
        _solid.points[:, items] += step

    else:
        raise RuntimeError('Unknown axis %r, expected x, y or z' % axis)




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
        translate(wall, -vertices[face[0],1], 'y')
        translate(wall, vertices[face[0],2], 'z')

    print(vertices[face[1],0])
    print(vertices[face[1],1])
    print(vertices[face[1],2])

    return wall

path = os.getcwd() + '/../result/res_panofull_ts_box_joint/mesh'

if not os.path.isdir(path):

    os.mkdir(path)


for i in range(45,46):

    txt = open('../result/res_panofull_ts_box_joint/box/' + str(i) + '.txt', 'r')
    vertices = get_vertices(txt)

    room = mesh.Mesh.from_file('../result/res_panofull_ts_box_joint/walls/' + str(i) + '-0m.stl')
    room.rotate([1, 0, 0], math.radians(90))
    face = get_face_vertices(vertices,get_faces(vertices)[0])[0]
    resolution_constant = 200

    for n in range(2):

        translate(room, resolution_constant*face[n], n)

    for j in range(1,5):

        face = get_face_vertices(vertices, get_faces(vertices)[j])[0]

        wall = mesh.Mesh.from_file('../result/res_panofull_ts_box_joint/walls/' + str(i) + '-' + str(j) + 'm.stl')

        for n in range(2):

            translate(wall, resolution_constant * face[n], n)

        room = mesh.Mesh(np.concatenate([room.data] + [wall.data]))

    room.save('../result/res_panofull_ts_box_joint/mesh/' + str(i) + '.stl')
