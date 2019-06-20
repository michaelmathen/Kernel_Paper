import csv
import numpy as np
import time
import pyscan
import random
import matplotlib.pyplot as plt
import math
from scipy.special import erfinv
import Mapping

def sqr_dist(pt, center):
    return (pt[0] - center[0]) ** 2 + (pt[1] - center[1]) ** 2

def kernel(pt, center, bandwidth):
    return math.exp(- sqr_dist(pt, center) / bandwidth ** 2)

"""
A number of different distance measurements that can be useful for comparing the similarity of the anomalies.
"""
def Kl_divergence(pts, bandwidth, planted, found):
    divergence = 0
    p_total = 0
    q_total = 0
    for pt in pts:
        P_x = kernel(pt, planted, bandwidth)
        Q_x = kernel(pt, found, bandwidth)
        p_total += P_x
        q_total += Q_x
    for pt in pts:
        try:
            P_x = kernel(pt, planted, bandwidth) / p_total
            Q_x = kernel(pt, found, bandwidth) / q_total
            if P_x > np.finfo(float).eps and Q_x > np.finfo(float).eps:
                divergence += P_x * math.log( P_x / Q_x)
        except ZeroDivisionError:
            continue

    return divergence

def l2_dist(pts, bandwidth, planted, found):
    dist_sqr = 0
    for pt in pts:
        P_x = kernel(pt, planted, bandwidth)
        Q_x = kernel(pt, found, bandwidth)
        dist_sqr += (P_x - Q_x) ** 2
    return math.sqrt(dist_sqr)

def angular_dist(pts, bandwidth, planted, found):
    inner_prod = 0
    p_sum = 0
    q_sum = 0
    for pt in pts:
        P_x = kernel(pt, planted, bandwidth)
        Q_x = kernel(pt, found, bandwidth)
        inner_prod += P_x * Q_x
        p_sum += P_x * P_x
        q_sum += Q_x * Q_x
    if q_sum == 0 or p_sum == 0:
        return 0.0
    return inner_prod / (math.sqrt(p_sum) * math.sqrt(q_sum))


def extended_jc(pts, bandwidth, planted, found):
    inner_prod = 0
    p_sum = 0
    q_sum = 0
    for pt in pts:
        P_x = kernel(pt, planted, bandwidth)
        Q_x = kernel(pt, found, bandwidth)
        inner_prod += P_x * Q_x
        p_sum += P_x * P_x
        q_sum += Q_x * Q_x

    return inner_prod / (p_sum + q_sum - inner_prod)


def run_power_test(actual_mx, disc, red, blue, n, s, annuli, count, two_level_sample):

    r_frac = len(red)
    b_frac = len(blue)
    power_count = 0
    for _ in range(count):
        pts = red + blue
        random.shuffle(pts)
        new_red = pts[:r_frac]
        new_blue = pts[b_frac:]
        m_sample = pyscan.my_sample(new_red, s)
        b_sample = pyscan.my_sample(new_blue, s)

        if two_level_sample:
            net_set1 = pyscan.my_sample(m_sample, n)
            net_set2 = pyscan.my_sample(b_sample, n)
        else:
            net_set1 = m_sample
            net_set2 = b_sample
            n = s

        net_set = net_set1 + net_set2
        m_sample = pyscan.to_weighted(m_sample)
        b_sample = pyscan.to_weighted(b_sample)

        reg, mx = pyscan.max_annuli_scale(net_set, m_sample, b_sample, annuli, disc)
        if mx > actual_mx:
            power_count += 1
    return power_count / count


