import sys
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry import LineString

def main():
    grid_space = sys.argv[4]
    power = sys.argv[5]
    radius = sys.argv[6]
    min_points = sys.argv[7]
    max_points = sys.argv[8]

    # get data source and feature layer for bathymetry, mask (outline), and centerline
    bathy_lyr = gpd.read_file(sys.argv[1])
    mask_lyr = gpd.read_file(sys.argv[2])
    cl_lyr = gpd.read_file(sys.argv[3])

    # create side, m_val, d_val columns in bathy layer
    createColumn(bathy_lyr, 'side', 'int64')
    createColumn(bathy_lyr, 'm_val', 'float64')
    createColumn(bathy_lyr, 'd_val', 'float64')

    # compare CRS for the three layers - need to be in the same CRS
    bathy_crs_code = bathy_lyr.crs.to_epsg(min_confidence=20)
    mask_crs_code = mask_lyr.crs.to_epsg(min_confidence=20)
    cl_crs_code = cl_lyr.crs.to_epsg(min_confidence=20)

    # check that layers have the same CRS code
    if bathy_crs_code != mask_crs_code or bathy_crs_code != cl_crs_code:
        sys.exit("mismatched layer CRS")

    # check that centerline, mask layers only have one feature
    featureCountCheck(cl_lyr)
    featureCountCheck(mask_lyr)

    # TODO create segment list

    # calculate side, m value, d value for bathy layer, add to bathymetry layer fields
    assignSide(bathy_lyr, cl_lyr)
    assignMDValues(bathy_lyr, cl_lyr)

    # get bounding box of mask layer - will clip later
    b_box = mask_lyr.total_bounds
    min_x = b_box[0]
    max_x = b_box[1]
    min_y = b_box[2]
    max_y = b_box[3]

    # generate grid layer, add necessary fields
    grid_lyr = gpd.GeoDataFrame(columns=['side', 'm_val', 'd_val', 'geom'], geometry='geom')

    # add points to grid layer based on spacing value provided
    for i in range((round((max_x - min_x) / grid_space)) - 1):
        for j in range((round((max_y - min_y) / grid_space)) - 1):
            x_coord = min_x + (i * grid_space)
            y_coord = min_y + (j * grid_space)
            pt = Point(x_coord, y_coord)
            grid_lyr.add(pt)

    # clip grid layer
    grid_lyr = gpd.clip(grid_lyr, mask_lyr)

    # calculate side, m value, d value for grid layer, add to grid layer fields
    assignSide(grid_lyr, cl_lyr)
    assignMDValues(grid_lyr, cl_lyr)

    # TODO run the IDW function, export the gdf as a shapefile

def createColumn(gdf, name, data_type):
    gdf.assign(name)
    gdf.astype({name : data_type})
    return gdf

def featureCountCheck(gdf):
    if len(gdf.index) > 1:
        sys.exit(f"multiple features in {gdf}")
    else:
        pass

def inverseDistanceWeighted(bathy_points, grid_points, power, radius, min_points, max_points):
    sum = 0
    for i in range(len(grid_points) - 1):
        dist_dict = {}
        l = 0
        gp = Point(grid_points[i].coords)
        gp_side = grid_points.at(i, 'side')
        for j in range(len(bathy_points) - 1):
            bp_side = bathy_points.at(j, 'side')
            if bp_side != gp_side:
                continue
            else:
                bp = Point(bathy_points[j].coords)
                dist = bp.distance(gp)
                temp_dict = {dist: j}
                dist_dict.append(temp_dict)
        for key in dist_dict:
            if key < radius:
                l += 1
        if l > max_points - 1:
            l = max_points - 1
        elif l < min_points - 1:
            l = min_points - 1
    
    return(grid_points)

def assignSide(point_layer, line_layer):
    line_coords = line_layer.apply(lambda geom: geom.coords, axis=1)
    for p in point_layer:
        temp_point = Point(p.coords)
        for i in range(len(line_coords) - 2):
            temp_line = LineString(coords[i], coords[i + 1])
            temp_area = signedTriangleArea(temp_line, temp_point)
            if coord == 0:
                area = temp_area
            if abs(temp_area) < abs(area):
                area = temp_area
        if area > 0:
            side = 0
        else:
            side = 1

        point_layer.at(p, 'side') = side 

        return point_layer

def signedTriangleArea(test_line, test_point):
    # the "signed triangle area" formula returns an area value that is < 0 when the test point is on the
    # right side of the line, > 0 when on the left. This determines the "sidedness" of each point.
    # smaller absolute value = closer to the line. This will be used to "associate" each point to the
    # nearest segment of the centerline.
    vertex_1 = test_line.coords[0]
    vertex_2 = test_line.coords[1]
    area = ((vertex_2.x - vertex_1.x) - (test_point.y - vertex_2.y)) - ((test_point.x - vertex_2.x) * (vertex_2.y - vertex_1.y))

    return area

def assignMDValues(point_layer, cl_layer):
    for p in point_layer:
        m_val = cl_layer.project(p)
        proj_point = cl_layer.interpolate(m_val)
        d_val = p.distance(proj_point)
        point_layer.at(p, 'm_val') = m_val
        point_layer.at(p, 'd_val') = d_val

    return point_layer

if __name__ == "__main__":
    main()
