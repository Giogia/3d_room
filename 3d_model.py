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



path = os.getcwd() + '/../result/res_panofull_ts_box_joint/mesh'

if not os.path.isdir(path):

    os.mkdir(path)


for i in range(1,54):

    txt = open('../result/res_panofull_ts_box_joint/box/' + str(i) + '.txt', 'r')
    vertices = get_vertices(txt)

    room = mesh.Mesh.from_file('../result/res_panofull_ts_box_joint/walls/' + str(i) + '-0m.stl')
    room.rotate([1, 0, 0], math.radians(90))

    face = get_face_vertices(vertices,get_faces(vertices)[0])
    face_base = face[0]
    resolution_constant = 200

    room.rotate([0.0, 1.0, 0.0], -get_angle(np.array(face[1])-np.array(face[0])))

    for n in range(2):

        translate(room, resolution_constant*face_base[n], n)

    for j in range(1,5):

        face = get_face_vertices(vertices, get_faces(vertices)[j])
        face_base = face[1]

        wall = mesh.Mesh.from_file('../result/res_panofull_ts_box_joint/walls/' + str(i) + '-' + str(j) + 'm.stl')

        wall.rotate([0.0, 1.0, 0.0], -get_angle(np.array(face[0])-np.array(face[1])))
        print(get_angle(np.array(face[0])-np.array(face[1])))

        for n in range(2):

            translate(wall, resolution_constant * face_base[n], n)

        room = mesh.Mesh(np.concatenate([room.data] + [wall.data]))

    room.save('../result/res_panofull_ts_box_joint/mesh/' + str(i) + '.stl')
