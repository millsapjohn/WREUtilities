import sys
import os
from collections import OrderedDict
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import pandas as pd
import shapely
import progressbar
# import argparse

def main():
    # TODO set up argparse
    grid_space = float(sys.argv[4])
    power = float(sys.argv[5])
    radius = float(sys.argv[6])
    min_points = int(sys.argv[7])
    max_points = int(sys.argv[8])

    # get data source and feature layer for bathymetry, mask (outline), and centerline
    print('loading layers')
    bathy_lyr = gpd.read_file(sys.argv[1])
    bathy_lyr.name = 'bathymetry layer'
    mask_lyr = gpd.read_file(sys.argv[2])
    mask_lyr.name = 'mask layer'
    cl_lyr = gpd.read_file(sys.argv[3])
    cl_lyr.name = 'centerline layer'
    
    # check that centerline, mask layers only have one feature
    print('checking centerline and mask layers')
    featureCountCheck(cl_lyr)
    featureCountCheck(mask_lyr)

    # check that bathy points have z value
    for index, row in bathy_lyr.iterrows():
        if row['geometry'].has_z != True:
            sys.exit("one or more features in point layer does not contain z value")
        else:
            pass

    # check feature types of all three layers
    print("Checking feature types")
    featureTypeCheck(bathy_lyr, 'Point')
    mask_lyr = polyTypeCheck(mask_lyr)
    featureTypeCheck(cl_lyr, 'LineString')

    # convert mask layer geometry to multipolygon
    mask_geom = mask_lyr['geometry'].iloc[0]
    if isinstance(mask_geom, shapely.Polygon):
        mask_geom = shapely.MultiPolygon([mask_geom])
        mask_lyr['geometry'].iloc[0] = mask_geom

    # compare CRS for the three layers - need to be in the same CRS
    print('checking layer CRSs')
    bathy_crs_code = bathy_lyr.crs.to_epsg(min_confidence=20)
    mask_crs_code = mask_lyr.crs.to_epsg(min_confidence=20)
    cl_crs_code = cl_lyr.crs.to_epsg(min_confidence=20)

    # check that layers have the same CRS code
    if bathy_crs_code != mask_crs_code or bathy_crs_code != cl_crs_code:
        sys.exit("mismatched layer CRS")

    # calculate side, m value, d value for bathy layer, add to bathymetry layer fields
    print('assigning side value to bathymetry points')
    assignSide(bathy_lyr, cl_lyr)
    print('\n assigning m, d values to bathymetry points')
    assignMDValues(bathy_lyr, cl_lyr)

    # get bounding box of mask layer - will clip later
    b_box = mask_lyr.total_bounds
    min_x = float(b_box[0])
    min_y = float(b_box[1])
    max_x = float(b_box[2])
    max_y = float(b_box[3])

    # add points to grid layer based on spacing value provided
    print('\n generating grid point layer')
    grid_point_list = []
    for i in range((round((max_x - min_x) / grid_space)) - 1):
        for j in range((round((max_y - min_y) / grid_space)) - 1):
            x_coord = min_x + (i * grid_space)
            y_coord = min_y + (j * grid_space)
            pt = Point(x_coord, y_coord, 0.00)
            grid_point_list.append({'geometry' : pt})
    grid_lyr = gpd.GeoDataFrame(grid_point_list, geometry='geometry', crs=bathy_lyr.crs)

    # clip grid layer
    print('\n clipping grid layer')
    gpd.clip(grid_lyr, mask_lyr)

    # calculate side, m value, d value for grid layer, add to grid layer fields
    print('assigning side value to grid points')
    assignSide(grid_lyr, cl_lyr)
    print('\n assigning m, d values to grid points')
    assignMDValues(grid_lyr, cl_lyr)

    # generate new bathy, grid layers with m, d coordinates
    print('generating new bathy, grid layers')
    md_bathy_lyr = mdPointLayer(bathy_lyr)
    bathy_index = md_bathy_lyr.sindex
    md_grid_lyr = mdPointLayer(grid_lyr)

    # perform the anisotropic IDW calculation
    print('\n performing IDW interpolation on anisotropic coordinates')
    grid_lyr = invDistWeight(grid_lyr, md_bathy_lyr, md_grid_lyr, power, radius, min_points, max_points, bathy_index)
    print('\n exporting grid points to Shapefile')
    grid_lyr.to_file("grid_points.shp")
    print('processing complete')

