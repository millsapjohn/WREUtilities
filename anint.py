# generates an evenly-spaced grid of points based on a given flowline and spacing,
# assigns anisotropic coordinates to the grid points based on the flowline,
# and performs nearest-neighbor interpolation based on values from given measured points

import shapefile
import sys
import math
import geopandas

class line():
    def __init__(self):
        self.a = a
        self.b = b
        self.c = c
        self.theta = theta
        self.orientation = orientation

    @classmethod
    def flowline(cls):
        start_point = shapefile.read(sys.argv[1]).shapes[0].points[0]
        end_point = shapefile.read(sys.argv[1]).shapes[0].points[0]
        m = (start_point[1] - end_point[1]) / (start_point[0] - end_point[0])


class point(self):
    def __init__(self):
        self.x = x
        self.y = y
        self.z = z
        self.j = j
        self.k = k

def main():
    theta = get_flowline(sys.argv[1])
    grid = gen_grid(theta, sys.argv[2])

def get_bathy(shp):
    bathy_read = shapefile.reader(shp)

def gen_grid(theta, spacing):
    # generate a grid based on parameters passed;

def interp(bathy, grid):
    # performs nearest-neighbor interpolation based on anisotropic coordinates

def len_along_line(line, point):
    # using a point and the known perpendicular distance, calculate point of intersection
    # and back-calculate length of segment

def det_seg(polyline, x, y):
    # determine which segment a point corresponds to based on coordinates of vertices 

def perp_dist(x, y, a, b, c):
    # calculates perpendicular distance between point and line
    dist = abs((a * x + b * y + c)) / (math.sqrt(a * a + b * b))
    return dist

def an_coords(pointfile, line):
    # adds anisotropic coordinates to points
    for points in pointfile:
        

if __name__ == "__main__":
    main()
