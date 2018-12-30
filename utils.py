import numpy as np
import math

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

        medium_point = 0.5*(np.array(face[i-1]) + np.array(face[i])) - np.array(offset) + 0.00000001

        medium_points.append(medium_point)

    return medium_points


def get_angle(vector):

    angle = np.arccos(
        np.clip(np.dot(np.array(vector), [1, 0, 0]) / (np.linalg.norm(vector) * np.linalg.norm([1, 0, 0])), -1, 1))

    if vector [1] < 0:

        angle = math.radians(360) - angle

    return angle


def get_orientation(face, center):

    vector = get_medium_points(face, center)[1]
    if vector[0] > 0:
        angle = 1 - 0.5 / (1 + math.exp(-vector[1]/vector[0]))

    if vector[0] < 0:
        angle = 0.5 - 0.5 / (1 + math.exp(-vector[1]/vector[0]))

    return angle


def get_fov(vertices, face, center):

    fov = []

    face = get_face_vertices(vertices, face)

    vectors = get_medium_points(face, center)

    if all(vector[2] == 0.00000001 for vector in vectors):

        for vector in vectors:

            vector[2] = 0.5

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