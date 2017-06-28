'''
 LibreConnect usb_scanner : Scan USB Serial port and connected them
 using connector
 Author : Remi Sarrailh (madnerd.org)
 Email : remi@madnerd.org
 License : MIT
'''
import argparse
import os
import sys
import time
from threading import Thread

import serial
from serial.tools import list_ports

VERSION = "1.0"
# Check serial ports every x seconds
SCAN_SPEED = 1
# If we failed to have an answer retry x times
RETRY_CONNECTION = 3


devices_ports = []
devices_name = []
devices_websocket = []


# Arguments
parser = argparse.ArgumentParser(
    description="Transform a serial port into a websocket")
parser.add_argument("--serial", default="", help="Serial port")
parser.add_argument("--port", default="42001",
                    help="Websocket port")
parser.add_argument("--secure", default=False, action="store_true",
                    help="Add SSL")
parser.add_argument("--power", default=False, action="store_true",
                    help="Add power management (@reboot/@poweroff)")
parser.add_argument("--password", default=False,
                    help="Password for the websocket")
parser.add_argument("--local", default=False, action="store_true",
                    help="Websocket will only be available locally")
parser.add_argument("--bantime", default=0,
                    help="Seconds before a ban user is unbanned")
parser.add_argument("--retry", default=10, help="Number of retry before ban")
parser.add_argument("--baudrate", default="115200",
                    help="Baudrate for serial com")
parser.add_argument("--keys", default="keys/",
                    help="folders where SSL certificates are")
parser.add_argument("--force", default=False, action="store_true",
                    help="Connect any serial devices")

args = vars(parser.parse_args())
arguments = " ".join(sys.argv[1:])
if args["force"]:
    arguments = arguments.replace("--force", "")

print("LibreConnect - version " + VERSION)
print("By madnerd.org (https://github.com/madnerdorg/libreconnect)")
print("----------------------------------------------------------")

# Check if python file existed, if not default to compiled version
if os.path.exists("connector.py"):
    connector_software = "python connector.py"
else:
    if sys.platform == "win32":
        connector_software = "connector.exe"
    else:
        connector_software = "./connector"



next_port = 40000
def get_info(usb_port):
    """
        # Connected to arduino send /info and get answer
    """
    retry = RETRY_CONNECTION
    try:
        arduino = serial.Serial(usb_port, args["baudrate"],
                                writeTimeout=1, timeout=1)
        if args["force"]:
            name = "unknown"
            global next_port
            port = next_port
            next_port = next_port + 1
        else:
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
    except Exception as serial_error:
        print("[ERROR]: " + str(serial_error))
        return "", ""



def get_ports():
    """
        # Get current serials port and put name in an array
    """
    raw_devices = list_ports.comports()
    devices = []
    for raw_device in raw_devices:
        devices.append(raw_device[0])
    return devices



def connector_thread(name, usb_port, websocket_port):
    """
        # Start connector
    """
    command = connector_software + ' --serial ' + str(usb_port)
    command = command + ' --name ' + name
    command = command + ' --port '+str(websocket_port)
    command = command + " " + arguments
    # print("[INFO]: " + command)
    os.system(command)


def connect(name, usb_port, websocket_port):
    """
        # Start seperate thread for connector
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
            name, ws_port = get_info(usb_port)

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
    time.sleep(SCAN_SPEED)
