#!/usr/bin/env python
import time

import data
import plot
import voronoi

start = time.time()

number_of_points = 1000
bounding_box = [(0, 1), (0, 1)]

vor = voronoi.relaxed_voronoi(number_of_points, bounding_box, 25)

world = data.convert_to_world(vor)

heightmap = data.create_heightmap(world)
plot.plot_hypsometric(world, heightmap)

print("Finished in ", time.time() - start, "seconds")
