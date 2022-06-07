import tkinter as tk
import json
from tello import Tello
from os.path import exists
from PIL import ImageTk, Image
import cv2
import jetson.inference
import jetson.utils
import numpy as np
from tkinter import messagebox

settings_window_open=False
settingsWindow=None
tello_connected=False
default_tello_ip='192.168.10.1'
settings_data=None
drone=None
lmain = None
tello_status=None
settings_data=None
detection_object=None

 
pid=[0.3,0.2,0]
pError=0

move_step=0
angle_step=0

direction=0

root = None

def on_settings_closing():
	global root
	global settingsWindow
	global settings_window_open
	settings_window_open=False
	settingsWindow.destroy()
	
	
def read_settings():
	global settings_data
	if (exists('settings.json')):
		with open('settings.json') as json_file:
			settings_data = json.loads(json_file.read())
		return True
	else:
		return False

def write_settings(data):
	# Using a JSON string
	json_string = json.dumps(data)
	with open('settings.json', 'w') as outfile:
		outfile.write(json_string)

def connect_to_tello(tello_ip_value):
	
	global drone
	res = False
	try:
		if (tello_ip_value=="192.168.10.1"):
			drone=Tello()
		else:
			drone=Tello(tello_ip=tello_ip_value)

		res= drone.send_command("command")
		
		if res == True:
			drone.connect()
			drone.stream_on()
		
	except:
		
		drone = None
		res = False
	return res
		

def settings_on_save(data):
	global settingsWindow
	global settings_window_open
	data_to_save={}
	try:
		data_to_save["tello_ip"]=data["tello_ip"].get()
		data_to_save["object_to_track"]=data["detection_object"].get()
		
		if (data["p_value"].get().strip()==""):
			data_to_save["p"]=0.0
		else:
			data_to_save["p"]=float(data["p_value"].get().strip())
			
		if (data["i_value"].get().strip()==""):
			data_to_save["i"]=0.0
		else:
			data_to_save["i"]=float(data["i_value"].get().strip())
		
		if (data["d_value"].get().strip()==""):
			data_to_save["d"]=0.0
		else:
			data_to_save["d"]=float(data["d_value"].get().strip())
		
		if (data["move_step"].get().strip()==""):
			data_to_save["move_step"]=0
		else:
			data_to_save["move_step"]=int(data["move_step"].get().strip())
		
		if (data["angle_step"].get().strip()==""):
			data_to_save["angle_step"]=0
		else:
			data_to_save["angle_step"]=int(data["angle_step"].get().strip())
	
		write_settings(data_to_save)
		messagebox.showinfo('Jetson Tools', 'Settings saved!')
	
	except Exception as e:
		print(e)
		messagebox.showerror('Jetson Tools', 'Couldn\'t save settings')


