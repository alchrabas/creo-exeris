import collections
import itertools
import math
import random
from typing import List

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
        self.heights = None
        self.terrains: List[TerrainGroup] = None
        self.rivers = None
        self.mountain_chains = None


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


def create_heightmap(world: World):
    heights = np.full(world.regions_count, -1.0)
    heights_prim = np.full(world.regions_count, 0.0)

    for chain in world.mountain_chains:
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


def _height_for_the_same_terrain(height_1, height_2):
    return height_to_terrain(height_1) == height_to_terrain(height_2)


class TerrainGroup:
    def __init__(self, terrain_name, group_poly, center_line):
        self.terrain_name = terrain_name
        self.group_poly = group_poly
        self.center_line = center_line


MIN_MOUNTAIN_HEIGHT = 0.6


def height_to_terrain(height):
    if height >= MIN_MOUNTAIN_HEIGHT:
        return "mountains"
    if height >= 0:
        return "grassland"
    if height >= -0.2:
        return "shallow_water"
    return "deep_water"


def merge_heights_into_blobs(world: World):
    to_visit = set(range(0, world.regions_count))

    groups = []
    while to_visit:
        region_id = to_visit.pop()

        regions_in_group = set()
        group_poly = Polygon()
        neighbours_to_visit = {region_id}
        first_height = world.heights[region_id]
        while neighbours_to_visit:
            neighbour = neighbours_to_visit.pop()
            if neighbour not in regions_in_group and _height_for_the_same_terrain(first_height,
                                                                                  world.heights[neighbour]):
                neighbours_to_visit.update(world.neighbours[neighbour])
                group_poly = group_poly.union(world.polygons[neighbour])
                regions_in_group.add(neighbour)

        # split groups which contain more than one mountain chain
        intersecting_chains = []
        for chain in world.mountain_chains:
            if chain.line.intersects(group_poly):
                intersecting_chains += [chain.line]
        if len(intersecting_chains) > 1:  # TODO SHOULD NEVER HAPPEN
            raise ValueError(
                "there should not be more than one intersecting chain, there are: " + str(intersecting_chains))
            group_polys = _split_intersecting_mountain_chains(intersecting_chains, regions_in_group, world)
        else:
            group_polys = [(group_poly, intersecting_chains[0] if len(intersecting_chains) else None)]
        for group_poly in group_polys:
            groups.append(TerrainGroup(height_to_terrain(first_height), group_poly[0], group_poly[1]))
        to_visit.difference_update(regions_in_group)
    return groups


def _split_intersecting_mountain_chains(intersecting_chains, regions_in_group, world: World):
    distances = {}
    colors = {}
    mountains_to_visit = []
    for region_id in regions_in_group:
        for chain_id, chain in enumerate(intersecting_chains):
            if chain.intersects(world.polygons[region_id]):
                distances[region_id] = 0
                colors[region_id] = chain_id
                mountains_to_visit += [region_id]
    while mountains_to_visit:
        region_id = mountains_to_visit.pop()
        neighbours = [n for n in world.neighbours[region_id] if
                      distances.get(n, 1000) > distances.get(region_id) + 1 and n in regions_in_group]
        for n in neighbours:
            distances[n] = distances[region_id] + 1
            colors[n] = colors[region_id]
    regions_in_subgroups = itertools.groupby(colors.items(), key=lambda x: x[1])
    group_polys = []
    for subgroup_id, regions in regions_in_subgroups:
        next_group_poly = Polygon()
        for r in [r[0] for r in regions]:
            next_group_poly = next_group_poly.union(world.polygons[r])
        group_polys += [(next_group_poly, intersecting_chains[subgroup_id])]
    return group_polys


class ChainDescriptor:
    def __init__(self, line, height, height_prim):
        self.line = line
        self.height = height
        self.height_prim = height_prim


