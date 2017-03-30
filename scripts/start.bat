@echo off
cd ..
echo "-- Arduino Connector -- Unsecure mode"
set /p name="Device Name: "
set /p port="Port: "

python connector.py --port "%port%" --device "%name%" 
pause