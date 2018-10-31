import collections
import random

import numpy as np


class World:
    def __init__(self, vertices, neighbours, centers):
        self.vertices = vertices
        self.neighbours = neighbours
        self.centers = centers
        self.regions_count = len(centers)


def convert_to_world(vor):
    regions_adjacent_to_vertex = {}
    neighbours = {}
    vertices = {}
    for region, region_vertices in enumerate(vor.filtered_regions):
        for vertex in region_vertices:
            regions_adjacent_to_vertex[vertex] = regions_adjacent_to_vertex.get(vertex, []) + [region]
        vertices[region] = vor.vertices[region_vertices, :]

    for vertex, regions in regions_adjacent_to_vertex.items():
        for region_1 in regions:
            for region_2 in regions:
                if region_1 != region_2:
                    neighbours[region_1] = neighbours.get(region_1, set()).union({region_2})

    vertices_array = np.array(list(map(lambda a: a[1], sorted(vertices.items()))))

    return World(vertices_array, neighbours, vor.filtered_points)


def create_heightmap(world):
    heights = np.full(world.regions_count, -1.0)
    heights_prim = np.full(world.regions_count, 0.0)

    for i in range(3):
        region_to_put_mointain_to = random.randint(0, world.regions_count - 1)

        visited_regions = set()
        heights[region_to_put_mointain_to] = 1.0
        heights_prim[region_to_put_mointain_to] = 0.1 + (0.5 - random.random()) / 5
        to_process = collections.deque([region_to_put_mointain_to])
        while to_process:
            region_id = to_process.popleft()
            if region_id in visited_regions:
                continue
            neighbours = [n for n in world.neighbours[region_id] if n not in visited_regions]
            to_process.extend(neighbours)

            visited_regions.add(region_id)
            for neighbour in neighbours:
                heights[neighbour] = max(heights[neighbour], heights[region_id] - heights_prim[region_id])
                heights_prim[neighbour] = heights_prim[region_id]

    return heights
