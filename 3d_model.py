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


wall0 = mesh.Mesh.from_file('assets/wallm0t.stl')
wall1 = mesh.Mesh.from_file('assets/wallm1t.stl')
wall2 = mesh.Mesh.from_file('assets/wallm2t.stl')
wall3 = mesh.Mesh.from_file('assets/wallm3t.stl')
wall4 = mesh.Mesh.from_file('assets/wallm4t.stl')

room = mesh.Mesh(np.concatenate([wall0.data] + [wall1.data] + [wall2.data] + [wall3.data] + [wall4.data]))

room.save('assets/room.stl')
