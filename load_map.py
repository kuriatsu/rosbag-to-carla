#!/usr/bin/python3
# -*- coding:utf-8 -*-

import glob
import os
import sys
import numpy as np

try:
    sys.path.append(glob.glob('**/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

# connect to calra
client = carla.Client('127.0.0.1', 2000)
client.set_timeout(2.0)
world = client.get_world()

# import map
xodr_path=sys.argv[1]
with open(xodr_path, encoding='utf-8') as od_file:
    try:
        data = od_file.read()
    except OSError:
        print('file could not be readed.')
        sys.exit()

print('load opendrive map %r.' % os.path.basename(xodr_path))
vertex_distance = 2.0  # in meters
max_road_length = 500.0 # in meters
wall_height = 0.0      # in meters
extra_width = 0.6      # in meters
world = client.generate_opendrive_world(
    data, carla.OpendriveGenerationParameters(
        vertex_distance=vertex_distance,
        max_road_length=max_road_length,
        wall_height=wall_height,
        additional_width=extra_width,
        smooth_junctions=True,
        enable_mesh_visibility=True))

