#!/bin/bash
pip install pyinstaller
cd ..;pyinstaller --onefile connector.py;pyinstaller --onefile usb_scanner.py