def testing_partial_framework(
        pts,
        output_file,
        l_s, h_s, count,
        r=.04,
        p=0.8,
        q=.5,
        annuli_eps=.1,
        two_level_sample = True,
        algorithm="annuli",
        statistic="k",
        power_test=None,
        max_time=None,
        seed =None,
        planted_reg=None):
    if seed is not None:
        random.seed(a=seed)
    else:
        seed = random.randint(0, 10000000)
        random.seed(a=seed)
    #seed = 9704595

    if planted_reg is None:
        red, blue, bandwidth, center_pt = pyscan.plant_kernel_disk_region(pts, r, p, q)
    else:
        red, blue, bandwidth, center_pt = planted_reg

    bernoulli_sample = [(pt, 1) for pt in red] + [(pt, 0) for pt in blue]
    print(bandwidth, center_pt)

    actual_mx = pyscan.disc_bernoulli_kern(red, blue, p, q, bandwidth, center_pt)

    try:
        with open(output_file, "r") as fh:
            exists = True
    except FileNotFoundError:
        exists = False
    with open(output_file, 'a+') as f:
        writer = None

        for i in np.logspace(l_s, h_s, count):
            eps = i
            n = 1 / eps
            s = 1 / (2 * eps * eps)
            n = int(round(n) + .1)
            s = int(round(s) + .1)

            start_time = time.time()
            if statistic == "bs":
                baseline_sample = pyscan.my_sample(bernoulli_sample, s)
                m_sample = [pt for (pt, id) in baseline_sample if id]
                b_sample = [pt for (pt, _) in baseline_sample]
                print(len(m_sample))
                print(len(baseline_sample))
                print("here")
            else:
                m_sample = pyscan.my_sample(red, s)
                b_sample = pyscan.my_sample(blue, s)

            if two_level_sample:
                net_set1 = pyscan.my_sample(m_sample, n)
                net_set2 = pyscan.my_sample(b_sample, n)
            else:
                net_set1 = m_sample
                net_set2 = b_sample
                n = s

            net_set = net_set1 + net_set2
            m_sample = pyscan.to_weighted(m_sample)
            b_sample = pyscan.to_weighted(b_sample)
            # kern = pyscan.gaussian_kernel(bandwidth)
            # disc = pyscan.Bernoulli_K(kern)

            r_g = bandwidth * math.sqrt(math.e) * eps * 5
            disk_r = bandwidth * math.sqrt(math.log(1 / eps))

            if algorithm == "kernel":
                reg, mx = pyscan.max_kernel_slow(m_sample, b_sample, r_g, disk_r, bandwidth)
            elif algorithm == "kernel2":
                reg, mx = pyscan.max_kernel_slow2(m_sample, b_sample, r_g, disk_r, bandwidth)
            elif algorithm == "kernel_adaptive":
                reg, mx = pyscan.max_kernel_adaptive(m_sample, b_sample, r_g, disk_r, bandwidth)
            elif algorithm == "kernel_prune":
                disk_r = bandwidth * math.sqrt(math.log((len(m_sample) + len(b_sample)) / eps))
                reg, mx = pyscan.max_kernel_prune_far(m_sample, b_sample, r_g, disk_r, bandwidth)
            elif algorithm == "kernel_fast":
                reg, mx = pyscan.max_kernel(m_sample, b_sample, r_g, disk_r, bandwidth)

            elif algorithm == "combinatorial" or "satscan" in algorithm:
                if statistic == "k":
                    disc_f = pyscan.RKULLDORF
                elif statistic == "b":
                    disc_f = pyscan.bernoulli(0)
                elif statistic == "bs":
                    disc_f = pyscan.rbernoulli(eps * .0001)
                    #disc_f = pyscan.bernoulli(len(red), len(blue), eps / 2)
                elif statistic == "d":
                    disc_f = pyscan.DISC

            if algorithm == "combinatorial":
                reg, mx = pyscan.max_disk(net_set, m_sample, b_sample, disc_f)
            elif algorithm == "satscan_grid":
                reg, mx = pyscan.satscan_grid(m_sample, b_sample, r_g, disk_r, disc_f)
            elif algorithm == "satscan_points":
                reg, mx = pyscan.satscan_points(m_sample, b_sample, disc_f)

            end_time = time.time()
            print("Finished this run.")
            print(reg, mx)

            (p_m, q_m, mx) = pyscan.measure_kernel(reg.get_origin(), pyscan.to_weighted(red), pyscan.to_weighted(blue), bandwidth)

            if power_test is not None:
                power = run_power_test(mx, disc, red, blue, n, s, annuli, power_test, two_level_sample)
            else:
                power = None

            # r_g = bandwidth * math.sqrt(math.e) * eps * 5
            # disk_r = bandwidth * math.sqrt(math.log((len(m_sample) + len(b_sample)) / eps))
            # centers = pyscan.kernel_centers(m_sample, b_sample, r_g, disk_r, bandwidth)
            #
            # fig, ax = plt.subplots(figsize=(20,20))
            #
            # bx = Mapping.get_bx(pts)
            # #ax, _ = Mapping.map_trajectories([], [], bx)
            # pyscan.plot_points(ax, m_sample, "r")
            # pyscan.plot_points(ax, b_sample, "b")
            # #pyscan.plot_points(ax, net_set, "k")
            # #pyscan.plot_kernel(ax, pts, center_pt, bandwidth, res=50)
            # #pyscan.plot_points(ax, centers, "k")
            # print(reg.get_origin())
            # pyscan.plot_kernel(ax, pts, reg.get_origin(), bandwidth, res=50)
            # plt.axis('off')

            # plt.show()
            #kl_val = Kl_divergence(pts, bandwidth, center_pt, reg.get_origin())
            kl_val = 0
            print("Finished kl div")
            l2 = l2_dist(pts, bandwidth, center_pt, reg.get_origin())
            print("Finished l2")
            angle = 0#angular_dist(pts, bandwidth, center_pt, reg.get_origin())
            print("Finished Angle")
            ejc = extended_jc(pts, bandwidth, center_pt, reg.get_origin())
            print("Finished EJC")
            row = {"disc": "bernoulli",
                    "n": n, "s": s, "r": r, "q": q, "p":p,
                   "p_m": p_m, "q_m": q_m,
                    "time": end_time - start_time,
                    "m_disc_approx": mx,
                    "m_disc": actual_mx,
                    "center_distance": reg.get_origin().dist(center_pt),
                    "kl_div": kl_val,
                    "l2_dist": l2,
                    "angular_dist": angle,
                    "jc": ejc,
                    "power": power,
                    "bandwidth": bandwidth,
                    "seed": seed}
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=list(row.keys()))
                if not exists:
                    writer.writeheader()

            writer.writerow(row)
            print("Run time {}".format(time.time() - start_time))
            print(row)
            f.flush()
            if max_time is not None and end_time - start_time > max_time:
                return

