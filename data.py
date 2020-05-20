import itertools
from typing import List, Tuple, Dict, Set

from shapely.geometry import Polygon, Point, LineString

MIN_MOUNTAIN_HEIGHT = 0.6

RegionId = int
VertexId = int

Pos = Tuple[float, float]


class World:
    def __init__(
            self,
            center_by_region: Dict[RegionId, Pos],
            pos_by_vertex: Dict[VertexId, Pos],
            regions_touching_region: Dict[RegionId, Set[RegionId]],
            vertices_by_region: Dict[RegionId, List[VertexId]],
            vertices_touching_vertex: Dict[VertexId, Set[VertexId]],
            regions_touching_vertex: Dict[VertexId, Set[RegionId]],
            polygon_by_region: Dict[RegionId, Polygon]
    ):
        self.center_by_region = center_by_region
        self.pos_by_vertex = pos_by_vertex
        self.vertices_by_region = vertices_by_region
        self.polygon_by_region = polygon_by_region
        self.regions_touching_region = regions_touching_region
        self.vertices_touching_vertex = vertices_touching_vertex
        self.regions_touching_vertex = regions_touching_vertex
        self.regions_count = len(center_by_region)
        self.vertices_count = len(regions_touching_vertex)
        self.height_by_vertex: Dict[VertexId, float] = None
        self.height_by_region: Dict[RegionId, float] = None
        self.terrain_by_region: Dict[RegionId, TerrainGroup] = None
        self.terrain_blobs: List[TerrainGroup] = None
        self.downslopes: Dict[VertexId, Set[VertexId]] = None
        self.borders_water_by_vertex: Dict[VertexId, bool] = None
        self.rivers: List[List[VertexId]] = []
        self.moisture_by_vertex: Dict[VertexId, float] = None
        self.mountain_chains = None


def convert_to_world(np_vertices_by_region, np_center_by_region, np_vertices):
    regions_touching_vertex = _calculate_regions_touching_vertex(np_vertices_by_region)
    vertices_by_region = _calculate_vertices_by_region(np_vertices_by_region)
    polygon_by_region = _calculate_polygon_by_region(np_vertices, np_vertices_by_region)
    pos_by_vertex = _calculate_pos_by_vertex(vertices_by_region, np_vertices)
    regions_touching_region = _calculate_region_neighbours(regions_touching_vertex, vertices_by_region)
    a = set()
    for vert in np_vertices_by_region:
        a = a.union(set(vert))
    vertices_touching_vertex = _calculate_neighbouring_vertices(np_vertices_by_region)
    print("LEN:", len(vertices_touching_vertex))

    center_by_region = {k: v for k, v in enumerate(np_center_by_region)}

    return World(center_by_region, pos_by_vertex, regions_touching_region, vertices_by_region, vertices_touching_vertex,
                 regions_touching_vertex, polygon_by_region)


def _calculate_pos_by_vertex(vertices_by_region, np_vertices):
    pos_by_vertex = {}
    for vertices in vertices_by_region.values():
        for vertex_id in vertices:
            pos_by_vertex[vertex_id] = tuple(np_vertices[vertex_id])
    return pos_by_vertex


def _calculate_regions_touching_vertex(np_vertices_by_region):
    regions_touching_vertex = {}
    for region_id, region_vertices in enumerate(np_vertices_by_region):
        for vertex in region_vertices:
            regions_touching_vertex[vertex] = regions_touching_vertex.get(vertex, set()).union({region_id})
    return regions_touching_vertex


def _calculate_polygon_by_region(np_vertices, np_vertices_by_region):
    polygon_by_region = {}
    for region_id, region_vertices in enumerate(np_vertices_by_region):
        polygon_by_region[region_id] = Polygon(np_vertices[region_vertices, :].tolist())
    return polygon_by_region


def _calculate_vertices_by_region(np_vertices_by_region):
    vertices_by_region = {}
    for region_id, region_vertices in enumerate(np_vertices_by_region):
        vertices_by_region[region_id] = region_vertices
    return vertices_by_region


def _calculate_region_neighbours(regions_touching_vertex, vertices_by_region):
    neighbours_by_region = {k: set() for k, _ in enumerate(vertices_by_region)}
    for vertex, regions in regions_touching_vertex.items():
        for region_1 in regions:
            for region_2 in regions:
                if region_1 != region_2:
                    neighbours_by_region[region_1] = neighbours_by_region.get(region_1, set()).union({region_2})
    return neighbours_by_region


def _calculate_neighbouring_vertices(np_vertices_by_region) -> Dict[VertexId, Set[VertexId]]:
    neighbouring_vertices = {}
    for region_id, region_vertices in enumerate(np_vertices_by_region):
        for vertex, _ in enumerate(region_vertices):
            curr_vertex = region_vertices[vertex]
            next_vertex = region_vertices[(vertex + 1) % len(region_vertices)]
            neighbouring_vertices[curr_vertex] = neighbouring_vertices.get(curr_vertex, set()).union({next_vertex})
            neighbouring_vertices[next_vertex] = neighbouring_vertices.get(next_vertex, set()).union({curr_vertex})
    return neighbouring_vertices


def _height_for_the_same_terrain(height_1, height_2):
    return height_to_terrain(height_1) == height_to_terrain(height_2)


class TerrainGroup:
    def __init__(self, terrain_name, group_poly, center_line):
        self.terrain_name = terrain_name
        self.group_poly = group_poly
        self.center_line = center_line


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
        first_height = world.height_by_region[region_id]
        while neighbours_to_visit:
            neighbour_region = neighbours_to_visit.pop()
            if neighbour_region not in regions_in_group and _height_for_the_same_terrain(first_height,
                                                                                         world.height_by_region[
                                                                                             neighbour_region]):
                neighbours_to_visit.update(world.regions_touching_region[neighbour_region])
                group_poly = group_poly.union(world.polygon_by_region[neighbour_region])
                regions_in_group.add(neighbour_region)

        # split groups which contain more than one mountain chain
        intersecting_chains = []
        for chain in world.mountain_chains:
            if chain.line.intersects(group_poly):
                intersecting_chains += [chain.line]
        if len(intersecting_chains) > 1:
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
            if chain.intersects(world.polygon_by_region[region_id]):
                distances[region_id] = 0
                colors[region_id] = chain_id
                mountains_to_visit += [region_id]
    while mountains_to_visit:
        region_id = mountains_to_visit.pop()
        neighbours = [n for n in world.regions_touching_region[region_id] if
                      distances.get(n, 1000) > distances.get(region_id) + 1 and n in regions_in_group]
        for n in neighbours:
            distances[n] = distances[region_id] + 1
            colors[n] = colors[region_id]
    regions_in_subgroups = itertools.groupby(colors.items(), key=lambda x: x[1])
    group_polys = []
    for subgroup_id, regions in regions_in_subgroups:
        next_group_poly = Polygon()
        for r in [r[0] for r in regions]:
            next_group_poly = next_group_poly.union(world.polygon_by_region[r])
        group_polys += [(next_group_poly, intersecting_chains[subgroup_id])]
    return group_polys


class ChainDescriptor:
    def __init__(self, line, height):
        self.line = line
        self.height = height


def fix_mountain_center_line_to_fully_cover_mountain_polygon(world: World):
    """
    A fix is needed because terra-exeris requires that LineStrings of mountain chains must touch
    the edge of terrain of the type 'mountain'
    :param world:
    :return:
    """
    mountains = [t for t in world.terrain_blobs if t.terrain_name == "mountains"]
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
