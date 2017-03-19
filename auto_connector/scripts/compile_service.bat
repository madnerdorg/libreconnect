@echo off
cd ..
pip install pyinstaller
pyinstaller --onefile --noconsole connector.py 