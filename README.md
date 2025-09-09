

![Python Version](https://img.shields.io/python/required-version-toml?tomlFilePath=http%3A%2F%2Fraw.githubusercontent.com%2Fwsdoprado%2Fevent-driven-automation%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)

# Curso - Semana de Capacitação 11 - NIC.br

Este repositório contém os arquivos e instruções para o laboratório do curso da Semana de Capacitação do NIC.br.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de que o sistema possui:

- **Linux (Debian 12.10.0 netinst instalação limpa) - 1 host [16G RAM(ou mais), 50G Disco, 8vcpu (ou mais)]**
- Acesso a Internet para download de arquivos
- IDE para visualizar arquivos .py, compose.yml, Dockerfile. (VS Code, Pycharm)
  
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
cd /opt/event-driven-automation/
./install_dependencies.sh
```

## 📦 NetBox (IPAM/DCIM)

O NetBox será utilizado como fonte da verdade - NSOT

```bash
git clone -b release https://github.com/netbox-community/netbox-docker.git
```
```bash
cd netbox-docker
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

alterar o docker-compose.yml (depende de cada cenario)

```bash
start_period: 500s
timeout: 30s
interval: 30s
retries: 5
```

Para subir
```bash
docker compose up
```
ou
```bash
docker compose up -d
```

Definir ou alterar o usuário de acesso
```bash
docker compose exec netbox /opt/netbox/netbox/manage.py createsuperuser
```

O NetBox estará disponível em:
👉 http://localhost:8000

## 🌐 Nginx (HTTPS Proxy)

Crie a pasta para os certificados:
```bash
mkdir -p /opt/event-driven-automation/exercicio_nginx/certs
```

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/event-driven-automation/exercicio_nginx/certs/privkey.pem \
  -out /opt/event-driven-automation/exercicio_nginx/certs/fullchain.pem \
  -subj "/CN=localhost"
```

Alterar IP Address em /opt/event-driven-automation/nginx/conf.d/default.conf

```bash
nano /opt/event-driven-automation/exercicio_nginx/conf.d/default.conf
```

Subindo o container do NGINX
```bash
cd  /opt/event-driven-automation/exercicio_nginx/
docker compose up ou docker compose up -d
```

## 🧪 Laboratório com Containerlab

Baixe as imagens de Arista cEOS:
📂 Google Drive - Imagens de Laboratório
 - https://drive.google.com/drive/folders/1uLDcgJuoxOE7c4ZD3WsPwLmvPrJKqeLE

OBS: cEOS-lab-4.34.2F.tar.xz precisa estar no host do laboratório.
Dica: Transferir por SCP

# Criando o container para Arista cEOS
Importe a imagem do Arista cEOS:
```bash
docker import cEOS-lab-4.34.2F.tar.xz ceos:4.34.2F
```

# Criando o laboratório do curso
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


## Ambiente para executar os exercícios
### 🐍 Ambiente Python para execução dos scripts

Para executar os scripts em python é necessário criar um ambiente virtual e instalar as dependências.

Por padrão, o uv é instalado em ~/.local/bin. Para poder usá-lo de qualquer lugar no terminal, é necessário adicionar esse diretório ao PATH.
```bash
export PATH=$PATH:/root/.local/bin
```
Criar o ambiente virtual
```bash
uv venv
```
Ativar o ambiente virtual
```bash
source .venv/bin/activate
```
Instalar ou atualizar as dependências dentro do ambiente virtual
```bash
uv sync
```
Sair do ambiente virtual
```bash
deactivate
```

## 🖥️ Iniciando os Exercícios de Automação de Rede

Criar um arquivo .env.dev na raiz do projeto. E modificar os dados de acordo
```bash
cp .env.dev.example .env.dev
```
Esse arquivo será utilizado tanto nos exercícios quanto no projeto completo para fornecer os dados de acesso entre os serviços.

## 🖥️ Iniciando os Exercícios do FastAPI e webhook no Netbox
Para o exercício do FastAPI, ter o ambiente virtual python ativado a instância do Netbox
e subir o containers da API dentro da pasta exercicio_fastapi.
```bash
docker compose pull
```
```bash
docker compose up --build -d
```


## 🧩 Temporal

O Temporal será utilizado para orquestração das atividades.

```bash
cd /opt/event-driven-automation/exercicio_temporal
```

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

## 🧩 Projeto Final

```bash
cd /opt/event-driven-automation/projeto_completo
```

Build/Ativar containers
```bash
docker compose up --build -d | docker compose up --build 
```
Parar containers
```bash
docker stop temporal-worker-interface-1 temporal-api-webhook-1 temporal-worker-device-1 temporal-admin-tools temporal-ui temporal temporal-postgresql 
```
Remover containers
```bash
docker rm temporal-worker-interface-1 temporal-api-webhook-1 temporal-worker-device-1 temporal-admin-tools temporal-ui temporal temporal-postgresql -f
```

Verificar Logs em:
```bash
cat /opt/event-driven-automation/projeto_completo/logs/api/fastapi.log
cat /opt/event-driven-automation/projeto_completo/logs/temporal/worker-device.log
cat /opt/event-driven-automation/projeto_completo/logs/temporal/worker-interface.log
```
