# Used code from https://stackoverflow.com/a/33602171
import sys

import numpy as np
import scipy as sp
import scipy.spatial


def _centroid_region(vertices):
    # Polygon's signed area
    A = 0
    # Centroid's x
    C_x = 0
    # Centroid's y
    C_y = 0
    for i in range(0, len(vertices) - 1):
        s = (vertices[i, 0] * vertices[i + 1, 1] - vertices[i + 1, 0] * vertices[i, 1])
        A = A + s
        C_x = C_x + (vertices[i, 0] + vertices[i + 1, 0]) * s
        C_y = C_y + (vertices[i, 1] + vertices[i + 1, 1]) * s
    A = 0.5 * A
    C_x = (1.0 / (6.0 * A)) * C_x
    C_y = (1.0 / (6.0 * A)) * C_y
    return np.array([[C_x, C_y]])


def _filter_regions(bounding_box, vor):
    eps = sys.float_info.epsilon
    regions = []
    for region in vor.regions:
        flag = True
        for index in region:
            if index == -1:
                flag = False
                break
            else:
                x = vor.vertices[index, 0]
                y = vor.vertices[index, 1]
                if not (bounding_box[0] - eps <= x <= bounding_box[1] + eps and
                        bounding_box[2] - eps <= y <= bounding_box[3] + eps):
                    flag = False
                    break
        if region != [] and flag:
            regions.append(region)
    return regions


def _mirror_points_along_boundaries(bounding_box, points_center):
    points_left = np.copy(points_center)
    points_left[:, 0] = bounding_box[0] - (points_left[:, 0] - bounding_box[0])
    points_right = np.copy(points_center)
    points_right[:, 0] = bounding_box[1] + (bounding_box[1] - points_right[:, 0])
    points_down = np.copy(points_center)
    points_down[:, 1] = bounding_box[2] - (points_down[:, 1] - bounding_box[2])
    points_up = np.copy(points_center)
    points_up[:, 1] = bounding_box[3] + (bounding_box[3] - points_up[:, 1])
    points = np.append(points_center,
                       np.append(np.append(points_left,
                                           points_right,
                                           axis=0),
                                 np.append(points_down,
                                           points_up,
                                           axis=0),
                                 axis=0),
                       axis=0)
    return points


def _filter_is_in_bounding_box(points, bounding_box):
    return np.logical_and(np.logical_and(bounding_box[0] <= points[:, 0],
                                         points[:, 0] <= bounding_box[1]),
                          np.logical_and(bounding_box[2] <= points[:, 1],
                                         points[:, 1] <= bounding_box[3]))


def _voronoi(points, bounding_box) -> sp.spatial.Voronoi:
    i = _filter_is_in_bounding_box(points, bounding_box)
    # Mirror points
    points_center = points[i, :]
    points = _mirror_points_along_boundaries(bounding_box, points_center)
    # Compute Voronoi
    vor = sp.spatial.Voronoi(points)
    # Filter regions
    vor.filtered_points = points_center
    vor.filtered_regions = _filter_regions(bounding_box, vor)
    return vor


def relaxed_voronoi(number_of_points, bounding_box_2d, relaxation_steps):
    random_points = np.random.rand(number_of_points, 2)
    bounding_box = np.array(bounding_box_2d).ravel()
    vor = _voronoi(random_points, bounding_box)
    for i in range(relaxation_steps):
        centroids = []
        for region in vor.filtered_regions:
            vertices = vor.vertices[region + [region[0]], :]
            centroid = _centroid_region(vertices)
            centroids.append(list(centroid[0, :]))
        vor = _voronoi(np.array(centroids), bounding_box)
    return vor
