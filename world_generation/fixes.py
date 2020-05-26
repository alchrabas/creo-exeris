import itertools

from shapely.geometry import LineString, Point

import data
from collections import Counter

from world_generation import terrains
from world_generation.terrains import TerrainTypes


def _most_frequent(list_of_values):
    occurence_count = Counter(list_of_values)
    return occurence_count.most_common(1)[0][0]


def remove_artifacts_before_clustering(world: data.World):
    add_shallow_water_near_coast(world)
    shallowize_isolated_deep_water(world)
    shallowize_lakes_touching_sea(world)
    deforest_near_coast(world)
    remove_river_segments_in_lakes(world)
    remove_mountain_chains_which_are_too_low(world)
    remove_small_isolated_terrain_areas(world)


def remove_artifacts_after_clustering(world: data.World):
    fix_mountain_center_line_to_fully_cover_mountain_polygon(world)


def remove_small_isolated_terrain_areas(world: data.World):
    blobs = _get_terrain_blobs(world)
    removed_blobs = 0
    for blob in blobs:
        # removing lake would make river go nowhere
        if len(blob) <= 3 and world.terrain_by_region[list(blob)[0]] != terrains.TerrainTypes.LAKE:
            neighbours = set()
            for region_id in blob:
                new_neighbours = [neighbour for neighbour in world.regions_touching_region[region_id]
                                  if neighbour not in blob]

                neighbours.update(new_neighbours)
            most_frequent_neighbour = _most_frequent([world.terrain_by_region[neighbour] for neighbour in neighbours])

            for region_id in blob:
                world.terrain_by_region[region_id] = most_frequent_neighbour
            removed_blobs += 1
    print("removed", removed_blobs, "artifacts")


def shallowize_lakes_touching_sea(world):
    shallow_waters = [region_id for region_id, terrain in world.terrain_by_region.items() if
                      terrain == TerrainTypes.SHALLOW_WATER]
    lakes_to_turn_into_shallow_water = data.walk_over_regions(shallow_waters,
                                                              lambda r: world.terrain_by_region[r] == TerrainTypes.LAKE,
                                                              world)
    for region_id in lakes_to_turn_into_shallow_water:
        world.terrain_by_region[region_id] = TerrainTypes.SHALLOW_WATER


def _get_terrain_blobs(world):
    regions_to_visit = set(world.regions_touching_region.keys())
    blobs = []
    while regions_to_visit:
        region_id = regions_to_visit.pop()
        terrain_type = world.terrain_by_region[region_id]

        current_blob = {region_id}
        regions_of_current_blob_to_visit = {region_id}
        while regions_of_current_blob_to_visit:
            region_of_same_terrain = regions_of_current_blob_to_visit.pop()
            new_neighbours = [neighbour for neighbour in world.regions_touching_region[region_of_same_terrain]
                              if world.terrain_by_region[neighbour] == terrain_type
                              and neighbour not in current_blob]
            current_blob.update(new_neighbours)
            regions_of_current_blob_to_visit.update(new_neighbours)
        blobs.append(current_blob)
        regions_to_visit.difference_update(current_blob)
    return blobs


def remove_river_segments_in_lakes(world: data.World):
    resultant_rivers = []
    for river in world.rivers:
        river_so_far = []
        for current_vertex in river:
            river_so_far += [current_vertex]
            if _any_region_touching_vertex_is_lake(current_vertex, world):
                break
        if len(river_so_far) > 1:
            resultant_rivers += [river_so_far]
    world.rivers = resultant_rivers


def _any_region_touching_vertex_is_lake(vertex: data.VertexId, world: data.World):
    for region_id in world.regions_touching_vertex[vertex]:
        if world.terrain_by_region[region_id] in (TerrainTypes.LAKE, TerrainTypes.SHALLOW_WATER):
            return True
    return False


def remove_mountain_chains_which_are_too_low(world: data.World):
    # replace with better, real-height-based algorithm if this approach is not good enough
    world.mountain_chains = [chain for chain in world.mountain_chains if chain.height >= data.MIN_MOUNTAIN_HEIGHT]


