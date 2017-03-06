#!/bin/bash
echo -n "Device name:"
read name
echo -n "Port:"
read port
python madnerd_connector.py "$port" "$name"
