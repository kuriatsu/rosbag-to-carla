# Test map folder

## Naming
dir name-file name-time stamp of rosbag

## osm2odr.osm
Osm for transformation of one point

### how to use
1. Uncomment `transform_point()` in generate_map.py
2. `python3 generate_map.py map/osm2odr.osm`
3. Check generated map (point.xodr)
4. road->planview->geometry->x, y is the converted point
