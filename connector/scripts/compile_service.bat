@echo off
cd ..
pip install pyinstaller
pyinstaller --onefile --noconsole madnerd_connector.py 