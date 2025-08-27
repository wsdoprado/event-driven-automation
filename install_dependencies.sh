apt install sudo -y

# Atualizar pacotes
sudo apt update -y

# Instalar dependências
sudo apt install -y ca-certificates curl gnupg lsb-release

# Criar pasta para a chave
sudo mkdir -p /etc/apt/keyrings

# Baixar e adicionar a chave GPG do Docker
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Adicionar o repositório Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update -y
sudo apt install -y docker-ce 
sudo apt install -y docker-ce-cli 
sudo apt install -y containerd.io 
sudo apt install -y docker-compose-plugin
sudo apt install -y curl

docker --version
docker compose version

curl -sL https://containerlab.dev/setup | sudo -E bash -s "all"
