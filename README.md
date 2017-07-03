[Français](readme_fr.md)


[![LibreConnect Banner](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/libreconnect_banner.png)](https://github.com/madnerdorg/libreconnect/releases) 
[![Downloads](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/lc_download.png)](https://github.com/madnerdorg/libreconnect/releases) 
[Download](https://github.com/madnerdorg/libreconnect/releases) / [Go to madnerd.org](https://madnerd.org) / [Videos](https://www.youtube.com/channel/UCODy2WlJf8FOgJzuKE14LkA)


<!-- TOC -->

- [What is libreConnect](#what-is-libreconnect)
- [Devices](#devices)
- [Setup LibreConnect](#setup-libreconnect)
    - [Do not connect to network](#do-not-connect-to-network)
    - [Connect any arduino and other serial devices](#connect-any-arduino-and-other-serial-devices)
    - [Password](#password)
    - [Encryption](#encryption)
    - [Power Management](#power-management)
- [How does libreConnect works](#how-does-libreconnect-works)
- [Build your own applications](https://github.com/madnerdorg/libreconnect/blob/master/doc/en/applications.md)
- [Compile LibreConnect](https://github.com/madnerdorg/libreconnect/blob/master/doc/en/compile.md)
- [Use libreConnect on a Raspberry Pi](https://github.com/madnerdorg/libreconnect/blob/master/doc/en/raspberrypi.md)
- [Useful links / source](#useful-links--source)
- [License](#license)

<!-- /TOC -->


# What is libreConnect
[![Video Demo](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/libreConnect_youtube.jpg)](https://www.youtube.com/watch?v=7xJIdO-WGD4) 
LibreConnect is an application to control arduino using **websockets**. 
Plug an arduino on a computer or a Raspberry Pi, and control it using your **web browser**
![How it works](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/libreconnect_app.jpg)


**No installation or settings are required**
* [Download](https://github.com/madnerdorg/libreconnect/releases) libreConnect
* Click on **usb_scanner**
* Plug your arduino on a USB port.
* Try your device at [madnerd.org/interface](http://madnerd.org/interface) 


# Devices
[![Video Demo](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/demo_youtube.jpg)](https://www.youtube.com/watch?v=7xJIdO-WGD4)


Here are the [devices]https://github.com/madnerdorg/libreconnect/blob/master/doc/en/devices.md) i build for LibreConnect, they are cheap and easy to make. 
They are also easy to **recycle** and **upgrade**. 


[![Devices](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/devices_av.png)]https://github.com/madnerdorg/libreconnect/blob/master/doc/en/devices.md)


As long as your arduino code is able **send/receive** commands using USB serial. 
You can use it with libreconnect. 
![What is Arduino](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/whatisarduino.png) 


Here are some cool things you can do with libreConnect 
* [Control lamps and power outlets](http://madnerd.org/interface/homeautomation).
* Get notified when you received a call , using [tasker for android](https://github.com/madnerdorg/leds/apps)
* Control a buzzer using any [music software](https://github.com/madnerdorg/buzzer).
* Build and use devices in the wild! [video](https://www.youtube.com/watch?v=UThz91hRcYQ)
* Build your own [web applications]() using your web browser


# Setup LibreConnect


## Arguments
While you don't need to setup libreConnect, you can use arguments to
* Use your arduino only on your computer
* Encrypt / Password-protect your websocket
* Connect any arduino (or serial devices). 


```
-h, --help show this help message and exit
--serial SERIAL Serial port
--port PORT Websocket port
--secure Add SSL
--power Add power management (@reboot/@poweroff)
--password PASSWORD Password for the websocket
--local Websocket will only be available locally
--bantime BANTIME Seconds before a ban user is unbanned
--retry RETRY Number of retry before ban
--baudrate BAUDRATE Baudrate for serial com
--keys KEYS folders where SSL certificates are
--force Connect any serial devices 
```


## Do not connect to network
If you want to use libreConnect only on the machine where it is plugged, just add **--local**. 
This is recommended if you are **not on your own network**. 
You can still use your **web applications**. 
```
usb_scanner --local
```


## Connect any arduino and other serial devices
You don't need to modify your arduino code to use **libreConnect**, just use **connector.exe** directly. 
As libreConnect can't guess the serial port of your device,
You will need to specify the **serial port** / **baudrate** and **websocket port**.
```
./connector --serial "COM7" --baudrate 115200 --port 43100
```


You can also use this command
```
usb_scanner --force --baudrate 9600
```
This will connect any serial devices using baudrate 9600 starting with 40001.


## Password
Passwords are implemented for **testing**, and should not be considered secure. 
I recommended using encrypted communication or your password will be sent **unencrypted** on your network. 
If encryption is not possible, use **temporary password** and don't leave your devices unattended. 
Password will later be saved, as a **hash** inside a setting file. 


```
usb_scanner --password HorseBatteryStaple
```


Here is how to log into your websocket.
```
password = HorseBatteryStaple
ws = new WebSocket("ws://localhost:42000");
ws.onmessage = ws_onmessage;


function ws_onmessage(event){
if(event.data == "@password"){
ws.send(password);
}
}
```


### Ban time / Retry
You can ban ip that enters the wrong password too many times. 
For example, here you can disconnect any user that failed to enter a password 5 times for 60 seconds.
``` 
usb_scanner --password HorseBatteryStaple --bantime 60 --retry 5
```


## Encryption
By default, websockets are unencrypted
To use an encrypted connection you need a **SSL Certificate**.


### Self Signed Certificate
You can easily create a self-signed certificate, but your web browser will not connect to it before you validate it. 


To validate a certificate , you need to go to the ip/port of your websocket:
https://ip:port 
For example, https://localhost:42001


An SSL Certificate is available in **keys/** if you want to test it, but it should not be considered secure, you need to build your own **SSL certificate**.


To connect your websocket in SSL, type:
```
usb_scanner --secure
```
You can use another folder for your certificate, by typing:
```
./usb_scanner --secure --keys "/etc/libreconnect/keys"
```


In **scripts/**, you can find a script (openssl.bat) to generate a new certificate.


### Let's encrypt Certificate
You can also generate a valid certificate, using let's encrypt, but this isn't an easy procedure and will only work if you use your websocket on the internet. 


Source: https://certbot.eff.org/#pip-other


* You need to have a DNS domain (**for examples devices.example.org**) that redirected to your ip address
* Open **port 80**, on your router
* On a **Raspberry Pi** / **Linux** terminal, type:
``` 
wget https://dl.eff.org/certbot-auto
chmod a+x certbot-auto
```
This will download the software that will generate our certificate.
Then you need to generate your certificate manually type:
```
./certbot-auto certonly --manual -d devices.example.org
```
* Follow instructions, start a temporary web server with another terminal.
* Get certificate files, and copy it inside **keys/**


## Power Management
If you want to be able to restart/stop your computer remotely, you can use --power
```
./usb_scanner --power
```


Then send using the websocket:
```
Turn off server: @poweroff
Reboot server: @reboot
```


# How does libreConnect works
LibreConnect is two compiled python scripts: 
![LibreConnect Software](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/LibreConnect_software.png) 
* usb_scanner search for new USB serial devices plugged on your computer. 
* It sends **/info** to each connected devices
* If the device returns **device:port**, 
* it starts an instance of **connector.exe** to connect a serial port to a websocket using [autobahn](http://crossbar.io/autobahn/) 
![](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/lc_newdevice_schematics.png)


# [Build your own applications](https://github.com/madnerdorg/libreconnect/blob/master/doc/en/applications.md)


# [Compile LibreConnect](https://github.com/madnerdorg/libreconnect/blob/master/doc/en/compile.md)


# [Use libreConnect on a Raspberry Pi](https://github.com/madnerdorg/libreconnect/blob/master/doc/en/raspberrypi.md)


# Useful links / source 
Crossbar.io - Echo_tls Autobahn example 
https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_tls 


Simplyautomationized.blogspot.fr 
5 ways to secure your raspberry pi's websocket server 
http://simplyautomationized.blogspot.fr/2015/09/5-ways-to-secure-websocket-rpi.html 


madnerd.org - Control Arduino with a portable app 
http://www.instructables.com/id/UTest-Make-USB-Devices-With-Arduino/ 


# License
* LibreConnect : MIT - Rémi Sarrailh (http://madnerd.org)
* Autobahn : MIT - Crossbar.io (http://autobahn.ws/python/)
* Pyserial : BSD-3 - Chris Liechti (https://github.com/pyserial/pyserial)
* Twisted : MIT - Glyph Lefkowitz (https://pypi.python.org/pypi/Twisted)
* Icons / Images are from the noun project (Creative Commons By): [licence.txt](https://github.com/madnerdorg/libreconnect/raw/master/doc/img/licence.txt)

