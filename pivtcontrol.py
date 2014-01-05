import logging
import asyncore
import asynchat
import socket
import shlex
import wx
from time import sleep
from csv import reader

class PiVTControl(asynchat.async_chat):
	"""Sends messages to a VT servers and handles status update responses
	
	"""
	
	playing = ""
	loaded = ""
	connected = False
	
	def __init__(self, server):
		splits = server.split(':')
		self.server = server
		try:
			host = splits[0]
			port = splits[1]
			if port == "" or host == "":
				raise IndexError
		except IndexError:
			# We didn't get a good server, just die
			return
		
		# Ok, try to connect
		self.databuffer = []
		asynchat.async_chat.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((host, port))
		return
	
	def handle_connect(self):
		self.connected = True
		self.set_terminator("\n")
		self.get_info()
		
	def collect_incoming_data(self, data):
		self.databuffer.append(data)
		
	def found_terminator(self):
		message = []		
		msg = ''.join(self.databuffer)
		for line in reader(msg):
			message = line
			
		self.databuffer = []
		
		if message[0].startswith('200'):
			# Got a 200 status update
			playgroups = shlex.split(message[0])
			
			if playgroups[1] == "Playing":
				self.playing = playgroups[2]
			else:
				self.playing = ""
				
			loadgroups = shlex.split(message[1])
			
			if loadgroups[1] == "Loaded":
				self.loaded = loadgroups[2]
			else:
				self.loaded = ""
				
		else:
			wx.MessageBox(msg, 'Error', wx.ICON_WARNING | wx.OK)	