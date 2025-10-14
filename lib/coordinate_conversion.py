#!/usr/bin/env python
"""
Welcome to CARLA scenario controller.
"""
import glob
import os
import sys
import numpy as np
import random
import json
import argparse

from lib.gnss2cartesian import gnss2cartesian

def coordinate_conversion(data, offset_x, offset_y):
    """convert coordinate in data(json), add it to the original data
    """

    ego_pose = None


    for step in data:

        ############################
        # Ego vehicle pose
        ############################
        ego_position = np.array([*gnss2cartesian(
                                step["pose"]["gnss"]["latitude"], 
                                step["pose"]["gnss"]["longitude"], 
                                offset_x, 
                                offset_y
                                )
                            ])
        
        ego_position[0] *= -1 # right-handed to left-handed coordinate 

        # calculate ego vehicle yaw, angle differential between previous step and current step
        # if step is 0
        if ego_pose is None:
            next_ego_position = np.array([*gnss2cartesian(
                                    data[1]["pose"]["gnss"]["latitude"], 
                                    data[1]["pose"]["gnss"]["longitude"], 
                                    offset_x, 
                                    offset_y
                                    )
                                ])
            next_ego_position[0] *= -1 # right-handed to left-handed coordinate
            ego_yaw = np.arctan((next_ego_position[1]-ego_position[1])/(next_ego_position[0]-ego_position[0]))

        else:
            ego_yaw = np.arctan((ego_position[1]-ego_pose["position"]["y"])/(ego_position[0]-ego_pose["position"]["x"]))

        ego_pose = {
            "position": {
                "x": ego_position[0],
                "y": ego_position[1],
                "z": 0.5, 
                },
            "rpy": {
                "roll": 0.0, 
                "pitch": 0.0, 
                "yaw": ego_yaw,
                }
            }


        ############################
        # Obstacle pose
        ############################
        for obj in step["objects"]:
            rpy = to_rpy(
                    obj["pose"]["orientation"]["x"], 
                    obj["pose"]["orientation"]["y"], 
                    obj["pose"]["orientation"]["z"], 
                    obj["pose"]["orientation"]["w"]
                    )

            pose = {
                    "position": {
                        "x": -obj["pose"]["position"]["x"], 
                        "y": obj["pose"]["position"]["y"], 
                        "z": obj["pose"]["position"]["z"]
                        },
                    "rpy": rpy 
                    }

            position, yaw = to_absolute_pose(ego_pose, pose) 
            
            # rotate vehicle in same flow 180 degree (right-handed to left-handed coordinate)
            if obj["relative_velocity"]["linear"]["x"] > -20.0:
                yaw += np.pi 

            # update obstacle coordinate
            obj["pose"]["position"] = position
            obj["pose"]["rpy"] = {"roll":0.0, "pitch":0.0, "yaw":np.degrees(yaw)}
            obj["speed"] = to_absolute_speed({"x":step["speed"], "y":0.0, "z":0.0}, obj["relative_velocity"]["linear"])

        # update ego vehicle coordinate
        step["pose"]["position"] = ego_pose["position"]
        step["pose"]["rpy"] = ego_pose["rpy"]
        step["pose"]["rpy"]["yaw"] = np.degrees(step["pose"]["rpy"]["yaw"]) 

    return data 


def find_closest_waypoint(map, v_loc):
    min_dist = 1e10000
    closest_waypoint = None
    for waypoint in map.generate_waypoints(1.0):
        w_loc = np.array([waypoint.transform.location.x, waypoint.transform.location.y])
        dist = np.linalg.norm(w_loc - v_loc)
        if dist < min_dist:
            min_dist = dist
            closest_waypoint = waypoint

    return closest_waypoint


def to_rpy(x, y, z, w):
    """convert quaternion to rpy
    """
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

    return {"roll": roll, "pitch": pitch, "yaw": yaw}


def to_absolute_pose(base, target):
    """convert relative pose to absolute pose
    (base=ego_vehicle pose, target=obstacle pose relative to ego_vehicle)
    base, target, out = {
        "position": {
            "x": ,
            "y": ,
            "z": ,
            }
        "rpy": {
            "roll": ,
            "pitch" ,
            "yaw": ,
            }
        }
    """
    target_yaw = base["rpy"]["yaw"]
    buf = [
        target["position"]["x"]*np.cos(target_yaw) - target["position"]["y"]*np.sin(target_yaw), 
        target["position"]["x"]*np.sin(target_yaw) + target["position"]["y"]*np.cos(target_yaw),
        target["position"]["z"]
        ]

    out = {
            "x": base["position"]["x"] + buf[0],
            "y": base["position"]["y"] + buf[1],
            "z": base["position"]["z"] + buf[2]
            }

    out_yaw = (base["rpy"]["yaw"] + target["rpy"]["yaw"])

    return out, out_yaw


def to_absolute_speed(base, target):
    """convert relative velocity to absolute speed
    (base=ego_vehicle, target=obstacle velocity relative to ego_vehicle)
    base, target = {
        "x": ,
        "y": ,
        "z": ,
        }
    """

    target_speed = (target["x"]**2 + target["y"]**2)**0.5
    base_speed = (base["x"]**2 + base["y"]**2)**0.5

    if target["x"] < 0.0:
        out_speed = abs(target_speed - base_speed)
    else:
        out_speed = target_speed + base_speed

    return out_speed


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=int, help="input json data (extracted from rosbag", required=True)
    parser.add_argument("-o", "--output", type=int, help="output json data", required=True)
    parser.add_argument("--offset_x", type=int, help="x offset when convert (osm has big coordinate)", required=True)
    parser.add_argument("--offset_y", type=int, help="y offset when convert (osm has big coordinate)", required=True)
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    out_data = coordinate_conversion(data, args.offset_x, args.offset_y)

    with open(args.out_data, "w") as f:
        json.dump(out_data, f, indent=2)

if __name__ == "__main__":
    main()


