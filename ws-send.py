#!/usr/bin/python

import sys
import argparse
from websocket import create_connection
import ssl
import urlparse

VERSION = "v1.0"
# Arguments
parser = argparse.ArgumentParser(description="Send a message to a websocket")
parser.add_argument("-u", "--url", required="True",
                    help="Websocket url ex: ws://127.0.0.1:42000")
parser.add_argument("-m", "--message", required="True",
                    help="Message ex: /info")
parser.add_argument("-p", "--password", default="")
args = vars(parser.parse_args())
# TODO Add password management

ws = create_connection(args["url"], sslopt={"cert_reqs": ssl.CERT_NONE})

if args["password"] is not "":
    result =  ws.recv()
    ws.send(args["password"])

ws.send(args["message"])
print("LibreConnect ws_send - version " + VERSION)
print("By madnerd.org (https://github.com/madnerdorg/libreconnect)")
print("----------------------------------------------------------")
print("--->" + args["message"])
