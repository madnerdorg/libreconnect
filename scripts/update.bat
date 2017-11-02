@echo off
cd ..
pip install pyserial --upgrade
pip install twisted --upgrade
pip install autobahn --upgrade
pip install service_identity --upgrade
pip install urlparse2 --upgrade
pip install websocket-client --upgrade
pip install pyinstaller --upgrade
pip install pypiwin32 --upgrade
pause
cd scripts