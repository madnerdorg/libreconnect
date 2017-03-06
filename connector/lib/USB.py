###########################
#  Arduino Management v1.1#
###########################

import serial
from serial.tools import list_ports
from threading import Thread
import time
import sys
import random


class Device:
	# Change the status label if it is sent to the manager
	def __init__(self,device_name,device_type,device_return_string,device_baudrate,label=False):
		self.name = device_name
		self.type = device_type
		self.baudrate = device_baudrate
		self.return_string = device_return_string
		self.status = label
		self.arduino = False
		self.isConnected = False
		
		search_thread = Thread(target = self.manager)
		search_thread.daemon = True #If thread is not a daemon application could crashed
		search_thread.start()


	def change_status(self,string):
		if self.status:
			try:
				self.status.config(text=string)
			except:
				print("Label wasn't ready when updated")
		else:
			print("LABEL:" + string)

	# Manage arduino connection in a thread
	def manager(self):
		self.search()

	def listen(self):
		data = False
		try:
			if self.isConnected and self.listen:
				self.arduino.flushInput()
				time.sleep(0.1)
				try:
					data = self.arduino.readline().strip()			
					return data.decode()
				except:
					data = ""
					self.isConnected = False
					search_thread = Thread(target = self.manager)
					search_thread.daemon = True #If thread is not a daemon application could crashed
					search_thread.start()
		except:
			if self.isConnected:
				self.isConnected = False
				print("Error cannot read from Arduino")
				print(e)
				search_thread = Thread(target = self.manager)
				search_thread.daemon = True #If thread is not a daemon application could crashed
				search_thread.start()
				return False


	# Write to Arduino
	def write(self,string):
		try:
			if self.isConnected:
				self.arduino.write(string.encode())
				
			else:
				print("Waiting for connection dismissed message...")
		except Exception as e:
			#If message was not send correctly we try to reconnect
			if self.isConnected:
				self.isConnected = False
				print("Error cannot write to arduino")
				print(e)
				search_thread = Thread(target = self.manager)
				search_thread.daemon = True #If thread is not a daemon application could crashed
				search_thread.start()

	def close(self):
		print("Arduino closed by user")
		self.arduino.close()

	# Detect Arduino Nano Clone and automatically reconnect
	def search(self):
		if not self.isConnected:
			devices = list(list_ports.grep(self.name))
			#devices = list(list_ports.comports())
		
			#We search each serial ports with CH340g chip
			for device in devices:
				print("Connected to " + str(device[0]))
				self.change_status("Searching : " + device[0])

				print(device[1])
				#print(device[2])

				self.isConnected = self.get_type(device[0])

				# If we found the correct arduino we return the serial connection
				if self.isConnected:
					self.change_status("Connected: " + self.port)
					print("Connected to " + self.type)
					break;
			if not self.isConnected:
				self.change_status("No device founded")
		time.sleep(1)
		if not self.isConnected:
			self.search()


	# Check if arduino is the droids humm the arduino you're looking for
	def get_type(self,port):
		try:
			self.arduino = serial.Serial(port,self.baudrate,timeout=2)
		except Exception as e:
			#If multiples application is looking to connect
			#This won't work so we add a random sleep
			print("Arduino wasn't opened correctly")
			print(e)
			time.sleep(random.randint(1,3))
		#print(arduino)
		
		if self.arduino:
			time.sleep(2)
		
			#Write device type to arduino
			try:
				self.arduino.write(self.type.encode())
				answer = self.arduino.read(2)
				self.arduino.flushInput()
				self.port = port
				print("Serial: " + answer.decode())
				if answer.decode() == self.return_string:
					return True
				else:
					#If the answer isn't correct close the serial connection.
					self.arduino.close()
					self.change_status("Incorrect return string")
					print("Closing arduino")
					return False
			#Unable to write to arduino , skip
			except:
				self.change_status("No connection possible")
				print("Error connecting to arduino")
				return False

		#Arduino connection not established skip	
		else:
			return False