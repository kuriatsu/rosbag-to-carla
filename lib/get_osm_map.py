#!/usr/bin/env python3
import json
import sys
import urllib.request

def get_osm_map(rosbag_data):

    latitude = []
    longitude = []
    for d in rosbag_data:
        latitude.append(d["pose"]["gnss"]['latitude'])
        longitude.append(d["pose"]["gnss"]['longitude'])

    lat_min = min(latitude)
    lat_max = max(latitude)
    lon_min = min(longitude)
    lon_max = max(longitude)

    url = 'https://api.openstreetmap.org/api/0.6/map?bbox={},{},{},{}'.format(lon_min, lat_min, lon_max, lat_max)
    with urllib.request.urlopen(url) as u:
        out_map = u.read()

    return out_map


def main():
    with open(sys.argv[1]) as f:
        rosbag_data = json.load(f)

    map = get_osm_map(rosbag_data)

    with open(sys.argv[2], 'bw') as o:
        o.write(map)


if __name__ == "__main__":

    main()
