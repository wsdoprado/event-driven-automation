# event-driven-automation
Curso para Semana de Capacitação 11 - NIC.br

NGINX:

- Criar Pasta Certs dentro de nginx
- openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /opt/nginx/certs/privkey.pem -out /opt/nginx/certs/fullchain.pem -subj "/CN=localhost"
