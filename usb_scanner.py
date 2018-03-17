'''
 LibreConnect usb_scanner : Scan USB Serial port and connected them
 using connector
 Author : Remi Sarrailh (madnerd.org)
 Email : remi@madnerd.org
 License : MIT
'''

import os
import sys
import time
from pyfirmata import Arduino, util
from threading import Thread

import serial
from serial.tools import list_ports

from modules import settings_parser

VERSION = "1.2"


devices_ports = []
devices_name = []
devices_websocket = []
config_file = False

args = settings_parser.get()
args, config_file = settings_parser.get_from_file(args)

# Remove Force from arguments as it doesn't need to be pass to connector
# if args["force"]:
# arguments = arguments.replace("--force", "")

# Generating arguments list for connector if config_file exists
# Just set settings file location so connector can get settings from there
if config_file:
    arguments = " " + "--settings " + args["settings_file"]
    if args["debug"]:
        arguments = arguments + " " + "--debug"
else:
    arguments = " ".join(sys.argv[1:])

next_port = args["port"]
print(next_port)
print("LibreConnect - version " + VERSION)
print("By madnerd.org (https://github.com/madnerdorg/libreconnect)")
print("----------------------------------------------------------")

# Get connector for windows or linux, if a python version exists use it instead
connector_software = settings_parser.get_connector()

def get_device(usb_port,device, baudrate, question):
    """ Check what device this is using a string as a question
        If the device send back a message with answer in it, return his name and port
    
    Arguments:
        usb_port {string} --  USB port (COM12 or /dev/ttyUSB0)
        device {string} -- usb device type (libreconnect/mysensors)
        baudrate {integer} -- serial baudrate
        question {string} -- message to send
        answer {string} -- message to receive
    
    Returns:
        name,port {string/integer} -- name of device and port
    """
    name = ""
    port = ""
    retry = args["serial_retry"] 
    try:
        arduino = serial.Serial(usb_port, baudrate,
                                writeTimeout=1, timeout=1)
        time.sleep(2)
        while retry > 0:
            arduino.write(question.encode())
            arduino.flushInput()

            # Get answer
            device_info = arduino.readline().strip()
            device_info = device_info.decode()
            
            if device is "mysensors":
                print("Check ...")
                if ";" in device_info:
                    name = "mysensors"
                    port = 42042
                    retry = 0
            elif device is "libreconnect":
                if ":" in device_info:
                    device_array = device_info.split(":")
                    name = device_array[0]
                    port = device_array[1]
                    retry = 0
            if name == "" and port == "":
                print("[WARN]: Retry")
            retry = retry - 1
        arduino.close()
        return name, port
    except Exception as serial_error:
        print("[ERROR]: " + str(serial_error))
        return "ERROR", ""

def get_firmata(usb_port):
    """ Try to connect to a firmata device
    
    Arguments:
        usb_port {[string]} -- USB port (COM12 or /dev/ttyUSB0)
    
    Returns:
        [name,port] -- Return name and port
    """

    retry = args["serial_retry"]
    while retry > 0:
        try: 
            board = Arduino(usb_port,timeout=1)
            if board.firmware is not None:
                print(board.firmware)
                board.exit()
                return "firmata","42043"
            board.exit()          
        except Exception as serial_error:
            print("[ERROR]: " + str(serial_error))
            return "ERROR",""
        retry = retry - 1
    return "",""


def get_devices(usb_port):
    global next_port
    """
        # Connected to arduino and check it using serial command
    """    
    if args["firmata"]:
        print("Firmata scan...")
        name,port = get_firmata(usb_port)
        if name != "" and port != "": return name,port
        if name == "ERROR": return "",""

    if args["mysensors"]:
        print("Mysensors scan...")
        name,port = get_device(usb_port, "mysensors", args["mysensors_baudrate"], "0;0;3;0;2;0;0\n")
        if name != "" and port != "": return name,port
        if name == "ERROR": return "",""

    if args["libreconnect"]:
        print("LibreConnect scan...")
        name, port = get_device(usb_port, "libreconnect", args["libreconnect_baudrate"], "/info")
        if name != "" and port != "": return name,port
        if name == "ERROR": return "",""

    if args["unknown"]:
        name = "unknown"
        port = next_port
        next_port = next_port + 1
    print(name,port)

    return name,port

def get_ports():
    """
        # Get serials port list and put it in an array

        return: devices list
    """
    raw_devices = list_ports.comports()
    devices = []
    for raw_device in raw_devices:
        devices.append(raw_device[0])
    return devices

def connector_thread(name, usb_port, websocket_port):
    """
        Start connector
    """
    command = connector_software + ' --serial ' + str(usb_port)
    command = command + ' --name ' + name
    command = command + ' --port '+str(websocket_port)
    command = command + " " + arguments
    if args["debug"]:
        print("[INFO]: " + command)
    os.system(command)

def connect(name, usb_port, websocket_port):
    """
        Start seperate thread for connector
    """
    new_connector = Thread(target=connector_thread,
                           args=(name, usb_port, websocket_port))
    new_connector.daemon = True
    new_connector.start()
    # connectors.append(new_connector)

def scan_devices():
    """
        # Search for serial devices (arduino)
    """
    scanned_devices = get_ports()
    for usb_port in scanned_devices:
        if usb_port not in devices_ports:
            print("[NEW]: " + usb_port)
            devices_ports.append(usb_port)
            name, ws_port = get_devices(usb_port)

            if name != "" and ws_port != "":
                connect(name, usb_port, ws_port)
                devices_name.append(name)
                devices_websocket.append(ws_port)
            else:
                print("[WARN]: " + usb_port + " not connected")
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
    time.sleep(args["serial_scan_interval"])