def testing_bandwidth_framework(
        pts,
        output_file,
        l_s, h_s, count,
        r=.04,
        p=0.8,
        q=.5,
        eps=.02,
        annuli_eps=.1,
        two_level_sample = True,
        algorithm="annuli",
        statistic="k",
        power_test=None,
        max_time=None,
        seed =None):
    if seed is not None:
        random.seed(a=seed)
    else:
        seed = random.randint(0, 10000000)
        random.seed(a=seed)
    #seed = 9704595


    red, blue, bandwidth_orig, center_pt = pyscan.plant_kernel_disk_region(pts, r, p, q)

    actual_mx = pyscan.disc_bernoulli_kern(red, blue, p, q, bandwidth_orig, center_pt)

    try:
        with open(output_file, "r") as fh:
            exists = True
    except FileNotFoundError:
        exists = False
    with open(output_file, 'a+') as f:
        writer = None

        for i in np.logspace(l_s, h_s, count):

            n = 1 / eps
            s = 1 / (2 * eps * eps)
            n = int(round(n) + .1)
            s = int(round(s) + .1)
            print(i)
            bandwidth = bandwidth_orig * i
            start_time = time.time()

            m_sample = pyscan.my_sample(red, s)
            b_sample = pyscan.my_sample(blue, s)

            if two_level_sample:
                net_set1 = pyscan.my_sample(m_sample, n)
                net_set2 = pyscan.my_sample(b_sample, n)
            else:
                net_set1 = m_sample
                net_set2 = b_sample
                n = s

            net_set = net_set1 + net_set2
            m_sample = pyscan.to_weighted(m_sample)
            b_sample = pyscan.to_weighted(b_sample)
            # kern = pyscan.gaussian_kernel(bandwidth)
            # disc = pyscan.Bernoulli_K(kern)

            r_g = bandwidth * math.sqrt(math.e) * eps * 5
            disk_r = bandwidth * math.sqrt(math.log(1 / eps))

            if algorithm == "kernel":
                reg, mx = pyscan.max_kernel_slow(m_sample, b_sample, r_g, disk_r, bandwidth)
            elif algorithm == "kernel2":
                reg, mx = pyscan.max_kernel_slow2(m_sample, b_sample, r_g, disk_r, bandwidth)
            elif algorithm == "kernel_adaptive":
                reg, mx = pyscan.max_kernel_adaptive(m_sample, b_sample, r_g, disk_r, bandwidth)
            elif algorithm == "kernel_prune":
                disk_r = bandwidth * math.sqrt(math.log((len(m_sample) + len(b_sample)) / eps))
                reg, mx = pyscan.max_kernel_prune_far(m_sample, b_sample, r_g, disk_r, bandwidth)
            elif algorithm == "kernel_fast":
                reg, mx = pyscan.max_kernel(m_sample, b_sample, r_g, disk_r, bandwidth)

            end_time = time.time()
            print(reg, mx)

            (p_m, q_m, mx) = pyscan.measure_kernel(reg.get_origin(), pyscan.to_weighted(red), pyscan.to_weighted(blue), bandwidth_orig)


            row = {"disc": "bernoulli",
                    "n": n, "s": s, "r": r, "q": q, "p":p,
                   "p_m": p_m, "q_m": q_m,
                    "time": end_time - start_time,
                    "m_disc_approx": mx,
                    "m_disc": actual_mx,
                    "center_distance": reg.get_origin().dist(center_pt),
                    "kl_div": Kl_divergence(pts, bandwidth_orig, center_pt, reg.get_origin()),
                    "l2_dist": l2_dist(pts, bandwidth_orig, center_pt, reg.get_origin()),
                    "angular_dist": angular_dist(pts, bandwidth_orig, center_pt, reg.get_origin()),
                    "jc": extended_jc(pts, bandwidth_orig, center_pt, reg.get_origin()),
                    "power": None,
                    "bandwidth": bandwidth_orig,
                    "seed": seed,
                    "scale": i}
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=list(row.keys()))
                if not exists:
                    writer.writeheader()

            writer.writerow(row)
            print(row)
            f.flush()
            if max_time is not None and end_time - start_time > max_time:
                return
