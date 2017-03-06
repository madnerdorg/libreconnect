#!/usr/bin/python
# Madnerd Connector
# Licence MIT

# Connect Arduino Serial to a Websocket
# python madnerd_connector.py port device_name
# python madnerd_connector.py 42001 UTest
# See arduino code example here : https://github.com/pigetArduino/utest#arduino

import sys
import time
import os
import serial
import json
import string
import threading
from websocket_server import WebsocketServer
import sys
from lib import USB

if len(sys.argv) == 3:
    socket_port=int(sys.argv[1])
    device_type=sys.argv[2]
else:
    socket_port = 42001
    device_type = "UTest"

device_name = "" #Device name in Windows
#device_type = "ULed" #Device type (in the arduino sketch)
device_return_string = "OK" #Answer when a response is correct
device_baudrate = 115200 #Baudrate
usb = USB.Device(device_name,device_type,device_return_string,device_baudrate,False)

"""
WebSocket
"""
# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    #server.send_message_to_all("Connected on Arduino")


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
    if message == "websocket_stop":
        print("Exit application sent")
        server.server_close()
        os._exit(0)
    print(message)

    writeThread = threading.Thread(target=write,args=(message,))
    writeThread.daemon = True 
    writeThread.start()

def write(message):
    print(message)
    usb.write(message + "\n")

PORT=socket_port
server = WebsocketServer(PORT, host='0.0.0.0')
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)

def start_server():
    server.run_forever()

server_thread = threading.Thread(target=start_server)
server_thread.daemon = True 
server_thread.start()


def start_listen():
    while True:
        if usb.isConnected:
            data = False
            data = str(usb.listen()).strip()
            if data is not "":
                print(data)
                server.send_message_to_all(data) 

listener_thread = threading.Thread(target=start_listen)
listener_thread.daemon = True 
listener_thread.start()

try:
    while True:
        time.sleep(0.025)

except KeyboardInterrupt:
    print("Closing Collector : Keyboard Interrupt")
    # server_socket.close()
    usb.close()
    os._exit(0)
