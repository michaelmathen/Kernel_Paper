#!/usr/bin/python
import argparse
import random
import csv
import bisect
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotting_tools
import json
import numpy as np
import statistics

from collections import Counter

matplotlib.rcParams.update({'font.size': 15})
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--x',
                        required=True,
                        help="Name of x")
    parser.add_argument('--x_diff',
                        help="Name of x")
    parser.add_argument('--y_diff',
                        help="Name of x")
    parser.add_argument("--y", required=True, help="Name of y")
    parser.add_argument("--filenames", required=True, nargs="+", help="help file csv to open")
    parser.add_argument("--labels", nargs="+", help="help file csv to open")
    parser.add_argument("--x_name", default="", help="help file csv to open")
    parser.add_argument("--y_name", default="", help="help file csv to open")
    parser.add_argument("--logx", action="store_true")
    parser.add_argument("--logy", action="store_true")
    parser.add_argument("--ybounds", nargs=2, help="The lower and upper bounds of y" )
    parser.add_argument("--xbounds", nargs=2, help="The lower and upper bounds of x" )
    parser.add_argument("--style", help="File containing markers and colors for various label names") 
    parser.add_argument("--inversex", action="store_true")
    parser.add_argument("--inversey", action="store_true")
    parser.add_argument("--smooth", type=float)
    parser.add_argument("--noline", action="store_false", default=True)
    parser.add_argument("--save", help="Name of the saved file")
    parser.add_argument("--avg_line", nargs="+", default=[], help="Names of the labels to replace with an avg line")
    parser.add_argument("--title", default="", help="Title of plot")
    parser.add_argument("--hline", type=float, help="x value for the horizontal line")
    parser.add_argument("--max_line", action="store_true", default=False)
    parser.add_argument("--no_yticks", action="store_true", default=False)
    parser.add_argument("--no_points", action="store_true", default=False)
    parser.add_argument("--error_plot", default=None, type=float, help="Replaces all the points by averaging points in a window to the mean.")
    parser.add_argument("--bounds", action="store_true", default=False)

    args = parser.parse_args()
    ax = plt.subplot(1, 1, 1)

    style_file = None
    if args.style is not None:
        with open(args.style, "r") as data_file:
            style_file = json.load(data_file)

    if args.logx:
        ax.set_xscale("log")
    if args.logy:
        ax.set_yscale("log")
    i = 0
    print(args.filenames, args.labels)
    for filename, label in zip(args.filenames, args.labels):
        print(label, filename)
        with open(filename, 'r') as csvFile:
            reader = csv.DictReader(csvFile)
            all_rows = [row for row in reader]
            try:
                if args.x_diff is not None:
                    x_col = [abs(float(row[args.x_diff]) - float(row[args.x])) for row in all_rows]
                else:
                    x_col = [float(row[args.x]) for row in all_rows]
                if args.inversex:
                    x_col = [1 / x_val for x_val in x_col] 

                if args.y_diff is not None:
                    y_col = [abs(float(row[args.y_diff]) - float(row[args.y])) for row in all_rows]
                else:
                    y_col = [float(row[args.y]) for row in all_rows]
                if args.inversey:
                    y_col = [ 1/ y_val for y_val in y_col]
            except:
                  
                for row in all_rows:
                    print(row[args.x], row[args.y])
                    x = float(row[args.x])
                    y = float(row[args.y])



            #plt.hold(True)
            
            if style_file is None:
                marker = "o"
                name = label
                color = None
            else:
                el = style_file[label]
                name = el["label"]
                marker = el["marker"]
                color = el["color"]

            if label in args.avg_line:
                print(label)
                obj = ax.axhline(y = np.percentile(y_col, 50), color=color, label=name, linestyle="-")
                obj = ax.axhline(y = np.percentile(y_col, 75), color=color, label=name, linestyle="dashed")
                obj = ax.axhline(y = np.percentile(y_col, 25), color=color, label=name, linestyle="dashed")
                #obj = ax.axhline(y = np.percentile(y_col, 100), color=color, label=name, linestyle="dotted")
                #obj = ax.axhline(y = np.percentile(y_col, 0), color=color, label=name, linestyle="dotted")
            elif args.error_plot is not None and x_col:
                zipped = list(zip(x_col, y_col))
                zipped.sort(key = lambda x: x[0])
                x_col = [x for (x, _) in zipped]
                y_col = [y for (_, y) in zipped]
                
                # Replace every point with a nearest neighbor
                new_x = []
                new_y = []
                first_x = x_col[0]
                x_ix = set()
                for x in x_col:
                    x_ix.add(int((x - first_x) / args.error_plot))
                x_centers = []
                for ix in x_ix:
                    x_centers.append(ix * args.error_plot + args.error_plot / 2.0 + first_x)
                x_centers.sort()
                print(x_centers)
                y_median = []
                #y_25 = []
                #y_75 = []
                y_buckets = []
                y_error = []
                for x_c in x_centers:
                    y_bucket = []
                    for x_d, y_d in zip(x_col, y_col):
                        if x_c - args.error_plot <= x_d < x_c + args.error_plot:
                            y_bucket.append(y_d)
                    try:
                        y_median.append(statistics.median(y_bucket))
                        y_error.append(statistics.stdev(y_bucket))
                    except:
                        y_median.append(y_bucket[0])
                        y_error.append(0)
                    #y_buckets.append(y_bucket)
                #ax.plot(x_centers, y_median, color=color, linestyle="-", label=name)
                (_, caps, _) = ax.errorbar(x_centers, y_median, color=color, label=name, yerr=y_error, capsize=10, elinewidth=3, fmt=marker + '-')
                #for cap in caps:
                    #cap.set_color('red')
                    #cap.set_markeredgewidth(10)
            else:
                if args.smooth is not None:
                    plotting_tools.plot_interp(ax, x_col, y_col, sig=args.smooth, logsc=args.logx, color=color)
                if args.max_line:
                    obj = ax.axhline(y = np.percentile(y_col, 100), color=color, linestyle=(random.randint(1, 5), (1, random.randint(1, 3))))
                #obj = ax.scatter(x_col, y_col, label=name, marker=marker, color=color)
                if args.noline:
                    ax.plot(x_col, y_col, color=color)
            if not args.no_points:
                ax.scatter(x_col, y_col, label=name, marker=marker, color=color)

            #p2, = ax.plot(r_fs, time_fs, color='b', label='SubSumScan')
    if args.hline is not None:
        ax.axhline(y = args.hline, color="k", linestyle="dashed")
    ax.legend()
    if args.ybounds is not None:
        ax.set_ylim([float(args.ybounds[0]), float(args.ybounds[1])]) 
    if args.xbounds is not None:
        ax.set_xlim([float(args.xbounds[0]), float(args.xbounds[1])])
    if args.no_yticks:
        print("got here")
        ax.get_yaxis().set_visible(False)
    ax.set_xlabel(args.x_name)
    ax.set_ylabel(args.y_name)
    ax.set_title(args.title)
    #plt.tight_layout()
    if args.save is not None:
        plt.savefig(args.save, format="pdf", bbox_inches='tight')
    else:
        plt.show()
        


