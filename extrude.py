import numpy as np
from stl import mesh
from PIL import Image
import cv2


def extrude(img, depth, blur=None):

    img = np.array(img)

    gray_img = preprocess(img, blur)

    # creates vertices from image with the height of the cube being based off of the pixels height
    vertices_array = []

    min = np.amin(gray_img)
    max = np.amax(gray_img)

    for y, column in enumerate(gray_img):
        for x, pixel in enumerate(column):

            pixel = ((pixel - min) / (max - min)) * depth

            if pixel > 0.1*depth:
                pixel = pixel - 0.1*depth + 1
            else:
                pixel = 1

            vertices = np.array([ \
                [x, y, 0],
                [x + 1, y, 0],
                [x + 1, y + 1, 0],
                [x, y + 1, 0],

                [x, y, pixel],
                [x + 1, y, pixel],
                [x + 1, y + 1, pixel],
                [x, y + 1, pixel],
            ])

            vertices_array.append(vertices)

    faces = np.array(
        [[0, 3, 1], [1, 3, 2], [0, 4, 7], [0, 7, 3], [4, 5, 6], [4, 6, 7], [5, 1, 2], [5, 2, 6], [2, 3, 6], [3, 7, 6],
         [0, 1, 5], [0, 5, 4]])

    # creates meshes from vertices
    meshes = []
    for vertice in vertices_array:
        cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                cube.vectors[i][j] = vertice[f[j], :]

        meshes.append(cube)

    # combines all meshes together
    total_length_data = 0
    for i in range(len(meshes)):
        total_length_data += len(meshes[i].data)

    data = np.zeros(total_length_data, dtype=mesh.Mesh.dtype)
    data['vectors'] = np.array(meshes).reshape((-1, 9)).reshape((-1, 3, 3))
    mesh_final = mesh.Mesh(data.copy())

    return mesh_final


def preprocess(img, blur = None):

    #img = cv2.bitwise_not(img)
    gray_img = cv2.flip(img,0)

    clahe = cv2.createCLAHE(clipLimit=5, tileGridSize=(1,1))

    lab = cv2.cvtColor(gray_img, cv2.COLOR_BGR2LAB)  # convert from BGR to LAB color space
    l, a, b = cv2.split(lab)  # split on 3 different channels

    l2 = clahe.apply(l)  # apply CLAHE to the L-channel

    lab = cv2.merge((l2, a, b))  # merge channels
    gray_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)  # convert from LAB to BGR

    gray_img = cv2.cvtColor(gray_img, cv2.COLOR_RGB2GRAY)

    if blur:
        img = cv2.blur(gray_img, blur)

    return gray_img


# test the class
if __name__ == '__main__':

    img = Image.open('assets/walld4.jpg')
    img = img.resize((int(0.1*img.size[0]),int(0.1*img.size[1])), Image.BILINEAR)

    mesh = extrude( img, 50)

    mesh.save('assets/wallm4.stl')

