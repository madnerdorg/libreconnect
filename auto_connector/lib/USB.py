'''
Arduino Manager
Autoconnect to the correct serial port and expose read/write

1 - Module try to connect to any available serial port
2 - Send a string to the serial port
3 - Wait for string : OK

Author  : Rémi Sarrailh (madnerd.org)
Email   : remi@madnerd.org
Licence : MIT
'''

import serial
from serial.tools import list_ports
from threading import Thread
import time
import sys
import random


class Device:
    # Change the status label if it is sent to the manager
    def __init__(self, port, device_baudrate):
        self.baudrate = device_baudrate
        self.port = port
        self.arduino = False
        self.isConnected = False
        try:
            self.arduino = serial.Serial(port, self.baudrate, timeout=2)
            self.isConnected = True
            print("Connected")
        except:
            self.isConnected = False
            print("Not Connected")

    # Listen to arduino serial port
    def listen(self):
        data = False
        try:
            data = self.arduino.readline()
        except:
            data = ""
            self.isConnected = False
        return data

    # Write to Arduino
    def write(self, string):
        # print(string)
        self.arduino.write(string.encode())

    def close(self):
        print("Arduino closed by user")
        self.arduino.close()
