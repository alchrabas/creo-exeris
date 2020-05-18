import collections
import statistics

import noise

import data


def create_heightmap(world: data.World):
    world.height_by_vertex = {}
    world.height_by_region = {}

    for chain in world.mountain_chains:
        vertices = set_heights_of_mountain_chain(chain, world)

        visited_vertices = set()
        to_process = collections.deque(vertices)

        while to_process:
            vertex_id = to_process.popleft()
            if vertex_id in visited_vertices:
                continue
            neighbours = [n for n in world.vertices_touching_vertex[vertex_id] if n not in visited_vertices]
            to_process.extend(neighbours)

            visited_vertices.add(vertex_id)
            for neighbour in neighbours:
                world.height_by_vertex[neighbour] = get_height(neighbour, vertex_id, world)

    for region_id, vertices in world.vertices_by_region.items():
        average_height = statistics.mean([world.height_by_vertex[vertex] for vertex in vertices])
        world.height_by_region[region_id] = average_height
    world.downslopes, world.borders_water_by_vertex = _calc_downslopes_and_water_borders(world)


def get_height(this_vertex: data.VertexId, neighbour: data.VertexId, world: data.World):
    neighbour_height = world.height_by_vertex[neighbour]
    current_height_coeff = (1 if neighbour_height > data.MIN_MOUNTAIN_HEIGHT else 0.15)
    applied_noise = 0.02 + min(0.2, abs(_noise(*world.pos_by_vertex[neighbour]))) * current_height_coeff
    return max(world.height_by_vertex.get(this_vertex, -1),
               neighbour_height - applied_noise)


def set_heights_of_mountain_chain(chain: data.ChainDescriptor, world: data.World):
    vertices = set()
    for region_id, polygon in world.polygon_by_region.items():
        if polygon.intersects(chain.line):
            for vertex_id in world.vertices_by_region[region_id]:
                world.height_by_vertex[vertex_id] = chain.height
                vertices.add(vertex_id)
    return vertices


def _calc_downslopes_and_water_borders(world: data.World):
    downslopes = {}
    borders_water_by_vertex = {k: False for k in world.vertices_touching_vertex.keys()}
    for vertex, neighbouring_vertices in world.vertices_touching_vertex.items():
        any_touching_region_is_water = any(
            [world.height_by_region[region_id] < 0 for region_id in world.regions_touching_vertex[vertex]])
        if any_touching_region_is_water:
            downslopes[vertex] = set()
            borders_water_by_vertex[vertex] = True
        else:
            current_height = world.height_by_vertex[vertex]
            downslopes[vertex] = set([n for n in neighbouring_vertices if world.height_by_vertex[n] < current_height])
    return downslopes, borders_water_by_vertex


def _noise(x, y):
    scale = 10.0
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0

    r = noise.pnoise2(x * scale,
                      y * scale,
                      octaves=octaves,
                      persistence=persistence,
                      lacunarity=lacunarity,
                      repeatx=1024,
                      repeaty=1024,
                      base=0)
    return r
