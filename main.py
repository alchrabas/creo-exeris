#!/usr/bin/env python
import time

import data
import exporter
import plot
from world_generation import voronoi, mountain_chains, heightmap
import world_generation

start = time.time()

number_of_points = 2000
bounding_box = [(0, 1), (0, 1)]

voronoi_diag = voronoi.relaxed_voronoi(number_of_points, bounding_box, 5)
after_v = time.time()
world = data.convert_to_world(voronoi_diag.filtered_regions, voronoi_diag.filtered_points, voronoi_diag.vertices)
after_conv = time.time()
world_generation.mountain_chains.create_mountain_chains(7, world)

world.height_by_region = world_generation.heightmap.create_heightmap(world)
after_height = time.time()

world.terrain_blobs = data.merge_heights_into_blobs(world)
after_blob = time.time()
data.fix_mountain_center_line_to_fully_cover_mountain_polygon(world)
after_fix = time.time()
dump = exporter.export(world.terrain_blobs)

with open("/tmp/terrains.json", "w") as file:
    file.write(dump)

after_export = time.time()
plot.plot_hypsometric(world)
after_plot = time.time()

print("voronoi", after_v - start)
print("conv", after_conv - after_v)
print("hei", after_height - after_conv)
print("blob", after_blob - after_height)
print("fix mountains", after_fix - after_blob)
print("export", after_export - after_fix)
print("plot", after_plot - after_export)

print("Finished in ", time.time() - start, "seconds")
