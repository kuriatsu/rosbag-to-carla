#!/usr/bin/python3
# -*-coding:utf-8-*-

import argparse
from xml.dom import minidom
import xml.etree.ElementTree as ET 

from lib.extract_data import extract_data_from_rosbag 
from lib.get_osm_map import get_osm_map
from lib.osm2xodr import osm2xodr
from lib.coordinate_conversion import coordinate_conversion
from lib.generate_carla_scenario import generate_carla_scenario


def rosbag_to_carla(args):
    print("extract data from rosbag")
    extracted_data = extract_data_from_rosbag(args.gnss, args.obj, args.start, args.end)
    print("get osm map")
    osm_map = get_osm_map(extracted_data)
    print("convert osm to opendrive")
    xodr_map, offset_x, offset_y = osm2xodr(osm_map, 6.0)
    print(offset_x, offset_y)
    print("convert driving data for opendrive coordinate")
    converted_data = coordinate_conversion(extracted_data, offset_x, offset_y)
    print("writing scenario")
    xml_scenario = generate_carla_scenario(converted_data)

    return xodr_map, xml_scenario


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gnss", type=str, help="gnss rosbag filename", required=True)
    parser.add_argument("--obj", type=str, help="object rosbag filename", required=True)
    parser.add_argument("-s", "--start", type=float, default="0.0", help="start timestamp")
    parser.add_argument("-e", "--end", type=float, default="-1.0", help="end timestamp")
    parser.add_argument("--xodr", type=str, default="map.xodr", help="opendrivemap")
    parser.add_argument("--scenario", type=str, default="scenario.xml", help="carla scenario file")
    args = parser.parse_args()
    xodr_map, xml_scenario = rosbag_to_carla(args)

    # save opendrive file
    with open(args.xodr, 'w') as f:
        f.write(xodr_map)

    doc = minidom.parseString(ET.tostring(xml_scenario, 'utf-8'))
    with open(args.scenario,"w") as f:
        doc.writexml(f, encoding='utf-8', newl='\n', indent='', addindent='  ')

