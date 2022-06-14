import tkinter as tk
import json
from tello import Tello
from os.path import exists
from os import makedirs
from PIL import ImageTk, Image
import cv2
import jetson.inference
import jetson.utils
import numpy as np
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime
import threading
from time import sleep
import pyttsx3
import random
task_network="Detection"
from segnet_utils import *
from depthnet_utils import depthBuffers


settings_track_objects_value=None
with_detections_value = None
frame_resolution=None

last_frame=None
font=None

recording=False
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
recording_label=None
recording_label_text = None
track_objects=False

net = None
cl_net = None
path_pictures="./media/pictures/"
path_videos="./media/videos/"


pid=[]
pError=0

move_step=0
angle_step=0

direction=0

root = None

tts_engine=pyttsx3.init()
tts_engine.setProperty('rate',120)
tts_engine.setProperty('voice', 'english_rp+f3')

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
	global frame_resolution
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
			frame_resolution=(960,720)
			drone.send_command("downvision 0")
		
	except:
		
		drone = None
		res = False
	return res
		

def settings_on_save(data):
	global settingsWindow
	global settings_window_open
	global settings_track_objects_value
	data_to_save={}
	try:
		data_to_save["tello_ip"]=data["tello_ip"].get()
		data_to_save["object_to_track"]=data["detection_object"].get()
		data_to_save["custom_model_path"]=data["custom_model_path"].get()
		
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

		data_to_save["tasks_select"]=data["tasks_select"].get().strip()
			
		#print(settings_track_objects_value.get())
		if settings_track_objects_value.get()==1:
			data_to_save["track_objects"]=True
		else:
			data_to_save["track_objects"]=False
			
		write_settings(data_to_save)
		messagebox.showinfo('Jetson Tools', 'Settings saved!')
	
	except Exception as e:
		print(e)
		messagebox.showerror('Jetson Tools', 'Couldn\'t save settings')