def create_polygonal_chain():
    x1 = random.uniform(0.3, 0.7)
    y1 = random.uniform(0.3, 0.7)

    x2 = x1 + random.uniform(-0.2, 0.2)
    y2 = y1 + random.uniform(-0.2, 0.2)

    line_string = LineString([(x1, y1), (x2, y2)])
    mountain_height = 1.0 - random.random() / 2
    mountain_height_prim = (0.3 + (0.5 - random.random()) / 20) * mountain_height
    return ChainDescriptor(line_string, mountain_height, mountain_height_prim)


def set_heights_of_mountain_chain(chain: ChainDescriptor, heights, heights_prim, world: World):
    regions = set()

    for region, polygon in enumerate(world.polygons):
        if polygon.intersects(chain.line):
            heights[region] = chain.height
            heights_prim[region] = chain.height_prim
            regions.add(region)
    return regions


def intersects_with_other_mountain_chains(
        candidate_chain: ChainDescriptor,
        existing_chains: List[ChainDescriptor],
        world: World):
    for existing_chain in existing_chains:
        distance = candidate_chain.line.distance(existing_chain.line)
        approx_region_diameter = 1.2 / math.sqrt(world.regions_count)

        candidate_chain_over_min_height = (candidate_chain.height - MIN_MOUNTAIN_HEIGHT)
        existing_chain_over_min_height = (existing_chain.height - MIN_MOUNTAIN_HEIGHT)

        number_of_regions_to_be_away = \
            math.ceil(candidate_chain_over_min_height / candidate_chain.height_prim) + \
            math.ceil(existing_chain_over_min_height / existing_chain.height_prim) + 1
        if distance / approx_region_diameter < number_of_regions_to_be_away:
            return True
    return False


def create_mountain_chains(number_of_chains, world: World):
    world.mountain_chains = []
    for _ in range(number_of_chains):
        new_chain = create_polygonal_chain()
        if not intersects_with_other_mountain_chains(new_chain, world.mountain_chains, world):
            world.mountain_chains += [new_chain]
        else:
            print("FAILED, TOO CLOSE!")


def fix_mountain_center_line_to_fully_cover_mountain_polygon(world: World):
    """
    A fix is needed because terra-exeris requires that LineStrings of mountain chains must touch
    the edge of terrain of the type 'mountain'
    :param world:
    :return:
    """
    mountains = [t for t in world.terrains if t.terrain_name == "mountains"]
    for mountain in mountains:
        mountain_center_line_points = mountain.center_line.coords

        new_p_first = _move_point_farther_away(mountain_center_line_points[0],
                                               mountain_center_line_points[1],
                                               mountain.group_poly)
        new_p_last = _move_point_farther_away(mountain_center_line_points[-1],
                                              mountain_center_line_points[-2],
                                              mountain.group_poly)

        mountain.center_line = LineString([new_p_first] + mountain_center_line_points[1:-1] + [new_p_last])


def _move_point_farther_away(border_point, second_point, poly):
    new_point = Point(second_point[0] + (border_point[0] - second_point[0]) * 100,
                      second_point[1] + (border_point[1] - second_point[1]) * 100)

    intersection = poly.exterior.intersection(LineString([new_point, second_point]))
    if not isinstance(intersection, Point):
        raise ValueError("the mountain chain cannot reach the border")
    intersection = Point(second_point[0] + (intersection.x - second_point[0]) * 1.001,
                         second_point[1] + (intersection.y - second_point[1]) * 1.001)
    return intersection


def create_precipitation_map(world: World):
    clouds_count = round(math.sqrt(world.regions_count))
    regions_sorted_by_x = sorted(enumerate(world.center_points), key=lambda id_and_point: id_and_point[1].x)
    regions_with_initial_clouds = [x[0] for x in regions_sorted_by_x[:clouds_count]]
    print(regions_with_initial_clouds)
    world.precipitation = np.full(world.regions_count, 0.0)
    for x in regions_with_initial_clouds:
        world.precipitation[x] = 1.0

    return None
