'''
 Madnerd Connector : Transform a serial port into a websocket
 Author : Rémi Sarrailh (madnerd.org)
 Email : remi@madnerd.org
 License : MIT

Generate SSL Certificate
You need to validate the ssl certificate in your browser.
Just go to https://ip:port to do this

openssl genrsa -out keys/server.key 2048
openssl req -new -key keys/server.key -out keys/server.csr
openssl x509 -req -days 3650 -in keys/server.csr -signkey keys/server.key -out keys/server.crt
openssl x509 -in keys/server.crt -out keys/server.pem

Source
------
Crossbar.io - Echo_tls Autobahn example
https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_tls

Simplyautomationized.blogspot.fr
5 ways to secure your raspberry pi's websocket server
http://simplyautomationized.blogspot.fr/2015/09/5-ways-to-secure-websocket-rpi.html

madnerd.org - Control Arduino with a portable app
http://www.instructables.com/id/UTest-Make-USB-Devices-With-Arduino/
'''

# Arguments/ Time
import sys
import time
import argparse
from subprocess import call
import platform
import os

# Autobahn/Twisted websocket
from twisted.internet import reactor, ssl, protocol
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol, listenWS

# Arduino Manager
from lib import USB
import threading

parser = argparse.ArgumentParser(
    description="Transform a serial port into a websocket")
parser.add_argument("--port", default="42001",
                    help="Websocket port")
parser.add_argument("--device", default="test", help="Device name")
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
parser.add_argument("--name", default="", help="USB identification")
parser.add_argument("--baudrate", default="115200",
                    help="Baudrate for serial com")
parser.add_argument("--keys", default="keys/",
                    help="folders where SSL certificates are")

args = vars(parser.parse_args())

# Default Settings
password = args["password"]
bantime = float(args["bantime"])
maxretry = args["retry"]
local = args["local"]
secure = args["secure"]
port = args["port"]
ssl_dir = args["keys"]

power_management = args["power"]

# Device name in Windows
device_name = args["name"]
# Device type (in the arduino sketch)
device_type = args["device"]
# Answer when a response is correct (can't be more than 2 characters)
device_return_string = "OK"
# Baudrate
device_baudrate = args["baudrate"]

# Clients managements
global clients
global suspected_clients
clients = []
suspected_clients = []

# We generate our device
device = USB.Device(device_name,
                    device_type, device_return_string, device_baudrate, False)


# Search for an element in a list and return element
def search(value, list, key):
    return [element for element in list if element[key] == value]


# Search for an element and return key
def search_key(value, list, key):
    for nb, element in enumerate(list):
        if element[key] == value:
            return nb
    return False


def websocket_off():
    try:
            device.close()
    except:
            print("No device to close...")
    reactor.stop()


def write(message):
    # Stop websocket
    print(message)
    if message == "@websocket_poweroff":
        print("Exit application sent")
        websocket_off()
        exit()

    elif message == "@reboot":
        if power_management:
            print("Reboot")
            websocket_off()
            if platform.system() == "Windows":
                call(["scripts\\reboot.bat"])
            else:
                call(["reboot"])

    elif message == "@poweroff":
        if power_management:
            print("Power off")
            websocket_off()
            if platform.system() == "Windows":
                call(["scripts\\poweroff.bat"])
            else:
                call(["poweroff"])

    else:
            # Send to arduino
            device.write(message)


# Websocket manager class
class ArduinoServerProtocol(WebSocketServerProtocol):
    # On connect we check if the user was banned
    def onConnect(self, request):
        # print(suspected_clients)
        print('Client connecting: '+self.peer)

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
            print("No password needed")
            if self not in clients:
                clients.append(self)

    # On open we ask for a password
    def onOpen(self):
        print("WebSocket connection open.")
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
            # print(message)
            if password is not False:
                # Check if client is registered
                if self in clients:
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
                                    self.sendMessage(str("@wrongpassword:"+str(suspected_clients[suspect]["retry"])+"/"+str(maxretry)).encode())
                                    print("Recorded suspect: " + str(suspected_clients[suspect]["retry"]))
                            else:
                                mess = str("@wrongpassword:1/"+str(maxretry))
                                self.sendMessage(mess.encode())
                                suspected = {"ip": ip, "time": time.time(), "retry": 1}
                                suspected_clients.append(suspected)
                                print('Recorded suspect: {0}'.format(ip))
            else:
                write(message)

    # On close, we remove user from approved list
    def onClose(self, wasClean, code, reason):
        global clients
        print("WebSocket connection closed: {0}".format(reason))
        if self in clients:
            clients.remove(self)


# Arduino send message list
def start_listen():
    global clients
    while True:
        if device.isConnected:
            data = False
            data = str(device.listen()).strip()
            if data is not "":
                print(data)
                for client in clients:
                    client.sendMessage(str.encode(data))

# We listen to arduino message in a thread
listener_thread = threading.Thread(target=start_listen)
listener_thread.daemon = True
listener_thread.start()

if secure:
    ws_type = "wss://"
else:
    ws_type = "ws://"

if local:
    interface = "localhost"
else:
    interface = ""

addr = ws_type+"0.0.0.0"+":"+port

# SSL server context: load server key and certificate
# We start the websocket here
print(addr)

factory = WebSocketServerFactory(addr)

if secure:
    contextFactory = ssl.DefaultOpenSSLContextFactory(ssl_dir+'/server.key',
                                                      ssl_dir+'/server.crt')
    listenWS(factory, contextFactory, interface=interface)
else:
    listenWS(factory, interface=interface)

factory.protocol = ArduinoServerProtocol
reactor.run()
