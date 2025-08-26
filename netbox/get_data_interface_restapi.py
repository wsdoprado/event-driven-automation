import os, requests, urllib3
from dotenv import load_dotenv

"""
Código	                          Tipo	        Descrição
200     OK	                    Sucesso	    Requisição realizada corretamente.
201     Created	                Sucesso	    Recurso criado com sucesso (POST).
204     No Content	            Sucesso	    Requisição bem-sucedida, mas sem conteúdo.
400     Bad Request	            Cliente	    Requisição mal-formada (ex.: parâmetros inválidos).
401     Unauthorized	        Cliente	    Token ou credenciais ausentes ou inválidas.
403     Forbidden	            Cliente	    Usuário não tem permissão para acessar o recurso.
404     Not Found	            Cliente	    Recurso não encontrado.
405     Method Not Allowed	    Cliente	    Método HTTP não permitido para o endpoint.
409     Conflict	            Cliente	    Conflito de dados (ex.: criar recurso que já existe).
422     Unprocessable Entity	Cliente	    Dados enviados são inválidos ou incompletos.
500     Internal Server Error	Servidor	Erro interno da API.
502     Bad Gateway	            Servidor	API fora do ar ou indisponível 
503     Service Unavailable     Servidor    API fora do ar ou indisponível
"""

# ----------------------------------------------
# Carregar variáveis de ambiente do arquivo .env
# ----------------------------------------------
load_dotenv()

# Desabilita avisos de segurança SSL/TLS (não recomendado em produção)
urllib3.disable_warnings() #não mostra warnings de segurança relacionados a SSL/TLS

NETBOX_URL = os.getenv("NETBOX_URL")     # URL do NetBox, ex.: https://netbox.example.com
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN") # Token de API do NetBox

# Validação básica para garantir que as variáveis existam
if not NETBOX_URL or not NETBOX_TOKEN:
    raise ValueError("Configure NETBOX_URL e NETBOX_TOKEN no .env")

# Headers padrão para requisições GraphQL/REST API
HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}", # Autenticação via token
    "Content-Type": "application/json"        # Informar que o payload é JSON
}

# Função para consumir devices
def get_devices(params=None):
    """
    params: dict opcional para filtros, ex: {"site": "sp-site", "role": "pe"}
    """
    url = f"{NETBOX_URL}/api/dcim/devices/"

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        data = response.json()  # converte o corpo da resposta em dict/list
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao consumir API: {e}")
    return data['results']

def get_interfaces(device_id):
    """
    Coleta as interfaces de um device específico no NetBox.

    Args:
        device_id (int): ID do device no NetBox

    Returns:
        list: Lista de interfaces (dicionários)
    """
    
    url = f"{NETBOX_URL}/api/dcim/interfaces/"
    
    try:
        params = {"device_id": device_id}

        response = requests.get(url, headers=headers, params=params, verify=False)
        data = response.json()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao consultar interfaces: {e}")

    return data['results']

# ----------------------------------------------
# Execução principal do script
# ----------------------------------------------
if __name__ == "__main__":
    devices = get_devices()
    
    for device in devices:
        if device.get('primary_ip'):
            ip_address = device['primary_ip']['address']
            ip_address = ip_address.split("/")[0]  # pega só o IP sem máscara
        else:
            ip_address = "N/A"

        device_id = device['id']

        interface_list = get_interfaces(device_id)
        
        interfaces = []
        for interface in interface_list:
            iface = {
                "name": interface.get('name', 'N/A'),
                "description": interface.get('description', ''),
                "mtu": interface.get('mtu', 'N/A'),
                "mac_address": interface.get('mac_address', 'N/A')
            }
            
            interfaces.append(iface)
        print(f"{device['name']} - Site: {device['site']['name']} - Role: {device['role']['name']} - Tenant: {device['tenant']['name']} - MGMT: {ip_address} - Interfaces: {interfaces}")