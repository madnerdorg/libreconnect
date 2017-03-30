LibreConnect : Transform a serial port into a websocket
--------------------------------------------------------------
* Author : Rémi Sarrailh (madnerd.org)
* Email : remi@madnerd.org
* License : MIT

![libreconnect](https://github.com/madnerdorg/libreconnect/blob/master/doc/libreconnect.jpg?raw=true)
![libreconnect_devices](https://github.com/madnerdorg/libreconnect/blob/master/doc/libreconnect_devices.jpg?raw=true)

# Presentation
LibreConnect scans serial ports and if it find a device that's answers to "/info" with     "devicename:websocketport" forward all serial messages thought a websocket server.      

It can then be access using a web browser or a client application whether it is connected locally / on a network or on the internet.      

I split LibreConnect in two software : usb_scanner / connector so you can use it without the device     identification which makes it compatible with any arduino projects.      

This project is based on autobahn / python, it has been tested on Raspberry Pi, Windows / Ubuntu / Synology NAS / Orange Pi.      
I compiled it using pyinstaller so it can works without any installation, just copy the executable and you are good to go!    

# Usage
All arguments send to usb_scanner will be transfer to connector.    
You don't need to use any argument for it to works, just start usb_scanner.    
```
usage: connector.py [-h] [--serial SERIAL] [--port PORT] [--secure] [--power]     
                    [--password PASSWORD] [--local] [--bantime BANTIME]    
                    [--retry RETRY] [--baudrate BAUDRATE] [--keys KEYS]     

Transform a serial port into a websocket    

optional arguments:    
  -h, --help           show this help message and exit   
  --serial SERIAL      Serial port   
  --port PORT          Websocket port   
  --secure             Add SSL   
  --power              Add power management (@reboot/@poweroff)   
  --password PASSWORD  Password for the websocket   
  --local              Websocket will only be available locally   
  --bantime BANTIME    Seconds before a ban user is unbanned   
  --retry RETRY        Number of retry before ban  
  --baudrate BAUDRATE  Baudrate for serial com   
  --keys KEYS          folders where SSL certificates are   
```
# Downloads
The easiest way to use this software is to download the compiled version.    
You can find it here:    
https://github.com/madnerdorg/libreconnect/releases

# Use password
You can use a password, just send it using the websocket.    
For example:    
```
usb_scanner --password HorseBatteryStaple
```
As for now you can only use the same password for each connector.    

# IP Ban
I also implement ip ban to disallow force brute.
```
usb_scanner --bantime seconds
```

# Power management
If you want to be able to turn on/off your system (this is useful if you don't have access to a terminal for ex.)    
You can use special commands.
```
usb_scanner --power
```
Then send using the websocket:
```
Turn off server: @poweroff
Reboot server: @reboot
```

# Use python version
I recommended using miniconda if you are on windows (https://conda.io/miniconda.html)  
This will work on python 2/3.

## Dependencies
```
pip install pyserial
pip install twisted
pip install autobahn
pip install service_identity
```

# Generate SSL Certificate
You should use a SSL certificate, or messages will be send in clear text.   

You need to validate the ssl certificate in your browser.         
Just go to https://ip:port to do this    
You can use the script openssl to autogenerate a certificate.   
You can use Let's encrypt if you want a valid certificate but you will only be able   
to use it properly if your websocket is exposed to the internet.


```
openssl genrsa -out keys/server.key 2048     
openssl req -new -key keys/server.key -out keys/server.csr     
openssl x509 -req -days 3650 -in keys/server.csr -signkey keys/server.key -out keys/server.crt    
openssl x509 -in keys/server.crt -out keys/server.pem    
```

# Compile
I used pyinstaller to compile, it seems it doesn't works with python 3.6    
Untested solution : http://stackoverflow.com/questions/41559171/pyinstaller-and-python3-6-tuple-index

```
pip install pyinstaller
pip install pypiwin32
```

# Source    
Crossbar.io - Echo_tls Autobahn example        
https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_tls      

Simplyautomationized.blogspot.fr      
5 ways to secure your raspberry pi's websocket server       
http://simplyautomationized.blogspot.fr/2015/09/5-ways-to-secure-websocket-rpi.html       

madnerd.org - Control Arduino with a portable app     
http://www.instructables.com/id/UTest-Make-USB-Devices-With-Arduino/      

# License
* Autobahn : MIT (http://autobahn.ws/python/)
* Pyserial : BSD-3 (https://github.com/pyserial/pyserial)
* Twisted : MIT (https://pypi.python.org/pypi/Twisted)
