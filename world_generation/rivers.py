import collections
import math
import random
from typing import List

import data


MIN_RIVER_LENGTH = 5


def generate_rivers(rivers: int, world: data.World):
    mountain_vertices = [vertex for vertex, height in world.height_by_vertex.items() if
                         height >= data.MIN_MOUNTAIN_HEIGHT]
    created_rivers = []
    vertices_having_river = set()
    attempts = 0
    while len(created_rivers) < rivers and attempts < 1000:
        attempts += 1
        spring_id = random.choice(mountain_vertices)

        river = [spring_id]
        failed_attempts = 0
        while True:
            last_river_segment = river[-1]
            if len(world.downslopes[last_river_segment]) == 0:  # no downslopes
                if world.height_by_vertex[last_river_segment] < 0:  # river reaches existing sea/lake
                    break

                failed_attempts += 1
                if failed_attempts > 50:
                    if len(river) > MIN_RIVER_LENGTH:
                        _generate_lake(last_river_segment, river[-2], world)
                    break
                elif len(river) > 3:  # remove previous segments to try again because they lead to a sink
                    for _ in range(min(len(river) - 1, math.ceil(failed_attempts / 5))):
                        river.pop()
                else:
                    break
            else:
                downslope_having_river = _downslope_having_river(world.downslopes[last_river_segment],
                                                                 vertices_having_river)
                if downslope_having_river:
                    river.append(downslope_having_river)
                    break

                next_river_vertex = random.choice(tuple(world.downslopes[last_river_segment]))
                river.append(next_river_vertex)

        if len(river) > MIN_RIVER_LENGTH:
            created_rivers.append(river)
            vertices_having_river = vertices_having_river.union(river)

    world.rivers = created_rivers


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

        if dist < 3 and height_difference < 0.03:
            to_process += [(vertex, dist + 1) for vertex in world.vertices_touching_vertex[vertex_id]]
            for region_id in world.regions_touching_vertex[vertex_id]:
                world.height_by_region[region_id] = -0.1
                lake_vertices += world.vertices_by_region[region_id]

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

