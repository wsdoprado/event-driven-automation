import os
import requests
from dotenv import load_dotenv
import urllib3

# ----------------------------------------------
# Carregar variáveis de ambiente do arquivo .env
# ----------------------------------------------
load_dotenv()

# Desabilita avisos de segurança SSL/TLS (não recomendado em produção)
urllib3.disable_warnings()

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

# ----------------------------------------------
# Função para consultar devices via GraphQL
# ----------------------------------------------
def get_data_device(device_id=None):
    """
    Consulta devices no NetBox via GraphQL.

    Args:
        device_id (int, opcional): ID do device a ser filtrado. Se None, retorna todos os devices.

    Returns:
        dict: Dados retornados pelo NetBox (device_list).
    """
    
    # Monta o filtro dinamicamente caso device_id seja fornecido
    filters = f"(filters: {{id: {device_id}}})" if device_id else ""
    
    # Query GraphQL completa para buscar devices + detalhes de interfaces
    GRAPHQL_QUERY = f"""
    query {{
    device_list{filters} {{
        id
        name
        role {{
            name
        }}
        site {{
            name
        }}
        tenant {{
            name
        }}
        primary_ip4 {{
            address
        }}
        interfaces {{
            name
            ip_addresses{{
                address
            }}
            description
            mtu
            mac_addresses {{
                mac_address
            }}
        }}
    }}
    }}
    """

    # Endpoint GraphQL do NetBox
    url = f"{NETBOX_URL}/graphql/"

    # Monta o payload JSON com a query
    payload = {"query": GRAPHQL_QUERY}
    
    try:
        # Executa a requisição POST
        response = requests.post(url, headers=HEADERS, json=payload, verify=False)
        response.raise_for_status() # Levanta erro se status code != 200
        result = response.json()    # Converte a resposta em JSON
        
        # Verifica se houve erros retornados pelo GraphQL
        if "errors" in result:
            print("❌ Erros na query GraphQL:", result["errors"])
            return None
        
        return result["data"] # Retorna apenas o bloco 'data'
    
    except requests.exceptions.RequestException as e:
        # Captura erros de conexão, timeout, etc.
        print(f"❌ Erro na requisição GraphQL: {e}")
        return None

# ----------------------------------------------
# Execução principal do script
# ----------------------------------------------
if __name__ == "__main__":
    # Chama a função para obter o device com ID 27
    data = get_data_device(27)
    
    # Se houver dados retornados
    if data:
        devices = data["device_list"] # Lista de devices
        
        # Itera sobre cada device retornado
        for device in devices:
            print(device)

