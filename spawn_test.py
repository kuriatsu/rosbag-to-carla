#!/usr/bin/env python
"""
Welcome to CARLA scenario controller.
"""
import glob
import os
import sys
import numpy as np
import random
try:
    sys.path.append(glob.glob('**/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    sys.path.append("./")
except IndexError:
    pass

# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================
import carla

def spawn_vehicle(transform, blueprint, world, id):
    blueprint.set_attribute("role_name", str(id))

    if blueprint.has_attribute("color"):
        color = random.choice(blueprint.get_attribute("color").recommended_values)
        blueprint.set_attribute("color", color)

    if blueprint.has_attribute("color"):
        color = random.choice(blueprint.get_attribute("color").recommended_values)
        blueprint.set_attribute("color", color)

    try:
        world.spawn_actor(blueprint, transform)
    except Exception as e:
        print(e)

def find_closest_waypoint(map, location):
    min_dist = 1e10000
    closest_waypoint = None
    for waypoint in map.generate_waypoints(1.0):
        dist = (waypoint.transform.location.x - location.x)**2 + (waypoint.transform.location.y - location.y)**2
        if dist < min_dist:
            min_dist = dist
            closest_waypoint = waypoint

    return closest_waypoint

def quat_to_rpy(x, y, z, w):
    q0q0 = w * w;
    q1q1 = x * x;
    q2q2 = y * y;
    q3q3 = z * z;
    q0q1 = w * x;
    q0q2 = w * y;
    q0q3 = w * z;
    q1q2 = x * y;
    q1q3 = x * z;
    q2q3 = y * z;

    roll = np.arctan2((2.0 * (q2q3 + q0q1)), (q0q0 - q1q1 - q2q2 + q3q3));
    pitch = -np.arcsin((2.0 * (q1q3 - q0q2)));
    yaw = np.arctan2((2.0 * (q1q2 + q0q3)), (q0q0 + q1q1 - q2q2 - q3q3));

    return roll, pitch, yaw

def calc_absolute_coodinate(ref_transform, target_transform):
    out_transform = carla.Transform()
    buf_location = carla.Location()
    yaw = np.radians(ref_transform.rotation.yaw)
    buf_location.x = target_transform.location.x*np.cos(yaw) - target_transform.location.y*np.sin(yaw)
    buf_location.y = target_transform.location.x*np.sin(yaw) + target_transform.location.y*np.cos(yaw)
    buf_location.z = target_transform.location.z
    out_transform.location = ref_transform.location + buf_location
    out_transform.rotation.yaw = ref_transform.rotation.yaw + target_transform.rotation.yaw

    return out_transform


if __name__ == "__main__":
    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    carla_map = world.get_map()
    blueprints = world.get_blueprint_library()
    
    # Set ego vehicle position on the map, then, find waypoint of the map to specify the rotation
    ego_vehicle_location = carla.Location(x=-650.046, y=1078.7574, z=3.0)
    closest_waypoint = find_closest_waypoint(carla_map, ego_vehicle_location)
    ego_vehicle_rotation = carla.Rotation(roll=0.0, pitch=0.0, yaw=closest_waypoint.transform.rotation.yaw)
    ego_vehicle_transform = carla.Transform(location=ego_vehicle_location, rotation=ego_vehicle_rotation)

    # show ego vehicle position for debug
    world.debug.draw_point(
            location=ego_vehicle_transform.location,
            life_time=100,
            size=0.1,
            color=carla.Color(255, 255, 200)
            )

    # Pose of the surrounding vehicles
    transform_list = {
            685: {
                "position": { "x": -22.44822247291882, "y": -1.0318179069563738, "z": 0.10449865460395813},
                "orientation": { "x": 0, "y": 0, "z": -0.02474895167044166, "w": 0.9996936977850837 } 
                },
            694: {
                "position": { "x": -59.03326470568213, "y": 4.207335056986939, "z": 0.5911996681354716 }, 
                "orientation": { "x": 0, "y": 0, "z": -0.03935309311605045, "w": 0.9992253670029597 }
                },
            707: {
                "position": { "x": -50.83865695923877, "y": 7.79395821125812, "z": -0.6824950575828552 },
                "orientation": { "x": 0, "y": 0, "z": -0.017440344449341946, "w": 0.9998479056263949 }
                },
            715: {
                "position": { "x": -16.82644986167707, "y": 6.394341357847163, "z": -0.18901893496513367 },
                "orientation": { "x": 0, "y": 0, "z": -0.001916393126847954, "w": 0.9999981637170057 }
                },
            717: {
                  "position": { "x": 19.000384827013836, "y": 5.637102313819424, "z": 0.8836928816164954 },
                  "orientation": { "x": 0, "y": 0, "z": -0.023367877593322272, "w": 0.9997269338658349 }
                },
            722: {
                   "position": { "x": -95.6434309961493, "y": -4.061462727203287, "z": 0.7468209266662598 },
                   "orientation": { "x": 0, "y": 0, "z": -0.021300222812212912, "w": 0.9997731245178328 } ,
                },
            724: {
                    "position": { "x": -36.219013318290806, "y": -14.53341724353793, "z": 0.8227064609527588 },
                    "orientation": { "x": 0, "y": 0, "z": -0.013575515650306985, "w": 0.9999078484414593 }
                },
            725: {
                    "position": { "x": 58.67164312691762, "y": 4.523833833468859, "z": 1.690355619224342 },
                    "orientation": { "x": 0, "y": 0, "z": -0.004651832950884377, "w": 0.9999891801665641 }
                },
            727: {
                    "position": { "x": 4.920238413512462, "y": -16.344380466978514, "z": 1.0168921542167666 },
                    "orientation": { "x": 0, "y": 0, "z": -0.01118352182254069, "w": 0.9999374624643507 }
                },
            }

    # Move ego vehicle and spectator camera
    ego_vehicle = None
    for actor in world.get_actors():
        print(actor.type_id)
        if actor.attributes.get('role_name') == 'hero':
            print("move ego vehicle")
            ego_vehicle = actor
            actor.set_transform(ego_vehicle_transform)
        if actor.type_id == "spectator":
            print("move camera")
            actor.set_location(ego_vehicle_transform.location)


    # Spawn surrounding vehicles
    for id, transform in transform_list.items():
        # Vehicle transform
        buf_rotation = quat_to_rpy(transform["orientation"]["x"], transform["orientation"]["y"], transform["orientation"]["z"], transform["orientation"]["w"])
        obj_relative_transform = carla.Transform(
                location=carla.Location(x=transform["position"]["x"], y=-transform["position"]["y"] , z=transform["position"]["z"]),
                rotation=carla.Rotation(roll=buf_rotation[0], pitch=buf_rotation[1], yaw=-buf_rotation[2])
                )

        # Calcurate transform of the surrounding vehicle
        obj_transform = calc_absolute_coodinate(ego_vehicle_transform, obj_relative_transform)

        blueprint = random.choice(blueprints.filter("vehicle.*"))
        spawn_vehicle(obj_transform, blueprint, world, id)

