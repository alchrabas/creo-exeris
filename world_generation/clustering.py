import data
from shapely.ops import cascaded_union


def cluster_terrains(world: data.World):
    all_regions = set(world.regions_touching_region.keys())
    clusters = []
    while all_regions:
        current_region = all_regions.pop()
        current_terrain = world.terrain_by_region[current_region]
        cluster = data.walk_over_regions([current_region],
                                         lambda x: world.terrain_by_region[x] == current_terrain,
                                         world)
        all_regions.difference_update(cluster)
        cluster_polygon = cascaded_union([world.polygon_by_region[r] for r in cluster])

        clusters += [data.Cluster(cluster_polygon, current_terrain, cluster)]

    world.clusters = clusters