def onControlPanel():
	global root
	global recording_label
	global recording_label_text
	global with_detections_value
	
	recording_label_text = tk.StringVar()
	
	with_detections_value = tk.IntVar()
	
	# Toplevel object which will
	# be treated as a new window
	controlWindow = tk.Toplevel(root)

	# sets the title of the
	# Toplevel widget
	controlWindow.title("Control Panel")

	# sets the geometry of toplevel
	controlWindow.geometry("800x270")
	
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
	
	#################################
	
	flip_forward_button = tk.Button(controlWindow, text="Flip Forward", command=lambda: send_command("flip_f"))
	flip_forward_button.grid(column=1, row=3, sticky=tk.NW, padx=5, pady=5)
	
	flip_left_button = tk.Button(controlWindow, text="Flip left", command=lambda: send_command("flip_l"))
	flip_left_button.grid(column=0, row=4, sticky=tk.NW, padx=5, pady=5)
	
	flip_right_button = tk.Button(controlWindow, text="Flip right", command=lambda: send_command("flip_r"))
	flip_right_button.grid(column=2, row=4, sticky=tk.NW, padx=5, pady=5)
		
	flip_backward_button = tk.Button(controlWindow, text="Flip Backward", command=lambda: send_command("flip_b"))
	flip_backward_button.grid(column=1, row=5, sticky=tk.NW, padx=5, pady=5)
	
	################################
	
	take_picture_button = tk.Button(controlWindow, text="Take Picture", command=lambda: send_command("take_pic"))
	take_picture_button.grid(column=3, row=3, sticky=tk.NW, padx=5, pady=5)
	
	start_video_button = tk.Button(controlWindow, text="Start Video", command=lambda: send_command("video_start"))
	start_video_button.grid(column=3, row=4, sticky=tk.NW, padx=5, pady=5)
	
	with_detections_entry = tk.Checkbutton(controlWindow,text="with Overlay",variable=with_detections_value,onvalue=1, offvalue=0)
	with_detections_entry.grid(column=4, row=4, sticky=tk.NW, padx=5, pady=5)
		
	stop_video_button = tk.Button(controlWindow, text="Stop Video", command=lambda: send_command("video_stop"))
	stop_video_button.grid(column=3, row=5, sticky=tk.NW, padx=5, pady=5)
	
	#################################
	
	recording_label = tk.Label(controlWindow, fg='red', textvariable=recording_label_text)
	recording_label.grid(column=4, row=5, sticky=tk.NW, padx=5, pady=5)
	
	
	###################################
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
	global settings_track_objects_value
	
	tasks_list = [
		"Detection",
		"Classification",
		"Segmentation",
		"PoseNet-Body",
		"PoseNet-Hand",
		"MonoDepth"
	]
	
	variable_task = tk.StringVar()
	variable_task.set(tasks_list[0])
	
	settings_track_objects_value = tk.IntVar()
	
	if not settings_window_open:
		# Toplevel object which will
		# be treated as a new window
		settingsWindow = tk.Toplevel(root)

		# sets the title of the
		# Toplevel widget
		settingsWindow.title("Settings")

		# sets the geometry of toplevel
		settingsWindow.geometry("500x400")
	 
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
		
		custom_model_path_label = tk.Label(settingsWindow, text="Custom Model path:")
		custom_model_path_label.grid(column=0, row=7, sticky=tk.NW, padx=5, pady=5)

		custom_model_path_entry = tk.Entry(settingsWindow)
		custom_model_path_entry.grid(column=1, row=7, sticky=tk.NW, padx=5, pady=5)

		track_object_entry = tk.Checkbutton(settingsWindow,text="Track Objects",variable=settings_track_objects_value,onvalue=1, offvalue=0)
		track_object_entry.grid(column=0, row=8, sticky=tk.NW, padx=5, pady=5)
		
		tasks_select_label = tk.Label(settingsWindow, text="Task:")
		tasks_select_label.grid(column=0, row=9, sticky=tk.NW, padx=5, pady=5)
		
		tasks_select_entry=tk.OptionMenu(settingsWindow,variable_task, *tasks_list)
		tasks_select_entry.config(width=15, font=('Helvetica', 12))
		tasks_select_entry.grid(column=1, row=9, sticky=tk.NW, padx=5, pady=5)
		
		entry_fields={
			"tello_ip":tello_ip_entry,
			"detection_object":detection_object_entry,
			"p_value":p_value_entry,
			"i_value":i_value_entry,
			"d_value":d_value_entry,
			"move_step":move_step_entry,
			"angle_step":angle_step_entry,
			"custom_model_path":custom_model_path_entry,
			"tasks_select":variable_task
			
		}
		custom_model_path_button=tk.Button(settingsWindow,text="Choose Dialog", command =lambda: pick_Model(entry_fields))
		custom_model_path_button.grid(column=2, row=7, sticky=tk.NW, padx=5, pady=5)
		
		restart_reminder_label = tk.Label(settingsWindow,text="Restart app after changes", fg='red')
		restart_reminder_label.grid(column=0, row=10, sticky=tk.NW, padx=5, pady=5)
		
		
		
		
		save_button = tk.Button(settingsWindow, text="Save", command=lambda: settings_on_save(entry_fields))
		save_button.grid(column=1, row=10, sticky=tk.NW, padx=5, pady=5)
		
		
		settings_read=read_settings()
		
		if not settings_read:
			# set default values
			tello_ip_entry.delete(0, tk.END)
			tello_ip_entry.insert(0, default_tello_ip)
			detection_object_entry.delete(0, tk.END)
			detection_object_entry.insert(0, "person")
			move_step_entry.delete(0, tk.END)
			move_step_entry.insert(0, 30)
			angle_step_entry.delete(0, tk.END)
			angle_step_entry.insert(0, 40)
			custom_model_path_entry.delete(0, tk.END)
			custom_model_path_entry.insert(0, "")
			
			p_value_entry.delete(0, tk.END)
			p_value_entry.insert(0,0.3)
			d_value_entry.delete(0, tk.END)
			d_value_entry.insert(0,0.2)
		else:
			# set values from settings
			tello_ip_entry.delete(0, tk.END)
			if "tello_ip" in settings_data:
				tello_ip_entry.insert(0, settings_data["tello_ip"])
			else:
				tello_ip_entry.insert(0, default_tello_ip)
				
			detection_object_entry.delete(0, tk.END)
			if "object_to_track" in settings_data:
				detection_object_entry.insert(0, settings_data["object_to_track"])
			else:
				detection_object_entry.insert(0, "person")
				
			p_value_entry.delete(0, tk.END)
			if "p_value_entry" in settings_data:
				p_value_entry.insert(0, settings_data["p"])
			else:
				p_value_entry.insert(0,0.3)
				
			i_value_entry.delete(0, tk.END)
			if "i_value_entry" in settings_data:
				i_value_entry.insert(0, settings_data["i"])
			else:
				i_value_entry.insert(0,0)
			d_value_entry.delete(0, tk.END)
			if "d_value_entry" in settings_data:
				d_value_entry.insert(0, settings_data["d"])
			else:
				d_value_entry.insert(0,0.2)
			move_step_entry.delete(0, tk.END)
			if "move_step" in settings_data:
				move_step_entry.insert(0, settings_data["move_step"])
			else:
				move_step_entry.insert(0, 30)
			angle_step_entry.delete(0, tk.END)
			if "angle_step" in settings_data:
				angle_step_entry.insert(0, settings_data["angle_step"])
			else:
				angle_step_entry.insert(0, 40)
			custom_model_path_entry.delete(0, tk.END)
			if "custom_model_path" in settings_data:
				custom_model_path_entry.insert(0, settings_data["custom_model_path"])
			else:
				custom_model_path_entry.insert(0, "")
			
			if "tasks_select" in settings_data:
				variable_task.set(settings_data["tasks_select"])
			
			
			
			if "track_objects" in settings_data:
				if settings_data["track_objects"]:
					track_object_entry.select()
		
		# set on close event
		settingsWindow.protocol("WM_DELETE_WINDOW", on_settings_closing)
		settingsWindow.grab_set() # open in modal mode
		img3 = tk.PhotoImage(file='./assets/logo3.png')
		settingsWindow.tk.call('wm', 'iconphoto', settingsWindow._w, img3)
		settings_window_open=True

