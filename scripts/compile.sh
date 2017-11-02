#!/bin/bash
pip install pyinstaller
cd ..;pyinstaller --onefile connector.py;pyinstaller --onefile usb_scanner.py;pyinstaller --onefile --icon=LibreConnect_icon.ico ws-send.py;pyinstaller --onefile --icon=LibreConnect_icon.ico generate_password.py
