import math
import random
from typing import List

from shapely.geometry import LineString

import data


def intersects_with_other_mountain_chains(
        candidate_chain: data.ChainDescriptor,
        existing_chains: List[data.ChainDescriptor],
        world: data.World):
    for existing_chain in existing_chains:
        distance = candidate_chain.line.distance(existing_chain.line)
        approx_region_diameter = 1.0 / math.sqrt(world.regions_count)

        candidate_chain_over_min_height = (candidate_chain.height - data.MIN_MOUNTAIN_HEIGHT)
        existing_chain_over_min_height = (existing_chain.height - data.MIN_MOUNTAIN_HEIGHT)

        number_of_regions_to_be_away = \
            math.ceil(candidate_chain_over_min_height / 0.06) + \
            math.ceil(existing_chain_over_min_height / 0.06) + 1
        if distance / approx_region_diameter < number_of_regions_to_be_away:
            return True
    return False


def create_mountain_chains(number_of_chains, world: data.World):
    world.mountain_chains = []
    for _ in range(number_of_chains):
        new_chain = create_polygonal_chain()
        if not intersects_with_other_mountain_chains(new_chain, world.mountain_chains, world):
            world.mountain_chains += [new_chain]
        else:
            print("FAILED, TOO CLOSE!")


def create_polygonal_chain():
    MIN_POS = 0.3
    MAX_POS = 0.7
    MAX_LEN = 0.2
    x1 = random.uniform(MIN_POS, MAX_POS)
    y1 = random.uniform(MIN_POS, MAX_POS)

    x2 = x1 + random.uniform(max(-MAX_LEN, x1 - MIN_POS), min(MAX_LEN, MAX_POS - x1))
    y2 = y1 + random.uniform(max(-MAX_LEN, y1 - MIN_POS), min(MAX_LEN, MAX_POS - y1))

    line_string = LineString([(x1, y1), (x2, y2)])
    mountain_height = 1.0 - random.random() / 2
    return data.ChainDescriptor(line_string, mountain_height)
