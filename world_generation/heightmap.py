import collections

import noise
import numpy as np

import data


def create_heightmap(world: data.World):
    heights = np.full(world.regions_count, -1.0)
    heights_prim = np.full(world.regions_count, 0.0)

    for chain in world.mountain_chains:
        regions = data.set_heights_of_mountain_chain(chain, heights, heights_prim, world)

        visited_regions = set()
        to_process = collections.deque(regions)

        while to_process:
            region_id = to_process.popleft()
            if region_id in visited_regions:
                continue
            neighbours = [n for n in world.regions_touching_region[region_id] if n not in visited_regions]
            to_process.extend(neighbours)

            visited_regions.add(region_id)
            for neighbour in neighbours:
                heights[neighbour] = max(heights[neighbour], heights[region_id] - heights_prim[region_id] / 6 - _noise(
                    *world.center_by_region[region_id]))
                heights_prim[neighbour] = heights_prim[region_id]

    return heights


def _noise(x, y):
    scale = 10.0
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0

    r = noise.pnoise2(x / scale,
                      y / scale,
                      octaves=octaves,
                      persistence=persistence,
                      lacunarity=lacunarity,
                      repeatx=1024,
                      repeaty=1024,
                      base=0)
    return r
