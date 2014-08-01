import asyncore
import asynchat2
import socket
import shlex
import wx
import threading
from time import sleep
import re

class PiVTControl(asynchat2.async_chat):
	"""Sends messages to a VT servers and handles status update responses
	
	"""
	
	playing = ""
	loaded = ""
	automode = False
	connected = False
	filelist = None
	
	def __init__(self, server, conn_cb, data_cb, connfail_cb):
		splits = server.split(':')
		self.server = server
		self.conn_cb = conn_cb
		self.data_cb = data_cb
		self.connfail_cb = connfail_cb
		
		host = splits[0]
		port = int(splits[1])
		if port == "" or host == "":
			wx.MessageBox('Bad server', 'Failed to connect', 
						wx.ICON_ERROR | wx.OK)
			raise IndexError
		
		# Ok, try to connect
		self.databuffer = []
		
		try:
			asynchat2.async_chat.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
			socket.setdefaulttimeout(15)
			self.connect((host, port))
		except socket.error, e:
			wx.MessageBox('Error: {0}'.format(e.message), 'Failed to connect', 
						  wx.ICON_ERROR | wx.OK)
			print "Fail!"
			raise Exception
	
	def get_info(self):
		if self.connected == True:
			self.push("i\r\n")
			sleep(0.5)
	
	def stop(self):
		if self.connected == True:
			self.push("s\r\n")
			self.playing = ""
			sleep(0.1)
			
	def play(self):
		if self.connected == True:
			if self.loaded != "":
				self.push("p\r\n")
				self.playing = self.loaded
				self.loaded = ""
				#sleep(0.5)
			else:
				wx.MessageBox('Cannot play with nothing loaded!', 'Error',
							wx.ICON_ERROR | wx.OK)
			
	def load(self, filename):
		if self.connected == True:
			self.push('l "{0}"\r\n'.format(filename))
			self.loaded = filename
			#sleep(0.5)
			
	def setauto(self, on):
		if on ^ self.automode:
			self.push('m \r\n')
			self.automode = on
			#sleep(0.5)			
			
	def getfilelist(self):
		# Prepare for new update
		self.updateready = False
		self.filelist = []
		
		self.push('g \r\n')
		
		# Wait for file listing to complete in network thread
		timeout = 50
		while self.updateready == False:
			sleep(0.1)
			timeout -= 1
			if (timeout <= 0):
				return None
			
		# Reset flag marking completion status
		self.updateready = None
		
		return self.filelist
	
	def handle_connect(self):
		print "Connected!"
		self.connected = True
		self.set_terminator("\n")
		self.conn_cb()
		
	def collect_incoming_data(self, data):
		self.databuffer.append(data)
		
	def found_terminator(self):		
		msg = ''.join(self.databuffer)
		self.databuffer = []
		
		if msg.startswith("Welcome to PiVT"):
			return
		
		# Split the returned line into comma separted blocks. Do not split on
		# commas in quotes
		message = re.split(',(?=(?:[^"]*"[^"]*")*[^"]*$)', msg)
		
		if len(message) < 1:
			return
		
		if message[0].startswith('200'):
			# Got a 200 status update
			playgroups = shlex.split(message[0])
			if playgroups[1] == "Playing":
				self.playing = playgroups[2]
			else:
				self.playing = ""
				
			loadgroups = shlex.split(message[1])
			if loadgroups[0] == "Loaded":
				self.loaded = loadgroups[1]
			else:
				self.loaded = ""
				
			# Was Auto mode enabled?
			if shlex.split(message[3])[1] == 'True':
				self.automode = True
			else:
				self.automode = False
				
			try:
				numbers = float(shlex.split(message[2])[0])
			except ValueError:
				numbers = 0
			
			self.data_cb(numbers)
			
		elif message[0].startswith('202'):
			
			# Trigger a real update to get some better numbers
			self.get_info()
		
		elif message[0].startswith('203'):
			# Got a 203 Loaded
			loadgroups = shlex.split(message[0])
			self.loaded = loadgroups[2]
			
			if (self.playing == ""):
				try:
					numbers = float(shlex.split(message[1])[0])
				except ValueError:
					numbers = 0
			else:
				numbers = None
			
			self.data_cb(numbers)
			
		elif message[0].startswith('204'):
			splits = shlex.split(message[0])
			
			self.get_info()
			
			if splits[len(splits)-1] == 'True':
				self.automode = True
			else:
				self.automode = False
			
			if splits[1] == 'Stopped':
				self.playing = ""
				
				# Check for a loaded video
				loadgroups = shlex.split(message[1])
				if loadgroups[0] == "Loaded":
					self.loaded = loadgroups[1]
					
					numbers = float(shlex.split(message[2])[0])
				else:
					self.loaded = ""
					numbers = None
				
				self.data_cb(numbers)
			else:
				self.playing = splits[2]
				numbers = float(splits[3])
				self.loaded = ""
				self.data_cb(numbers, changeover=True)
		
		elif message[0].startswith('205'):
			# 205 File listing complete
			self.updateready = True
			
		elif message[0].startswith('206'):
			splits = shlex.split(message[0])
			
			self.filelist.append((splits[1], float(splits[2])))
		
		elif message[0].startswith('Auto Enabled set to'):
			if shlex.split(message[0])[4] == True:
				self.automode = True
			else:
				self.automode = False
		
		elif message[0].startswith('Shutting down'):
			self.run = False
			self.close_when_done()
		else:
			wx.MessageBox(msg, 'Error', wx.ICON_WARNING | wx.OK)	
			
	def startup_async(self):
		self.run = True
		self.netthread = threading.Thread(target=self.runner)
		self.netthread.start()
			
	def runner(self):
		connecttimer = 8
		while self.run:
			asyncore.poll(0.1)
			
			if self.connected != True:
				connecttimer = connecttimer - 0.1
				sleep(0.1)
				if connecttimer < 0:
					self.connected = False
					self.run = False
					print("Connection failed!")
					self.connfail_cb()
					del(self)
					break