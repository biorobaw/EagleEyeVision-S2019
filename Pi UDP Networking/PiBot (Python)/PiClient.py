import time
import struct
import random
import math
from enum import Enum
from socket import *
from Event import Event
from threading import Thread


class PiNetworkCommand(Enum):
	HEARTBEAT = 0
	SHUTDOWN = 1
	ACK = 2
	USER_MESSAGE = 3


class PiConnectionStatus(Enum):
	OFFLINE = 1
	ONLINE = 2
	TIMEOUT = 3


class PiPacketInfo:
	def __init__(self, msg, sendTime, packetNum):
		self.msg = msg
		self.sendTime = sendTime
		self.packetNum = packetNum


class PiClient:
	"""Sends and receives UDP packets from a server"""

	_MAX_BUFFER_SIZE = 1024  # In bytes

	_HEARTBEAT_CHECK_RATE = 1.0  # How often to check for heartbeats, in s.
	_HEARTBEAT_SEND_RATE = 4.0  # How often to SEND a heartbeat, in s.
	_HEARTBEAT_TIMEOUT = 5.0  # Maximum allowed time between RECEIVED heartbeats, in s.

	_ACK_CHECK_RATE = 0.01  # How often to check for timed out packets, in s
	_ACK_TIMEOUT = 0.05  # Maximum allowed time for a RECEIVED packet acknowledgement, in s

	_DEBUG = True

	def __init__(self, serverIP, serverPort, endian, botID):
		"""Constructs the Pi client"""

		self._serverIP = serverIP
		self._serverPort = serverPort
		self._endian = endian
		self._botID = botID
		self._running = False
		self._helperRunning = False
		self._heartbeatReceiveTime = 0
		self._serverStatus = PiConnectionStatus.OFFLINE
		self._clientSocket = None
		self._thread = None
		self._helperThread = None
		self._sentPackets = []
		self._nextPacketNum = 0
		self._startTime = 0

		self.onMessageReceived = Event()
		self.onStatusChanged = Event()

	def start(self):
		"""Sets up the client and listens for packets on a new thread.

		Call this method before doing anything else."""

		if self._clientSocket is not None:
			raise RuntimeError('PiNetwork already started')

		self._clientSocket = socket(AF_INET, SOCK_DGRAM)
		self._clientSocket.settimeout(1)

		self._startTime = time.time()

		self._thread = Thread(target=self._run, name='main thread', args=())
		self._thread.daemon = True
		self._thread.start()

		self._helperThread = Thread(target=self._runHelper, name='helper thread', args=())
		self._helperThread.daemon = True
		self._helperThread.start()

	def stop(self):
		"""Stops listening for packets and closes the client.

		Call this method when you intend to never use the client again."""

		if self._clientSocket is None:
			raise RuntimeError('PiNetwork not running')

		print('Stopping client...')

		self._sendMessage(PiNetworkCommand.SHUTDOWN)

		self._running = False
		self._helperRunning = False

		self._thread.join()
		self._helperThread.join()

		self._clientSocket.close()
		self._clientSocket = None

		print('Client stopped.')

	def waitUntilOnline(self):
		"""Waits until the server's status is online"""

		while self._serverStatus != PiConnectionStatus.ONLINE:
			time.sleep(.01)

	def sendMessage(self, data):
		"""Sends a message to the server"""

		self._sendMessage(PiNetworkCommand.USER_MESSAGE, data)

	def _sendMessage(self, command, data=None):
		"""Sends a message to the server"""

		packetNum = self._nextPacketNum
		currentTime = time.time()
		msg = struct.pack(('>' if self._endian == 'BIG' else '<') + 'iii', packetNum, self._botID, command.value)

		if data is not None:
			msg += data

		if command == PiNetworkCommand.USER_MESSAGE:
			if self._serverStatus == PiConnectionStatus.TIMEOUT:
				print('Attempting to send message to timed out server!')
			elif self._serverStatus == PiConnectionStatus.OFFLINE:
				print('Attempting to send message to disconnected server!')

			info = PiPacketInfo(msg, currentTime, packetNum)
			self._sentPackets.append(info)

		if PiClient._DEBUG:
			print('<- {:15}\tMy ID:\t{}\tTime:\t{:8.3f} s'.format(command.name, packetNum, currentTime - self._startTime))

		self._nextPacketNum += 1

		self._clientSocket.sendto(msg, (self._serverIP, self._serverPort))

	def _setServerStatus(self, status):
		"""Stores the status of the server and raises the status changed event"""
		if self._serverStatus == status:
			return

		self._serverStatus = status

		self.onStatusChanged(status)

	def _run(self):
		"""Listens for UDP packets."""

		if self._running:
			raise RuntimeError('PiNetwork already running')

		self._running = True
		while self._running:
			try:
				data, addr = self._clientSocket.recvfrom(PiClient._MAX_BUFFER_SIZE)
				self._processPacket(data)
			except timeout:
				continue

	def _runHelper(self):
		"""Checks for heartbeats from the server, sends heartbeats to the server, and checks for timed out packets"""
		if self._helperRunning:
			raise RuntimeError('PiNetwork already running')

		self._helperRunning = True
		heartbeatCheckTime = 0
		heartbeatSendTime = 0
		ackTime = 0

		while self._helperRunning:
			currentTime = time.time()

			if currentTime >= heartbeatCheckTime + PiClient._HEARTBEAT_CHECK_RATE:
				if self._serverStatus == PiConnectionStatus.OFFLINE or self._serverStatus == PiConnectionStatus.TIMEOUT:
					if self._heartbeatReceiveTime > currentTime - PiClient._HEARTBEAT_TIMEOUT:
						print('Server restored.')
						self._setServerStatus(PiConnectionStatus.ONLINE)
				elif self._serverStatus == PiConnectionStatus.ONLINE:
					if self._heartbeatReceiveTime < currentTime - PiClient._HEARTBEAT_TIMEOUT:
						print('Server timed out! No heartbeat received.')
						self._setServerStatus(PiConnectionStatus.TIMEOUT)

				heartbeatCheckTime = currentTime

			if currentTime >= heartbeatSendTime + PiClient._HEARTBEAT_SEND_RATE:
				# Always send a new heartbeat even if the server is offline
				self._sendMessage(PiNetworkCommand.HEARTBEAT)

				heartbeatSendTime = currentTime

			if currentTime >= ackTime + PiClient._ACK_CHECK_RATE:
				for info in self._sentPackets:
					a = currentTime
					b = info.sendTime + PiClient._ACK_TIMEOUT
					if currentTime > info.sendTime + PiClient._ACK_TIMEOUT:
						info.sendTime = currentTime
						print('Packet {} timed out. Resending...'.format(info.packetNum))
						self._clientSocket.sendto(info.msg, (self._serverIP, self._serverPort))
						self._sentPackets.remove(info)

				ackTime = currentTime

			time.sleep(0.01) # Sleep an arbitrary amount of time

	def _processPacket(self, data):
		results = struct.unpack_from(('>' if self._endian == 'BIG' else '<') + 'ii', data, 0)
		packetNum = results[0]
		command = PiNetworkCommand(results[1])
		currentTime = time.time()

		if command == PiNetworkCommand.HEARTBEAT:
			if PiClient._DEBUG:
				print('-> {:15}\tPC ID:\t{}\tTime:\t{:8.3f} s'.format(command.name, packetNum, currentTime - self._startTime))

			self._heartbeatReceiveTime = time.time()
		elif command == PiNetworkCommand.SHUTDOWN:
			if PiClient._DEBUG:
				print('-> {:15}\tPC ID:\t{}\tTime:\t{:8.3f} s'.format(command.name, packetNum, currentTime - self._startTime))

			print('Server is shutting down.')

			self._setServerStatus(PiConnectionStatus.OFFLINE)
			self._heartbeatReceiveTime = 0
		elif command == PiNetworkCommand.ACK:
			if PiClient._DEBUG:
				print('-> {:15}\tMy ID:\t{}\tTime:\t{:8.3f} s'.format(command.name, packetNum, currentTime - self._startTime), end='')

			for info in self._sentPackets:
				if info.packetNum == packetNum:
					if PiClient._DEBUG:
						rttMs = (time.time() - info.sendTime) * 1000
						print('\tRTT:\t{:6.1f} ms'.format(rttMs), end='')

					self._sentPackets.remove(info)
					break

			if PiClient._DEBUG:
				print()
		elif command == PiNetworkCommand.USER_MESSAGE:
			if PiClient._DEBUG:
				print('-> {:15}\tPC ID:\t{}\tTime:\t{:8.3f} s'.format(command.name, packetNum, currentTime - self._startTime))

			ackMsg = struct.pack(('>' if self._endian == 'BIG' else '<') + 'iii', packetNum, self._botID, PiNetworkCommand.ACK.value)

			if PiClient._DEBUG:
				print('<- {:15}\tPC ID:\t{}\tTime:\t{:8.3f} s'.format(PiNetworkCommand.ACK.name, packetNum, currentTime - self._startTime))

			self._clientSocket.sendto(ackMsg, (self._serverIP, self._serverPort))

			self.onMessageReceived(data[8:])
		else:
			print('Unexpected PiNetworkCommand')
