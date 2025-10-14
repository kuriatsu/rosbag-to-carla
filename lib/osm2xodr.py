#!/usr/bin/python3
# -*- coding:utf-8 -*-

import glob
import os
import sys
import numpy as np
import xml.etree.ElementTree as ET 
import argparse
from lib.gnss2cartesian import gnss2cartesian

try:
    sys.path.append(glob.glob('**/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def osm2xodr(osm_data, lane_width):
    """convert map from openstreetmap to opendrive
    """
    # get origin of the map
    root = ET.fromstring(osm_data)
    if root.tag != "osm":
        print("map doesn't contain osm tag")
    elif root.find("bounds") is not None:
        bound = root.find("bounds")
        lat = bound.get("minlat")
        lon = bound.get("minlon")
    else:
        node = root.find("node")
        lat = node.get("lat")
        lon = node.get("lon")

    buf = gnss2cartesian(lat, lon, 0, 0)

    # calculate map offset
    offset_x = buf[0]
    offset_y = buf[1]
    print(offset_x, offset_y)

    # Define the desired settings. In this case, default values.
    settings = carla.Osm2OdrSettings()

    # Set OSM road types to export to OpenDRIVE
    settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])
    ## Keep original origin
    settings.center_map = False 

    ## UE4 cannot deal with the huge map
    settings.use_offsets = True
    settings.offset_x = offset_x
    settings.offset_y = offset_y

    settings.default_lane_width = lane_width
    settings.generate_traffic_lights = True

    # Convert to .xodr
    xodr_data = carla.Osm2Odr.convert(osm_data, settings)
    return xodr_data, offset_x, offset_y


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--osm", type=str, help="open street map filepath", required=True)
    parser.add_argument("-x", "--xodr", type=str, help="open drive map filepath", required=True)
    args = parser.parse_args()

    # read osm data
    with open(args.osm, 'r') as f:
        osm_data = f.read()

    # transform map from osm to opendrive
    xodr_data, offset_x, offset_y = osm2xodr(osm_data, 6.0)

    # save opendrive file
    with open(args.xodr, 'w') as f:
        f.write(xodr_data)

    # print map offset
    print(f"offset x={offset_x}, y={offset_y}")


if __name__ == "__main__":
    main()