def create_media_folder():
	global path_pictures
	global path_videos
	
	if not exists(path_pictures):
		makedirs(path_pictures)
	
	if not exists(path_videos):
		makedirs(path_videos)
		
def pick_Model(entry_fields):
	folder_selected = filedialog.askdirectory()
	entry_fields["custom_model_path"].delete(0, tk.END)
	entry_fields["custom_model_path"].insert(0, folder_selected)

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
		speak("Taking off")
		drone.takeoff()
	elif (command=="land"):
		speak("Landing")
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
	elif (command=="flip_f"):
		drone.flip("forward")
	elif (command=="flip_l"):
		drone.flip("left")
	elif (command=="flip_r"):
		drone.flip("right")
	elif (command=="flip_b"):
		drone.flip("backward")
	elif (command=="take_pic"):
		take_picture()
	elif (command=="video_start"):
		start_video()
	elif (command=="video_stop"):
		stop_video()

def speak(text):
	global tts_engine
	tts_engine.say(text)
	tts_engine.runAndWait()
	
def take_picture():
	global drone
	global path_pictures
	global with_detections_value
	global last_frame
	
	if with_detections_value.get() == 1:
		while last_frame is not None:
			
			write_image(path_pictures,last_frame)
			messagebox.showinfo('Jetson Tools', 'Took image!')
			break
	else:
		while drone.read_frame() is not None:
			
			write_image(path_pictures,drone.read_frame())
			messagebox.showinfo('Jetson Tools', 'Took image!')
			break

def start_video():
	global recording
	global recording_label_text
	recording_label_text.set("Recording...")
	recording=True
	threading.Thread(target=record_frames).start()

