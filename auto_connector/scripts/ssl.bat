@echo off
echo Generating SSL certificate...
cd ..
scripts\openssl genrsa -out keys/server.key 2048
scripts\openssl req -new -key keys/server.key -out keys/server.csr -config "scripts\openssl.cnf"
scripts\openssl x509 -req -days 3650 -in keys/server.csr -signkey keys/server.key -out keys/server.crt
scripts\openssl x509 -in keys/server.crt -out keys/server.pem
pause
