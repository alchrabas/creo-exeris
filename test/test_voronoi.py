import numpy as np

from world_generation import voronoi
import unittest


class TestVoronoi(unittest.TestCase):
    def test_single_point(self):
        points = np.array([[0.5, 0.5]])
        bounding_box = np.array([(0, 1), (0, 1)]).ravel()
        vor = voronoi._voronoi(points, bounding_box)
        self.assertEqual([[0.5, 0.5]], vor.filtered_points.tolist())  # the same point
        self.assertEqual({(0, 0), (0, 1), (1, 1), (1, 0)}, self._to_set_of_tuples(vor.vertices))
        self.assertEqual(1, len(vor.filtered_regions))
        self.assertEqual({0, 1, 2, 3}, set(vor.filtered_regions[0]))

    def _to_set_of_tuples(self, np_array):
        return set(map(tuple, np_array.tolist()))


if __name__ == "__main__":
    unittest.main()
