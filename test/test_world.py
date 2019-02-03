import numpy as np

import data
import unittest


class TestVoronoi(unittest.TestCase):
    def test_four_square_regions(self):
        """
        the map is between 0 and 4 in both dimensions

        regions:
        3 2
        0 1

        vertices:
        4 5 6
        3 2 7
        0 1 8
        """

        vertices_by_region = np.array([[0, 1, 2, 3], [1, 2, 7, 8], [2, 5, 6, 7], [2, 3, 4, 5]])
        centers_by_region = np.array([[1, 1], [3, 1], [3, 3], [1, 3]])
        vertices = np.array([[0, 0], [2, 0], [2, 2], [0, 2], [0, 4], [2, 4], [4, 4], [4, 2], [4, 0]])
        world = data.convert_to_world(vertices_by_region, centers_by_region, vertices)

        self.assertEqual({0: {0}, 1: {0, 1}, 2: {0, 1, 2, 3}, 3: {0, 3}, 4: {3}, 5: {2, 3}, 6: {2}, 7: {1, 2}, 8: {1}},
                         world.regions_touching_vertex)
        self.assertEqual({0: {1, 3}, 1: {0, 2, 8}, 2: {1, 3, 5, 7}, 3: {0, 2, 4},
                          4: {3, 5}, 5: {2, 4, 6}, 6: {5, 7}, 7: {2, 6, 8}, 8: {1, 7}},
                         world.vertices_touching_vertex)

    def test_calculate_neighbouring_vertices(self):
        vertices_touching_vertex = data._calculate_neighbouring_vertices([[0, 1, 3], [2, 3, 1]])
        self.assertEqual({0: {1, 3}, 1: {0, 2, 3}, 2: {1, 3}, 3: {0, 1, 2}}, vertices_touching_vertex)
