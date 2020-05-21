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
    attempts = 0
    mountains_created = 0
    while mountains_created < number_of_chains and attempts < 1000:
        new_chain = create_polygonal_chain()
        if not intersects_with_other_mountain_chains(new_chain, world.mountain_chains, world):
            world.mountain_chains += [new_chain]
            mountains_created += 1
        else:
            attempts += 1


def create_polygonal_chain():
    MIN_POS = 0.25
    MAX_POS = 0.75
    MAX_LEN = 0.2
    x1 = random.uniform(MIN_POS, MAX_POS)
    y1 = random.uniform(MIN_POS, MAX_POS)

    x2 = x1 + random.uniform(max(-MAX_LEN, x1 - MAX_POS), min(MAX_LEN, MAX_POS - x1))
    y2 = y1 + random.uniform(max(-MAX_LEN, y1 - MAX_POS), min(MAX_LEN, MAX_POS - y1))

    fraction_of_point_on_chain = 0.25 + 0.5 * random.random()  # in [0.25, 0.75]
    dx = x2 - x1
    dy = y2 - y1

    middle_x, middle_y = x1 + fraction_of_point_on_chain * dx, y1 + fraction_of_point_on_chain * dy

    scale = (random.random() - 0.5) * 2 * (- abs(fraction_of_point_on_chain - 0.5) + 0.5)  # [-0.5, 0.5]
    break_pt_x, break_pt_y = middle_x + dx * scale, middle_y - dy * scale

    line_string = LineString([(x1, y1), (break_pt_x, break_pt_y), (x2, y2)])

    mountain_height = 1.0 - random.random() / 2
    return data.ChainDescriptor(line_string, mountain_height)
