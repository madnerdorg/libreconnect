'''
 LibreConnect usb_scanner : Scan USB Serial port and connected them
 using connector
 Author : Remi Sarrailh (madnerd.org)
 Email : remi@madnerd.org
 License : MIT
'''

import serial
from serial.tools import list_ports
import time
import sys
from threading import Thread
import subprocess
import os

# We use 115200 as default baudrate
baudrate = 115200
# Check serial ports every x seconds
scan_speed = 1
# If we failed to have an answer retry x times
retry_connection = 3

devices_ports = []
devices_name = []
devices_websocket = []

# Check if python file existed, if not default to compiled version
if os.path.exists("connector.py"):
    connector_software = "python connector.py"
else:
    if sys.platform == "win32":
        connector_software = "connector.exe"
    else:
        connector_software = "./connector"

arguments = " ".join(sys.argv[1:])


# Connected to arduino send /info and get answer
def getInfo(usb_port):
    retry = retry_connection
    try:
        arduino = serial.Serial(usb_port, baudrate,
                                writeTimeout=1, timeout=1)
        time.sleep(2)
        while retry > 0:
            # Ask for information
            arduino.write("/info".encode())
            arduino.flushInput()

            # Get answer
            device_info = arduino.readline().strip()
            device_info = device_info.decode()

            if ":" in device_info:
                device_array = device_info.split(":")
                name = device_array[0]
                port = device_array[1]
                retry = 0
            else:
                print("[WARNING]: Retry")
                name = ""
                port = ""
            retry = retry - 1
        arduino.close()
        return name, port
    except Exception as e:
        print("[ERROR]: " + str(e))
        return "", ""


# Get current serials port and put name in an array
def getPorts():
    raw_devices = serial.tools.list_ports.comports()
    devices = []
    for raw_device in raw_devices:
        devices.append(raw_device[0])
    return devices


# Start connector
def connector_thread(usb_port, websocket_port):
    command = connector_software + ' --serial ' + str(usb_port)
    command = command + ' --port '+str(websocket_port)
    command = command + " " + arguments
    print("[INFO]: " + command)
    os.system(command)


# Start seperate thread for connector
def connect(usb_port, websocket_port):
    new_connector = Thread(target=connector_thread,
                           args=(usb_port, websocket_port))
    new_connector.daemon = True
    new_connector.start()
    # connectors.append(new_connector)


# Search for arduino
def scan_devices():
    scanned_devices = getPorts()
    for usb_port in scanned_devices:
        if usb_port not in devices_ports:
            print("[NEW]: " + usb_port)
            devices_ports.append(usb_port)
            name, ws_port = getInfo(usb_port)
            if name != "" and ws_port != "":
                print("[INFO]: " + name + " connected")
                connect(usb_port, ws_port)
                devices_name.append(name)
                devices_websocket.append(ws_port)
            else:
                print("[WARNING]: " + usb_port + " not connected")
    for device_port in devices_ports:

        if device_port not in scanned_devices:
            print("[INFO]: " + device_port + " was removed")
            devices_ports.remove(device_port)

while True:
    scan_devices()
    """
    print("Devices")
    print(devices_name)
    print("Ports")
    print(devices_ports)
    print("Websockets")
    print(devices_websocket)
    """
    time.sleep(scan_speed)