def onControlPanel():
	global root
	
	# Toplevel object which will
	# be treated as a new window
	controlWindow = tk.Toplevel(root)

	# sets the title of the
	# Toplevel widget
	controlWindow.title("Control Panel")

	# sets the geometry of toplevel
	controlWindow.geometry("670x130")
	
	up_button = tk.Button(controlWindow, text="Up", command=lambda: send_command("up"))
	up_button.grid(column=1, row=0, sticky=tk.NW, padx=5, pady=5)
	
	forward_button = tk.Button(controlWindow, text="Forward", command=lambda: send_command("forward"))
	forward_button.grid(column=5, row=0, sticky=tk.NW, padx=5, pady=5)
	
	left_button = tk.Button(controlWindow, text="Left", command=lambda: send_command("left"))
	left_button.grid(column=0, row=1, sticky=tk.NW, padx=5, pady=5)
	
	to_button = tk.Button(controlWindow, text="Take off", command=lambda: send_command("takeoff"))
	to_button.grid(column=1, row=1, sticky=tk.NW, padx=5, pady=5)
	
	right_button = tk.Button(controlWindow, text="Right", command=lambda: send_command("right"))
	right_button.grid(column=2, row=1, sticky=tk.NW, padx=5, pady=5)
	
	change_camera_button = tk.Button(controlWindow, text="Change Camera", command=lambda: send_command("cc"))
	change_camera_button.grid(column=3, row=1, sticky=tk.NW, padx=5, pady=5)
	
	lw_button = tk.Button(controlWindow, text="Move left", command=lambda: send_command("move_left"))
	lw_button.grid(column=4, row=1, sticky=tk.NW, padx=5, pady=5)
	
	land_button = tk.Button(controlWindow, text="Land", command=lambda: send_command("land"))
	land_button.grid(column=5, row=1, sticky=tk.NW, padx=5, pady=5)
	
	rw_button = tk.Button(controlWindow, text="Move right", command=lambda: send_command("move_right"))
	rw_button.grid(column=6, row=1, sticky=tk.NW, padx=5, pady=5)
	
	down_button = tk.Button(controlWindow, text="Down", command=lambda: send_command("down"))
	down_button.grid(column=1, row=2, sticky=tk.NW, padx=5, pady=5)
	
	back_button = tk.Button(controlWindow, text="Back", command=lambda: send_command("back"))
	back_button.grid(column=5, row=2, sticky=tk.NW, padx=5, pady=5)
	
	
	img3 = tk.PhotoImage(file='./assets/logo3.png')
	controlWindow.tk.call('wm', 'iconphoto', controlWindow._w, img3)

# Settings window
def onSettings():
	global root
	global settings_data
	global default_tello_ip
	global default_tello_port
	global default_tello_udp_port
	global settingsWindow
	global settings_window_open
	
	if not settings_window_open:
		# Toplevel object which will
		# be treated as a new window
		settingsWindow = tk.Toplevel(root)

		# sets the title of the
		# Toplevel widget
		settingsWindow.title("Settings")

		# sets the geometry of toplevel
		settingsWindow.geometry("380x270")
	 
		# A Label widget to show in toplevel
		root.resizable(0, 0)

		# configure the grid
		#settingsWindow.columnconfigure(0, weight=1)
		#settingsWindow.columnconfigure(1, weight=1)

		# Tello IP
		tello_ip_label = tk.Label(settingsWindow, text="Tello IP:")
		tello_ip_label.grid(column=0, row=0, sticky=tk.NW, padx=5, pady=5)

		tello_ip_entry = tk.Entry(settingsWindow)
		tello_ip_entry.grid(column=1, row=0, sticky=tk.NW, padx=5, pady=5)
		
		
		detection_object_label = tk.Label(settingsWindow, text="Detection Object:")
		detection_object_label.grid(column=0, row=1, sticky=tk.NW, padx=5, pady=5)

		detection_object_entry = tk.Entry(settingsWindow)
		detection_object_entry.grid(column=1, row=1, sticky=tk.NW, padx=5, pady=5)
		
		
		p_value_label = tk.Label(settingsWindow, text="P Value:")
		p_value_label.grid(column=0, row=2, sticky=tk.NW, padx=5, pady=5)

		p_value_entry = tk.Entry(settingsWindow)
		p_value_entry.grid(column=1, row=2, sticky=tk.NW, padx=5, pady=5)
		

		i_value_label = tk.Label(settingsWindow, text="I Value:")
		i_value_label.grid(column=0, row=3, sticky=tk.NW, padx=5, pady=5)

		i_value_entry = tk.Entry(settingsWindow)
		i_value_entry.grid(column=1, row=3, sticky=tk.NW, padx=5, pady=5)
		

		d_value_label = tk.Label(settingsWindow, text="D Value:")
		d_value_label.grid(column=0, row=4, sticky=tk.NW, padx=5, pady=5)

		d_value_entry = tk.Entry(settingsWindow)
		d_value_entry.grid(column=1, row=4, sticky=tk.NW, padx=5, pady=5)	
		
		move_step_label = tk.Label(settingsWindow, text="Move step (sm)")
		move_step_label.grid(column=0, row=5, sticky=tk.NW, padx=5, pady=5)

		move_step_entry = tk.Entry(settingsWindow)
		move_step_entry.grid(column=1, row=5, sticky=tk.NW, padx=5, pady=5)
		
		
		angle_step_label = tk.Label(settingsWindow, text="Angle step (deg):")
		angle_step_label.grid(column=0, row=6, sticky=tk.NW, padx=5, pady=5)

		angle_step_entry = tk.Entry(settingsWindow)
		angle_step_entry.grid(column=1, row=6, sticky=tk.NW, padx=5, pady=5)
		
		restart_reminder_label = tk.Label(settingsWindow,text="Restart app after changes", fg='red')
		restart_reminder_label.grid(column=0, row=7, sticky=tk.NW, padx=5, pady=5)
		
		entry_fields={
			"tello_ip":tello_ip_entry,
			"detection_object":detection_object_entry,
			"p_value":p_value_entry,
			"i_value":i_value_entry,
			"d_value":d_value_entry,
			"move_step":move_step_entry,
			"angle_step":angle_step_entry
			
		}
		
		
		save_button = tk.Button(settingsWindow, text="Save", command=lambda: settings_on_save(entry_fields))
		save_button.grid(column=1, row=7, sticky=tk.NW, padx=5, pady=5)
		
		
		settings_read=read_settings()
		
		if not settings_read:
			# set default values
			tello_ip_entry.delete(0, tk.END)
			tello_ip_entry.insert(0, default_tello_ip)
			move_step_entry.delete(0, tk.END)
			move_step_entry.insert(0, 0)
			angle_step_entry.delete(0, tk.END)
			angle_step_entry.insert(0, 0)
		else:
			# set values from settings
			tello_ip_entry.delete(0, tk.END)
			tello_ip_entry.insert(0, settings_data["tello_ip"])
			detection_object_entry.delete(0, tk.END)
			detection_object_entry.insert(0, settings_data["object_to_track"])
			p_value_entry.delete(0, tk.END)
			p_value_entry.insert(0, settings_data["p"])
			i_value_entry.delete(0, tk.END)
			i_value_entry.insert(0, settings_data["i"])
			d_value_entry.delete(0, tk.END)
			d_value_entry.insert(0, settings_data["d"])
			move_step_entry.delete(0, tk.END)
			move_step_entry.insert(0, settings_data["move_step"])
			angle_step_entry.delete(0, tk.END)
			angle_step_entry.insert(0, settings_data["angle_step"])
		
		
		# set on close event
		settingsWindow.protocol("WM_DELETE_WINDOW", on_settings_closing)
		settingsWindow.grab_set() # open in modal mode
		img3 = tk.PhotoImage(file='./assets/logo3.png')
		settingsWindow.tk.call('wm', 'iconphoto', settingsWindow._w, img3)
		settings_window_open=True

