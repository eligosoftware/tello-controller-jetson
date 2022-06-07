# Tello Control App with GUI

This app is designed to control Tello drone from PC / laptop over WiFi connection and view the camera video. It can be run both on Linux and Windows computers.

##  Installation
Before running ensure that the following python libraries are present in your system:
- tello-python
- Tkinter
- opencv
- pillow

Tello-python installation (Windows)

```bash
>> git clone https://github.com/harleylara/tello-python.git
>> cd tello-python
>> python setup.py install `
```
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

#### !!Important!!
On Windows PCs check firewall settings for TCP and UDP port blocking.

![firewall_settings_3.png](https://github.com/eligosoftware/tello-controller/blob/main/readme_images/firewall_settings_3.png?raw=true)

![firewall_settings_1.png](https://github.com/eligosoftware/tello-controller/blob/main/readme_images/firewall_settings_1.png?raw=true)

![firewall_settings_2.png](https://github.com/eligosoftware/tello-controller/blob/main/readme_images/firewall_settings_2.png?raw=true)

## Running

```bash
git clone https://github.com/eligosoftware/tello-controller.git
cd tello-controller
python main.py
```

## Settings

In the Settings menu it is possible to set the drone IP address, movement and angle step values. The standard IP is 192.168.10.1 for the station mode. User should change the IP if the drone is in AP mode. Move and angle step affect the drone movement behaviour. See more in Control part. The new settings take place only when the app is launched again.

![settings_1.png](https://github.com/eligosoftware/tello-controller/blob/main/readme_images/settings_1.png?raw=true)

![settings_2.png](https://github.com/eligosoftware/tello-controller/blob/main/readme_images/settings_2.png?raw=true)

## Control

Control window enables Tello drone control using pre-configured buttons

![control.png](https://github.com/eligosoftware/tello-controller/blob/main/readme_images/control.png?raw=true)

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