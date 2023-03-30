import sys
import os
from collections import OrderedDict
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import pandas as pd
import shapely
import progressbar
import pathlib
import argparse

def main(): 
    parser = argparse.ArgumentParser(description='joining multiple line segments')
    parser.add_argument('source', type=fileCheck, help='source file')
    parser.add_argument('destination', type=fileCheck, help='output Shapefile')
    parser.add_argument('radius', type=intCheck, help='search radius for snapping vertices')
    args = parser.parse_args()
    source = args.source
    destination = args.destination
    radius = args.radius
    
    print('reading source file')
    source_lyr = gpd.read_file(args.source)
    
    # explodes all multipart geometries to singlepart. Singlepart geometries
    # are unaffected. This creates a gdf of all single line segments.
    print('\nconverting geometry to singlepart')
    seg_lyr = source_lyr.explode(ignore_index=True)
    end_points = []
    print('\nextracting points')
    # extract only beginning and ending vertices from all multilinestrings
    for index, row in source_lyr.iterrows():
        row_coords = shapely.get_coordinates(row['geometry']).tolist()
        pt = shapely.Point(row_coords[0])
        end_points.append({'geometry' : pt})
        pt = shapely.Point(row_coords[-1])
        end_points.append({'geometry' : pt})
    point_layer = gpd.GeoDataFrame(end_points, geometry='geometry', crs=source_lyr.crs)
    point_index = point_layer.sindex
    
    # create bounding box to check for beginning/ending points of the overall layer
    minx, miny, maxx, maxy = point_layer.geometry.total_bounds
    bounds = shapely.Polygon([(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)])
    
    print('\ncreating new segments')
    seg_list = []
    used_list = []
    bar = progressbar.ProgressBar(min_value=0).start()
    for index, row in point_layer.iterrows():
        pt = point_layer.at[index, 'geometry']
        # check that the point isn't at the bounds of the layer
        bounds_check = shapely.buffer(pt, 1)
        if shapely.contains(bounds, bounds_check) == False:
            continue
        # check that the vertex hasn't already has a new line segment attached to it
        elif index in used_list:
            continue
        else: 
            # search for vertices within the specified radius
            buff = shapely.buffer(pt, radius)
            possible_matches_index = list(point_index.intersection(buff.bounds))
            possible_matches = point_layer.iloc[possible_matches_index]
            precise_matches = possible_matches[possible_matches.intersects(buff)]
            if len(precise_matches) == 1: 
                continue
            else: 
                # create dictionary of unused vertices within search radius
                match_dist_dict = {}
                for index2, row2 in precise_matches.iterrows(): 
                    # create dictionary entry of point number and distance to current point
                    temp_pt = precise_matches.at[index2, 'geometry']
                    match_dist_dict.update({row2['geometry'].distance(pt) : index2})
                # sort match dict by distance to pt
                match_dist_dict = OrderedDict(sorted(match_dist_dict.items(), key=lambda t: t[0]))
                # create list of point numbers only, from nearest to furthest
                match_list = list(match_dist_dict.values())
                for i in range(len(match_list) - 1): 
                    # search will return the current point - discard
                    if i == 0: 
                        continue
                    elif match_list[i] not in used_list: 
                        update_pt = point_layer.at[match_list[i], 'geometry']
                        new_seg = shapely.LineString([pt, update_pt])
                        seg_list.append({'geometry' : new_seg})
                        used_list.append(index)
                        used_list.append(match_list[i])
                        break
                    else:
                        continue
        bar.update(index)
        
    new_lyr = gpd.GeoDataFrame(seg_list, geometry='geometry', crs=source_lyr.crs)
    print('\nprocessing complete')
    new_lyr.to_file(destination)
    
def fileCheck(file):
    ext = os.path.splitext(file)[1][1:]
    if ext != 'shp': 
        parser.error('files must be of type Shapefile')
    return file
    
def intCheck(arg): 
    try: 
        arg = int(arg)
    except ValueError: 
        parser.error(f'{arg} is not numeric')
    if arg < 1: 
        parser.error(f'{arg} is not greater than zero')
    return arg
    
if __name__ == "__main__": 
    main()