def record_frames():
	global path_videos
	global recording
	global with_detections_value
	global last_frame
	global frame_resolution
	
	now = datetime.now() # current date and time
	video_file='video_'+now.strftime("%Y%d%m%H%M%S")+'.avi'
	if with_detections_value.get() == 1:
		w,h,c=last_frame.shape
		
		out = cv2.VideoWriter(path_videos+video_file,cv2.VideoWriter_fourcc(*'DIVX'),30,(h,w))
	else:
		out = cv2.VideoWriter(path_videos+video_file,cv2.VideoWriter_fourcc(*'DIVX'),30,frame_resolution)
	if with_detections_value.get() == 0:
		
		while drone.read_frame() is not None:
			frame=drone.read_frame()
			out.write(frame)
			sleep(0.01)
			if not recording:
				out.release()
				break
	else:
		while last_frame is not None:
			out.write(last_frame)
			sleep(0.01)
			if not recording:
				out.release()
				break

def stop_video():
	global recording
	global recording_label_text
	recording=False
	recording_label_text.set("")
	
def write_image(image_path, image):
	now = datetime.now() # current date and time
	image_file='image_'+now.strftime("%Y%d%m%H%M%S")+'.jpg'
	cv2.imwrite(image_path+image_file,image)


def switch_camera():
	global direction
	global drone
	global frame_resolution
	direction+=1
	if direction%2 ==0:
		frame_resolution=(960,720)
	else:
		frame_resolution=(320,240)
	drone.send_command("downvision "+str(direction%2))

# main window function
def get_random_phrase(found_object):
	phrases=[
		f"I think, I've found {found_object}",
		f"Maybe, this is {found_object}",
		f"Ooh, looks like this is {found_object}",
		f"Do you show me {found_object}?",
		f"Am I wrong or this is {found_object}?",
	]
	
	return random.choice(phrases)
	
def classify():
	global cl_net
	
	while drone.read_frame() is not None:
		frame=drone.read_frame()
		cuda_image=jetson.utils.cudaFromNumpy(frame)
		
		
		try:
			class_id, confidence = cl_net.Classify(cuda_image)
			# find the object description
			class_desc = cl_net.GetClassDesc(class_id)
			
			speak(get_random_phrase(class_desc))
		except:
			speak("Unfortunately, I couldn't find anything!")
		break


def main():
	global pid
	global lmain
	global root
	global tello_status
	global drone
	global detection_object
	global move_step
	global angle_step
	global net
	global track_objects
	global cl_net
	global task_network
	global font
	
	
	model_path=""
	try:
		settings_read=read_settings()
		if settings_read:
			#print(settings_data)
			res = connect_to_tello(settings_data["tello_ip"])
			detection_object = settings_data["object_to_track"]
			pid.append(settings_data["p"])
			pid.append(settings_data["i"])
			pid.append(settings_data["d"])
			move_step = settings_data["move_step"]
			angle_step = settings_data["angle_step"]
			if "custom_model_path" in settings_data:
				model_path = settings_data["custom_model_path"]
			else:
				model_path=""				
			
			if "tasks_select" in settings_data:
				task_network = settings_data["tasks_select"]
			else:
				task_network="Detection"
			
			track_objects=settings_data["track_objects"]
			if not task_network=="Detection":
				track_objects=False
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
	
	tasksmenu = tk.Menu(menubar)
	tasksmenu.add_command(label="Classify",command=classify)

	
	menubar.add_cascade(label="Tasks", menu=tasksmenu)
	
	
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
			
			if task_network=="Detection":
				if model_path=="":
					net = jetson.inference.detectNet("ssd-mobilenet-v2")
				else:
					net = jetson.inference.detectNet(argv=['--model='+model_path+'/ssd-mobilenet.onnx','--labels='+model_path+'/labels.txt', '--input-blob=input_0', '--output-cvg=scores','--output-bbox=boxes'])
			
			elif task_network=="Segmentation":
				alpha=150
				net = jetson.inference.segNet("fcn-resnet18-voc")
				net.SetOverlayAlpha(alpha)
			elif task_network=="PoseNet-Body":
				net = jetson.inference.poseNet("resnet18-body")
			elif task_network=="PoseNet-Hand":
				net = jetson.inference.poseNet("resnet18-hand")
			elif task_network=="MonoDepth":
				net = jetson.inference.depthNet("fcn-mobilenet")
			elif task_network=="Classification":
				net = jetson.inference.imageNet("googlenet")
				font = jetson.utils.cudaFont()
			
			video_stream()
	
	cl_net = jetson.inference.imageNet("googlenet")
	
	img2 = tk.PhotoImage(file='./assets/logo2.png')
	root.tk.call('wm', 'iconphoto', root._w, img2)
	
	create_media_folder()
	root.mainloop()


