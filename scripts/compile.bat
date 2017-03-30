@echo off
cd ..
pip install pyinstaller
pyinstaller --onefile connector.py
