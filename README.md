# event-driven-automation
Curso para Semana de Capacitação 11 - NIC.br

INSTALAR DEPENDENCIAS:

./install_dependencies.sh

CONTAINERLAB:

imagens: https://drive.google.com/drive/folders/1uLDcgJuoxOE7c4ZD3WsPwLmvPrJKqeLE?usp=sharing
- git clone https://github.com/hellt/vrnetlab.git

- docker import cEOS64-lab-4.32.0F.tar.xz ceos:4.32.0F

- containerlab deploy -t lab02.yml

- containerlab destroy -t topo-xrv9k.yml --cleanup

- containerlab destroy -a --yes

- containerlab inspect --all

NETBOX:

git clone -b release https://github.com/netbox-community/netbox-docker.git
cd netbox-docker
tee docker-compose.override.yml <<EOF
services:
  netbox:
    ports:
      - 8000:8080
EOF
docker compose pull
docker compose up

NGINX:

- Criar Pasta Certs dentro de nginx
- openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /opt/nginx/certs/privkey.pem -out /opt/nginx/certs/fullchain.pem -subj "/CN=localhost"
  
