Madnerd Connector : Transform a serial port into a websocket
--------------------------------------------------------------
* Author : Rémi Sarrailh (madnerd.org)
* Email : remi@madnerd.org
* License : MIT

# Usage
usage: connector.py [-h] [--port PORT] [--device DEVICE] [--secure]    
                    [--password PASSWORD] [--local] [--bantime BANTIME]     
                    [--retry RETRY] [--name NAME] [--baudrate BAUDRATE]    

Transform a serial port into a websocket    

optional arguments:    
  -h, --help           show this help message and exit   
  --port PORT          Websocket port    
  --device DEVICE      Device name   
  --secure             Add SSL    
  --password PASSWORD  Password for the websocket    
  --local              Websocket will only be available locally   
  --bantime BANTIME    Seconds before a ban user is unbanned   
  --retry RETRY        Number of retry before ban    
  --name NAME          USB identification   
  --baudrate BAUDRATE  Baudrate for serial com    

# Generate SSL Certificate
You need to validate the ssl certificate in your browser.     
Just go to https://ip:port to do this      

openssl genrsa -out keys/server.key 2048     
openssl req -new -key keys/server.key -out keys/server.csr     
openssl x509 -req -days 3650 -in keys/server.csr -signkey keys/server.key -out keys/server.crt    
openssl x509 -in keys/server.crt -out keys/server.pem    

# Source    
Crossbar.io - Echo_tls Autobahn example        
https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_tls      

Simplyautomationized.blogspot.fr      
5 ways to secure your raspberry pi's websocket server       
http://simplyautomationized.blogspot.fr/2015/09/5-ways-to-secure-websocket-rpi.html       

madnerd.org - Control Arduino with a portable app     
http://www.instructables.com/id/UTest-Make-USB-Devices-With-Arduino/      
