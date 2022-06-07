# Tello Control and Object Detection / Tracking App with GUI

This app is designed to control Tello drone from Nvidia's Jetson Nano / Xavier devices over WiFi connection and view the camera video. The project was completed with the technical and informational support of IoTLab at the Rhine-Waal University of Applied Sciences and its teaching staff [https://www.hochschule-rhein-waal.de/en/faculties/communication-and-environment/laboratories/iot-lab](https://www.hochschule-rhein-waal.de/en/faculties/communication-and-environment/laboratories/iot-lab).

##  Installation
Before running ensure that the following python libraries are present in your system:
- tello-python
- Tkinter
- opencv
- pillow

Ensure that Jetson Inference is installed and SSD-Mobilenet-V2 model downloaded. For more information see the following links:
[https://github.com/dusty-nv/jetson-inference](https://github.com/dusty-nv/jetson-inference)<br>
[https://github.com/dusty-nv/jetson-inference/blob/master/docs/building-repo-2.md](https://github.com/dusty-nv/jetson-inference/blob/master/docs/building-repo-2.md)

Tello-python installation (Linux)

```bash
>> git clone https://github.com/harleylara/tello-python.git
>> cd tello-python
>> sudo python setup.py install `
```
Opencv installation
```bash
conda install -c conda-forge opencv 
```
or
```bash
pip install opencv-python
```

Pillow installation
```bash
conda install -c conda-forge pillow
```
or
```bash
pip install Pillow
```

Tkinter installation
```bash
conda install -c conda-forge tk
```
or
```bash
pip install tk
```

## Running

```bash
git clone https://github.com/eligosoftware/tello-controller-jetson.git
cd tello-controller-jetson
python main.py
```

## Settings

In the Settings menu it is possible to set the drone IP address, movement and angle step values. The standard IP is 192.168.10.1 for the station mode. User should change the IP if the drone is in AP mode. Move and angle step affect the drone movement behaviour. See more in Control part. Detection object can be choosen out of 91 trained objects from COCO dataset ([https://tech.amikelive.com/node-718/what-object-categories-labels-are-in-coco-dataset/](https://tech.amikelive.com/node-718/what-object-categories-labels-are-in-coco-dataset/)). P, I and D values affect the object tracking behaviour. The stable values found out after experiments are:

- P = 0.3	
- I = 0
- D = 0.2

You can read more about PID controller here: [https://en.wikipedia.org/wiki/PID_controller](https://en.wikipedia.org/wiki/PID_controller)

The new settings take place only when the app is launched again.

![settings_1.png](https://github.com/eligosoftware/tello-controller-jetson/blob/main/readme_images/settings_1.png?raw=true)

![settings_2.png](https://github.com/eligosoftware/tello-controller-jetson/blob/main/readme_images/settings_2.png?raw=true)

## Control

Control window enables Tello drone control using pre-configured buttons

![control.png](https://github.com/eligosoftware/tello-controller-jetson/blob/main/readme_images/control.png?raw=true)

- Up  - move drone vertically up by move step value
- Down  - move drone vertically down by move step value
- Left  - turn drone left (counter-clockwise) by angle step value
- Right  - turn drone right (clockwise) by angle step value
- Takeoff  - take off the drone from ground

- Forward  - move drone forward by move step value
- Back  - move drone backward by move step value
- Move left  - move drone left by move step value
- Move right  - move drone right by move step value
- Land  - perform drone landing

## Video

[https://www.youtube.com/watch?v=6cWCYj8ceQ8](https://www.youtube.com/watch?v=6cWCYj8ceQ8)
