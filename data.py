import numpy as np


class World:
    def __init__(self, vertices, neighbours, centers):
        self.vertices = vertices
        self.neighbours = neighbours
        self.centers = centers


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