# this function receives drone instance, information about center coordinates (x,y) of person, pid k values
# and the last error value, calculas yaw speed and new error, sends this yaw speed to drone (or stop movement
# signal, in case of missing detection), and returns new error value back to calling thread
def trackPerson(myDrone, center, w, pid,pError):
	global drone
	# calculate new PID error based on the center x value of detected Person and the center of image
	error=center[0] -w//2
	speed=pid[0]*error+pid[2]*(error-pError)
	speed=int(np.clip(speed,-100,100))

	# if there is a detection, value of center is different from 0
	if center[0]==0:
		error=0
	send_command_js(speed)
	# return error for the next iteration
	return error

def send_command_js(yaw):
    global drone
    drone.joystick_control(0,0,0,0)
    drone.joystick_control(0,0,yaw,0)

def send_command(command):
	global drone
	global move_step
	global angle_step
	
	if (command=="takeoff"):
		drone.takeoff()
	elif (command=="land"):
		drone.land()
	elif (command=="up"):
		drone.move_up(move_step)
	elif (command=="down"):
		drone.move_down(move_step)
	elif (command=="left"):
		drone.rotate_counterclockwise(angle_step)
	elif (command=="right"):
		drone.rotate_clockwise(angle_step)
	elif (command=="cc"):
		switch_camera()
	elif (command=="move_left"):
		drone.move_left(move_step)
	elif (command=="move_right"):
		drone.move_right(move_step)
	elif (command=="forward"):
		drone.move_forward(move_step)
	elif (command=="back"):
		drone.move_backward(move_step)

