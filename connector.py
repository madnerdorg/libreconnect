'''
 Madnerd Connector : Transform a serial port into a websocket
 Author : Remi Sarrailh (madnerd.org)
 Email : remi@madnerd.org
 License : MIT
'''

# Arguments/ Time
import sys
import time
import argparse
from subprocess import call
import platform
import os
import serial
import json

# Autobahn/Twisted websocket
from twisted.internet import reactor, ssl, protocol
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol, listenWS

import threading

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

args = vars(parser.parse_args())

# Settings
port = args["port"]
local = args["local"]

# Serial
device_baudrate = args["baudrate"]
device_serial = args["serial"]

# Password
password = args["password"]

# SSL
secure = args["secure"]
ssl_dir = args["keys"]
bantime = float(args["bantime"])
maxretry = args["retry"]

# Power
power_management = args["power"]

# Settings
user_settings_file = port+".json"
user_settings = ""

if os.path.isfile(user_settings_file):
    with open(user_settings_file) as json_data_file:
        try:
            user_settings = json.load(json_data_file)
        except:
            print("user_settings doesn't works")

# Clients managements
global clients
global suspected_clients
clients = []
suspected_clients = []


# We generate our device
try:
    device = serial.Serial(device_serial, device_baudrate, timeout=0.01)
except:
    print("[ERROR]: Serial connection failed")


# Search for an element in a list and return element
def search(value, list, key):
    return [element for element in list if element[key] == value]


# Search for an element and return key
def search_key(value, list, key):
    for nb, element in enumerate(list):
        if element[key] == value:
            return nb
    return False


# Force websocket to stop
def websocket_off():
    try:
            device.close()
    except:
            print("[WARNING]: Device not closed properly")
    os._exit(1)


def write(message, client):
    global user_settings, user_settings_file
    if message == "@reboot":
        if power_management:
            print("Reboot")
            if platform.system() == "Windows":
                call(["scripts\\reboot.bat"])
            else:
                call(["reboot"])

    elif message == "@poweroff":
        if power_management:
            print("Power off")
            if platform.system() == "Windows":
                call(["scripts\\poweroff.bat"])
            else:
                call(["poweroff"])

    elif message.startswith('@save:', 0, 6):
        # Save user settings
        print("Save settings")
        print(message[6:])
        user_settings = message[6:]
        with open(user_settings_file, 'w') as outfile:
            json.dump(message[6:], outfile)

    elif message == "@load":
        # Load user settings
        print("Load Settings")
        print("@" + json.dumps(user_settings))
        settings = "@" + json.dumps(user_settings)
        client.sendMessage(settings.encode())

    else:
        # Send to arduino
        device.write(message.encode())


# Websocket manager class
class ArduinoServerProtocol(WebSocketServerProtocol):
    # On connect we check if the user was banned
    def onConnect(self, request):
        # print(suspected_clients)
        print('[INFO]: New Client -- '+self.peer)

        # Ban manager
        if password is not False:
            global suspected_clients
            ip, port = self.transport.client
            connectiontime = time.time()

            # Check list of blocked client
            suspected = search(ip, suspected_clients, 'ip')
            if suspected:
                user = suspected[0]
                ban_remaining_time = connectiontime - user["time"]
                print(ip+" ban for " + str(ban_remaining_time))

                # If user ban time is over, unban
                if connectiontime-(user['time']) > bantime:
                    suspected_clients.remove(suspected[0])
                    print(ip+" unbanned")
                else:
                    # If password failed for maxretry block user
                    if user["retry"] >= maxretry:
                        print(ip + " has been blocked")

        else:
            print("[INFO]: No password needed")
            if self not in clients:
                clients.append(self)

    # On open we ask for a password
    def onOpen(self):
        # print("[INFO]: WebSocket connection open.")
        if password is not False:
            self.sendMessage(str("@password").encode())

    # On message we check for the password
    # If user is logged, we send the message to the arduino
    def onMessage(self, payload, isBinary):
        global clients
        global suspected_clients
        # print(clients)
        if not isBinary:
            message = payload.decode("utf-8")
            print("[INFO]: <-- "+message)
            if password is not False:
                # Check if client is registered
                if self in clients:
                    write(message, self)
                else:
                    ip, port = self.transport.client
                    if len(suspected_clients) > 0:
                        blocked = search(ip, suspected_clients, 'ip')
                        if blocked[0]["retry"] < maxretry:
                            blocked = False
                    else:
                        blocked = False
                    # print(blocked)

                    if blocked is False:
                        if message == password:
                            print("Access granted")
                            self.sendMessage(str("@logged").encode())
                            if self not in clients:
                                clients.append(self)
                        else:
                            print("Wrong Password")
                            # self.sendMessage("Wrong Password")
                            # self.close()
                            print(suspected_clients)
                            suspect = search_key(ip, suspected_clients, 'ip')
                            if suspect is not False:
                                print("Suspected IP")
                                user = suspected_clients[suspect]
                                # print(user)
                                if user["retry"] >= maxretry:
                                    print('Banned:{0}'.format(ip))
                                    self.sendMessage(str("@banned").encode())
                                else:
                                    suspected_clients[suspect]["retry"] = user["retry"] + 1
                                    error_message = "@wrongpassword:" + str(suspected_clients[suspect]["retry"]) + "/" + str(maxretry)
                                    self.sendMessage(error_message.encode())
                                    print("Recorded suspect: " +
                                          str(suspected_clients[suspect]["retry"]))
                            else:
                                mess = str("@wrongpassword:1/"+str(maxretry))
                                self.sendMessage(mess.encode())
                                suspected = {"ip": ip,
                                             "time": time.time(),
                                             "retry": 1}
                                suspected_clients.append(suspected)
                                print('Recorded suspect: {0}'.format(ip))
            else:
                write(message, self)

    # On close, we remove user from approved list
    def onClose(self, wasClean, code, reason):
        global clients
        print("[INFO]: Client disconnected -- {0}".format(reason))
        if self in clients:
            clients.remove(self)


# Arduino send message list
def start_listen():
    global clients
    while True:
        try:
            data = False
            data = device.readline().strip()
            if data is not b'':
                for client in clients:
                    print("[INFO]: --> "+str(data))
                    client.sendMessage(data)
        except Exception as e:
            websocket_off()

# We listen to arduino message in a thread
listener_thread = threading.Thread(target=start_listen)
listener_thread.daemon = True
listener_thread.start()
print("[INFO]: Websocket started: " + port)

if secure:
    print("[INFO]: Websocket SSL")
    ws_type = "wss://"
else:
    ws_type = "ws://"

if local:
    print("[INFO]: Websocket only on local")
    interface = "localhost"
else:
    interface = ""

addr = ws_type+"0.0.0.0"+":"+port

# We start the websocket here
factory = WebSocketServerFactory(addr)

if secure:
    contextFactory = ssl.DefaultOpenSSLContextFactory(ssl_dir+'/server.key',
                                                      ssl_dir+'/server.crt')
    listenWS(factory, contextFactory, interface=interface)
else:
    listenWS(factory, interface=interface)

factory.protocol = ArduinoServerProtocol
reactor.run()
