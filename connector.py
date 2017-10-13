'''
 Madnerd Connector : Transform a serial port into a websocket
 Author : Remi Sarrailh (madnerd.org)
 Email : remi@madnerd.org
 License : MIT
'''

# Arguments/ Time
import time
import argparse
from subprocess import call
import platform
import os
import threading
# Autobahn/Twisted websocket
from twisted.internet import reactor, ssl, protocol
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
import serial
import socket

import ConfigParser
next_port = 40000

# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
server_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

config_file = False
# Arguments
parser = argparse.ArgumentParser(
    description="Transform a serial port into a websocket")
parser.add_argument("--serial", default="", help="Serial port")
parser.add_argument("--port", default=next_port,
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
parser.add_argument("--settings", default="libreconnect.ini",
                    help="Setting file")
parser.add_argument("--debug", default=False, action="store_true",
                    help="Debug Mode")

parser.add_argument("--name", default="unknown",
                    help="Device name")

args = vars(parser.parse_args())

if args["debug"]:
    print("Arguments -------------")
    print(args)

# Configuration File
if os.path.isfile(args["settings"]):
    config_file = True
    # print("Settings founded")
    settings = ConfigParser.ConfigParser()
    settings.read(args["settings"])
    # print args
    for name,arg in args.items():
        try:
            args[name] = settings.get("settings",name)
        #print(name)
        #print(arg)
        except:
            pass
            # print("Pass" + name)
    #print args
    if args["debug"]:
        print("Configuration File -------------")
        print(args)   

# Settings
password = args["password"]
bantime = float(args["bantime"])
maxretry = int(args["retry"])
local = args["local"]
secure = args["secure"]
port = args["port"]
ssl_dir = args["keys"]
name = args["name"]

power_management = args["power"]

# Baudrate
device_baudrate = args["baudrate"]
# Serial
device_serial = args["serial"]

# Clients managements
global clients
global suspected_clients
clients = []
suspected_clients = []


# We generate our device
try:
    device = serial.Serial(device_serial, device_baudrate, timeout=0.01)
except:
    print("["+name+"] "  + "[ERROR]: Serial connection failed")



def search(value, list, key):
    """
        # Search for an element in a list and return element
    """
    return [element for element in list if element[key] == value]



def search_key(value, list, key):
    """
        # Search for an element and return key
    """
    for nb, element in enumerate(list):
        if element[key] == value:
            return nb
    return False


# Force websocket to stop
def websocket_off():
    try:
            device.close()
    except:
            print("["+name+"] "  + "[WARN]: Device not closed properly")
    os._exit(1)


def write(message):
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

    else:
        # Send to arduino
        device.write(message.encode())


# Websocket manager class
class ArduinoServerProtocol(WebSocketServerProtocol):
    # On connect we check if the user was banned
    def onConnect(self, request):
        # print(suspected_clients)
        ip, port = self.transport.client
        print("["+name+"] " + '[INFO]: '+ ip + ":" + args["port"] + ' connected')

        # Ban manager
        if password is not False:
            global suspected_clients
            connectiontime = time.time()

            # Check list of blocked client
            suspected = search(ip, suspected_clients, 'ip')
            if suspected:
                user = suspected[0]
                ban_remaining_time = connectiontime - user["time"]
                
                # If user ban time is over, unban
                if connectiontime-(user['time']) > bantime:
                    suspected_clients.remove(suspected[0])
                    print("["+name+"] "   + "[INFO]: " + ip+" is unbanned")
                else:
                    # If password failed for maxretry block user
                    if user["retry"] >= maxretry:
                        print("["+name+"] "  + "[INFO]: " + ip + " has been blocked ("+str(int(ban_remaining_time))+"/"+args["bantime"]+" seconds)")

        else:
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
            if password is not False:
                # Check if client is registered
                if self in clients:
                    print("["+name+"] [INFO]: <-- " + message)
                    write(message)
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
                            print("["+name+"] [INFO]: " + ip +":"+args["port"] + " is logged in")
                            self.sendMessage(str("@logged").encode())
                            if self not in clients:
                                clients.append(self)
                        else:                            
                            # print(suspected_clients)
                            suspect = search_key(ip, suspected_clients, 'ip')
                            if suspect is not False:
                                user = suspected_clients[suspect]
                                # print(user)
                                if user["retry"] < maxretry:
                                    suspected_clients[suspect]["retry"] = user["retry"] + 1
                                    error_message = "@wrongpassword:" + str(suspected_clients[suspect]["retry"]) + "/" + str(maxretry)
                                    self.sendMessage(error_message.encode())
                            else:
                                mess = str("@wrongpassword:1/"+str(maxretry))
                                self.sendMessage(mess.encode())
                                suspected = {"ip": ip,
                                             "time": time.time(),
                                             "retry": 1}
                                suspected_clients.append(suspected)
                            print("["+name+"] [WARN]: " + ip+":"+args["port"] + " - Wrong Password " + str(suspected_clients[suspect]["retry"]) + "/" + str(maxretry))
                    else:
                        print("["+name+"] [ERROR]: " + ip + ":" + args["port"] + " banned")
                        self.sendMessage("@banned")
            else:
                print("["+name+"] [INFO]: <-- " + message)
                write(message)

    # On close, we remove user from approved list
    def onClose(self, wasClean, code, reason):
        global clients
        ip,port = self.transport.client
        if code != 1006:
            print("["+name+"] [INFO]: " + ip + ":" + args["port"] + " disconnected")
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
                    print("["+name+"] [INFO]: --> "+str(data))
                    client.sendMessage(data)
        except Exception as e:
            websocket_off()

settings_text = ""
if secure:
    settings_text = settings_text + "SSL "
    ws_type = "wss://"
else:
    ws_type = "ws://"

if local:
    settings_text = settings_text + "LOCAL "
    interface = "localhost"
else:
    interface = ""

if password:
    settings_text = settings_text + "PASSWORD "

addr = ws_type+"0.0.0.0"+":"+port

# We start the websocket here
factory = WebSocketServerFactory(addr)

failed_start = False

if secure:
    if os.path.isfile(ssl_dir+"/privkey.pem") and os.path.isfile(ssl_dir+"/cert.pem"):
        contextFactory = ssl.DefaultOpenSSLContextFactory(ssl_dir+'/privkey.pem',
                                                        ssl_dir+'/cert.pem')
        listenWS(factory, contextFactory, interface=interface)
    else:
        print("[ERROR]: I can't find "+ ssl_dir +"cert.pem"+" and/or "+ ssl_dir +'privkey.pem')
        failed_start = True
else:
    listenWS(factory, interface=interface)

if not failed_start:
    print("["+name+"] "  + "[INFO]: " + ws_type + server_ip + ":" + port + " " + settings_text)

    factory.protocol = ArduinoServerProtocol

    # We listen to arduino message in a thread
    listener_thread = threading.Thread(target=start_listen)
    listener_thread.daemon = True
    listener_thread.start()
    reactor.run()
