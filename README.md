# rosbag-to-carla
![version](https://img.shields.io/badge/ver-v0.1-blue) ![carla version](https://img.shields.io/badge/CARLA-0.9.12-green)  ![GitHub last commit](https://img.shields.io/github/last-commit/TakedaLab/rosbag-to-carla)  ![issues](https://img.shields.io/github/issues/TakedaLab/rosbag-to-carla)    
Reproduction of real driving scenes in simulator environment. Ego vehicle (lat, lon, speed) and traffic participants (relative position to the ego vehicle) are extracted from driving data (e.g., scripts for rosbag (ROS1) is included in this repo). Retrieve map from OpenStreetMap&reg;. Then convert the extracted data to driving scenario and OSM map to OpenDriveMap&reg;. Load the map to CARLA and run the scenario using [carla-scenario](https://github.com/kuriatsu/carla-scenario/tree/nedo). The result is shown in the following image.
![bitmap](https://user-images.githubusercontent.com/38074802/194993335-6e2ed651-a818-4063-879e-cc7dc6502ab5.png)

## SETUP
1. Install CARLA (0.9.12 is tested)
2. Install repos
```bash
git clone https://github.com/TakedaLab/rosbag-to-carla
git clone https://github.com/kuriatsu/carla-scenario
cd carla-scenario
git fetch nedo
git checkout nedo
```
3. Install ROS1

## RUN
### 1. Generate scenario and map
```bash
source /opt/ros/noetic/setup.bash
python3 rosbag_to_carla.py --gnss <gnss_rosbag> --obj <object_rosbag> --start <start timestamp> --end <end timestamp> --xodr map.xodr --scenario scenario.xml
```
* gnss_rosbag : As for meti dataset, this is ssd4xxx.bag
* object_rosbag : This should contain perception and tracking data. As for the meti dataset, this name is the same name with the folder.
* start timestamp : Simulation start time
* end timestamp : Simulation end time
* map.xodr : OpenDriveMap for simulation 
* scenario.xml : scenario file 

### 2. Run CARLA

```bash
# package installation
./CarlaUE4.sh
# source installation
make launch-only
```

### 3. Load OpenDriveMap
```bash
python3 rosbag-to-carla/load_map.py opendrive.xodr
```

### 4. Run scenario
```bash
python3 carla-scenario/scenario_xml.py -s scenario.xml
```

## Test w/ scenario creation
Move ego vehicle and spawn vehicles  
### Data source: 
[datawaretools](https://tools.bsplab.org/data-browser/databases) 
* object_rosbag : METI-2021/20211018_102528_000_car3/20211018_102528_000_car3_2847095013759f3e98d7b0ea5fdb0f2d.bag 
* gnss_rosbag : METI-2021/20211018_102528_000_car3/ssd4_autoware_2021-10-18-10-25-29_0.bag
* timestamp: 1634520331 - 1634520341 (20sec)

```bash
# Extract data
python3 rosbag_to_carla.py --gnss ssd4_autoware_2021-10-18-10-25-29_0.bag --obj ssd4_autoware_2021-10-18-10-25-29_0.bag -s 1634520331 -e 1634520341 --xodr map.xodr --scenario scenario.xml

# Run simulation
/opt/carla-simulator/CarlaUE4.sh
python3 rosbag-to-carla/load_map.py opendrivemap.xodr
python3 carla-scenario/warp.py # move spectator camera to the scenario position, you may need to change the coodinate of the camera according to the scenario.
python3 carla-scenario/scenario_xml.py -s scenario.xml
python3 rosbag-to-carla/ego_vehicle_camera.py # view camera on the ego_vehicle
```

## Test w/ prepared scenario
```bash
/opt/carla-simulator/CarlaUE4.sh
python3 rosbag-to-carla/load_map.py rosbag-to-carla/map/ssd4_autoware-2021-10-18-11-15-29_3-1634522222.775191000/opendrivemap.xodr
python3 carla-scenario/warp.py # move spectator camera to the scenario position
python3 carla-scenario/scenario_xml.py -s rosbag-to-carla/map/ssd4_autoware-2021-10-18-11-15-29_3-1634522222.775191000/scenario.xml
python3 rosbag-to-carla/ego_vehicle_camera.py # view camera on the ego_vehicle
```

https://user-images.githubusercontent.com/38074802/197950809-6d37489f-96ab-4471-b68f-fff750ce6ece.mp4
