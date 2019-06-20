import pyscan
import matplotlib.pyplot as plt
import random
import math
import statistics
import csv
import itertools
import numpy as np
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

# projection = ccrs.PlateCarree(central_longitude=40.0)
projection = ccrs.PlateCarree()

# projection = ccrs.Geodetic()
request = cimgt.Stamen(style='toner')
crg = request.crs
# projection = ccrs.LambertCylindrical(central_longitude=40.0)

seed = 5483970
random.seed(a=seed)


def plot_points(ax, pts, c, transform=None):
    xs = []
    ys = []
    for pt in pts:
        xs.append(pt[0])
        ys.append(pt[1])
    ax.scatter(xs, ys, color=c, transform=transform, marker=".", s=100)


def plot_points_traj(ax, pts, c, transform=None):
    xs = []
    ys = []
    for pt in pts:
        xs.append(pt[0])
        ys.append(pt[1])
    ax.plot(xs, ys, color=c, transform=transform, linewidth=1)


def plot_approx(ax, traj_pts, core_set_pts):
    ax.set_xlim([-.01, 1.01])
    ax.set_ylim([-.01, 1.01])
    plot_points_traj(ax, traj_pts, "g")
    plot_points(ax, core_set_pts, "b")
    ax.set_axis_off()


def plot_full_trajectories(red, blue, ax, transform=None):
    plot_set = [(reg, True) for reg in blue] + [(reg, False) for reg in red]
    random.shuffle(plot_set)

    for traj, is_blue in plot_set:
        if is_blue:
            plot_points_traj(ax, traj, "b", transform=transform)
        else:
            plot_points_traj(ax, traj, "r", transform=transform)


def remove_long_trajectories(trajectories, percent=.9):
    def toTraj(pts):
        return pyscan.Trajectory([pyscan.Point(p[0], p[1], 1.0) for p in pts])

    ltraj = sorted(toTraj(traj).get_length() for traj in trajectories)
    perc_len_traj = ltraj[int(percent * len(trajectories))]
    del ltraj
    return [traj for traj in trajectories if toTraj(traj).get_length() <= perc_len_traj]


def normalize(pt, mxx, mnx, mxy, mny):
    scale = get_scale((mxx, mnx, mxy, mny))
    return (pt[0] - mnx) / scale, (pt[1] - mny) / scale


def compute_radius(ortho, radius_degrees, lon, lat):
    phi1 = lat + radius_degrees if lat <= 0 else lat - radius_degrees
    _, y1 = ortho.transform_point(lon, phi1, ccrs.PlateCarree())
    return abs(y1)


def get_square_box(bx, extent_scale=.8):
    (mxx, mnx, mxy, mny) = bx
    LL = crg.transform_point(mny, mnx, projection)
    UR = crg.transform_point(mxy, mxx, projection)
    EW = UR[0] - LL[0]
    SN = UR[1] - LL[1]

    # get side of the square extent (in map units, usually meters)
    side = min(EW, SN)  # smaller vallue
    mid_x, mid_y = LL[0] + EW / 2.0, LL[1] + SN / 2.0  # center location
    # the extent preserves the center location
    extent = [mid_x - side / 2.0, mid_x + side / 2.0, mid_y - side / 2.0 * extent_scale,
              mid_y + side / 2.0 * extent_scale]
    return extent, mid_x, mid_y  # This is in the geo space.


def map_disk(disk, bx, ax, color='g'):
    (mxx, mnx, mxy, mny) = bx
    center = reverse_normalization(disk.get_origin(), bx)
    r = disk.get_radius()
    scale = get_scale(bx)
    r = r * scale
    _, midlx, midly = get_square_box(bx)
    # proj = ccrs.Orthographic(central_longitude=center[1], central_latitude=center[0])
    ncx, ncy = crg.transform_point(center[0], center[1], projection)
    rcx, _ = crg.transform_point(center[0] + r, center[1], projection)
    # radius = compute_radius(proj, r, ncx, ncy)
    # proj = ccrs.Orthographic(central_longitude=lon, central_latitude=lat)
    actor = plt.Circle((ncx, ncy), abs(ncx - rcx),
                       alpha=.2,
                       fill=True,
                       color=color)
    ax.add_artist(actor)

    actor = plt.Circle((ncx, ncy), abs(ncx - rcx),
                       alpha=1.0,
                       linewidth=5.0,
                       fill=False,
                       color=color)
    ax.add_artist(actor)


def get_scale(bx):
    (mxx, mnx, mxy, mny) = bx
    return max(mxx - mnx, mxy - mny)


def reverse_normalization(pt, bx):
    (mxx, mnx, mxy, mny) = bx
    scale = get_scale(bx)
    return (pt[1] * scale + mny, pt[0] * scale + mnx)


def reverse_all(trajectories, bx):
    return [[reverse_normalization(pt, bx) for pt in traj] for traj in trajectories]


def reverse_pts(pts, bx):
    return [reverse_normalization(pt, bx) for pt in pts]


def get_bx(pts):

    mnx = float("inf")
    mxx = -float("inf")
    mny = float("inf")
    mxy = -float("inf")

    for pt in pts:
        y, x = pt
        mnx = min(mnx, x)
        mny = min(mny, y)
        mxx = max(mxx, x)
        mxy = max(mxy, y)
    return (mxx, mnx, mxy, mny)



def map_trajectories(red_net, blue_net, bx):
    (mxx, mnx, mxy, mny) = bx

    # request = cimgt.MapQuestOpenAerial()
    fig = plt.figure(figsize=(16, 9))

    ax = plt.axes(projection=request.crs)

    extent, _, _ = get_square_box(bx)
    ax.add_image(request, 14, cmap='gray', interpolation="spline36")
    plot_full_trajectories(reverse_all(red_net, bx), reverse_all(blue_net, bx), ax, transform=projection)
    ax.set_extent(extent, crs=crg)
    #     plt.gca().set_aspect('equal', adjustable='box')
    #     plt.axis('scaled')
    return ax, request.crs


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def cut_trajectories(trajectories, max_length=20):
    trajectory_pieces = []
    for traj in trajectories:
        for traj_part in divide_chunks(traj, max_length):
            trajectory_pieces.append(traj_part)
    return trajectory_pieces


import paths

eps = .1
s= 800
r = .08
p = .5
q = .8

pts = paths.load_philly()
red, blue, bandwidth, center_pt = pyscan.plant_kernel_disk_region(pts, r, p, q)

bx = get_bx(pts)


m_sample = pyscan.my_sample(red, s)
b_sample = pyscan.my_sample(blue, s)


# r_g = bandwidth * math.sqrt(math.e) * eps * 5
# disk_r = bandwidth * math.sqrt(math.log(1 / eps))
#reg, mx = pyscan.max_kernel_slow(pyscan.to_weighted(m_sample), pyscan.to_weighted(b_sample), r_g, disk_r, bandwidth)

ax, _ = map_trajectories([], [], bx)
plot_points(ax, m_sample, "r", transform=projection)
plot_points(ax, b_sample, "b", transform=projection)

pyscan.plot_kernel(ax, pts, center_pt, bandwidth, res=50, transform=projection)
#pyscan.plot_kernel(ax, pts, reg.get_origin(), bandwidth, res=50, transform=projection)
#plt.show()
plt.savefig("philly.pdf", bbox_inches='tight')