#!/usr/bin/env python
import time
from typing import Iterator

import data
import exporter
import plot
import world_generation
from world_generation import voronoi, mountain_chains, heightmap, rivers


def time_from_last_checkpoint() -> Iterator[float]:
    """
    Generator returning seconds elapsed since the previous call of the generator
    """
    start = time.time()
    yield 0.0
    while True:
        last_checkpoint = time.time()
        yield last_checkpoint - start
        start = last_checkpoint


start = time.time()

number_of_points = 5000
bounding_box = [(0, 1), (0, 1)]

checkpoint = time_from_last_checkpoint()
next(checkpoint)

voronoi_diag = voronoi.relaxed_voronoi(number_of_points, bounding_box, 8)
print("voronoi", next(checkpoint))

world = data.convert_to_world(voronoi_diag.filtered_regions, voronoi_diag.filtered_points, voronoi_diag.vertices)
print("conversion", next(checkpoint))

world_generation.mountain_chains.create_mountain_chains(5, world)
world_generation.heightmap.create_heightmap(world)
print("heightmap", next(checkpoint))

world_generation.rivers.generate_rivers(17, world)
print("rivers", next(checkpoint))

# world.terrain_blobs = data.merge_heights_into_blobs(world)
# print("convert to blobs", next(checkpoint))

# data.fix_mountain_center_line_to_fully_cover_mountain_polygon(world)
# print("fix mountains", next(checkpoint))

# dump = exporter.export(world.terrain_blobs)

# with open("/tmp/terrains.json", "w") as file:
#     file.write(dump)
# print("export", next(checkpoint))

plot.plot_hypsometric(world, True)
print("plot", next(checkpoint))

print("Finished in {} seconds".format(time.time() - start))
