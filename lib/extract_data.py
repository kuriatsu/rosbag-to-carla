#!/usr/bin/python3

import json
import rosbag
import argparse

def extract_data_from_rosbag(gnss_bag, obj_bag, start_time, end_time):

    #####################################
    print("extracting gnss data")
    #####################################
    gnss_bag = rosbag.Bag(gnss_bag)
    gnss_data = {}
    speed = 0.0

    for topic, msg, ts in gnss_bag.read_messages():

        if ts.secs < start_time:
            continue
        elif end_time < ts.secs: 
            break

        if topic == "/gps_m2/sensor":
            speed = msg.speed

        if topic == "/gps_m2/gnss":
            print(ts.secs, topic)
            tmp = {
                "header_gnss": {
                    "seq":msg.header.stamp.to_sec(),
                    "nseq":msg.header.stamp.to_nsec(), 
                    "frame_id":msg.header.frame_id
                    },
                "pose":{
                    "gnss": {
                        "latitude": msg.latitude, 
                        "longitude": msg.longitude, 
                        "height": msg.height
                        },
                    "position": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 0.0,
                        },
                    "rpy": {
                        "roll": 0.0,
                        "pitch": 0.0,
                        "yaw": 0.0,
                        },
                    },
                "speed": speed,
                }

            gnss_data[ts] = tmp

    #####################################
    print("extracting object data")
    #####################################
    object_bag = rosbag.Bag(obj_bag)
    object_data = {}

    for topic, msg, ts in object_bag.read_messages():

        if ts.secs < start_time:
            continue
        elif end_time < ts.secs: 
            break

        if topic == "/autoware/tracked_object":
            print(ts.secs, topic)
            tmp = {
                "header_obj":{"seq":msg.header.stamp.to_sec(), "nseq":msg.header.stamp.to_nsec(), "frame_id":msg.header.frame_id},
                "num_objects":msg.num_objects,
                "objects":[],
                }
            for object in msg.objects:
                tmp_obj = {
                        "id": object.id,
                        "label": object.label,
                        "pose":{
                            "position":{"x": object.pose.position.x, 
                                        "y": object.pose.position.y, 
                                        "z": object.pose.position.z
                                        },
                            "orientation":{
                                "x":object.pose.orientation.x, 
                                "y":object.pose.orientation.y, 
                                "z": object.pose.orientation.z, 
                                "w": object.pose.orientation.w
                                },
                            },
                        "size":{
                            "x": object.size.x, 
                            "y": object.size.y, 
                            "z": object.size.z
                            },
                        "relative_velocity":{
                            "linear":{
                                "x": object.relative_velocity.linear.x, 
                                "y": object.relative_velocity.linear.y, 
                                "z": object.relative_velocity.linear.z
                                },
                            },
                        "speed": None,
                        "score": object.score,
                        }
                
                tmp["objects"].append(tmp_obj)
            object_data[ts] = tmp
        
    #####################################
    print("merging object data to gnss data (gnss=1hz, object=10hz)")
    #####################################
    out_data = []
    for gnss_ts in gnss_data.keys():
        for object_ts in object_data.keys():
            if object_ts >= gnss_ts:
                out_data.append({**gnss_data[gnss_ts], **object_data[object_ts]})
                break
    
    return out_data
                

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gnss", type=str, help="gnss rosbag filename", required=True)
    parser.add_argument("--obj", type=str, help="object rosbag filename", required=True)
    parser.add_argument("-s", "--start", type=float, default="0.0", help="start timestamp")
    parser.add_argument("-e", "--end", type=float, default="-1.0", help="end timestamp")
    parser.add_argument("-o", "--out", type=str, default="out.json", help="output json")
    args = parser.parse_args()
    out_data = extract_data_from_rosbag(args.gnss, args.obj, args.start, args.end)
    
    # save
    with open(args.out, "w") as f:
        json.dump(out_data, f, indent=2)
