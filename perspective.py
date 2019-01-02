from math import pi
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

from utils import *

class NFOV():
    def __init__(self, fov, height, width):
        self.FOV = fov
        self.PI = pi
        self.PI_2 = pi * 0.5
        self.PI2 = pi * 2.0
        self.height = height
        self.width = width
        self.screen_points = self._get_screen_img()

    def _get_coord_rad(self, isCenterPt, center_point=None):
        return (center_point * 2 - 1) * np.array([self.PI, self.PI_2]) \
            if isCenterPt \
            else \
            (self.screen_points * 2 - 1) * np.array([self.PI, self.PI_2]) * (
                np.ones(self.screen_points.shape) * self.FOV)

    def _get_screen_img(self):
        xx, yy = np.meshgrid(np.linspace(0, 1, self.width), np.linspace(0, 1, self.height))
        return np.array([xx.ravel(), yy.ravel()]).T

    def _calcSphericaltoGnomonic(self, convertedScreenCoord, center_point):
        x = convertedScreenCoord.T[0] + center_point[0]
        y = convertedScreenCoord.T[1] + center_point[1]

        rou = np.sqrt(x ** 2 + y ** 2)
        c = np.arctan(rou)
        sin_c = np.sin(c)
        cos_c = np.cos(c)

        lat = np.arcsin(cos_c * np.sin(self.cp[1]) + (y * sin_c * np.cos(self.cp[1])) / rou)
        lon = self.cp[0] + np.arctan2(x * sin_c, rou * np.cos(self.cp[1]) * cos_c - y * np.sin(self.cp[1]) * sin_c)

        lat = (lat / self.PI_2 + 1.) * 0.5
        lon = (lon / self.PI + 1.) * 0.5

        return np.array([lon, lat]).T

    def _bilinear_interpolation(self, screen_coord):
        uf = np.mod(screen_coord.T[0],1) * self.frame_width  # long - width
        vf = np.mod(screen_coord.T[1],1) * self.frame_height  # lat - height

        x0 = np.floor(uf).astype(int) # coord of pixel to bottom left
        y0 = np.floor(vf).astype(int)
        _x2 = np.add(x0, np.ones(uf.shape).astype(int))  # coords of pixel to top right
        y2 = np.add(y0, np.ones(vf.shape).astype(int))

        x2 = np.mod(_x2, self.frame_width)
        y2 = np.minimum(y2, self.frame_height - 1)

        base_y0 = np.multiply(y0, self.frame_width)
        base_y2 = np.multiply(y2, self.frame_width)

        A_idx = np.add(base_y0, x0)
        B_idx = np.add(base_y2, x0)
        C_idx = np.add(base_y0, x2)
        D_idx = np.add(base_y2, x2)

        flat_img = np.reshape(self.frame, [-1, self.frame_channel])

        A = np.take(flat_img, A_idx, axis=0)
        B = np.take(flat_img, B_idx, axis=0)
        C = np.take(flat_img, C_idx, axis=0)
        D = np.take(flat_img, D_idx, axis=0)

        wa = np.multiply(_x2 - uf, y2 - vf)
        wb = np.multiply(_x2 - uf, vf - y0)
        wc = np.multiply(uf - x0, y2 - vf)
        wd = np.multiply(uf - x0, vf - y0)

        # interpolate
        AA = np.multiply(A, np.array([wa, wa, wa]).T)
        BB = np.multiply(B, np.array([wb, wb, wb]).T)
        CC = np.multiply(C, np.array([wc, wc, wc]).T)
        DD = np.multiply(D, np.array([wd, wd, wd]).T)
        nfov = np.reshape(np.round(AA + BB + CC + DD).astype(np.uint8), [self.height, self.width, 3])

        return nfov

    def toNFOV(self, frame, look_point, center_point):
        self.frame = frame
        self.frame_height = frame.shape[0]
        self.frame_width = frame.shape[1]
        self.frame_channel = frame.shape[2]

        self.cp = self._get_coord_rad(center_point=look_point, isCenterPt=True)
        convertedScreenCoord = self._get_coord_rad(isCenterPt=False)
        sphericalCoord = self._calcSphericaltoGnomonic(convertedScreenCoord, center_point)
        return self._bilinear_interpolation(sphericalCoord)


def perspective_view(img, fov, width, height, look_point, center_point):

    img = np.array(img)
    nfov = NFOV(fov, height, width)
    look_point = np.array(look_point)
    center_point = np.array(center_point)
    img = nfov.toNFOV(img, look_point, center_point)

    return img


path = os.getcwd() + '/../result/persp'

if not os.path.isdir(path):

    os.mkdir(path)

for i in range(1,54):

    img = Image.open('../result/img/' + str(i) + '.png')
    txt = open('../result/box/' + str(i) + '.txt', 'r')

    vertices = get_vertices(txt)

    for j in range(len(get_faces(vertices))):

        face = get_faces(vertices)[j]

        center = get_center_offset(vertices)

        fov = get_fov(vertices, face, center)

        width, height = get_dimensions(vertices, face)

        orientation = get_orientation(get_face_vertices(vertices, face), center)

        wall_center = get_medium_points(get_face_vertices(vertices, face), center)[1]

        # normalization to 1
        wall_center = (wall_center) / (max(wall_center) - min(wall_center))

        # axis incongruence
        wall_center[1] = - wall_center[1]

        offset = sum(np.array(center) * np.array(wall_center))

        if j == 0:
            persp = perspective_view(img, fov, width, height, [orientation + 0.5, 1], center)

        if j != 0:
            persp = perspective_view(img, fov, width, height, [orientation, 0.5], [offset, 0])

        #plt.imshow(persp)
        #plt.show()

        persp = Image.fromarray(persp)
        persp.save('../result/persp/' + str(i) + '-' + str(j) + '.png')

    print(i)

