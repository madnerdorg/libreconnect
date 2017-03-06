@echo off
cd ..
set /p name="Device Name: "
set /p port="Port: "

python connector.py "%port%" "%name%" 
pause