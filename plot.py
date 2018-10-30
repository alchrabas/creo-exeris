import collections

import matplotlib.pyplot as plt
import numpy as np


def plot_regions(world, to_file=False):
    fig = plt.figure()
    ax = fig.gca()

    ax.plot(world.centers[:, 0], world.centers[:, 1], 'b.')

    for poly_vertices in world.vertices:
        ax.plot(poly_vertices[:, 0], poly_vertices[:, 1], 'go')
        vertices = np.append(poly_vertices, [poly_vertices[0, :]], axis=0)
        ax.plot(vertices[:, 0], vertices[:, 1], 'k-')

    ax.set_xlim([0., 1.])
    ax.set_ylim([0., 1.])

    _plot(world, to_file)


def plot_hypsometric(world, to_file):
    HYPSOMETRIC_COLORS = collections.OrderedDict([
        (0.8, "#e42423"),
        (0.7, "#e5452b"),
        (0.6, "#ee7d3b"),
        (0.5, "#f5b26b"),
        (0.4, "#ffe64c"),
        (0.3, "#f6ee81"),
        (0.2, "#76b648"),
        (0.0, "#bee3eb"),
        (-0.5, "#bee3eb"),
    ])

    # TODO


def _plot(world, to_file):
    if to_file:
        plt.savefig("bounded_voronoi.png")
    else:
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
