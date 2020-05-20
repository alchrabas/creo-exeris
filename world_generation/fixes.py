import data
from collections import Counter

from world_generation import terrains
from world_generation.terrains import TerrainTypes


def _most_frequent(list_of_values):
    occurence_count = Counter(list_of_values)
    return occurence_count.most_common(1)[0][0]


def remove_artifacts(world: data.World):
    remove_isolated_terrain_areas(world)
    remove_river_segments_in_lakes(world)

def remove_isolated_terrain_areas(world: data.World):
    blobs = _get_terrain_blobs(world)
    removed_blobs = 0
    for blob in blobs:
        if len(blob) <= 3 and world.terrain_by_region[list(blob)[0]] != terrains.TerrainTypes.LAKE:  # would make river go nowhere
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
