import csv
import pyscan


def inRegion(pt):
    return pt[0] < -74.8 and 39.8 < pt[1] and -76 < pt[0] and pt[1] < 40.15

def load_philly():
    pts = []
    with open("../Data/police_inct.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                x = float(row["POINT_X"])
                y = float(row["POINT_Y"])
                if not inRegion((x, y)):
                    continue
            except:
                continue
            pts.append((x, y))
    return pts


def load_chicago():
    pts = []
    with open("../Data/Chicago.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                x = float(row["X Coordinate"])
                y = float(row["Y Coordinate"])
            except:
                continue
            pts.append((x, y))
    pts.sort(key=lambda pt: pt[0])
    pts = pts[int(len(pts)*.01):int(len(pts) - len(pts)*.01)]
    pts.sort(key=lambda pt: pt[1])
    pts = pts[int(len(pts) * .01):int(len(pts) - len(pts) * .01)]
    return pts
