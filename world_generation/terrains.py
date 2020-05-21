import data
from collections import Counter


def most_frequent(list_of_values):
    occurence_count = Counter(list_of_values)
    return occurence_count.most_common(1)[0][0]


class TerrainTypes:
    LAKE = "lake"
    DEEP_WATER = "deep_water"
    SHALLOW_WATER = "shallow_water"
    MOUNTAIN = "mountain"
    CONIFEROUS_FOREST = "pine_forest"
    DECIDUOUS_FOREST = "oak_forest"
    GRASSLAND = "grassland"
    PLAINS = "plains"


def generate_terrains(world: data.World):
    world.moisture_by_vertex = _generate_moisture(world)
    terrain_by_vertex = {}
    lake_vertices = _get_inland_water_vertices(world)
    for vertex_id in world.vertices_touching_vertex:
        if vertex_id in lake_vertices:
            terrain_by_vertex[vertex_id] = TerrainTypes.LAKE
        else:
            terrain_by_vertex[vertex_id] = _terrain_by_height_and_moisture(
                world.height_by_vertex[vertex_id],
                world.moisture_by_vertex[vertex_id])
    terrain_by_region = {}
    for region_id, vertices in world.vertices_by_region.items():
        most_common_terrain_across_vertices = most_frequent([terrain_by_vertex[v] for v in vertices])
        terrain_by_region[region_id] = most_common_terrain_across_vertices
    world.terrain_by_region = terrain_by_region


def _terrain_by_height_and_moisture(height, moisture):
    if height < -0.2:
        return TerrainTypes.DEEP_WATER
    if height < 0:
        return TerrainTypes.SHALLOW_WATER
    if height > 0.6:
        return TerrainTypes.MOUNTAIN
    if height > 0.45 and moisture > 0.7:
        return TerrainTypes.CONIFEROUS_FOREST
    if height > 0.1 and moisture > 0.7:
        return TerrainTypes.DECIDUOUS_FOREST
    if moisture > 0.5:
        return TerrainTypes.GRASSLAND
    else:
        return TerrainTypes.PLAINS


def _generate_moisture(world: data.World):
    lake_vertices = _get_inland_water_vertices(world)
    moisture = {vertex_id: 0.0 for vertex_id in world.vertices_touching_vertex.keys()}
    for vertex_id in lake_vertices:
        moisture[vertex_id] = 1.0
    for river in world.rivers:
        for vertex_id in river:
            moisture[vertex_id] = 1.0

    to_visit = set([vertex_id for vertex_id, m in moisture.items() if m == 1.0])
    visited = set()
    while to_visit:
        curr_vertex = to_visit.pop()
        if curr_vertex in visited:
            continue
        for neighbour in world.vertices_touching_vertex[curr_vertex]:
            new_moisture = moisture[curr_vertex] * 0.98
            if new_moisture > moisture[neighbour]:
                moisture[neighbour] = new_moisture
                to_visit.add(neighbour)
        visited.add(curr_vertex)

    return moisture


def _get_inland_water_vertices(world: data.World):
    vertices_touching_border = [v for v, pos in world.pos_by_vertex.items() if
                                pos[0] in (0.0, 1.0) or pos[1] in (0.0, 1.0)]

    visited = set()
    to_visit = set(vertices_touching_border)
    while to_visit:
        curr_vertex = to_visit.pop()
        if curr_vertex in visited:
            continue
        visited.add(curr_vertex)
        to_visit.update([neighbour for neighbour in world.vertices_touching_vertex[curr_vertex]
                         if world.height_by_vertex[neighbour] < 0 and neighbour not in visited])

    return [v for v, height in world.height_by_vertex.items() if height < 0 and v not in visited]
