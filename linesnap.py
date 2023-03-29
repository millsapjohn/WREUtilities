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
    # extract all vertices from lines. Vertices that have one line segment
    # attached get a "z" value of 0, vertices with two attached get 1. This
    # will be used to filter points when snapping later on.
    end_points = []
    print('\nextracting points')
    for index, row in source_lyr.iterrows():
        row_coords = shapely.get_coordinates(row['geometry']).tolist()
        pt = shapely.Point(row_coords[0])
        end_points.append({'geometry' : pt})
        pt = shapely.Point(row_coords[-1])
        end_points.append({'geometry' : pt})
    point_layer = gpd.GeoDataFrame(end_points, geometry='geometry', crs=source_lyr.crs)
    point_index = point_layer.sindex
    
    minx, miny, maxx, maxy = point_layer.geometry.total_bounds
    bounds = shapely.Polygon([(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)])
    
    print('\ncreating new segments')
    seg_list = []
    used_list = []
    bar = progressbar.ProgressBar(min_value=0).start()
    for index, row in point_layer.iterrows():
        pt = point_layer.at[index, 'geometry']
        bounds_check = shapely.buffer(pt, 1)
        if shapely.contains(bounds, bounds_check) == False:
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
                # create dictionary of matches filtered by number of connected segments
                match_dist_dict = {}
                for index2, row2 in precise_matches.iterrows(): 
                    temp_pt = precise_matches.at[index2, 'geometry']
                    match_dist_dict.update({row2['geometry'].distance(pt) : index2})
                # sort match dict by distance to pt
                match_dist_dict = OrderedDict(sorted(match_dist_dict.items(), key=lambda t: t[0]))
                # grab nearest point (index 0 is the point itself), create new segment
                try: 
                    update_pt = shapely.Point(point_layer.at[list(match_dist_dict.values())[1], 'geometry'])
                except IndexError: 
                    continue
                if list(match_dist_dict.values())[1] in used_list: 
                    continue
                new_seg = shapely.LineString([shapely.force_2d(pt), shapely.force_2d(update_pt)])
                # update points to reflect added segment (exclude from future searches)
                seg_list.append({'geometry' : new_seg})
                used_list.extend([index, list(match_dist_dict.values())[1]])
        bar.update(index)
        
    print('\nconverting segments to multipart')
    new_lyr = gpd.GeoDataFrame(seg_list, geometry='geometry', crs=source_lyr.crs)
    # seg_lyr.dissolve()
    print('\nprocessing complete')
    new_lyr.to_file(destination)
    
def featureTypeCheck(layer): 
    for index, row in gdf.iterrows(): 
        if row['geometry'].geom_type != 'LineString': 
            sys.exit('Geometry is not linestrings')
        else: 
            pass
            
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