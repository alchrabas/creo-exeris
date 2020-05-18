import collections

import matplotlib.pyplot as plt
import numpy as np

import data
from world_generation.terrains import TerrainTypes


def plot_regions(world, to_file=False):
    fig = plt.figure()
    ax = fig.gca()

    ax.plot(world.centers[:, 0], world.centers[:, 1], 'b.')

    for poly_vertices in world.vertices_by_region:
        ax.plot(poly_vertices[:, 0], poly_vertices[:, 1], 'go')
        vertices = np.append(poly_vertices, [poly_vertices[0, :]], axis=0)
        ax.plot(vertices[:, 0], vertices[:, 1], 'k-')
    ax.set_axis_off()
    ax.set_xlim([0., 1.])
    ax.set_ylim([0., 1.])

    _display(to_file)


def plot_hypsometric(world, to_file=False):
    # plot_polygons(world)
    # plot_mountain_chains(world)
    plot_terrain(world)
    plot_rivers(world)
    # plot_downslopes(world)
    # plot_moisture(world)

    _display(to_file)


def plot_polygons(world: data.World):
    HYPSOMETRIC_COLORS = collections.OrderedDict([
        (0.9, "#e42423"),
        (0.8, "#e5452b"),
        (0.6, "#ee7d3b"),
        (0.5, "#f5b26b"),
        (0.4, "#ffe64c"),
        (0.3, "#f6ee81"),
        (0.0, "#76b648"),
        (-0.2, "#bee3eb"),
        (-1, "#71c7d6"),
    ])

    def color_for_height(height):
        for min_height, hex_color in HYPSOMETRIC_COLORS.items():
            if height >= min_height:
                return hex_color

    fig = plt.figure()
    ax = fig.gca()
    for region_id, vertices in world.vertices_by_region.items():
        height = world.height_by_region[region_id]
        hex_color = color_for_height(height)
        pos_of_vertices = np.array([world.pos_by_vertex[vertex] for vertex in vertices])
        ax.fill(pos_of_vertices[:, 0], pos_of_vertices[:, 1], hex_color)


def plot_mountain_chains(world: data.World):
    for terrain in [t for t in world.terrain_blobs if t.terrain_name == "mountains"]:
        xes = [p[0] for p in terrain.center_line.coords]
        yes = [p[1] for p in terrain.center_line.coords]
        plt.plot(xes, yes, color="purple")


def plot_rivers(world: data.World):
    for river in world.rivers:
        river_pos = [world.pos_by_vertex[vertex] for vertex in river]
        xes = [p[0] for p in river_pos]
        yes = [p[1] for p in river_pos]
        plt.plot(xes, yes, color="blue")


def plot_moisture(world: data.World):
    for vertex_id, moisture in world.moisture_by_vertex.items():
        river_pos = world.pos_by_vertex[vertex_id]
        if moisture > 0:
            plt.plot(river_pos[0], river_pos[1], marker='o', markersize=1, color=(moisture, moisture, moisture))


def plot_terrain(world: data.World):
    color_by_terrain = {
        TerrainTypes.MOUNTAIN: "#B0B0B0",
        TerrainTypes.CONIFEROUS_FOREST: "#1E3C00",
        TerrainTypes.DECIDUOUS_FOREST: "#006600",
        TerrainTypes.GRASSLAND: "#A7E541",
        TerrainTypes.PLAINS: "#DCFF5E",
        TerrainTypes.BUSH: "#15FF00",
        TerrainTypes.DEEP_WATER: "#007ad0",
        TerrainTypes.SHALLOW_WATER: "#0091cf",
        TerrainTypes.LAKE: "#95daf0",
    }
    fig = plt.figure()
    ax = fig.gca()
    for region_id, vertices in world.vertices_by_region.items():
        terrain = world.terrain_by_region[region_id]
        hex_color = color_by_terrain[terrain]
        pos_of_vertices = np.array([world.pos_by_vertex[vertex] for vertex in vertices])
        ax.fill(pos_of_vertices[:, 0], pos_of_vertices[:, 1], hex_color)


def plot_downslopes(world: data.World):
    for vertex, pos in world.pos_by_vertex.items():
        downslopes = world.downslopes[vertex]
        for downslope in downslopes:
            downslope_pos = world.pos_by_vertex[downslope]
            plt.arrow(pos[0], pos[1], (downslope_pos[0] - pos[0]) / 2, (downslope_pos[1] - pos[1]) / 2,
                      head_width=0.0005, head_length=0.001)


def _display(only_to_file):
    plt.axis('off')
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.savefig("bounded_voronoi.png", dpi=400, bbox_inches=0, pad_inches=0)

    if not only_to_file:
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
