import collections

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import shapely

import data
from world_generation.terrains import TerrainTypes


def plot_map(world, to_file=False):
    # plot_polygons(world)
    plot_clusters(world)
    plot_mountain_chains(world)
    plot_rivers(world)
    # plot_downslopes(world)
    # plot_moisture(world)

    _display("map.png", to_file)


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


def plot_resources(resources, background_image: str, to_file=False):
    fig = plt.figure(figsize=(1, 1))
    ax = fig.gca()
    img_shape = plot_background_image(background_image)
    plot_resource_areas(resources, img_shape, ax)

    _display("resources.png", to_file)


def plot_background_image(background_image):
    img = mpimg.imread(background_image)
    plt.imshow(img)
    return img.shape


def plot_resource_areas(resources, img_shape, ax):
    for resource_area in resources:
        scaled_area = shapely.affinity.scale(resource_area, xfact=img_shape[1], yfact=img_shape[0], origin=(0, 0))
        print(img_shape)
        print(scaled_area)
        pos_of_vertices = np.array(scaled_area.exterior.coords)

        ax.fill(pos_of_vertices[:, 0], pos_of_vertices[:, 1], "#ff000080")


def plot_mountain_chains(world: data.World):
    for chain in world.mountain_chains:
        xes = [p[0] for p in chain.line.coords]
        yes = [p[1] for p in chain.line.coords]
        plt.plot(xes, yes, color="purple", linewidth=0.3)


def plot_rivers(world: data.World):
    for river in world.rivers:
        river_pos = [world.pos_by_vertex[vertex] for vertex in river]
        xes = [p[0] for p in river_pos]
        yes = [p[1] for p in river_pos]
        plt.plot(xes, yes, color="blue", linewidth=0.15)


def plot_moisture(world: data.World):
    for vertex_id, moisture in world.moisture_by_vertex.items():
        river_pos = world.pos_by_vertex[vertex_id]
        if moisture > 0:
            plt.plot(river_pos[0], river_pos[1], marker='o', markersize=0.25, color=(moisture, moisture, moisture))


COLOR_BY_TERRAIN = {
    TerrainTypes.MOUNTAIN: "#B0B0B0",
    TerrainTypes.CONIFEROUS_FOREST: "#1E3C00",
    TerrainTypes.DECIDUOUS_FOREST: "#006600",
    TerrainTypes.GRASSLAND: "#A7E541",
    TerrainTypes.PLAINS: "#DCFF5E",
    TerrainTypes.DEEP_WATER: "#007ad0",
    TerrainTypes.SHALLOW_WATER: "#0091cf",
    TerrainTypes.LAKE: "#95daf0",
}


def plot_terrain(world: data.World):
    fig = plt.figure()
    ax = fig.gca()
    for region_id, vertices in world.vertices_by_region.items():
        terrain = world.terrain_by_region[region_id]
        hex_color = COLOR_BY_TERRAIN[terrain]
        pos_of_vertices = np.array([world.pos_by_vertex[vertex] for vertex in vertices])
        ax.fill(pos_of_vertices[:, 0], pos_of_vertices[:, 1], hex_color)


sort_order = {
    TerrainTypes.MOUNTAIN: 6,
    TerrainTypes.CONIFEROUS_FOREST: 4,
    TerrainTypes.DECIDUOUS_FOREST: 3,
    TerrainTypes.GRASSLAND: 2,
    TerrainTypes.PLAINS: 2,
    TerrainTypes.LAKE: 5,
    TerrainTypes.SHALLOW_WATER: 1,
    TerrainTypes.DEEP_WATER: 0,
}


def plot_clusters(world):
    fig = plt.figure(figsize=(1, 1))
    ax = fig.gca()
    for cluster in sorted(world.clusters, key=lambda x: sort_order[x.terrain_type]):
        hex_color = COLOR_BY_TERRAIN[cluster.terrain_type]
        pos_of_vertices = np.array(cluster.polygon.exterior.coords)
        ax.fill(pos_of_vertices[:, 0], pos_of_vertices[:, 1], hex_color)


def plot_downslopes(world: data.World):
    for vertex, pos in world.pos_by_vertex.items():
        downslopes = world.downslopes[vertex]
        for downslope in downslopes:
            downslope_pos = world.pos_by_vertex[downslope]
            plt.arrow(pos[0], pos[1], (downslope_pos[0] - pos[0]) / 2, (downslope_pos[1] - pos[1]) / 2,
                      head_width=0.0005, head_length=0.001)


def _display(file_name, only_to_file):
    plt.axis('off')
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.savefig(file_name, dpi=2000, bbox_inches=0, pad_inches=0)

    if not only_to_file:
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