def add_shallow_water_near_coast(world):
    shallowize_neighbours = []
    for region_id, terrain in world.terrain_by_region.items():
        if terrain == TerrainTypes.DEEP_WATER:
            for neighbour in world.regions_touching_region[region_id]:
                if world.terrain_by_region[neighbour] not in (TerrainTypes.DEEP_WATER, TerrainTypes.SHALLOW_WATER):
                    shallowize_neighbours += [neighbour]
                    _turn_into_shallow_water(neighbour, world)
    for region_id in shallowize_neighbours:
        _turn_into_shallow_water(region_id, world)
    shallowize_neighbours = list(itertools.chain(*[world.regions_touching_region[r] for r in shallowize_neighbours]))
    for region_id in shallowize_neighbours:  # second line of shallow water
        if world.terrain_by_region[region_id] == TerrainTypes.DEEP_WATER:
            _turn_into_shallow_water(region_id, world)


def shallowize_isolated_deep_water(world: data.World):
    border_vertices = data.vertices_touching_border(world)
    border_regions = set()
    for v in border_vertices:
        border_regions.update(world.regions_touching_vertex[v])

    deep_water_touching_border = data.walk_over_regions(border_regions,
                                                        lambda r: world.terrain_by_region[r] == TerrainTypes.DEEP_WATER,
                                                        world)
    for region_id, terrain in world.terrain_by_region.items():
        if region_id not in deep_water_touching_border and terrain == TerrainTypes.DEEP_WATER:
            _turn_into_shallow_water(region_id, world)


def _turn_into_shallow_water(region_id: data.RegionId, world: data.World):
    world.height_by_region[region_id] = -0.1
    world.terrain_by_region[region_id] = TerrainTypes.SHALLOW_WATER


def deforest_near_coast(world: data.World):
    neighbours_to_deforest = []
    for region_id, terrain in world.terrain_by_region.items():
        neighbouring_terrains = [world.terrain_by_region[n] for n in world.regions_touching_region[region_id]]
        if terrain in (TerrainTypes.CONIFEROUS_FOREST,
                       TerrainTypes.DECIDUOUS_FOREST,
                       TerrainTypes.GRASSLAND) and TerrainTypes.SHALLOW_WATER in neighbouring_terrains:
            world.terrain_by_region[region_id] = TerrainTypes.GRASSLAND
            neighbours_to_deforest += world.regions_touching_region[region_id]

    for region_id in neighbours_to_deforest:
        if world.terrain_by_region[region_id] in (TerrainTypes.CONIFEROUS_FOREST, TerrainTypes.DECIDUOUS_FOREST):
            world.terrain_by_region[region_id] = TerrainTypes.GRASSLAND


def fix_mountain_center_line_to_fully_cover_mountain_polygon(world: data.World):
    """
    A fix is needed because terra-exeris requires that LineStrings of mountain chains must touch
    the edge of terrain of the type 'mountain'
    :param world:
    :return:
    """
    mountains = [cluster for cluster in world.clusters if cluster.terrain_type == TerrainTypes.MOUNTAIN]
    for mountain_chain in world.mountain_chains:
        intersecting_mountains = [mountain for mountain in mountains if mountain.polygon.intersects(mountain_chain.line)]
        if not intersecting_mountains:
            continue
        if len(intersecting_mountains) > 1:
            print("COS SIE POPSULO", intersecting_mountains)
        intersecting_mountain = intersecting_mountains[0]

        mountain_center_line_points = mountain_chain.line.coords

        new_p_first = _move_point_farther_away(mountain_center_line_points[0],
                                               mountain_center_line_points[1],
                                               intersecting_mountain.polygon)
        new_p_last = _move_point_farther_away(mountain_center_line_points[-1],
                                              mountain_center_line_points[-2],
                                              intersecting_mountain.polygon)

        mountain_chain.line = LineString([new_p_first] + mountain_center_line_points[1:-1] + [new_p_last])


def _move_point_farther_away(border_point, second_point, poly):
    new_point = Point(second_point[0] + (border_point[0] - second_point[0]) * 100,
                      second_point[1] + (border_point[1] - second_point[1]) * 100)

    intersection = poly.exterior.intersection(LineString([new_point, second_point]))
    if not isinstance(intersection, Point):
        raise ValueError("the mountain chain cannot reach the border")
    intersection = Point(second_point[0] + (intersection.x - second_point[0]) * 1.001,
                         second_point[1] + (intersection.y - second_point[1]) * 1.001)
    return intersection
