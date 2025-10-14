#!/usr/bin/python3

import xml.etree.ElementTree as ET
from xml.dom import minidom

import json

def esmini_object(entities, name):

    value = "car_white" if name == "ego_vehicle" else "car_red"
    esmini_name = "Ego" if name == "ego_vehicle" else name

    scenario_object = ET.SubElement(entities, "ScenarioObject", attrib={"name": esmini_name}) 
    ET.SubElement(scenario_object, "CatalogReference", attrib={
        "catalogName":"VehicleCatalog",
        "entryName": value,
        })

def carla_object(entities, name):
    return

def autoware_object(entities, name):
    return


def generate_openscenario(data_json):
    scenario = ET.Element("OpenSCENARIO")
    header = ET.SubElement(scenario, "FileHeader", attrib={
        "author" : "brainIV",
        "date": "",
        "description": "rosbag2carla",
        "revMajor": "1",
        "revMinor": "1",
        })

    parameter_declarations = ET.SubElement(scenario, "ParameterDeclarations")
    catalog_locations = ET.SubElement(scenario, "CatalogLocations")
    # add vehicle catalog for esmini
    ET.SubElement(ET.SubElement(catalog_locations, "VehicleCatalog"), "Directory", attrib={"path": "Catalogs/Vehicles"})
    
    road_network = ET.SubElement(scenario, "RoadNetwork")
    ET.SubElement(road_network, "LogicFile", attrib={"filepath": "map.xodr"})
    ET.SubElement(road_network, "SceneGraphFile", attrib={"filepath": ""})

    entities = ET.SubElement(scenario, "Entities")
    # add ego vehicle
    esmini_object(entities, "Ego", "car_white")

    storyboard = ET.SubElement(scenario, "StoryBoard")
    for i, frame in enumerate(data_json):
        # init 
        actions = ET.SubElement(ET.SubElement(storyboard, "Init"), "Actions")
        teleport_action = ET.SubElement(
                              ET.SubElement(
                                  ET.SubElement(actions, "Private", attrib={"entityRef" : "Ego"}), 
                              "PrivateActions"), 
                           "TeleportAction")
        position = ET.SubElement(
                       ET.SubElement(teleport_action, "Position"),
                       "WorldPosition"
                       )
