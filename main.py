#!/usr/bin/env python


import data
import plot
import voronoi

number_of_points = 10
bounding_box = [(0, 1), (0, 1)]

vor = voronoi.relaxed_voronoi(number_of_points, bounding_box, 25)

world = data.convert_to_world(vor)

plot.plot_regions(world)
