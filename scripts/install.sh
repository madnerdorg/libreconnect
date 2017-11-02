#!/bin/bash
apt-get install pip
pip install pyserial
pip install twisted
pip install autobahn
pip install service_identity
pip install urlparse2
pip install websocket-client
pip install pyinstaller
pip install argon2_cffi

#Fix for TLSVersion.TLSv1_1: SSL.OP_NO_TLSv1_1

apt-get remove python-openssl
pip install pyopenssl