# function for video streaming
def video_stream():
	global pError, pError_fb
	global lmain
	global pid
	global pError
	global drone
	global net
	global track_objects
	global last_frame
	global task_network
	global font
	
	if drone.read_frame() is not None:
		frame = drone.read_frame()
		#print(frame.shape)
		cuda_image=jetson.utils.cudaFromNumpy(frame)
		
		if task_network=="Detection":
			detections = net.Detect(cuda_image)
			if track_objects:
				objectsListC = []
				objectsArea = []
				
				
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
					
		elif task_network=="Segmentation":
			
			filter_mode="linear"
			visualize="overlay,mask"
			stats=False			
			
			# create buffer manager
			buffers = segmentationBuffers(net, stats,visualize)
			
			# allocate buffers for this size image
			buffers.Alloc(cuda_image.shape, cuda_image.format)
			
			
			net.Process(cuda_image)
			
			# generate the overlay
			if buffers.overlay:
				net.Overlay(buffers.overlay, filter_mode=filter_mode)

			# generate the mask
			if buffers.mask:
				net.Mask(buffers.mask, filter_mode=filter_mode)

			# composite the images
			if buffers.composite:
				jetson.utils.cudaOverlay(buffers.overlay, buffers.composite, 0, 0)
				jetson.utils.cudaOverlay(buffers.mask, buffers.composite, buffers.overlay.width, 0)
			
			cuda_image=buffers.output
			
		elif task_network=="PoseNet-Body" or task_network=="PoseNet-Hand":
			
						
			
			net.Process(cuda_image)
			
		
		elif task_network=="Segmentation":
			
			filter_mode="linear"
			visualize="overlay,mask"
			stats=False			
			
			# create buffer manager
			buffers = segmentationBuffers(net, stats,visualize)
			
			# allocate buffers for this size image
			buffers.Alloc(cuda_image.shape, cuda_image.format)
			
			
			net.Process(cuda_image)
			
			# generate the overlay
			if buffers.overlay:
				net.Overlay(buffers.overlay, filter_mode=filter_mode)

			# generate the mask
			if buffers.mask:
				net.Mask(buffers.mask, filter_mode=filter_mode)

			# composite the images
			if buffers.composite:
				jetson.utils.cudaOverlay(buffers.overlay, buffers.composite, 0, 0)
				jetson.utils.cudaOverlay(buffers.mask, buffers.composite, buffers.overlay.width, 0)
			
			cuda_image=buffers.output
			
		elif task_network=="MonoDepth":
			visualize="input,depth"
			buffers = depthBuffers(visualize)
			# allocate buffers for this size image
			buffers.Alloc(cuda_image.shape, cuda_image.format)
			
			
			net.Process(cuda_image,buffers.depth, "viridis-inverted", "linear")
			
			 # composite the images
			if buffers.use_input:
				jetson.utils.cudaOverlay(cuda_image, buffers.composite, 0, 0)
				
			if buffers.use_depth:
				jetson.utils.cudaOverlay(buffers.depth, buffers.composite, cuda_image.width if buffers.use_input else 0, 0)
			
			cuda_image=buffers.composite
		
		elif task_network=="Classification":
			# classify the image
			class_id, confidence = net.Classify(cuda_image)

			# find the object description
			class_desc = net.GetClassDesc(class_id)
			
			font.OverlayText(cuda_image, cuda_image.width, cuda_image.height, "{:05.2f}% {:s}".format(confidence * 100, class_desc), 5, 5, font.White, font.Gray40)
			
		frame_2=jetson.utils.cudaToNumpy(cuda_image)
		last_frame=frame_2
		
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


# Set Interval
connection_screen.after(1000,main)


 
# Execute tkinter
tk.mainloop()