def switch_camera():
    global direction
    global drone
    direction+=1 
    drone.send_command("downvision "+str(direction%2))

# main window function
def main():
	global pid
	global lmain
	global root
	global tello_status
	global drone
	global detection_object
	global move_step
	global angle_step
	
	try:
		settings_read=read_settings()
		if settings_read:
			res = connect_to_tello(settings_data["tello_ip"])
			detection_object = settings_data["object_to_track"]
			pid.append(settings_data["p"])
			pid.append(settings_data["i"])
			pid.append(settings_data["d"])
			move_step = settings_data["move_step"]
			angle_step = settings_data["angle_step"]
	except Exception as e:
		print(e)
		res=False
			
	connection_screen.destroy()
	
	root = tk.Tk()
	root.title('Jetson Tools')

	root.geometry('960x720')
	
	menubar = tk.Menu(root)

	filemenu = tk.Menu(menubar)
	filemenu.add_command(label="Control panel",command=onControlPanel)
	filemenu.add_command(label="Settings",command=onSettings)
	filemenu.add_command(label="Exit", command=root.destroy)

	
	menubar.add_cascade(label="File", menu=filemenu)
	
	root.config(menu=menubar)
	
	# Tello Status
	tello_status = tk.Label(root, fg="green", text="")
	tello_status.grid(column=0, row=0, sticky=tk.NW, padx=5, pady=5)
		
	lmain = tk.Label(root)
	lmain.grid(row=1, column=0, sticky=tk.NW, padx=5, pady=5)
	
	if not settings_read:
		tello_status.config(fg="red")
		tello_status['text']="Check settings"
	else:
		if res == False:
			tello_status.config(fg="red")
			tello_status['text']="Tello is not connected"
		else:
			
			tello_status.config(fg="green")
			tello_status['text']="Tello connected"
			video_stream()
	
	
	
	img2 = tk.PhotoImage(file='./assets/logo2.png')
	root.tk.call('wm', 'iconphoto', root._w, img2)
	
	root.mainloop()


# function for video streaming
def video_stream():
	global pError, pError_fb
	global lmain
	global pid
	global pError
	global drone
	
	
	if drone.read_frame() is not None:
		frame = drone.read_frame()
		#print(frame.shape)
		cuda_image=jetson.utils.cudaFromNumpy(frame)
		
		objectsListC = []
		objectsArea = []
		detections = net.Detect(cuda_image)
		
		for detection in detections:
			cl_name=net.GetClassDesc(detection.ClassID)
			center=detection.Center
			
			if (cl_name==detection_object):
				objectsListC.append(detection.Center)
				objectsArea.append(detection.Area)
		
		if len(objectsArea) != 0:
			i = objectsArea.index(max(objectsArea))
			pError = trackPerson(drone, objectsListC[i],720, pid, pError)
		else:
			pError=0
			drone.joystick_control(0,0,0,0)
		
		frame_2=jetson.utils.cudaToNumpy(cuda_image)
		cv2image = cv2.cvtColor(frame_2, cv2.COLOR_BGR2RGBA)
		img = Image.fromarray(cv2image)
		imgtk = ImageTk.PhotoImage(image=img)
		lmain.imgtk = imgtk
		lmain.configure(image=imgtk)
	lmain.after(1, video_stream) 

connection_screen = tk.Tk()

connection_screen.title('Jetson Tools')
   
# Adjust size
connection_screen.geometry("180x20")


# Set Label
connection_label = tk.Label(connection_screen,text="Connecting to Tello..."  ,font=18)
connection_label.pack()


img = tk.PhotoImage(file='./assets/logo.png')
connection_screen.tk.call('wm', 'iconphoto', connection_screen._w, img)

net = jetson.inference.detectNet("ssd-mobilenet-v2")
# Set Interval
connection_screen.after(1000,main)


 
# Execute tkinter
tk.mainloop()



