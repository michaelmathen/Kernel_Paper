import pyscan
import matplotlib.pyplot as plt
import itertools


def plot_points(ax, pts, c):
    xs = []
    ys = []
    for pt in pts:
        xs.append(pt[0] )
        ys.append(pt[1])
    ax.scatter(xs, ys, color=c, marker='.')

def plot_points_traj(ax, pts, c):
    xs = []
    ys = []
    for pt in pts:
        xs.append(pt[0])
        ys.append(pt[1])
    ax.plot(xs, ys, color=c)

def plot_approx(ax, regions, core_set_pts):
    for reg in regions:
        plot_points_traj(ax, reg, "g")
    plot_points(ax, core_set_pts, "b")
    ax.set_axis_off()

import paths
regions = paths.load_regions("/home/mmath/Data/GIS/nhgis0002_shape/US_tract_2010.shp")

pyscan.plant_full_disk_region(regions, )

print(len(regions))

