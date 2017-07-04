[English](https://madnerdorg.github.io/libreconnect/)

[![LibreConnect Banner](doc/img/libreconnect_banner.png)](https://github.com/madnerdorg/libreconnect/releases)    
[![Downloads](doc/img/lc_download.png)](https://github.com/madnerdorg/libreconnect/releases)    
[Télécharger](https://github.com/madnerdorg/libreconnect/releases) / [Aller sur madnerd.org](https://madnerd.org) / [Vidéos](https://www.youtube.com/channel/UCdtmROCsWKdaN7JEuqZoquA)

- [C'est quoi libreConnect ?](#cest-quoi-libreconnect-)
- [Appareils](#appareils)
- [Paramétrer LibreConnect](#paramétrer-libreconnect)
- [Comment libreConnect fonctionne](#comment-libreconnect-fonctionne)
- [Créer ses propres applications](doc/fr/applications.md)
- [Compiler LibreConnect](doc/fr/compile.md)
- [Utiliser libreConnect sur un Raspberry Pi](doc/fr/raspberrypi.md)]
- [Liens utiles / source](#liens-utiles--source)
- [License](#license)

# C'est quoi libreConnect ?
[![Video Demo](doc/img/libreconnect_youtube.jpg)](https://www.youtube.com/watch?v=RrZaXerJBO8)  
LibreConnect est un logiciel qui permet de contrôler des arduinos à l'aide de **websockets**.    
Brancher un arduino sur un ordinateur ou un Raspberry Pi et controlez le à l'aide de votre **navigateur web**        

![How does it works](doc/img/libreconnect_app.jpg)

**Aucun installation ou configuration n'est nécessaire**
* [Télécharger](https://github.com/madnerdorg/libreconnect/releases) libreConnect
* Cliquer sur **usb_scanner**
* Brancher votre Arduino en USB.
* Essayer votre appareil sur [madnerd.org/interface](http://madnerd.org/interface)    

# Appareils
[![Video Demo](doc/img/demo_youtube.jpg)](https://www.youtube.com/watch?v=7xJIdO-WGD4)

Voici les [appareils](doc/fr/devices.md) que j'ai fabriqué pour LibreConnect, ils ne coûtent pas cher et sont facile à fabriquer.     
Ils sont aussi facile à **recycler** et **améliorer**.    

[![Appareils](doc/img/devices_av.png)](doc/fr/devices.md)

Du moment que votre code Arduino est capable **d'envoyer/recevoir** des commandes à l'aide de l'USB.    
Vous pouvez l'utiliser avec libreconnect.    
![What is Arduino](doc/img/whatisarduino.png) 

Voilà quelques projets sympa , que vous pouvez faire avec libreConnect  
* [Contrôler des lampes et des prises de courants](http://madnerd.org/interface/homeautomation).
* Soyez prévenu quand vous recevez un appel , à l'aide de [tasker sur android](https://madnerdorg.github.io/leds/readme.fr)
* Contrôler un buzzer à l'aide de n'importe quel [logiciel de musique](https://madnerdorg.github.io/buzzer/readme.fr).
* Construire des appareils et les utiliser en pleine nature! [video](https://www.youtube.com/edit?o=U&video_id=sHwIgMWFc-8)
* Faire ses propres [applications web](http://madnerd.org/interface/editor) en utilisant uniquement son navigateur web

# Paramétrer LibreConnect

## Paramètres
Bien qu'l ne soit pas nécessaire de paramétrer libreConnect, vous pouvez utiliser des paramètres pour
* Utiliser votre ordinateur uniquement depuis votre ordinateur
* Chiffrer / Protégé à l'aide d'un mot de passe votre websocket
* Connectez n'importe quel arduino (ou périphériques série)

```
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
  --force              Connect any serial devices  
```

## Ne pas connecter au réseau
Si vous voulez utiliser libreConnect uniquement sur la machine sur laquelle il est branché, ajouter simplement **--local**.
> Il est recommandé de faire ceci **si vous n'êtes pas sur votre réseau.** 
>
```
usb_scanner --local
```
Vous pourrez toujours utiliser vos **applications web** 

## Connectez n'importe quel périphérique série.
Vous n'avez pas besoin de modifier votre code arduino pour utiliser **libreConnect**, utiliser **connector.exe** à la place de **usb_scanner.exe**
Comme libreConnect ne peut pas deviner le port série de votre arduino, vous devrez le préciser, ainsi que le **baudrate** et le **port websocket**:
```
./connector --serial "COM7" --baudrate 115200 --port 43100
```

Vous pouvez aussi utiliser la commande
```
usb_scanner --force --baudrate 9600
```
Ceci connectera tout les périphériques série avec un baudrate de 9600 en commençant par le port 40001

##  Mot de passe
Les **mot de passe** ne sont pour le moment qu'implémenter afin d'être tester, et de doivent pas être considéré comme sécurisé. 
Je vous recommande fortement d'utiliser une connexion chiffré où votre mot de passe sera envoyé **en clair** sur votre réseau.
Si vous ne pouvez pas utiliser des certificats SSL, utiliser un **mot de passe temporaire**

```
usb_scanner --password HorseBatteryStaple
```

Voici un code pour connecter un websocket avec un mot de passe.
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

###  Bannisement / Essai
Vous pouvez bannir une ip qui a entré trop de fois un mauvais mot de passe.
Par examples ici, tout ip qui aura échoué de rentrer un mot de passe 5 fois, ne pourra plus se connecter pendant 60 secondes.
``` 
usb_scanner --password HorseBatteryStaple --bantime 60 --retry 5
```

##  Chiffrement
Par défaut, les websockets ne sont pas chiffré.
Pour utiliser une connexion chiffré, il nous faut un **certificat SSL**

###  Certificate autosigné (self-signed)
Créer un certificat autosigné est relativement facile, toutefois, votre navigateur ne se connectera pas à un websocket chiffré avec un certificat autosigné.  
       
Il vous faut valider le certificat, en allant sur l'ip et le port de votre websocket : https://ip:port.    
Par example, https://localhost:42001

Un certificat SSL est disponible dans keys/ pour tester, attention, il vous faut recréer ce certificat pour vraiment avoir une communication protégé (car la clé privée est accessible publiquement)

Pour connecter vos websocket en SSL tapez:
```
usb_scanner --secure
```
Si vous voulez mettre les certificats dans un autre dossier que keys/, vous pouvez le changer comme ceci:
```
./usb_scanner --secure --keys "/etc/libreconnect/keys"
```

Dans **scripts/** il y a un scripts (openssl.bat) pour générer un nouveau certificat


###  Certificat Let's Encrypt
Vous pouvez aussi générer un certificat valide grâce à let's encrypt.     
Mais ceci est loin d'être simple et n'est utile que si vous accéder à votre websocket depuis internet.
 
Source: https://certbot.eff.org/#pip-other

* Il nous faut un domaine dns (**par example devices.example.org**) qui redirige vers votre adresse ip
* Il nous faut aussi ouvrir un **port 80**, depuis notre router
* Sur un terminal **Raspberry Pi** / **Linux**, tapez:
```    
wget https://dl.eff.org/certbot-auto
chmod a+x certbot-auto
```
Ceci va récupérer le programme pour générer un certificat.    
Après il nous faut générer le certificat manuellement
```
./certbot-auto certonly --manual -d devices.example.org
```
* Suivez les instructions, et lancer un serveur web temporaire sur un autre terminal
* Récupérer les certificats crées, et copiez les dans keys/

##  Allumer / Eteindre à distance
Si vous voulez pouvoir allumer/éteindre une machine à distance, vous pouvez utiliser --power
```
./usb_scanner --power
```

Puis envoyer sur le websocket:
```
Turn off server: @poweroff
Reboot server: @reboot
```

# Comment libreConnect fonctionne
LibreConnect , c'est deux scripts python compilé:    
![](doc/img/LibreConnect_software.png)     
* usb_scanner cherches des périphériques USB série qui viennent d'être branché.
* Puis leur envoie **/info**
* Si le périphérique réponds **device:port**,      
* Alors une instance de **connector.exe** est crée et connecte le port série à un websocket grâce à [autobahn](http://crossbar.io/autobahn/)   
           
![New device schematics](doc/img/lc_newdevice_schematics.png)

# [Créer ses propres applications](doc/fr/applications.md)

# [Compiler LibreConnect](doc/fr/compile.md)

# [Utiliser libreConnect sur un Raspberry Pi](doc/fr/raspberrypi.md)

# Liens utiles / source    
Crossbar.io - Echo_tls Autobahn example        
[https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_tls](https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_tls)  

Simplyautomationized.blogspot.fr      
5 ways to secure your raspberry pi's websocket server       
[http://simplyautomationized.blogspot.fr/2015/09/5-ways-to-secure-websocket-rpi.html](http://simplyautomationized.blogspot.fr/2015/09/5-ways-to-secure-websocket-rpi.html)

madnerd.org - Control Arduino with a portable app     
[http://www.instructables.com/id/UTest-Make-USB-Devices-With-Arduino/](http://www.instructables.com/id/UTest-Make-USB-Devices-With-Arduino/)

# License
* LibreConnect : MIT - Rémi Sarrailh [http://madnerd.org](http://madnerd.org)
* Autobahn : MIT - Crossbar.io [http://autobahn.ws/python/](http://autobahn.ws/python/)
* Pyserial : BSD-3 - Chris Liechti [https://github.com/pyserial/pyserial](https://github.com/pyserial/pyserial)
* Twisted : MIT - Glyph Lefkowitz [https://pypi.python.org/pypi/Twisted](https://pypi.python.org/pypi/Twisted)
* Icons / Images are from the [https://thenounproject.com/](https://thenounproject.com/) (Creative Commons By): [Complete licence](doc/img/licence.txt)
