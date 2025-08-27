# Curso - Semana de Capacitação 11 - NIC.br

Este repositório contém os arquivos e instruções para o laboratório do curso da Semana de Capacitação do NIC.br.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de que o sistema possui:

- **Linux (Debian 12 instalacao limpa)**
- Acesso a Internet para Download de Arquivos 
  
## 🚀 Instalação das Dependências

Execute o script abaixo para instalar as dependências necessárias:

```bash
./install_dependencies.sh
```

🧪 Laboratórios com Containerlab

Baixe as imagens necessárias:
📂 Google Drive - Imagens de Laboratório
 - https://drive.google.com/drive/folders/1uLDcgJuoxOE7c4ZD3WsPwLmvPrJKqeLE

Clone o repositório vrnetlab:
- git clone https://github.com/hellt/vrnetlab.git

Importe a imagem do Arista cEOS:
- docker import cEOS64-lab-4.32.0F.tar.xz ceos:4.32.0F

Suba o laboratório de exemplo:
- containerlab deploy -t lab02.yml

Destrua um laboratório específico:
- containerlab destroy -t topo-xrv9k.yml --cleanup

Liste e inspecione laboratórios ativos:
- containerlab inspect --all

📦 NetBox (IPAM/DCIM)

O NetBox será utilizado como fonte de dados de rede.

Clone o repositório oficial do NetBox com suporte a Docker:
```bash
git clone -b release https://github.com/netbox-community/netbox-docker.git
```

```bash
tee docker-compose.override.yml <<EOF
services:
  netbox:
    ports:
      - 8000:8080
EOF
```

```bash
docker compose pull
```

```bash
docker compose up
```

O NetBox estará disponível em:
👉 http://localhost:8000

🌐 Nginx (HTTPS Proxy)

Crie a pasta para os certificados:
```bash
mkdir -p /opt/event-driven-automation/nginx/certs
```

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/event-driven-automation/nginx/certs/privkey.pem \
  -out /opt/event-driven-automation/nginx/certs/fullchain.pem \
  -subj "/CN=localhost"
```

  
