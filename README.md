# Interceptor 4.0 - Team Delamain

![Python version](https://img.shields.io/badge/python-v3.7-blue)
![GitHub contributors](https://img.shields.io/github/contributors/heng2j/delamain)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

Team Members:
   * Zhongheng (Heng) Li aka heng2j
   * Nicolas Morant aka DevGlitch
   * Huayu (Jack) Tsu aka codejacktsu


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/heng2j/delamain">
    <img src="images/police_car_picture.png" alt="Logo" height="300">
  </a>
</p>


<!-- DESCRIPTION OF THE PROJECT -->
## Description
We wanted to build a level 4 autonomous law enforcement vehicle, Interceptor 4.0, 
that patrols neighborhoods and when needed chases vehicles. 

The challenges Interceptor 4.0 would face are as follows: lane detection and tracking, 
object detection and avoidance, GPS navigation, self-parking, specific vehicle tracking, and car chasing.


<!-- PROJECT REPORT-->
## Project Report
https://github.com/heng2j/delamain/blob/master/Project_Report/Project_Report_Team_Delamain.pdf

<!-- PROJECT PRESENTATION-->
## Presentation
https://youtu.be/7PMrhMN3heU


<!-- DEMO OF THE PROJECT -->
## Demos
https://github.com/heng2j/delamain/tree/master/demos


<!-- GETTING STARTED -->
## Getting Started

Follow the below instructions in order to run Interceptor 4.0 on your machine.


### Prerequisites

* CARLA v0.9.10<br>
  https://github.com/carla-simulator/carla <br>
  This project was developed using this specific version of CARLA.<br>
  We cannot guarantee that it would work with any higher version.
  
  
### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/heng2j/delamain.git
   ```
2. Install any missing packages. 
   + We recommend using a conda environment with Python 3.7.
    

### Running

1. Start Server Map: Open CARLAUE4.exe


2. Load the map that you'd like. By default CARLA loads map Town03


3. Run any of the command below.<br>
   Please make sure you are in the correct directory.
   

* #### Base Model 3

Third iteration of our base model with full capabilities.<br>
Press "i" to activate GPS from current location to destination.<br>
Press "p" to toggle autopilot<br>
Press "h" to toggle hotkey map
```sh
   python base_model3.py
   ```

* #### GPS Navigation Base Model

This file gives you a short demo of the navigation system. You can change the destination location.
Please ensure the destination is for the load CARLA map.
```sh
   python base_model_nav.py
   ```

* #### Self-Parking Base Model

This file gives you a short demo of the self-parking feature. In this file you have the option to change from perpendicular to parallel parking.
```sh
   python base_model_park.py
   ```

* #### Road Network Map

This script enables you to visualize the road network of any CARLA map.
```sh
   python road_network_map.py
   ```

* #### Spectator Location

This script gave you the ability to get the exact location of the spectator view. 
It gives you the location in CARLA Location (x, y, z).
```sh
   python spectator_location.py
   ```

* #### Topology Edge & Node

This script enables you to store the topology data (edges and nodes) in two parquet files.
These files are in a format that enables you to use with Network X.
```sh
   python topology_edge_and_node.py.py
   ```

* #### Topology Waypoints Visualizer

This script is a visualizer in CARLA of the topology waypoints. Make sure to run the previous script in order for this one to work.
```sh
   python topology_waypoints_visualizer.py
   ```

* #### Base Model 3 Car Chasing

Drive as leading car
```sh
   python base_model3_car_chasing.py
   ```

* #### Car Chase Demo v2

Run as chasing car
```sh
   python car_chase_demo_v2.py
   ```

* #### Car Chase Demo v3

Run car chasing with dynamic Frenet short-term trajectory planning
```sh
   python car_chase_demo_v3.py
   ```


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact

Zhongheng (Heng) Li  - [Github](https://github.com/heng2j)

Nicolas Morant - [Personal Website](https://www.nicolasmorant.com/)
 & [Github](https://github.com/DevGlitch)

Huayu (Jack) Tsu - [Github](https://github.com/codejacktsu)


<br>

Project Link: [https://github.com/heng2j/delamain](https://github.com/heng2j/delamain)
