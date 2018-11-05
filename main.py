#!/usr/bin/env python
import time

import data
import exporter
import plot
import voronoi

start = time.time()

number_of_points = 400
bounding_box = [(0, 1), (0, 1)]

vor = voronoi.relaxed_voronoi(number_of_points, bounding_box, 25)

world = data.convert_to_world(vor)

data.create_mountain_chains(7, world)
world.heights = data.create_heightmap(world)


world.terrains = data.merge_heights_into_blobs(world)
data.fix_mountain_center_line_to_fully_cover_mountain_polygon(world)
print(len(world.terrains))

dump = exporter.export(world.terrains)

with open("/tmp/terrains.json", "w") as file:
    file.write(dump)

plot.plot_hypsometric(world)

print("Finished in ", time.time() - start, "seconds")
