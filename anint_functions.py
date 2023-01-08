import numpy as np
from shapely.geometry import Point
from shapely.geometry import LineString

def signedTriangleArea(test_line, test_point):
    vertex_1 = test_line.coords[0]
    vertex_2 = test_line.coords[1]
    area = ((vertex_2.x - vertex_1.x) * (test_point.y - vertex_2.y))- ((test_point.x - vertex_2.x) * (vertex_2.y - vertex_1.y))
    return area

def pointProjection(test_line, test_point):
    m_val = test_line.project(test_point)
    proj_point = test_line.interpolate(m_val)
    d_val = test_point.distance(proj_point)
    return m_val, d_val
