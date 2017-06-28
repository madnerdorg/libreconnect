@echo off
echo Generating SSL certificate...
cd ..
scripts\openssl genrsa -out keys/privkey.pem 4096
pause
scripts\openssl req -new -key keys/privkey.pem -out keys/request.csr -config "scripts\openssl.cnf"
pause
scripts\openssl x509 -req -days 3650 -in keys/request.csr -signkey keys/privkey.pem -out keys/cert.pem
pause
cd scripts
