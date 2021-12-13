sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/server-self.key -out /etc/ssl/certs/server-self.crt -subj "/C=US/ST=VA/L=FFX/O=GMU/OU=SWE681/CN=192.168.1.174"

sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
