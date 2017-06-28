@echo off
cd ..
pyinstaller --onefile --icon=LibreConnect_icon.ico connector.py
pyinstaller --onefile --icon=LibreConnect_icon.ico usb_scanner.py
pyinstaller --onefile --icon=LibreConnect_icon.ico ws-send.py
cd scripts