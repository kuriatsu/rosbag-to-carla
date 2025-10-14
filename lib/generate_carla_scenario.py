#!/usr/bin/python3

import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import json
import copy
import argparse

def spawn(trigger, id, actor_type, prob, bp, pose):
    elem = ET.SubElement(trigger, "spawn")
    # transform = f'{pose["x"]}, {pose["y"]}, 1.0, 0.0, {pose["yaw"]}, 0.0}'

    elem.set("id", str(id))
    sp_type = ET.SubElement(elem, "type")
    sp_prob = ET.SubElement(elem, "probability")
    sp_bp = ET.SubElement(elem, "blueprint")
    sp_trans = ET.SubElement(elem, "transform")

    sp_type.text = actor_type
    sp_prob.text = str(prob)
    sp_bp.text = bp
    # transform = '{}, {}, {}, 0.0, {}, 0.0'.format(pose["position"]["x"], pose["position"]["y"], pose["position"]["z"],pose["rpy"]["yaw"])
    transform = '{}, {}, 0.5, 0.0, {}, 0.0'.format(pose["position"]["x"], pose["position"]["y"], pose["rpy"]["yaw"])
    sp_trans.text = transform

def add_waypoint(e_trigger, e_moves, id, pose, speed):
    # id = e_trigger["id"]
    if id not in e_moves.keys():
        e_moves[id] = ET.SubElement(e_trigger, "move")
        e_moves[id].set("id", str(id))
    else:
        e_waypoint = ET.SubElement(e_moves[id], "waypoint")
        e_waypoint.text = '{}, {}, 0.0'.format(pose["position"]["x"], pose["position"]["y"])  
        e_waypoint.set("speed", str(speed))


def add_kill(e_trigger, e_moves, id):
    kill = ET.SubElement(e_trigger, "kill")
    kill.set("id", str(id))
    # remove actor from moving list
    del e_moves[id]


def generate_carla_scenario(data_json):

    data = ET.Element("data")
    ego_waypoints = []
    e_moves = {} # currently moving actor list (not to spawn actor twice) 

    for i, frame in enumerate(data_json):
        # init trigger
        e_trigger = ET.SubElement(data, "trigger")
        e_trigger.set("id", str(i))
        e_trigger.set("thres", str(5.0))
        e_trigger_location = ET.SubElement(e_trigger, "location")
        e_trigger_location.text = f'{frame["pose"]["position"]["x"]}, {frame["pose"]["position"]["y"]}, 0.0'
            
        # spawn ego vehicle
        if "ego_vehicle" not in e_moves.keys():
            spawn(e_trigger, "ego_vehicle", "vehicle", 100, "vehicle.audi.tt", frame["pose"])

        # spawn actor
        for object in frame["objects"]:
            id = object["id"]
            if id in e_moves.keys(): continue

            spawn(e_trigger, id, "vehicle", str(object["score"]), "random", object["pose"])

        # move ego vehicle
        print(frame["speed"])
        add_waypoint(e_trigger, e_moves, "ego_vehicle", frame["pose"], frame["speed"])  

        # move actors
        for object in frame["objects"]:
            add_waypoint(e_trigger, e_moves, object["id"], object["pose"], object["speed"])  
                
        # kill actors
        kill_list = []
        for id in e_moves.keys():
            if id == "ego_vehicle": continue
            is_exist = False
            for object in frame["objects"]:
                if id == object["id"]:
                    is_exist = True

            if not is_exist: 
                kill_list.append(id) 
            
        for id in kill_list:
            add_kill(e_trigger, e_moves, id)
            

    for id in [i for i in e_moves.keys()]:
        add_kill(e_trigger, e_moves, id)

    # tree = ET.ElementTree(data)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="input json driving data", required=True)
    parser.add_argument("-o", "--output", type=str, help="output xml filename", required=True)
    args.parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    scenario_xml = generate_carla_scenario(data)

    doc = minidom.parseString(ET.tostring(data, 'utf-8'))
    with open(args.output,"w") as f:
        doc.writexml(f, encoding='utf-8', newl='\n', indent='', addindent='  ')