# function to calculate the z value for grid points using inverse distance weighted method of m, d coordinates
def invDistWeight(grid_lyr, bathy_md_lyr, grid_md_lyr, power, radius, min_points, max_points, sindex):
    for index, row in grid_md_lyr:
        pt = row['geometry']
        # generate a polygon corresponding to the search radius specified
        buff = shapely.buffer(pt, radius, quad_segs=64)
        # rough estimate of possible matches based on spatial index
        possible_matches_index = list(sindex.intersection(buff))
        possible_matches = bathy_md_lyr.iloc[possible_matches_index]
        # exact list of matches
        precise_matches = possible_matches[possible_matches.intersects(buff)]
        # if total matches less than specified minimum, expand search radius until criteria is met
        if len(precise_matches) < min_points:
            i = 1
            while len(precise_matches) < min_points:
                new_rad = radius + (i * 5)
                buff = shapely.buffer(pt, new_rad, quad_segs=64)
                possible_matches_index = list(sindex.intersection(buff))
                possible_matches = bathy_md_lyr.iloc[possible_matches_index]
                precise_matches = possible_matches[possible_matches.intersects(buff)]
                i += 1
        # putting this here because I think this minimizes the number of duplicate operations...
        match_pts = gpd.GeoDataFrame(precise_matches)
        match_dist_dict = {}
        for index, row2 in match_pts:
            dist = row2['geometry'].distance(pt)
            temp_dict = {dist : row2}
            match_dist_dict.update(temp_dict)
        # this has to come second in case expanding the search radius above grabs a ton of points
        if len(match_dist_dict) > max_points:
            extra_rows = len(match_dist_dict) - max_points
            match_dist_dict = OrderedDict(sorted(match_dist_dict.items(), key=lambda t: t[0]))
            count = 0
            while count < extra_rows - 1:
                od.popitem(last=True)
                count += 1
        numerator = 0
        denominator = 0
        # iterate through the range of points within the search radius
        point_list = list(match_dist_dict.values())
        dist_list = list(match_dist_dict.keys())
        for m in range(len(point_list) - 1):
            # get the bathy point index
            point_no = point_list[m]
            # get the z value from the indexed point
            bathy_z_val = bathy_md_lyr.iloc[point_no].geometry.z
            # calculate numerator and denominator values for that point
            temp_num = bathy_z_val / (dist_list[m] ** power)
            temp_den = 1 / (dist_list[m] ** power)
            # sum numerator and denominator values
            numerator = numerator + temp_num
            denominator = denominator + temp_den
        grid_z_val = numerator / denominator
        grid_lyr.loc[i, 'geometry'] = Point(x_coord, y_coord, grid_z_val)

    return(grid_lyr)

# function to create new gdf from m, d values
def mdPointLayer(gdf):
    point_list = []
    for index, row in gdf.iterrows():
        m_val = row['m_val']
        d_val = row['d_val']
        if row['geometry'].has_z == True:
            z_val = row['geometry'].z
        else:
            z_val = 0.00
        pt = shapely.Point(m_val, d_val, z_val)
        point_list.append({'geometry' : pt})
    new_layer = gpd.GeoDataFrame(point_list, geometry='geometry')
    return new_layer

# simple check to ensure centerline, mask layers don't have multiple features, which would screw up
# other functions
def featureCountCheck(gdf):
    if len(gdf.index) > 1:
        sys.exit(f"multiple features in {gdf}")
    else:
        pass

# simple check to ensure layers only have the correct geometry types
def featureTypeCheck(gdf, geom_type):
    for index, row in gdf.iterrows():
        if row['geometry'].geom_type != geom_type:
            sys.exit(f'geometry in {gdf.name} is not of type {geom_type}')
        else:
            pass

