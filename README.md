# Curso - Semana de Capacitação 11 - NIC.br

Este repositório contém os arquivos e instruções para o laboratório do curso da Semana de Capacitação do NIC.br.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de que o sistema possui:

- **Linux (Debian 12.10.0 netinst instalação limpa) - 3 hosts [netbox, automation, containerlab]**
- Acesso a Internet para Download de Arquivos 
  
## 🚀 Instalação das Dependências

Instalac̨ão do GIT

```bash
apt install git -y
```

Git clone do Repositorio

```bash
cd /opt
git clone https://github.com/wsdoprado/event-driven-automation.git
```

Execute o script abaixo para instalar as dependências necessárias:

```bash
./install_dependencies.sh
```


🧪 Laboratórios com Containerlab

Baixe as imagens de Arista e Cisco IOS:
📂 Google Drive - Imagens de Laboratório
 - https://drive.google.com/drive/folders/1uLDcgJuoxOE7c4ZD3WsPwLmvPrJKqeLE

Clone o repositório vrnetlab:
```bash
git clone https://github.com/hellt/vrnetlab.git
```

Importe a imagem do Arista cEOS:
```bash
docker import cEOS64-lab-4.32.0F.tar.xz ceos:4.32.0F
```

Suba o laboratório de exemplo:
```bash
containerlab deploy -t lab-semanacap.yml
```

Destrua um laboratório específico:
```bash
containerlab destroy -t lab-semanacap.yml --cleanup
```

Liste e inspecione laboratórios ativos:
```bash
containerlab inspect --all
```

🐍 Ambiente Python para execução dos scripts

Para executar os scritps em python é necessário criar um ambiente virtual e instalar as dependências.
```bash
uv venv
```
```bash
source .venv/bin/activate
```
```bash
uv sync
```

Sair do ambiente virtual
```bash
deactivate
```

📦 NetBox (IPAM/DCIM)

O NetBox será utilizado como fonte de dados de rede.

```bash
git clone -b release https://github.com/netbox-community/netbox-docker.git
cd netbox-docker
tee docker-compose.override.yml <<EOF
services:
  netbox:
    ports:
      - 8000:8080
EOF
docker compose pull
```

alterar o docker-compose.yml (depende de cada cenario)

```bash
start_period: 500s
timeout: 30s
interval: 30s
retries: 5
```

```bash
docker compose up ou docker compose up -d
```
```bash
docker compose exec netbox /opt/netbox/netbox/manage.py createsuperuser
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

Alterar IP Address em /opt/event-driven-automation/nginx/conf.d/default.conf

```bash
nano /opt/event-driven-automation/nginx/conf.d/default.conf
```

🖥️ Iniciando os Exercícios de Automação de Rede

Criar um arquivo .env na raiz do projeto
```bash
# Arquivo: .env
# URL do NetBox (ex.: http://localhost:8000)
NETBOX_URL=http://localhost:8000

# Token de API do NetBox
NETBOX_TOKEN=seu_token_aqui

# Usuário SSH dos dispositivos
USER_DEVICE=admin

# Senha SSH dos dispositivos
PASSW_DEVICE=sua_senha_aqui
```

🧩 Temporal

O Temporal será utilizado para orquestração das atividades.
Subir o Temporal
```bash
docker compose pull
```
```bash
docker compose up --build -d
```

A interface do Temporal (Temporal UI) estará disponível em 👉 http://localhost:8080

Execução do worker (lembrando de está no ambiente virtual python)

```bash
python -m workers.worker
```

Execução do client com a solicitação de workflow (lembrando de está no ambiente virtual python)

```bash
python client.py
```




  
