import collections
import random
from typing import List

import data


def generate_rivers(rivers: int, world: data.World):
    mountain_vertices = [vertex for vertex, height in world.height_by_vertex.items() if
                         height >= data.MIN_MOUNTAIN_HEIGHT]
    created_rivers = []
    vertices_having_river = set()
    for _ in range(rivers):
        spring_id = random.choice(mountain_vertices)

        river = [spring_id]
        while True:
            last_river_segment = river[-1]
            if len(world.downslopes[last_river_segment]) == 0:
                if not world.borders_water_by_vertex[last_river_segment] and len(river) > 2:
                    _generate_lake(last_river_segment, river[-2], world)
                break

            downslope_having_river = _downslope_having_river(world.downslopes[last_river_segment],
                                                             vertices_having_river)
            if downslope_having_river:
                river.append(downslope_having_river)
                break

            next_river_vertex = random.choice(tuple(world.downslopes[last_river_segment]))
            river.append(next_river_vertex)

        if len(river) > 2:
            created_rivers.append(river)
        vertices_having_river = vertices_having_river.union(river)

    world.rivers = _remove_river_segments_in_lakes(created_rivers, world)


def _generate_lake(start_vertex_id: data.VertexId, previous_vertex_id: data.VertexId, world: data.World):
    start_vertex = world.pos_by_vertex[start_vertex_id]
    previous_vertex = world.pos_by_vertex[previous_vertex_id]
    vector_x = start_vertex[0] - previous_vertex[0]
    vector_y = start_vertex[1] - previous_vertex[1]

    center_of_lake = _closest_vertex(start_vertex[0] + vector_x, start_vertex[1] + vector_y, world)

    _create_lake_around_center(center_of_lake, world)


def _create_lake_around_center(center: data.VertexId, world: data.World):
    to_process = collections.deque([(center, 0)])

    lake_vertices = []
    while to_process:
        vertex_id, dist = to_process.popleft()
        height_difference = abs(world.height_by_vertex[vertex_id] - world.height_by_vertex[center])
        if dist < 3 and height_difference < 0.10:
            lake_vertices += world.vertices_touching_vertex[vertex_id]
            to_process += [(vertex, dist + 1) for vertex in world.vertices_touching_vertex[vertex_id]]
            for region_id in world.regions_touching_vertex[vertex_id]:
                world.height_by_region[region_id] = -0.1

    for vertex in lake_vertices:
        world.height_by_vertex[vertex] = -0.1


def _closest_vertex(x, y, world: data.World) -> data.VertexId:
    closest_vertex = 0
    min_distance = 9999
    for vertex_id, pos in world.pos_by_vertex.items():
        if distance(x, y, pos[0], pos[1]) < min_distance:
            closest_vertex = vertex_id
            min_distance = distance(x, y, pos[0], pos[1])
    return closest_vertex


def distance(a_x, a_y, b_x, b_y):
    return ((b_x - a_x) ** 2 + (b_y - a_y) ** 2) ** 0.5


def _downslope_having_river(downslopes, vertices_having_river):
    for downslope in downslopes:
        if downslope in vertices_having_river:
            return downslope
    return None


def _remove_river_segments_in_lakes(original_rivers: List[List[data.VertexId]], world: data.World):
    resultant_rivers = []
    for river in original_rivers:
        river_so_far = [river[0]]
        pos = 1
        while pos < len(river):
            previous_vertex, current_vertex = river[pos - 1], river[pos]

            if _any_region_touching_vertex_is_lake(previous_vertex, world) \
                    and _any_region_touching_vertex_is_lake(current_vertex, world):
                if len(river_so_far) > 2:
                    resultant_rivers += [river_so_far]
                river_so_far = []
            else:
                river_so_far += [current_vertex]
            pos += 1
        if len(river_so_far) > 1:
            resultant_rivers += [river_so_far]
    return resultant_rivers


def _any_region_touching_vertex_is_lake(vertex: data.VertexId, world: data.World):
    for region_id in world.regions_touching_vertex[vertex]:
        if world.height_by_region[region_id] < 0:
            return True
    return False
