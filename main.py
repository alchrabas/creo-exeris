#!/usr/bin/env python

import matplotlib.pyplot as plt

import voronoi

number_of_points = 100
bounding_box = [(0, 1), (0, 1)]

vor = voronoi.relaxed_voronoi(number_of_points, bounding_box, 5)

fig = plt.figure()
ax = fig.gca()

ax.plot(vor.filtered_points[:, 0], vor.filtered_points[:, 1], 'b.')

for region in vor.filtered_regions:
    vertices = vor.vertices[region, :]
    ax.plot(vertices[:, 0], vertices[:, 1], 'go')

for region in vor.filtered_regions:
    vertices = vor.vertices[region + [region[0]], :]
    ax.plot(vertices[:, 0], vertices[:, 1], 'k-')

ax.set_xlim([0., 1.])
ax.set_ylim([0., 1.])
plt.savefig("bounded_voronoi.png")
