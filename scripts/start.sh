#!/bin/bash
echo -n "Device name:"
read name
echo -n "Port:"
read port
python connector.py --port "$port" --device "$name"
