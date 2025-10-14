import csv
import sys
import glob
import os.path
from typing import Tuple
import pandas as pd
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree

try:
    sys.path.append(glob.glob('**/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def _pretty_print(current, parent=None, index=-1, depth=0):
    for i, node in enumerate(current):
        _pretty_print(node, current, i, depth + 1)
    if parent is not None:
        if index == 0:
            parent.text = '\n' + ('\t' * depth)
        else:
            parent[index - 1].tail = '\n' + ('\t' * depth)
        if index == len(parent) - 1:
            current.tail = '\n' + ('\t' * (depth - 1))
            
def gnss2cartesian(lat: float, lon: float, offset_x: int =0, offset_y: int =0)->Tuple:
    '''
    convert latitude and longitude to cartesian coordinate(x,y)
    '''
    root = Element("osm")
    
    element_way = Element("way")
    element_way.set("id", "1")
    element_way.set("visible", "true")

    for i in range(2):
        element_node = Element("node")
        element_node.set("id", str(i+1))
        element_node.set("visible", "true")
        if i == 0:
            element_node.set("lat", str(lat))
            element_node.set("lon", str(lon))
        else:
            element_node.set("lat", "0,0")
            element_node.set("lon", "0.0")
        
        root.append(element_node)
        
        sub_element_nd = SubElement(element_way, "nd")
        sub_element_nd.set("ref", str(i+1))
    
    sub_element_tag = SubElement(element_way, "tag")
    sub_element_tag.set("k", "highway")
    sub_element_tag.set("v", "motorway")

    root.append(element_way)
    
    # _pretty_print(root)
    
    lane_width = 0.0
    cartesian_data = transform_point(ET.tostring(root),offset_x ,offset_y, lane_width)  
    cartesian_root = ET.fromstring(cartesian_data)
    for child in cartesian_root:
        if child.tag == 'header':
            x = -float(child.get('east'))
            y = -float(child.get('north'))
            break
        
    # print(f"convert [{lat=}, {lon=}] to [{x=}, {y=}]")
    
    return x, y

def transform_point(osm_data, offset_x, offset_y, lane_width):

    # Define the desired settings. In this case, default values.
    settings = carla.Osm2OdrSettings()

    # Set OSM road types to export to OpenDRIVE
    settings.set_osm_way_types(["motorway"])
    ## Keep original origin
    settings.center_map = False 

    ## UE4 cannot deal with the huge map
    settings.use_offsets = True
    settings.offset_x = offset_x 
    settings.offset_y = offset_y 

    settings.default_lane_width = lane_width
    
    # WANT TO DO : using proj (https://proj.org/about.html)    
    # settings.proj_string = "proj"

    # Convert to .xodr
    xodr_data = carla.Osm2Odr.convert(osm_data, settings)
    
    return xodr_data

def main():
    csv_path = sys.argv[1]
    df_gnss = pd.read_csv(csv_path)
    
    x,y = gnss2cartesian(35.053224300000004, 136.8577113, -4040000, -15140000)
    
    for row in df_gnss.itertuples():
        x,y = gnss2cartesian(row[6], row[7], -4040000, -15140000)
        break
        
if __name__ == "__main__":
    main()