# more complex function for polygons, as some polygon shapefiles come in as multilinestrings...
# multilinestring shapefiles have to be manually converted to polygons with holes
def polyTypeCheck(gdf):
    for index, row in gdf.iterrows():
        if row['geometry'].geom_type == 'Polygon':
            # length of layer is checked first, so if row 0 is correct, simply pass on the existing gdf
            new_mask_lyr = gdf
        elif row['geometry'].geom_type == 'MultiLineString':
            inner_list = []
            exploded = gdf.explode(index_parts=True)
            for index, row in exploded.iterrows():
                coord_list = shapely.get_coordinates(row['geometry']).tolist()
                ring = shapely.linearrings(coord_list)
                inner_list.append(ring)
                polygon = shapely.polygons(inner_list[0], holes=inner_list[0:])
                poly_list = []
                poly_dict = {'geometry' : polygon}
                poly_list.append(poly_dict)
                new_mask_lyr = gpd.GeoDataFrame(poly_list, geometry='geometry', crs=gdf.crs)
        else:
            sys.exit('mask layer cannot be converted to polygons')
    return new_mask_lyr

def assignSide(point_layer, line_layer):
    # create a list of all line coordinates to iterate over each segment
    line_coords = []
    for index, row in line_layer.iterrows():
        for pt in list(row['geometry'].coords):
            line_coords.append(Point(pt))
    point_coords = []
    for index, row in point_layer.iterrows():
        for pt in list(row['geometry'].coords):
            point_coords.append(Point(pt))
    bar = progressbar.ProgressBar(min_value=0).start()
    side_values = pd.Series(dtype='int64')
    for i in range(len(point_coords) - 1):
        for j in range(len(line_coords) - 2):
            # creating a line segment out of only two points
            temp_line = LineString([line_coords[j], line_coords[j + 1]])
            temp_area = signedTriangleArea(temp_line, point_coords[i])
            # set the initial area value on the first segment
            if i == 0:
                area = temp_area
            # if abs area is smaller, replace. The assumption here is that the segment to which each point is
            # closest (perpendicular distance) is the "correct" one. On a complicated line string a point could
            # be on different sides of different segments.
            if abs(temp_area) < abs(area):
                area = temp_area
        if area > 0:
            side = 0
        else:
            side = 1
        side_values = pd.concat([side_values, pd.Series(index=[i], data=[side])])
        bar.update(i)

    point_layer['side'] = side_values
    return point_layer

def signedTriangleArea(test_line, test_point):
    # the "signed triangle area" formula returns an area value that is < 0 when the test point is on the
    # right side of the line, > 0 when on the left. This determines the "sidedness" of each point.
    # smaller absolute value = closer to the line. 
    vertex_1 = Point(test_line.coords[0])
    vertex_2 = Point(test_line.coords[1])
    test_point = Point(test_point)
    area = ((vertex_2.x - vertex_1.x) - (test_point.y - vertex_2.y)) - ((test_point.x - vertex_2.x) * (vertex_2.y - vertex_1.y))

    return area

def assignMDValues(point_layer, cl_layer):
    m_values = pd.Series(dtype='float64')
    d_values = pd.Series(dtype='float64')
    cl_string = LineString(cl_layer.at[0, 'geometry'])
    bar = progressbar.ProgressBar(min_value=0).start()
    for i in range(len(point_layer) - 1):
        p = Point(point_layer.at[i, 'geometry'])
        m_val = cl_string.project(p)
        proj_point = cl_string.interpolate(m_val)
        d_val = p.distance(proj_point)
        if point_layer.at[i, 'side'] == 0:
            d_val = d_val * -1
        m_values = pd.concat([m_values, pd.Series(index=[i], data=[m_val])])
        d_values = pd.concat([d_values, pd.Series(index=[i], data=[d_val])])
        bar.update(i)
    point_layer['m_val'] = m_values
    point_layer['d_val'] = d_values

    return point_layer

if __name__ == "__main__":
    main()
