import json


def _priority_by_terrain_name(terrain_name):
    if terrain_name == "mountains":
        return 3
    elif terrain_name == "grassland":
        return 2
    elif terrain_name == "shallow_water":
        return 1
    return 0


def export(terrains):
    return json.dumps([{
        "priority": _priority_by_terrain_name(t.terrain_name),
        "terrain_name": t.terrain_name,
        "wkt": t.group_poly.wkt,
        "center_line": t.center_line.wkt if t.center_line else None,
    } for t in terrains])
