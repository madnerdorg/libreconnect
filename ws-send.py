#!/usr/bin/python

import sys
import argparse
from websocket import create_connection
import ssl
import urlparse

VERSION = "1.1"
# Arguments
parser = argparse.ArgumentParser(description="Send a message to a websocket")
parser.add_argument("-v","--version", action='version', version="ws_send - v"+VERSION)
parser.add_argument("-u", "--url", required="True",
                    help="Websocket url ex: ws://127.0.0.1:42000")
parser.add_argument("-m", "--message", required="True",
                    help="Message ex: /info")
parser.add_argument("-p", "--password", default="")
parser.add_argument("-s", "--silent",  action="store_true", default=False)
args = vars(parser.parse_args())

send_password = True
send_message = True
websocket_status = True

if args["silent"]:
    verbose = False
else:
    verbose = True

if verbose:
    print("LibreConnect ws_send - v" + VERSION)
    print("By madnerd.org (https://github.com/madnerdorg/libreconnect)")
    print("----------------------------------------------------------")
    print("--->" + args["message"])

try:
    ws = create_connection(args["url"], sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.settimeout(1)
except:
    print("Unable to connect to websocket")
    websocket_status = False

if websocket_status:
    if args["password"] is not "":
        try:
            password_message =  ws.recv()
        except:
            print("No request for password from websocket")
            send_password = False

        if send_password:
            if verbose: print(password_message)
            if password_message == "@password":
                ws.send(args["password"])
                password_result = ws.recv()
                if verbose:print(password_result)
                if password_result != "@logged":
                    send_message = False
            else:
                print("Not a password prompt")
        
    if send_message:
        ws.send(args["message"])
        try:
            print(ws.recv())
        except:
            print("No answer")
            sys.exit(2)
    else:
        print("Message not sent (Wrong Password)")
        sys.exit(126)
else:
    sys.exit(1)


