from stl import mesh
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image
from nfov import *

wall0 = mesh.Mesh.from_file('assets/wallm0t.stl')
wall1 = mesh.Mesh.from_file('assets/wallm1t.stl')
wall2 = mesh.Mesh.from_file('assets/wallm2t.stl')
wall3 = mesh.Mesh.from_file('assets/wallm3t.stl')
wall4 = mesh.Mesh.from_file('assets/wallm4t.stl')

room = mesh.Mesh(np.concatenate([wall0.data] + [wall1.data] + [wall2.data] + [wall3.data] + [wall4.data]))

room.save('assets/room.stl')
