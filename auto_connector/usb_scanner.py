'''
 LibreConnect : Scan USB Serial port and connected them
 using connector
 Author : Rémi Sarrailh (madnerd.org)
 Email : remi@madnerd.org
 License : MIT
'''

# Arguments/ Time
import serial
from serial.tools import list_ports
import time
from threading import Thread
import subprocess
import os

devices = []
connected_devices = []
baudrate = 115200
connectors = []

devices_ports = {
    "test": 42000,
    "leds": 42001,
    "radio433": 42002,
    "openlight": 42003,
    "buzzer": 42004,
    "temphum": 42005
}


# Connected to arduino send /info and show response
def getName(port):
    try:
        arduino = serial.Serial(port, baudrate, timeout=2)
        time.sleep(2)
        arduino.write("/info".encode())
        arduino.flushInput()
        device_info = arduino.readline().strip()
        device_info = device_info.decode()
        arduino.close()
        return device_info
    except Exception as e:
        return ""


# Get current serials port and put name in an array
def getPorts():
    raw_devices = serial.tools.list_ports.comports()
    devices = []
    for raw_device in raw_devices:
        devices.append(raw_device[0])
    return devices


# Start connector
def connector_thread(port, websocket_port):
    command = "connector.exe"
    print(command+' --serial '+str(port)+' --port '+str(websocket_port))
    os.system(command+' --serial '+str(port)+' --port "'+str(websocket_port))
    print("Print stop")


# Start seperate thread for connector
def connect(port, websocket_port):
    new_connector = Thread(target=connector_thread,
                           args=(port, websocket_port))
    new_connector.daemon = True
    new_connector.start()
    # connectors.append(new_connector)


def scan_devices():
    scanned_devices = getPorts()
    for port in scanned_devices:
        if port not in devices:
            print("ADDED:" + port)
            devices.append(port)
            name = getName(port)
            if name != "":
                print("CONNECTED: " + name)
                connect(port, devices_ports[name])
            else:
                print("NOT CONNECTED: " + port)
    for device in devices:
        if device not in scanned_devices:
            print("REMOVED:" + device)
            devices.remove(device)

while True:
    scan_devices()
    print(devices)
    # print(connectors)
    time.sleep(2)
