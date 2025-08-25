# event-driven-automation
Curso para Semana de Capacitação 11 - NIC.br

CONTAINERLAB:

- containerlab deploy -t lab02.yml

- containerlab destroy -t topo-xrv9k.yml --cleanup

- containerlab destroy -a --yes

-containerlab inspect --all

NGINX:

- Criar Pasta Certs dentro de nginx
- openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /opt/nginx/certs/privkey.pem -out /opt/nginx/certs/fullchain.pem -subj "/CN=localhost"
