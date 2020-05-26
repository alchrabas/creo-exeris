#!/usr/bin/env python
import pickle

from shapely.geometry import Point

import plot
from checkpoint import time_from_last_checkpoint

file_name = "generated_map_25000_38257"
world = pickle.load(open("dumps/" + file_name, "rb"))

background_image = "rendered_maps/" + file_name

checkpoint = time_from_last_checkpoint()
next(checkpoint)

buffer = Point(0.7, 0.5).buffer(0.2)

resouces = [buffer]


plot.plot_resources(resouces, background_image, True)
