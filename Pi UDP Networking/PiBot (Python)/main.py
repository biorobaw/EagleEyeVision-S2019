import time
import signal
import struct
from PiClient import *

IP = "192.168.50.118"
PORT = 5555
ENDIAN = 'BIG'
ID = 3


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
	msg = struct.pack(('>' if ENDIAN == 'BIG' else '<') + 'ifc?5s', num1, num2, ch, bol, st)

	network.sendMessage(msg)
	time.sleep(1)

# Ensure proper exiting
ctrlC(None, None)