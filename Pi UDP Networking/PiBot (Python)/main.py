import time
import signal
import struct

import RPi.GPIO as GPIO
import servos
import encoders
import subprocess
import camera
#import sensors

import cv2
import numpy as np
import socket
import sys
import pickle

from PiClient import *

#IP = "192.168.50.118" default IP
#IP = "10.226.9.89" #Bryce laptop in lab
IP = "192.168.0.8" #Bryce desktop at home
#IP = "192.168.0.6" #Bryce laptop at home
PORT = 5555
ENDIAN = 'BIG'
ID = 3

serv = servos.Servos()
enc = encoders.Encoders()
cam = camera.Camera()
#sens = sensors.Sensors()

colorList = []
strColList = []

pink = {'minH': 152, 'minS': 120, 'minV': 85, 'maxH': 180, 'maxS': 255, 'maxV': 255, 'name': 'pink'}
colorList.append(pink)
strColList.append("pink")

yellow = {'minH': 17, 'minS': 235, 'minV': 129, 'maxH': 35, 'maxS': 255, 'maxV': 207, 'name': 'yellow'}
colorList.append(yellow)
strColList.append("yellow")

green = {'minH': 29, 'minS': 209, 'minV': 79, 'maxH': 51, 'maxS': 255, 'maxV': 208, 'name': 'green'}
colorList.append(green)
strColList.append("green")

blue = {'minH': 57, 'minS': 44, 'minV': 77, 'maxH': 109, 'maxS': 160, 'maxV': 171, 'name': 'blue'}
colorList.append(blue)
strColList.append("blue")

# Note: these callback functions don't run on the main thread
def onStatusChanged(command):
	print('USER NTWK CMD ' + command.name)


def onMessageReceived(data):
	print('USER MSG RECV ', end='')
	# for c in data:
	# 	print(c, end=', ')
	# print()

	# Placeholder random logic, replace everything below with something more useful
	results = struct.unpack_from(('>' if ENDIAN == 'BIG' else '<') + 'ifc?5s', data, 0)
	num1 = results[0]
	num2 = results[1]
	ch = results[2]
	bol = results[3]
	st = results[4]
	
	print(str(num1) + ", " + str(num2) + ", " + str(ch) + ", " + str(bol) + ", " + str(st))
	# print(str(type(num1)) + ", " + str(type(num2)) + ", " + str(type(ch)) + ", " + str(type(bol)) + ", " + str(type(st)))
	ch = ch.decode('UTF-8')
	st = st.decode('UTF-8')
	st = st.replace('\x00','')
	print(ch)
	print(st)
	if ch == "g":
            serv.setSpeeds(1,1)
            time.sleep(1)
            serv.stopServos()
	#elif ch == "b":
            #b = subprocess.Popen(['python', 'blob.py'])
            #time.sleep(30)
            #b.terminate()
	elif ch == "c":
            for color in colorList:
                for strCol in strColList:
                    if st == strCol:
                        stats = cam.getBlobStatsColored(color)
                        if stats['totalArea'] == 0:
                            print("looking for")
                            print(color)
                            serv.setSpeeds(0.5,0)
                            time.sleep(3)
                            serv.stopServos()
                            print("not found")
                        elif stats['totalArea'] > 500 and stats['totalArea'] < 20000:
                            print("found")
                            print(color)
                            print("approaching")
                            serv.setSpeeds(0.5,0.5)
                        elif stats['totalArea'] >= 20000:
                            print("found")
                            print(color)
                            print("stopping")
                            serv.stopServos()
                        else:
                            serv.stopServos()
                    else:
                        print("")
                        #print("string provide does not match current color in colorlist")
                serv.stopServos()
	#elif ch == "v":
            #capture = cv2.VideoCapture(0)
            #clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            #clientsocket.connect((IP, PORT))
            #while True:
                #serialize frame
                #data = pickle.dumps(frame)
                #send message length first
                #message_size = struct.pack("L", len(data))
                #then data
                #client_sock.sendall(message_size + data)
                #time.sleep(30)
                #break

def ctrlC(signum, frame):
	global onMessageReceived
	global onStatusChanged
	network.onMessageReceived -= onMessageReceived
	network.onStatusChanged -= onStatusChanged
	network.stop()
	exit()


signal.signal(signal.SIGINT, ctrlC)

print("Press Ctrl+C to exit")

network = PiClient(IP, PORT, ENDIAN, ID)
network.onMessageReceived += onMessageReceived
network.onStatusChanged += onStatusChanged
network.start()

print('Wait until server is online...')
network.waitUntilOnline()
print('Server is online!')

# Placeholder random logic, replace everything below with something more useful
for i in range(100):
	num1 = 43
	num2 = 7.98
	ch = b'z'
	bol = False
	st = str.encode("howdy")
	#msg = struct.pack(('>' if ENDIAN == 'BIG' else '<') + 'ifc?5s', num1, num2, ch, bol, st)

	#network.sendMessage(msg)
	time.sleep(1)

# Ensure proper exiting
ctrlC(None, None)