import collections
import random

import numpy as np
from shapely.geometry import Polygon, Point, LineString


class World:
    def __init__(self, vertices, neighbours, centers, center_points, polygons):
        self.vertices = vertices
        self.neighbours = neighbours
        self.centers = centers
        self.center_points = center_points
        self.regions_count = len(centers)
        self.polygons = polygons


def convert_to_world(vor):
    regions_adjacent_to_vertex = {}
    neighbours = {}
    vertices = {}
    polygons = {}
    for region, region_vertices in enumerate(vor.filtered_regions):
        for vertex in region_vertices:
            regions_adjacent_to_vertex[vertex] = regions_adjacent_to_vertex.get(vertex, []) + [region]
        vertices[region] = vor.vertices[region_vertices, :]
        polygons[region] = Polygon(vertices[region])

    for vertex, regions in regions_adjacent_to_vertex.items():
        for region_1 in regions:
            for region_2 in regions:
                if region_1 != region_2:
                    neighbours[region_1] = neighbours.get(region_1, set()).union({region_2})

    vertices_array = np.array(list(map(lambda a: a[1], sorted(vertices.items()))))
    centers = np.array(vor.filtered_points)
    center_points = [Point(p) for p in vor.filtered_points]
    polygons = np.array(list(map(lambda a: a[1], sorted(polygons.items()))))

    return World(vertices_array, neighbours, centers, center_points, polygons)


def create_heightmap(world):
    heights = np.full(world.regions_count, -1.0)
    heights_prim = np.full(world.regions_count, 0.0)

    for _ in range(7):
        chain = create_polygonal_chain()
        regions = set_heights_of_mountain_chain(chain, heights, heights_prim, world)

        visited_regions = set()
        to_process = collections.deque(regions)

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


def create_polygonal_chain():
    x1 = random.uniform(0.3, 0.7)
    y1 = random.uniform(0.3, 0.7)

    x2 = x1 + random.uniform(-0.2, 0.2)
    y2 = y1 + random.uniform(-0.2, 0.2)

    return LineString([(x1, y1), (x2, y2)])


def set_heights_of_mountain_chain(chain, heights, heights_prim, world):
    regions = set()
    mountain_height = 1.0 - random.random() / 2
    for region, polygon in enumerate(world.polygons):
        if polygon.intersects(chain):
            heights[region] = mountain_height
            heights_prim[region] = (0.05 + (0.5 - random.random()) / 20) * mountain_height
            regions.add(region)
    return regions
