#!/usr/bin/env python
import random
import shutil
import time
import pickle
from os import path

import data
import plot
import world_generation
from checkpoint import time_from_last_checkpoint
from world_generation import voronoi, mountain_chains, heightmap, rivers, terrains, fixes, clustering

start = time.time()

number_of_points = 25000
bounding_box = [(0, 1), (0, 1)]

checkpoint = time_from_last_checkpoint()
next(checkpoint)

if not path.exists("dumps/world_post_voronoi_" + str(number_of_points)):
    print("No cached voronoi found. Generating it...")
    voronoi_diag = voronoi.relaxed_voronoi(number_of_points, bounding_box, 8)
    print("voronoi", next(checkpoint))

    world = data.convert_to_world(voronoi_diag.filtered_regions, voronoi_diag.filtered_points, voronoi_diag.vertices)
    print("conversion", next(checkpoint))
    pickle.dump(world, open("dumps/world_post_voronoi_" + str(number_of_points), "wb"))
else:
    world = pickle.load(open("dumps/world_post_voronoi_" + str(number_of_points), "rb"))

world_generation.mountain_chains.create_mountain_chains(11, world)
world_generation.heightmap.create_heightmap(world)
print("heightmap", next(checkpoint))

world_generation.rivers.generate_rivers(17, world)
print("rivers", next(checkpoint))

world_generation.terrains.generate_terrains(world)
print("terrains", next(checkpoint))

world_generation.fixes.remove_artifacts_before_clustering(world)
print("remove_artifacts_before_clustering", next(checkpoint))

world_generation.clustering.cluster_terrains(world)
print("clustering", next(checkpoint))

world_generation.fixes.remove_artifacts_after_clustering(world)
print("remove_artifacts_after_clustering", next(checkpoint))

# dump = exporter.export(world.terrain_blobs)

# with open("/tmp/terrains.json", "w") as file:
#     file.write(dump)
# print("export", next(checkpoint))

plot.plot_map(world, True)
print("plot", next(checkpoint))

file_id = random.randint(0, 1000000)
file_name = "generated_map_{}_{}".format(number_of_points, file_id)
shutil.copyfile("map.png", "rendered_maps/" + file_name)

print("Generated map with name generated_map_" + str(number_of_points) + "_" + str(file_id))
pickle.dump(world, open("dumps/" + file_name, "wb"))

print("Finished in {} seconds".format(time.time() - start))
