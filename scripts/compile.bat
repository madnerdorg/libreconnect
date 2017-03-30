@echo off
cd ..
pip install pyinstaller
pip install pypiwin32
pyinstaller --onefile connector.py
pyinstaller --onefile usb_scanner.py
